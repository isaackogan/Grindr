import logging
from functools import cached_property
from pathlib import Path
from typing import Any, Literal

import curl_cffi.requests
from curl_cffi.requests import AsyncSession, Response

from Grindr.client.ext.client_logger import GrindrLogHandler
from Grindr.web.routes.fetch.fetch_session import FetchSessionRouteResponse, FetchSessionRefreshRoutePayload, FetchSessionNewRoutePayload, SessionCredentials
from Grindr.web.tls_match.tls_match import create_async_client
from Grindr.web.web_extras import generate_device_info_android
from Grindr.web.web_logger import GrindrWebFileLogger
from Grindr.web.web_schemas import GrindrHTTPClientAuthSession
from Grindr.web.web_settings import DEFAULT_REQUEST_PARAMS, DEFAULT_REQUEST_HEADERS


class GrindrHTTPClient:
    """
    HTTP Client for making requests to the Grindr API

    """

    def __init__(
            self,
            web_proxy: str | None = None,
            web_kwargs: dict | None = None,
            credentials: SessionCredentials | None = None
    ):
        """
        Create an HTTP client for interacting with the various APIs

        :param web_proxy: An optional proxy for the HTTP client
        :param web_kwargs: Additional kwargs

        """

        # Local time in format DD/MM/YYYY HH:MM:SS
        self._auth_session: GrindrHTTPClientAuthSession = GrindrHTTPClientAuthSession(credentials=credentials)
        self._user_agent: str | None = None

        # File Logger
        log_dir: str | None = web_kwargs.pop('request_dump_directory') if web_kwargs else None
        self._file_logger: GrindrWebFileLogger | None = GrindrWebFileLogger(Path(log_dir), self._auth_session) if log_dir else None

        # HTTP Client Session
        self.headers = {**(web_kwargs or {}).pop("headers", {}), **DEFAULT_REQUEST_HEADERS}
        self.params: dict[str, Any] = {**(web_kwargs or {}).pop("params", {}), **DEFAULT_REQUEST_PARAMS}
        self.headers['L-Device-Info'] = generate_device_info_android()
        self.logger.debug('Creating HTTP client')
        self._http_session = create_async_client(proxy=web_proxy, **web_kwargs)

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

    @property
    def auth_session(self) -> GrindrHTTPClientAuthSession:
        """The current auth session"""
        return self._auth_session

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

        if self._file_logger:
            self._file_logger.log(
                response=response,
                headers=headers,
                params=params,
                kwargs=kwargs
            )

        return response

    def update_session_credentials(
            self,
            *,
            details: FetchSessionNewRoutePayload | FetchSessionRefreshRoutePayload
    ) -> GrindrHTTPClientAuthSession:
        """Update the credentials attached to a session object"""

        self._auth_session.credentials = details
        return self._auth_session

    def update_session_data(
            self,
            *,
            session_data: FetchSessionRouteResponse,
    ) -> GrindrHTTPClientAuthSession:
        """Update the current session data used by the client"""

        self._auth_session.session_data = session_data
        self.headers['Authorization'] = f'Grindr3 {session_data.session_id}'

        return self._auth_session
