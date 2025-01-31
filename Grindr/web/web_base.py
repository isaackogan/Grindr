import logging
import textwrap
from functools import cached_property
from typing import Any, Literal

import curl_cffi.requests
from curl_cffi.requests import AsyncSession, Response

from Grindr.client.ext.client_logger import GrindrLogHandler
from Grindr.web.tls_match.tls_match import create_async_client
from Grindr.web.web_extras import generate_device_info_android
from Grindr.web.web_settings import DEFAULT_REQUEST_PARAMS, DEFAULT_REQUEST_HEADERS


class GrindrHTTPClient:
    """
    HTTP Client for making requests to the Grindr API

    """

    def __init__(
            self,
            web_curl_proxy: str | None = None,
            web_curl_kwargs: dict | None = None,
    ):
        """
        Create an HTTP client for interacting with the various APIs

        :param web_curl_proxy: An optional proxy for the HTTP client
        :param web_curl_kwargs: Additional kwargs

        """

        # HTTP Client Session
        web_curl_kwargs: dict = (web_curl_kwargs or {})

        self.headers = {**web_curl_kwargs.pop("headers", {}), **DEFAULT_REQUEST_HEADERS}
        self.params: dict[str, Any] = {**(web_curl_kwargs or {}).pop("params", {}), **DEFAULT_REQUEST_PARAMS}
        self.headers['L-Device-Info'] = generate_device_info_android()
        self.logger.debug('Creating HTTP client')
        self._http_session = create_async_client(proxy=web_curl_proxy, **web_curl_kwargs)

    def set_proxy(self, proxy: str | None):
        """Update the current proxy on the client"""
        self._http_session.proxies = {"all": proxy}

    def clear_cookies(self):
        """Clear the cookies on the client"""
        self._http_session.cookies.clear()

    @property
    def http_session(self) -> AsyncSession:
        """The HTTP client for the API"""
        return self._http_session

    async def close(self) -> None:
        """Close the HTTP client gracefully"""
        await self._http_session.close()

    @cached_property
    def logger(self) -> logging.Logger:
        """Logger for the HTTP client"""
        return GrindrLogHandler.get_logger()

    @property
    def android_device_id(self) -> str:
        """Extract the uuid4 Device ID from the device info"""
        return self.headers['L-Device-Info'].split(";")[0]

    async def request(
            self,
            method: Literal["GET", "POST", "PUT", "DELETE"],
            base_url: str,
            *,
            extra_params: dict = None,
            extra_headers: dict = None,
            web_client: AsyncSession | None = None,
            base_params: bool = True,
            base_headers: bool = True,
            file_logger: Any | None = None,
            **kwargs
    ) -> Response:
        """Make a request to the Grindr API"""

        headers: dict = {**(self.headers if base_headers else {}), **(extra_headers or {})}
        params: dict[str, str] = {**(self.params if base_params else {}), **(extra_params or {})}

        # Make the request
        response: curl_cffi.requests.Response = await (web_client or self._http_session).request(
            method=method,
            url=base_url,
            params=params,
            headers=headers,
            **kwargs
        )

        if file_logger:
            file_logger.log(
                response=response,
                headers=headers,
                params=params,
                kwargs=kwargs
            )

        return response


class URLTemplate:
    """A simple URL template to build requests on the fly"""

    def __init__(self, base_url: str, path: str):
        """
        Create the URL template
        :param base_url: The URL acting as a template

        """

        self._url: str = textwrap.dedent(
            (base_url.rstrip("/") + "/" + path.lstrip("/"))
            .replace("\n", " ")
            .replace(" ", "")
        )

    def __mod__(self, data: dict) -> str:
        """
        Overload modulus operator to allow formatting
        :param data: The data to format the URL with
        :return: The filled template

        """

        # Take the params and add them and return a string
        data = {k: str(v).lower() if isinstance(str, bool) else v for k, v in data.items() if v is not None}
        d = self._url.format(**data)
        return d
