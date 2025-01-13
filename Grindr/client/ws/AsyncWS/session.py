import asyncio
from typing import Optional, Union, Literal, Tuple, Dict, List

from curl_cffi import CurlOpt, CurlHttpVersion
from curl_cffi.requests import AsyncSession, ExtraFingerprints, ExtraFpDict, BrowserTypeLiteral, ProxySpec, HeaderTypes, CookieTypes
from curl_cffi.requests.utils import set_curl_options, not_set

from Grindr.client.ws.AsyncWS.client import AsyncWebSocket, AsyncGrindrWebSocket


class AsyncWebSocketSession(AsyncSession):
    """
    Override the default curl_cffi AsyncSession to provide a custom instance of the WebSocket connection

    """

    async def ws_connect(
            self,
            url: str,
            autoclose: bool = True,
            params: Union[Dict, List, Tuple] | None = None,
            headers: HeaderTypes | None = None,
            cookies: CookieTypes | None = None,
            auth: Tuple[str, str] | None = None,
            timeout: Union[float, Tuple[float, float], object] | None = not_set,
            allow_redirects: bool | None = None,
            max_redirects: int | None = None,
            proxies: ProxySpec | None = None,
            proxy: str | None = None,
            proxy_auth: Tuple[str, str] | None = None,
            verify: bool | None = None,
            referer: str | None = None,
            accept_encoding: str | None = "gzip, deflate, br",
            impersonate: BrowserTypeLiteral | None = None,
            ja3: str | None = None,
            akamai: str | None = None,
            extra_fp: Union[ExtraFingerprints, ExtraFpDict] | None= None,
            default_headers: bool | None = None,
            quote: Union[str, Literal[False]] = "",
            http_version: CurlHttpVersion | None = None,
            interface: str | None = None,
            cert: Union[str, Tuple[str, str]] | None = None,
            max_recv_speed: int = 0,
    ) -> AsyncWebSocket:
        """Connects to a WebSocket.

        Args:
            url: url for the requests.
            autoclose: whether to close the WebSocket after receiving a close frame.
            params: query string for the requests.
            headers: headers to send.
            cookies: cookies to use.
            auth: HTTP basic auth, a tuple of (username, password), only basic auth is supported.
            timeout: how many seconds to wait before giving up.
            allow_redirects: whether to allow redirection.
            max_redirects: max redirect counts, default 30, use -1 for unlimited.
            proxies: dict of proxies to use, format: ``{"http": proxy_url, "https": proxy_url}``.
            proxy: proxy to use, format: "http://user@pass:proxy_url".
                Can't be used with `proxies` parameter.
            proxy_auth: HTTP basic auth for proxy, a tuple of (username, password).
            verify: whether to verify https certs.
            referer: shortcut for setting referer header.
            accept_encoding: shortcut for setting accept-encoding header.
            impersonate: which browser version to impersonate.
            ja3: ja3 string to impersonate.
            akamai: akamai string to impersonate.
            extra_fp: extra fingerprints options, in complement to ja3 and akamai strings.
            default_headers: whether to set default browser headers.
            quote: Set characters to be quoted, i.e. percent-encoded. Default safe string
                is ``!#$%&'()*+,/:;=?@[]~``. If set to a sting, the character will be removed
                from the safe string, thus quoted. If set to False, the url will be kept as is,
                without any automatic percent-encoding, you must encode the URL yourself.
            curl_options: extra curl options to use.
            http_version: limiting http version, defaults to http2.
            interface: which interface to use.
            cert: a tuple of (cert, key) filenames for client cert.
            max_recv_speed: maximum receive speed, bytes per second.
        """

        self._check_session_closed()

        curl = await self.pop_curl()
        set_curl_options(
            curl=curl,
            method="GET",
            url=url,
            base_url=self.base_url,
            params_list=[self.params, params],
            headers_list=[self.headers, headers],
            cookies_list=[self.cookies, cookies],
            auth=auth or self.auth,
            timeout=self.timeout if timeout is not_set else timeout,
            allow_redirects=self.allow_redirects if allow_redirects is None else allow_redirects,
            max_redirects=self.max_redirects if max_redirects is None else max_redirects,
            proxies_list=[self.proxies, proxies],
            proxy=proxy,
            proxy_auth=proxy_auth or self.proxy_auth,
            verify_list=[self.verify, verify],
            referer=referer,
            accept_encoding=accept_encoding,
            impersonate=impersonate or self.impersonate,
            ja3=ja3 or self.ja3,
            akamai=akamai or self.akamai,
            extra_fp=extra_fp or self.extra_fp,
            default_headers=self.default_headers if default_headers is None else default_headers,
            quote=quote,
            http_version=http_version or self.http_version,
            interface=interface or self.interface,
            max_recv_speed=max_recv_speed,
            cert=cert or self.cert,
            queue_class=asyncio.Queue,
            event_class=asyncio.Event,
        )
        curl.setopt(CurlOpt.CONNECT_ONLY, 2)  # https://curl.se/docs/websocket.html

        await self.loop.run_in_executor(None, curl.perform)
        return AsyncGrindrWebSocket(self, curl, autoclose=autoclose)
