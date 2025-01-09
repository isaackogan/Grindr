import json
import logging
from typing import Union, Type, AsyncIterator

import httpx
from python_socks import ProxyType, parse_proxy_url
from websockets.legacy.client import Connect, WebSocketClientProtocol
from websockets.legacy.exceptions import InvalidStatusCode
from websockets_proxy import websockets_proxy
from websockets_proxy.websockets_proxy import ProxyConnect

from Grindr.events import WebsocketResponse

"""Type hint for a WebcastProxy, which can be either an HTTPX Proxy or a Websockets Proxy"""
GrindrWSProxy: Type = Union[httpx.Proxy, websockets_proxy.Proxy]
GrindrWSIterator: Type = AsyncIterator[WebsocketResponse]


class GrindrConnect(Connect):

    def __init__(
            self,
            logger: logging.Logger,
            uri: str | None = None,
            **kwargs
    ):
        super().__init__(uri, logger=logger, **kwargs)
        self.logger = self._logger = logger
        self._ws: WebSocketClientProtocol | None = None

    @property
    def ws(self) -> WebSocketClientProtocol | None:
        """Get the current WebSocketClientProtocol"""

        return self._ws

    async def __aiter__(self) -> GrindrWSIterator:
        try:
            async with self as protocol:
                self._ws = protocol
                async for message in protocol:
                    yield WebsocketResponse(**json.loads(message))
        except InvalidStatusCode:
            raise
        finally:
            self._ws = None


class GrindrProxyConnect(ProxyConnect, GrindrConnect):
    """
    Add Proxy support to the WebcastConnect class

    """

    def __init__(
            self,
            proxy: GrindrWSProxy | None,
            **kwargs
    ):
        super().__init__(
            proxy=self._convert_proxy(proxy) if isinstance(proxy, httpx.Proxy) else proxy,
            **kwargs
        )

    @classmethod
    def _convert_proxy(cls, proxy: httpx.Proxy) -> websockets_proxy.Proxy:
        """Convert an HTTPX proxy to a websockets_proxy Proxy"""
        parsed: tuple[ProxyType, str, int, str, str] | None = parse_proxy_url(str(proxy.url))
        parsed: list = list(parsed)

        # Add auth back
        parsed[3] = proxy.auth[0]
        parsed[4] = proxy.auth[1]

        return websockets_proxy.Proxy(*parsed)
