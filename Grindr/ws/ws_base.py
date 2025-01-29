import asyncio
from typing import AsyncIterator

from Grindr.client.ext.client_logger import GrindrLogHandler
from Grindr.web.tls_match.tls_match import create_client_kwargs
from Grindr.ws.lib.async_session import AsyncGrindrWSSession
from Grindr.ws.lib.async_ws import AsyncGrindrWS


class BaseGrindrWebSocketClient:
    """Websocket client responsible for connections to Grindr"""

    def __init__(
            self,
            ws_kwargs: dict = None,
            ws_proxy: str | None = None
    ):
        """
        Initialize GrindrWSClient

        :param ws_kwargs: Overrides for the websocket connection

        """

        self._ws_kwargs: dict = ws_kwargs or {}
        self._ws_cancel: asyncio.Event | None = None
        self._ws: AsyncGrindrWS | None = None
        self._ws_proxy: str | None = ws_proxy or ws_kwargs.get("proxy")
        self._logger = GrindrLogHandler.get_logger()

    @property
    def ws(self) -> AsyncGrindrWS | None:
        """
        Get the current WS

        :return: WS

        """

        return self._ws

    @property
    def connected(self) -> bool:
        """
        Check if the WebSocket is open

        :return: WebSocket status

        """

        return self.ws and not self.ws.closed

    async def disconnect(self) -> None:
        """
        Request to stop the websocket connection & wait
        :return: None

        """

        if not self.connected:
            return

        await self._ws.close()

    async def connect(
            self,
            url: str,
            headers: dict[str, str]
    ) -> AsyncIterator[bytes]:

        # Build the kwargs object
        ws_kwargs: dict = self._ws_kwargs.copy()
        ws_kwargs["proxy"] = ws_kwargs.get("proxy", self._ws_proxy)
        ws_kwargs["headers"] = {**ws_kwargs.get("headers", {}), **headers}

        # Create the full client kwargs that respects the ja3
        client_kwargs = create_client_kwargs(**ws_kwargs)

        # Connect to the WS & return responses
        async with AsyncGrindrWSSession(**client_kwargs) as session:
            self._ws = await session.ws_connect(url=url)

            async for message in self._ws:
                yield message

        # When disconnecting, set the WS to None
        self._ws = None
