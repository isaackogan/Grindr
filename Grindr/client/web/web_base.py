import json
import logging
import os
import random
import textwrap
import traceback
import uuid
from functools import cached_property
from json import JSONDecodeError
from typing import Any, Literal, ForwardRef, Type

import curl_cffi.requests
from curl_cffi.requests import AsyncSession, Response
from pydantic import BaseModel, ValidationError, TypeAdapter

from Grindr.client.errors import CloudflareWAFResponse, LoginFailedResponse, GrindrRequestError, AccountBannedError
from Grindr.client.logger import GrindrLogHandler
from Grindr.client.tls_match.tls_match import create_async_client
from Grindr.client.web.web_settings import DEFAULT_REQUEST_PARAMS, DEFAULT_REQUEST_HEADERS, get_mobile_user_agent, get_desktop_user_agent


class GrindrHTTPClient:

    def __init__(
            self,
            web_proxy: str | None = None,
            web_kwargs: dict | None = None
    ):
        """
        Create an HTTP client for interacting with the various APIs

        :param web_proxy: An optional proxy for the HTTP client
        :param web_kwargs: Additional kwargs

        """

        self._logger = GrindrLogHandler.get_logger()
        self._session_token: str | None = None

        self._session = self._create_http_client(
            web_proxy=web_proxy,
            web_kwargs=web_kwargs
        )

    def set_proxy(self, proxy: str | None):
        """Update the current proxy on the client"""
        self._session.proxies = {"all": proxy}

    def clear_cookies(self):
        """Clear the cookies on the client"""
        self._session.cookies.clear()

    @property
    def http_client(self) -> AsyncSession:
        return self._session

    def _create_http_client(
            self,
            web_proxy: str | None,
            web_kwargs: dict[str, Any] | None
    ) -> AsyncSession:
        web_kwargs = web_kwargs or {}
        self.headers = {**web_kwargs.pop("headers", {}), **DEFAULT_REQUEST_HEADERS}
        self.params: dict[str, Any] = {**web_kwargs.pop("params", {}), **DEFAULT_REQUEST_PARAMS}
        self.refresh_device_info(refresh_user_agent=False)

        # Create the async client
        self._logger.debug('Creating HTTP client')
        return create_async_client(
            proxy=web_proxy,
            **web_kwargs
        )

    async def request(
            self,
            method: Literal["GET", "POST", "PUT", "DELETE"],
            url: str,
            extra_params: dict = None,
            extra_headers: dict = None,
            client: AsyncSession | None = None,
            base_params: bool = True,
            base_headers: bool = True,
            **kwargs
    ) -> Response:
        headers: dict = {
            **(self.headers if base_headers else {}),
            **(extra_headers or {}),
        }

        # Make the request
        return await (client or self._session).request(
            method=method,
            url=url,
            params={**(self.params if base_params else {}), **(extra_params or {})},
            headers=headers,
            **kwargs
        )

    async def close(self) -> None:
        """
        Close the HTTP client gracefully

        :return: None

        """

        await self._session.close()

    def set_session(self, session_token: str) -> None:
        """
        Set the session for the HTTP client

        :param session_token: The (must be valid) session token
        :return: None

        """

        self._session_token = session_token
        self.headers['Authorization'] = f'Grindr3 {session_token}'

    @property
    def session_token(self) -> str:
        return self._session_token

    @classmethod
    def _deprecated_generate_device_info_ios(cls):
        """iOS device info generator"""
        return f"{str(uuid.uuid4()).upper()};appStore;2;2107621376;1334x750"

    @classmethod  # Not used anymore
    def generate_device_info_android(cls):
        identifier = uuid.uuid4()
        hex_identifier = identifier.hex
        random_integer = random.randint(1000000000, 9999999999)
        return f"{hex_identifier};GLOBAL;2;{random_integer};2277x1080;{identifier}"

    def refresh_device_info(self, refresh_user_agent: bool, user_agent_type: Literal["web", "mobile"] = "web"):
        """Refresh the device info"""
        self.headers['L-Device-Info'] = self.generate_device_info_android()

        # May lead to ja3 mismatch, it just depends on how strictly cloudflare checks
        if refresh_user_agent:
            self.headers['User-Agent'] = get_mobile_user_agent() if user_agent_type == "mobile" else get_desktop_user_agent()


class QueryParams(BaseModel):
    pass


class BodyParams(BaseModel):
    pass


class URLTemplate:
    """
    A simple URL template to build requests on the fly

    """

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


class ImageBody(BaseModel):
    image_data: bytes
    image_mimetype: str


