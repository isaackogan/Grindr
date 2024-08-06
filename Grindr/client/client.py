from __future__ import annotations

import asyncio
import logging
import os
import traceback
import uuid
from asyncio import AbstractEventLoop, Task, CancelledError
from logging import Logger
from typing import Optional, Dict, List

from pydantic import ValidationError

from Grindr.client.emitter import GrindrEmitter
from Grindr.client.errors import AuthenticationDetailsMissingError, AlreadyConnectedError
from Grindr.client.extension import Extension
from Grindr.client.logger import GrindrLogHandler, LogLevel
from Grindr.client.web.routes.fetch_session import SessionData, FetchSessionRoutePayload, FetchSessionRefreshRoutePayload, FetchSessionRouteResponse
from Grindr.client.web.web_client import GrindrWebClient
from Grindr.client.web.web_settings import GRINDR_WS
from Grindr.client.ws.ws_client import GrindrWSClient
from Grindr.client.ws.ws_settings import DEFAULT_WS_HEADERS
from Grindr.events import Event, DisconnectEvent, ConnectEvent
from Grindr.events.mappings import get_event
from Grindr.models.context import Context
from Grindr.models.conversation import Conversation
from Grindr.models.inbox import Inbox
from Grindr.models.profile import Profile


class GrindrClient(GrindrEmitter):
    """
    A client to connect to & read from Grindr

    """

    REFRESH_SESSION_INTERVAL: int = int(os.environ.get("GRINDR_REFRESH_INTERVAL", "1200"))

    def __init__(
            self,
            web_proxy: Optional[str] = None,
            ws_proxy: Optional[str] = None,
            web_kwargs: dict = None,
            ws_kwargs: dict = None,
            extensions: Optional[List[Extension]] = None
    ):
        """
        Instantiate the GrindrClient object

        :param web_proxy: An optional proxy used for HTTP requests
        :param ws_proxy: An optional proxy used for the WebSocket connection
        :param web_kwargs: Optional arguments used by the HTTP client
        :param ws_kwargs: Optional arguments used by the WebSocket client

        """

        super().__init__()

        self._ws: GrindrWSClient = GrindrWSClient(
            ws_kwargs=ws_kwargs or dict(),
            proxy=ws_proxy
        )

        self._web: GrindrWebClient = GrindrWebClient(
            session_kwargs=web_kwargs or dict(),
            proxy=web_proxy
        )

        self._logger: Logger = GrindrLogHandler.get_logger(
            level=LogLevel.ERROR
        )

        # Properties
        self._email: Optional[str] = None
        self._session: Optional[SessionData] = None
        self._context: Optional[Context] = None
        self._event_loop_task: Optional[Task] = None
        self._session_loop_task: Optional[Task] = None
        self._extensions: Dict[str, Extension] = dict()

        self.add_extensions(*extensions or [])

    async def start(
            self,
            *,
            email: str,
            password: str
    ) -> Task:
        """
        Create a non-blocking connection to Grindr & return the task. The username/password OR session token must be passed, not both.

        :param email: The username of the user
        :param password: The password of the user.
        :return: Task containing the heartbeat of the client

        """

        if email is None or password is None:
            raise AuthenticationDetailsMissingError("Authentication details must be sent! Either username/password, or session_token.")

        # Generate the session
        await self.login(
            email=email,
            password=password
        )

        self._context = Context(
            profile_id=self._session.profileId,
            _web=self.web,
            _ws=self.ws,
            _emitter=self
        )

        # Prevent dupes
        if self._ws.connected:
            raise AlreadyConnectedError("You can only make one connection per client!")

        # Start the websocket connection & return it
        self._event_loop_task = self._asyncio_loop.create_task(self._ws_loop())
        return self._event_loop_task

    async def login(
            self,
            email: str,
            password: str
    ) -> SessionData:

        self._email = email

        self._session = await self._web.fetch_session_new(
            body=FetchSessionRoutePayload(
                email=self._email,
                password=password
            )
        )

        self._web.set_session(self._session.sessionId)
        return self._session

    async def _refresh_session_loop(self) -> None:

        while self.connected:

            # Note: Sessions expire after 30 minutes
            await asyncio.sleep(self.REFRESH_SESSION_INTERVAL)

            try:
                response: SessionData = await self._web.fetch_session_refresh(
                    body=FetchSessionRefreshRoutePayload(
                        email=self._email,
                        token=self._session.sessionId,
                        authToken=self._session.authToken
                    )
                )

                self._logger.debug("Refreshed Grindr client session!")
                self.web.set_session(response.sessionId)
            except Exception as ex:
                self._logger.error("Failed to refresh session!")
                raise ex

    async def connect(self, **kwargs) -> Task:
        """
        Start a future-blocking connection to Grindr

        :param kwargs: Kwargs to pass to start
        :return: The task, once it's finished

        """

        task: Task = await self.start(**kwargs)

        try:
            await task
        except CancelledError:
            self._logger.debug("The client has been manually stopped with 'client.stop()'.")

        return task

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

        # Wait gracefully for things to finish
        await self._ws.disconnect()
        await self._unload_extensions()
        await self._event_loop_task

        # Reset state vars
        self._event_loop_task = None

    async def _ws_loop(self) -> None:
        """
        Run the websocket loop to handle incoming WS messages

        :return: None

        """

        # Emit events while connected
        first_event: bool = True

        async for message in self._ws.connect(uri=GRINDR_WS, headers={**self._web.headers, **DEFAULT_WS_HEADERS, "Sec-Websocket-Key": "8y/TkqcKQ6snPVQTsvpvWg=="}):

            # Keep session continually updated
            if first_event:
                first_event = False
                await self._on_connect()

            try:
                ev: Event = get_event(message)
                self.emit(ev.event_type, ev)
            except ValidationError:
                self._logger.error("Failed to parse event due to validation error!\n" + traceback.format_exc())

        # After for loop finishes, disconnected
        await self._on_disconnect()

    async def _on_connect(self):
        """Handle the client connect"""
        await self._load_extensions()
        self._session_loop_task = self._asyncio_loop.create_task(self._refresh_session_loop())

    async def _on_disconnect(self):
        """Handle the client disconnect"""

        ev = DisconnectEvent()
        self.emit(ev.event_type, ev)
        self._session_loop_task.cancel()

    @property
    def web(self) -> GrindrWebClient:
        """
        The HTTP client that this client uses for requests

        :return: A copy of the GrindrWebClient

        """

        return self._web

    @property
    def ws(self) -> GrindrWSClient:
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
        """
        Whether the WebSocket client is currently connected to Grindr

        :return: Connection status

        """

        return self._ws.connected

    @property
    def logger(self) -> logging.Logger:
        """
        The internal logger used by Grindr

        :return: An instance of a `logging.Logger`

        """

        return self._logger

    @property
    def session(self) -> SessionData:
        return self._session

    async def retrieve_profile(self, profile_id: int) -> Profile:
        conversation: Conversation = self.get_conversation(profile_id=profile_id)
        profile: Profile = await conversation.retrieve_profile()
        return profile

    async def retrieve_conversation(self, profile_id: int) -> Conversation:
        conversation: Conversation = self.get_conversation(profile_id=profile_id)
        return await conversation.retrieve_all()

    def get_conversation(self, profile_id: Optional[int]):
        return Conversation.from_defaults(
            target_id=profile_id,
            context=self._context
        )

    async def get_inbox(self) -> Inbox:
        return Inbox.from_defaults(
            context=self._context
        )

    async def retrieve_inbox(self) -> Inbox:
        inbox: Inbox = await self.get_inbox()
        return await inbox.retrieve_all()

    def add_extensions(self, *extensions: Extension) -> List[str]:
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
        self._logger.debug(f"Loaded the {extension.__class__.__name__} extension with ID {extension_id}")
        return extension_id

    async def unload_extension(self, extension: Extension):
        """Unload an extension manually"""

        instance = self._extensions.get(extension.instance_id)

        if instance is None:
            return

        await instance.unload()
        self._logger.debug(f"Unloaded the {extension.__class__.__name__} extension with ID {extension.instance_id}")
        del self._extensions[extension.instance_id]

    async def _load_extensions(self) -> None:
        """Load multiple extensions"""

        for instance_id, extension in self._extensions.copy().items():
            await self.load_extension(extension)

    async def _unload_extensions(self) -> None:
        """Unload all extensions"""

        for extension in self._extensions.values():
            await self.unload_extension(extension)

    @property
    def profile_id(self) -> int:
        return int(self._session.profileId)
