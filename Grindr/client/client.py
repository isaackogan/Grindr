import asyncio
import logging
import os
import traceback
from asyncio import AbstractEventLoop, Task, CancelledError
from logging import Logger
from typing import Optional, Union, Callable, Type

from httpx import Proxy
from pydantic import ValidationError
from pyee import AsyncIOEventEmitter
from pyee.base import Handler

from Grindr.client.errors import AuthenticationDetailsMissingError, AlreadyConnectedError
from Grindr.client.logger import GrindrLogHandler, LogLevel
from Grindr.client.web.routes.fetch_session import SessionData, FetchSessionRoutePayload, FetchSessionRefreshRoutePayload
from Grindr.client.web.web_client import GrindrWebClient
from Grindr.client.web.web_settings import GRINDR_WS
from Grindr.client.ws.ws_client import GrindrWSClient
from Grindr.client.ws.ws_objects import WSMessage
from Grindr.client.ws.ws_settings import DEFAULT_WS_HEADERS
from Grindr.events import Event, DisconnectEvent
from Grindr.events.mappings import get_event


class GrindrClient(AsyncIOEventEmitter):
    """
    A client to connect to & read from TikTok LIVE streams

    """

    REFRESH_SESSION_INTERVAL: int = int(os.environ.get("GRINDR_REFRESH_INTERVAL", "600"))

    def __init__(
            self,
            web_proxy: Optional[Proxy] = None,
            ws_proxy: Optional[Proxy] = None,
            web_kwargs: dict = None,
            ws_kwargs: dict = None
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
            httpx_kwargs=web_kwargs or dict(),
            proxy=web_proxy
        )

        self._logger: Logger = GrindrLogHandler.get_logger(
            level=LogLevel.ERROR
        )

        # Properties
        self._session: Optional[SessionData] = None
        self._event_loop_task: Optional[Task] = None
        self._session_loop_task: Optional[Task] = None

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
        self._session = await self._web.fetch_session_new(
            params=None,
            body=FetchSessionRoutePayload(
                email=email,
                password=password
            )
        )

        # Update the headers
        self._web.set_session(self._session.sessionId)

        # Prevent dupes
        if self._ws.connected:
            raise AlreadyConnectedError("You can only make one connection per client!")

        # Start the websocket connection & return it
        self._event_loop_task = self._asyncio_loop.create_task(self._ws_loop())
        return self._event_loop_task

    async def refresh_session_loop(self) -> None:

        while self.connected:
            await asyncio.sleep(self.REFRESH_SESSION_INTERVAL)

            response: SessionData = await self._web.fetch_session_refresh(
                params=None,
                body=FetchSessionRefreshRoutePayload(
                    email=self._session.email,
                    token=self._session.sessionId,
                    authToken=self._session.authToken
                )
            )

            self._logger.debug("Refreshed Grindr client session!")
            self.web.set_session(response.sessionId)

    async def connect(self, **kwargs) -> Task:
        """
        Start a future-blocking connection to TikTokLive

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
        Start a thread-blocking connection to TikTokLive

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
        await self._event_loop_task

        # Reset state vars
        self._event_loop_task = None

    async def _ws_loop(self) -> None:
        """
        Run the websocket loop to handle incoming WS messages

        :return: None

        """

        # Emit events while connected
        first_event: bool = False

        async for message in self._ws.connect(uri=GRINDR_WS, headers={**self._web.headers, **DEFAULT_WS_HEADERS}):

            # Keep session continually updated
            if first_event:
                first_event = False
                self._session_loop_task = self._asyncio_loop.create_task(self.refresh_session_loop())

            try:
                ev: Event = get_event(message)
                self.emit(ev.event_type, ev)
            except ValidationError:
                self._logger.error("Failed to parse event due to validation error!\n" + traceback.format_exc())

        # After for loop finishes, disconnected
        ev = DisconnectEvent()
        self.emit(ev.event_type, ev)
        self._session_loop_task.cancel()

    def on(self, event: Type[Event], f: Optional[Callable] = None) -> Union[Handler, Callable[[Handler], Handler]]:
        """
        Decorator that can be used to register a Python function as an event listener

        :param event: The event to listen to
        :param f: The function to handle the event
        :return: The wrapped function as a generated `pyee.Handler` object

        """

        return super(GrindrClient, self).on(event.get_event_type(), f)

    def add_listener(self, event: Type[Event], f: Callable) -> Handler:
        """
        Method that can be used to register a Python function as an event listener

        :param event: The event to listen to
        :param f: The function to handle the event
        :return: The generated `pyee.Handler` object

        """
        if isinstance(event, str):
            return super().add_listener(event=event, f=f)

        return super().add_listener(event=event.get_event_type(), f=f)

    async def send(self, profile_id: int, text: str) -> None:
        await self._ws.ws.send(
            WSMessage.from_defaults(
                token=self._session.sessionId,
                profile_id=profile_id,
                text=text
            ).model_dump_json()
        )

    def has_listener(self, event: Type[Event]) -> bool:
        """
        Check whether the client is listening to a given event

        :param event: The event to check listening for
        :return: Whether it is being listened to

        """

        return event.__name__ in self._events

    @property
    def web(self) -> GrindrWebClient:
        """
        The HTTP client that this client uses for requests

        :return: A copy of the TikTokWebClient

        """

        return self._web

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
        Whether the WebSocket client is currently connected to TikTok

        :return: Connection status

        """

        return self._ws.connected

    @property
    def logger(self) -> logging.Logger:
        """
        The internal logger used by TikTokLive

        :return: An instance of a `logging.Logger`

        """

        return self._logger

    @property
    def session(self) -> SessionData:
        return self._session
