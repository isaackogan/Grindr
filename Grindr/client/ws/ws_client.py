import asyncio
import json
from typing import Optional, AsyncIterator, Dict

from curl_cffi.requests import AsyncSession

from Grindr.client.logger import GrindrLogHandler
from Grindr.client.ws.AsyncWS.client import AsyncWebSocket
from Grindr.events import WebsocketResponse
from . import AsyncWS


class GrindrWSClient:
    """Websocket client responsible for connections to Grindr"""

    def __init__(
            self,
            ws_kwargs: dict = None,
            proxy: str = None
    ):
        """
        Initialize GrindrWSClient

        :param ws_kwargs: Overrides for the websocket connection

        """

        self._ws_kwargs: dict = ws_kwargs or {}
        self._ws_cancel: Optional[asyncio.Event] = None
        self._ws: Optional[AsyncWebSocket] = None
        self._ws_proxy: Optional[str] = proxy
        self._logger = GrindrLogHandler.get_logger()

        if self._ws_proxy:
            self._ws_kwargs["proxy"] = self._ws_proxy

    async def disconnect(self) -> None:
        """
        Request to stop the websocket connection & wait
        :return: None

        """

        if not self.connected:
            return

        self._ws_cancel = asyncio.Event()
        await self._ws_cancel.wait()
        self._ws_cancel = None

    async def connect(
            self,
            uri: str,
            headers: Dict[str, str]
    ) -> AsyncIterator[WebsocketResponse]:
        """
        Connect to the Webcast websocket server & handle cancellation

        :param uri:
        :param headers:
        :return:
        """

        # Reset the cancel var
        self._ws_cancel = None

        # Yield while existent
        async for webcast_message in self.connect_loop(uri, headers):
            yield webcast_message

        # After loop breaks, gracefully shut down & send the cancellation event
        if self._ws_cancel is not None:
            await self._ws.close()
            self._ws_cancel.set()

    async def connect_loop(
            self,
            url: str,
            headers: Dict[str, str]
    ) -> AsyncIterator[WebsocketResponse]:
        # Run connection loop
        async with AsyncWS.connect(
                url=self._ws_kwargs.pop("url", url),
                headers={**headers, **self._ws_kwargs.pop("headers", {})},
                **self._ws_kwargs
        ) as websocket:
            self._ws = websocket

            # Each time we receive a message, process it
            async for message in websocket:

                yield WebsocketResponse(**json.loads(message))

                # Handle cancellation request
                if self._ws_cancel is not None:
                    return

            if self._ws_cancel is not None:
                return

    @property
    def connected(self) -> bool:
        """
        Check if the websocket is currently connected

        :return: Connection status

        """

        return self._ws and self._ws.keep_running

    @property
    def ws(self) -> AsyncWebSocket:
        return self._ws
