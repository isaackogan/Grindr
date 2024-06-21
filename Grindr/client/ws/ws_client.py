import asyncio
import json
from typing import Optional, AsyncIterator, Dict, Any, Callable, Tuple

from httpx import Proxy
from python_socks import parse_proxy_url, ProxyType
from websockets.legacy.client import Connect, WebSocketClientProtocol
from websockets_proxy import websockets_proxy
from websockets_proxy.websockets_proxy import ProxyConnect

from Grindr.client.logger import GrindrLogHandler
from Grindr.events import WebsocketResponse


class WebcastProxyConnect(ProxyConnect):

    def __init__(self, uri: str, *, proxy: Optional[Proxy], **kwargs):
        self.logger = kwargs.get("logger", GrindrLogHandler.get_logger())
        super().__init__(uri, proxy=proxy, **kwargs)


class GrindrWSClient:
    """Websocket client responsible for connections to TikTok"""

    def __init__(
            self,
            ws_kwargs: dict = None,
            proxy: Optional[Proxy] = None
    ):
        """
        Initialize WebcastWSClient

        :param ws_kwargs: Overrides for the websocket connection

        """

        self._ws_kwargs: dict = ws_kwargs or {}
        self._ws_cancel: Optional[asyncio.Event] = None
        self._ws: Optional[WebSocketClientProtocol] = None
        self._ws_proxy: Optional[Proxy] = proxy
        self._logger = GrindrLogHandler.get_logger()

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

    def build_connection_args(
            self,
            uri: str,
            headers: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Build the `websockets` library connection arguments dictionary

        :param uri: URI to connect to TikTok
        :param headers: Headers to send to TikTok on connecting
        :return: Connection dictionary

        DEVELOP SANITY NOTE:

        When ping_timeout is set (i.e. not None), the client waits for a pong for N seconds.
        TikTok DO NOT SEND pongs back. Unfortunately the websockets client after N seconds assumes the server is dead.
        It then throws the following infamous exception:

        websockets.exceptions.ConnectionClosedError: sent 1011 (unexpected error) keepalive ping timeout; no close frame received

        If you set ping_timeout to None, it doesn't wait for a pong. Perfect, since TikTok don't send them.
        """

        # Copy & remove ping intervals so people can't destroy their clients by accident
        ws_kwargs = self._ws_kwargs.copy()
        ws_kwargs.pop("ping_timeout", None)

        base_config: dict = (
            {
                "subprotocols": ["echo-protocol"],
                "ping_timeout": None,  # DO NOT OVERRIDE THIS. SEE DOCSTRING.
                "ping_interval": 10.0,
                "logger": self._logger,
                "uri": self._ws_kwargs.pop("uri", uri),
                "extra_headers": {**headers, **self._ws_kwargs.pop("headers", {})},
                **self._ws_kwargs
            }
        )

        if self._ws_proxy is not None:
            base_config["proxy_conn_timeout"] = 10.0
            base_config["proxy"] = self._convert_proxy()

        return base_config

    def _convert_proxy(self) -> websockets_proxy.Proxy:

        # (proxy_type, host, port, username, password)
        parsed: Tuple[ProxyType, str, int, Optional[str], Optional[str]] = parse_proxy_url(str(self._ws_proxy.url))
        parsed: list = list(parsed)

        # Add auth back
        parsed[3] = self._ws_proxy.auth[0]
        parsed[4] = self._ws_proxy.auth[1]

        return websockets_proxy.Proxy(*parsed)

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
            uri: str,
            headers: Dict[str, str]
    ) -> AsyncIterator[WebsocketResponse]:

        connect: Callable = WebcastProxyConnect if self._ws_proxy else Connect

        # Run connection loop
        async for websocket in connect(**self.build_connection_args(uri, headers)):

            # Update the stored websocket
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

        return self._ws and self._ws.open

    @property
    def ws(self) -> WebSocketClientProtocol:
        return self._ws
