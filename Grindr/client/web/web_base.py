import json
import logging
import os
import random
import textwrap
import time
import traceback
import uuid
from functools import cached_property
from json import JSONDecodeError
from pathlib import Path
from typing import Any, Literal, ForwardRef, Type, TypedDict

import curl_cffi.requests
from curl_cffi.requests import AsyncSession, Response
from pydantic import BaseModel, ValidationError, TypeAdapter

from Grindr.client.errors import CloudflareWAFResponse, LoginFailedResponse, GrindrRequestError, AccountBannedError
from Grindr.client.logger import GrindrLogHandler
from Grindr.client.tls_match.tls_match import create_async_client
from Grindr.client.web.web_settings import DEFAULT_REQUEST_PARAMS, DEFAULT_REQUEST_HEADERS, ANDROID_VERSION_API_LEVEL_MAP, DEVICE_SCREEN_DIMENSIONS


class GrindrHTTPLog(TypedDict):
    request: dict
    response: dict


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

        # Local time in format DD/MM/YYYY HH:MM:SS
        self._client_create_time = time.strftime("%d_%m_%Y-%H_%M_%S")
        self._logger = GrindrLogHandler.get_logger()
        self._session_id: str | None = None
        self._session_token: str = ""
        self._request_id: int = 0
        self._session_profile_id: str | None = None
        self._mobile_user_agent: str | None = None
        self._web_user_agent: str | None = None
        self._request_dump_directory: str = web_kwargs.pop('request_dump_directory') if web_kwargs else None

        self._http_session = self._create_http_client(
            web_proxy=web_proxy,
            web_kwargs=web_kwargs
        )

    def set_proxy(self, proxy: str | None):
        """Update the current proxy on the client"""
        self._http_session.proxies = {"all": proxy}

    def clear_cookies(self):
        """Clear the cookies on the client"""
        self._http_session.cookies.clear()

    @property
    def http_client(self) -> AsyncSession:
        return self._http_session

    def _create_http_client(
            self,
            web_proxy: str | None,
            web_kwargs: dict[str, Any] | None
    ) -> AsyncSession:
        web_kwargs = web_kwargs or {}
        self.headers = {**web_kwargs.pop("headers", {}), **DEFAULT_REQUEST_HEADERS}
        self.params: dict[str, Any] = {**web_kwargs.pop("params", {}), **DEFAULT_REQUEST_PARAMS}
        self.headers['L-Device-Info'] = self.generate_device_info_android()

        # Create the async client
        self._logger.debug('Creating HTTP client')
        return create_async_client(
            proxy=web_proxy,
            **web_kwargs
        )

    def add_log_to_file(self, log_data: GrindrHTTPLog) -> None:

        if not self._request_dump_directory:
            return

        # Base request dump directory
        base_request_dir = Path(self._request_dump_directory)
        if not base_request_dir.exists():
            base_request_dir.mkdir()

        # Profile request dump directory
        profile_request_dir = base_request_dir.joinpath(f'./{self._session_profile_id or 'anonymous'}')
        if not profile_request_dir.exists():
            profile_request_dir.mkdir()

        # Request file path
        request_fp = profile_request_dir.joinpath(f'./{self._client_create_time}.json')
        if not request_fp.exists():
            with open(request_fp, "w") as f:
                f.write("[]")

        # Write the new data
        with open(request_fp, "r+") as f:
            file_data = json.load(f)
            file_data.append(log_data)
            f.seek(0)
            f.write(json.dumps(file_data, indent=2))
            f.truncate()

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

        url_params: dict = {**(self.params if base_params else {}), **(extra_params or {})}

        # Make the request
        self._request_id += 1
        response: curl_cffi.requests.Response = await (client or self._http_session).request(
            method=method,
            url=url,
            params=url_params,
            headers=headers,
            **kwargs
        )

        # Log the request
        self.add_log_to_file({
            "request": {
                "id": self._request_id,
                "method": method,
                "url": url,
                "params": url_params,
                "headers": dict(headers.items()),
                "kwargs": {k: v for k, v in kwargs.items() if k != 'content'}  # Exclude binary content
            },
            "response": {
                "status_code": response.status_code,
                "content": response.content.decode("utf-8", errors="replace"),
                "headers": dict(response.headers.items()),
                "cookies": dict(response.cookies.items()),
                "elapsed": response.elapsed
            }
        })

        return response

    async def close(self) -> None:
        """
        Close the HTTP client gracefully

        :return: None

        """

        await self._http_session.close()

    def set_session(
            self,
            session_id: str,
            session_profile_id: str,
            *,
            token: str | None = None
    ) -> None:
        """
        Set the session for the HTTP client

        :param session_id: The (must be valid) session token
        :param session_profile_id: The profile ID for the session
        :param token: Token for requesting session
        :return: None

        """

        self._session_id = session_id
        self._session_profile_id = session_profile_id
        self._session_token = token if token else self._session_token
        self.headers['Authorization'] = f'Grindr3 {session_id}'

    @property
    def session_id(self) -> str:
        return self._session_id

    @property
    def session_token(self) -> str:
        return self._session_token

    @classmethod
    def _deprecated_generate_device_info_ios(cls):
        """iOS device info generator"""
        return f"{str(uuid.uuid4()).upper()};appStore;2;2107621376;1334x750"

    @classmethod
    def generate_device_info_android(
            cls,
            android_device_id: str | None = None,
    ):
        android_advertising_id: str = str(uuid.uuid4())  # Not validated

        # How much memory does the phone have, in bytes. Should be some multiple of 1024 (i.e. Some # of megabytes summing to some # of gigabytes)
        memory_on_phone: int = (
                random.randint(2800, 3600)  # Mb
                * 1024  # Kb
                * 1024  # Bytes
        )

        # The value "2" represents the follow code from the Grindr APK: "x86".equals(Build.CPU_ABI) ? 1 : 2
        # The value "GLOBAL" is statically set in the APK. No clue what it does.
        return f"{android_device_id or f'{random.getrandbits(64):016x}'};GLOBAL;2;{memory_on_phone};{random.choice(DEVICE_SCREEN_DIMENSIONS)};{android_advertising_id}"

    @property
    def android_api_level(self) -> list[int]:
        app_version, build, free, android_version, device, manufacturer = self._mobile_user_agent.split(";")
        return ANDROID_VERSION_API_LEVEL_MAP[int(android_version.split(" ")[1])]

    @property
    def android_device_id(self) -> str:
        return self.headers['L-Device-Info'].split(";")[0]

    @property
    def profile_id(self) -> str:
        return self._session_profile_id


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

    def __init__(self, web: GrindrHTTPClient):
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
    def web(self):
        return self._web

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
            self._logger.debug(f"Sent Payload to {response.request.method} {response.request.url} with code {response.status_code}: " + json.dumps(kwargs.get('json', {})))
        elif os.environ.get("G_DEBUG_BASIC"):
            self._logger.debug(f'Sent request {response.request.method} to  {response.request.url} and received code {response.status_code}')

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

        # Return the response if empty
        if not response.content:
            return None

        # Build the payload reply
        try:
            data: dict = response.json()
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
            raise ex