class ClientRoute[Method: Literal["GET", "POST", "PUT", "DELETE"], Url: URLTemplate, Params: Any, Body: Any, Response: Any]:

    def __init__(self, web: GrindrHTTPClient) -> object:
        self._logger = GrindrLogHandler.get_logger()
        self._web: GrindrHTTPClient = web

    @classmethod
    def __get_generic(cls, index: int) -> Any:
        base = getattr(cls, "__orig_bases__")[0]

        generics = base.__args__
        method = generics[index]

        if isinstance(method, ForwardRef):
            return method.__forward_arg__

        return method

    @property
    def method(self) -> Method:
        return self.__get_generic(0)

    @property
    def url(self) -> Url:
        return self.__get_generic(1)

    @property
    def params(self) -> Type[Params]:
        return self.__get_generic(2)

    @property
    def body(self) -> Type[Body]:
        return self.__get_generic(3)

    @property
    def response(self) -> Type[Response]:
        return self.__get_generic(4)

    @cached_property
    def adapter(self) -> TypeAdapter:
        return TypeAdapter(self.response)

    async def __call__(
            self,
            params: Params = None,
            body: Body = None,
            url_override: URLTemplate = None,
            header_override: dict[str, str] = None,
            **kwargs: Any
    ) -> Response | None:
        """
        Method used for calling the route as a function

        :param kwargs: Arguments to be overridden
        :return: Return to be overridden

        """

        if header_override is not None:
            kwargs['extra_headers'] = {
                **kwargs.get('extra_headers', {}),
                **header_override
            }

        # Upload an image
        if isinstance(body, ImageBody):
            kwargs['data'] = body.image_data
            kwargs['extra_headers'] = {
                **kwargs.get('extra_headers', {}),
                'Content-Type': body.image_mimetype
            }
        # If the body is a model
        elif isinstance(body, BaseModel):
            # Otherwise encode as JSON
            kwargs['json'] = kwargs.get('json', body.model_dump())

        elif body is not None:
            raise NotImplementedError("This body type has not been implemented!")

        url: str = (url_override or self.url) % (params.model_dump() if params else {})

        response: curl_cffi.requests.Response = await self._web.request(
            method=self.method,
            url=url,
            **kwargs
        )

        if os.environ.get("G_DEBUG_JSON"):
            self._logger.debug(f"Sent Payload to {response.request.url}: " + json.dumps(kwargs.get('json', {})))

        if response.status_code == 403:
            try:
                data = response.json()
                if data.get('code') == 4:
                    logging.error("Failed login attempt. Invalid account credentials (wrong user/pass)." + str(data))
                    raise LoginFailedResponse(response, "Invalid account credentials (wrong user/pass).")
                else:

                    if data.get('code') == 27:
                        raise AccountBannedError(response, "Account has been banned.")

                    raise LoginFailedResponse(response, "Failed login attempt. Something went wrong: " + str(data))

            except JSONDecodeError:
                raise CloudflareWAFResponse(response, "Blocked by the Grindr Cloudflare WAF!")

        if response.status_code != 200:

            if isinstance(body, ImageBody):
                payload_preview = f"Image: {body.image_mimetype} ({len(body.image_data)} bytes)"
            elif isinstance(body, BaseModel):
                payload_preview = body.model_dump()
            elif body is not None:
                payload_preview = str(body)[:100] + "..." if len(str(body)) > 100 else str(body)
            else:
                payload_preview = None

            self._logger.debug(f"Request Failed ({response.status_code}): Payload: {payload_preview} - URL: {url} - Response: {(response.content or b'').decode('utf-8')}")
            raise GrindrRequestError(response, f"A request to Grindr at {response.url} failed with status code {response.status_code}!")

        # Build the payload reply
        try:
            data: dict = response.json() if response.content else {}
            if os.environ.get("G_DEBUG_JSON"):
                self._logger.debug("Received JSON: " + json.dumps(data))

            # Handle the parsing of the object
            return self.adapter.validate_python(data)
        except JSONDecodeError as ex:
            content_preview = response.content.decode("utf-8", errors="replace")  # Convert bytes to string
            content_excerpt = content_preview[:2500]  # truncate for readability
            raise JSONDecodeError(
                f"Failed to decode JSON response at {response.url} for a successful request (200): {content_excerpt or '<Empty>'}",
                content_preview,
                ex.pos,
            ) from ex
        except ValidationError as ex:
            if os.environ.get('G_DEBUG_JSON'):
                self._logger.error(f"Failed due to ValidationError: {response.status_code} {response.url}\n" + traceback.format_exc())
            raise ValidationError(response, ex)
