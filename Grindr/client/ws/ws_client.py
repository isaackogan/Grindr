import asyncio
from ssl import SSLContext
from typing import Optional, AsyncIterator, Union, Type

from websockets.legacy.client import WebSocketClientProtocol

from Grindr.client.logger import GrindrLogHandler
from Grindr.client.web.tls_patch.tls_patch import patched_ssl_context
from Grindr.client.ws.ws_connect import GrindrConnect, GrindrProxyConnect, GrindrWSProxy
from Grindr.events import WebsocketResponse


class GrindrWSClient:
    """Websocket client responsible for connections to Grindr"""

    def __init__(
            self,
            ws_kwargs: dict = None,
            ws_proxy: GrindrWSProxy = None,
            ws_ssl_context: SSLContext | None = None
    ):
        """
        Initialize GrindrWSClient

        :param ws_kwargs: Overrides for the websocket connection

        """

        self._ws_kwargs: dict = ws_kwargs or {}
        self._ws_cancel: asyncio.Event | None = None
        self._ws: Optional = None
        self._ws_proxy: str | None = ws_proxy or ws_kwargs.get("proxy")
        self._ssl_context: SSLContext | None = ws_ssl_context or ws_kwargs.get('ws_ssl_context', patched_ssl_context())
        self._logger = GrindrLogHandler.get_logger()
        self._connect_generator_class: Union[Type[GrindrConnect], Type[GrindrProxyConnect]] = GrindrProxyConnect if self._ws_proxy else GrindrConnect
        self._connection_generator: Union[GrindrConnect, GrindrProxyConnect | None] = None

    @property
    def ws(self) -> WebSocketClientProtocol | None:
        """
        Get the current WebSocketClientProtocol

        :return: WebSocketClientProtocol

        """

        # None because there's no generator
        if not self._connection_generator:
            return None

        # WebSocketClientProtocol | None
        return self._connection_generator.ws

    @property
    def connected(self) -> bool:
        """
        Check if the WebSocket is open

        :return: WebSocket status

        """

        return self.ws and self.ws.open

    async def disconnect(self) -> None:
        """
        Request to stop the websocket connection & wait
        :return: None

        """

        if not self.connected:
            return

        await self.ws.close()

    async def connect(
            self,
            url: str,
            headers: dict[str, str]
    ) -> AsyncIterator[WebsocketResponse]:

        ws_kwargs: dict = self._ws_kwargs.copy()

        if self._ws_proxy is not None:
            ws_kwargs["proxy_conn_timeout"] = ws_kwargs.get("proxy_conn_timeout", 10.0)
            ws_kwargs["proxy"] = self._ws_proxy

        self._connection_generator = self._connect_generator_class(
            uri=url,
            extra_headers=headers,
            logger=self._logger,
            ssl=self._ssl_context,
            **ws_kwargs
        )

        async for message in self._connection_generator:
            yield message
