from __future__ import annotations

import asyncio
import logging
import traceback
import uuid
from asyncio import AbstractEventLoop, Task, CancelledError
from functools import cached_property
from typing import Any

from pydantic import ValidationError

from Grindr.client.errors import AlreadyConnectedError
from Grindr.client.ext.client_emitter import GrindrEventEmitter
from Grindr.client.ext.client_extension import Extension
from Grindr.client.ext.client_logger import GrindrLogHandler, LogLevel
from Grindr.client.schemas.conversation import Conversation
from Grindr.client.schemas.inbox import Inbox
from Grindr.client.schemas.profile import Profile
from Grindr.client.schemas.sessioncontext import SessionContext
from Grindr.web.routes.fetch.fetch_session import SessionCredentials
from Grindr.web.web_client import GrindrWebClient
from Grindr.web.web_settings import GRINDR_WS
from Grindr.ws.events.events import DisconnectEvent
from Grindr.ws.ws_client import GrindrWebSocketClient
from Grindr.ws.ws_settings import DEFAULT_WS_HEADERS


class GrindrClient(GrindrEventEmitter):
    """
    An HTTP client to connect to & read from Grindr

    """

    def __init__(
            self,
            web_credentials: SessionCredentials,
            web_curl_proxy: str | None = None,
            web_curl_kwargs: dict[str, Any] = None,
            web_request_dump_directory: str | None = None,
            web_max_auth_retries: int = 2,
            ws_proxy: str | None = None,
            ws_kwargs: dict[str, Any] = None,

    ):
        """
        Instantiate the GrindrClient object

        :param web_curl_proxy: An optional proxy used for HTTP requests
        :param ws_proxy: An optional proxy used for the WebSocket connection
        :param web_curl_kwargs: Optional arguments used by the HTTP client
        :param ws_kwargs: Optional arguments used by the WebSocket client
        :param web_credentials: The session credentials to use

        """

        super().__init__()

        self._web: GrindrWebClient = GrindrWebClient(
            web_curl_kwargs=web_curl_kwargs,
            web_curl_proxy=web_curl_proxy,
            web_credentials=web_credentials,
            web_request_dump_directory=web_request_dump_directory,
            web_max_auth_retries=web_max_auth_retries
        )

        self._ws: GrindrWebSocketClient = GrindrWebSocketClient(
            ws_kwargs=ws_kwargs or dict(),
            ws_proxy=ws_proxy,
            auth_session=self._web.auth_session
        )

        self._context: SessionContext | None = None
        self._event_loop_task: Task | None = None
        self._extensions: dict[str, Extension] = dict()

    async def start(self, *, use_auth_token: bool = True) -> Task:
        """
        Create a non-blocking connection to Grindr & return the task.
        :return: Task containing the heartbeat of the client

        """

        await self._web.refresh_session_data(use_auth_token=use_auth_token)

        self._context = SessionContext(
            web=self.web,
            ws=self.ws,
            emitter=self
        )

        # Prevent duplicate connections
        if self._ws.connected:
            raise AlreadyConnectedError("You can only make one connection per client!")

        # Start the websocket connection & return it
        self.logger.debug("Starting the Grindr client event loop...")
        self._event_loop_task = self._asyncio_loop.create_task(self._ws_loop())
        return self._event_loop_task

    async def connect(self, **kwargs) -> Task:
        """
        Start a future-blocking connection to Grindr

        :param kwargs: Kwargs to pass to start
        :return: The task, once it's finished

        """

        try:
            task: Task = await self.start(**kwargs)
            return await task
        except CancelledError:
            self.logger.debug("The client has been manually stopped with 'client.stop()'.")
        except Exception:
            await self.web.close()
            self.logger.error("An error occurred while running the client!\n" + traceback.format_exc())
            raise

    def run(self, **kwargs) -> Task:
        """
        Start a thread-blocking connection to Grindr

        :param kwargs: Kwargs to pass to start
        :return: The task, once it's finished

        """

        return self._asyncio_loop.run_until_complete(self.connect(**kwargs))

    async def disconnect(self) -> None:
        """
        Disconnect the client from the websocket

        :return: None

        """

        await self._ws.disconnect()
        await self._event_loop_task
        self._event_loop_task = None

    async def _ws_loop(self) -> None:
        """Listen for events on the Grindr WebSocket"""

        first_event: bool = True
        async for event in self._ws.connect(url=GRINDR_WS, headers={**self._web.headers, **DEFAULT_WS_HEADERS}):

            # Keep session continually updated
            if first_event:
                first_event = False
                await self._load_extensions()

            try:
                self.emit(event.type, event)
            except ValidationError:
                self.logger.error("Failed to parse event due to validation error!\n" + traceback.format_exc())

        # After for loop finishes, disconnected
        self.emit(DisconnectEvent())
        await self._unload_extensions()
        await self._web.close()

    @cached_property
    def web(self) -> GrindrWebClient:
        """
        The HTTP client that this client uses for requests

        :return: A copy of the GrindrWebClient

        """

        return self._web

    @property
    def ws(self) -> GrindrWebSocketClient:
        """
        The HTTP client that this client uses for requests

        :return: A copy of the GrindrWSClient

        """

        return self._ws

    @property
    def _asyncio_loop(self) -> AbstractEventLoop:
        """
        Property to return the existing or generate a new asyncio event loop

        :return: An asyncio event loop

        """

        try:
            return asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.new_event_loop()

    @property
    def connected(self) -> bool:
        """Whether the WebSocket client is currently connected to Grindr"""
        return self._ws.connected

    @cached_property
    def logger(self) -> logging.Logger:
        """Logger for the Grindr client"""
        return GrindrLogHandler.get_logger(level=LogLevel.ERROR)

    async def retrieve_profile(self, profile_id: int) -> Profile:
        """Retrieve a profile by ID"""
        conversation: Conversation = self.get_conversation(profile_id=profile_id)
        profile: Profile = await conversation.retrieve_profile()
        return profile

    async def retrieve_conversation(self, profile_id: int) -> Conversation:
        """Retrieve a conversation by ID"""
        conversation: Conversation = self.get_conversation(profile_id=profile_id)
        return await conversation.retrieve_all()

    def get_conversation(self, profile_id: int | None):
        """Get a conversation by ID"""
        return Conversation.from_defaults(
            target_id=profile_id,
            context=self._context
        )

    async def get_inbox(self) -> Inbox:
        """Get the inbox object"""
        return Inbox.from_data(
            context=self._context
        )

    async def retrieve_inbox(self) -> Inbox:
        """Retrieve the inbox"""
        inbox: Inbox = await self.get_inbox()
        return await inbox.retrieve_all()

    def add_extensions(self, *extensions: Extension) -> list[str]:
        """Add multiple extensions"""
        return [self.add_extension(extension) for extension in extensions]

    def add_extension(self, extension: Extension) -> str:
        """Add an extension to be loaded on connect"""

        extension_id: str = str(uuid.uuid4())
        self._extensions[extension_id] = extension
        return extension_id

    async def load_extension(self, extension: Extension) -> str:
        """Load a single extension"""

        if not (extension_id := self._extensions.get(extension.instance_id)):
            extension_id = self.add_extension(extension)

        await extension.load(client=self, instance_id=extension_id)
        self.logger.debug(f"Loaded the {extension.__class__.__name__} extension with ID {extension_id}")
        return extension_id

    async def unload_extension(self, extension: Extension):
        """Unload an extension manually"""

        instance = self._extensions.get(extension.instance_id)

        if instance is None:
            return

        await instance.unload()
        self.logger.debug(f"Unloaded the {extension.__class__.__name__} extension with ID {extension.instance_id}")
        del self._extensions[extension.instance_id]

    async def _load_extensions(self) -> None:
        """Load multiple extensions"""

        for instance_id, extension in self._extensions.copy().items():
            await self.load_extension(extension)

    async def _unload_extensions(self) -> None:
        """Unload all extensions"""

        for extension in self._extensions.values():
            await self.unload_extension(extension)
