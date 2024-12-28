import json
import logging
import os
import random
import textwrap
import traceback
import uuid
from json import JSONDecodeError
from typing import Optional, Any, Dict, Literal, TypeVar, Generic, ForwardRef, Type

import curl_cffi.requests
from curl_cffi.requests import AsyncSession
from pydantic import BaseModel, ValidationError

from Grindr.client.errors import CloudflareWAFResponse, LoginFailedResponse
from Grindr.client.logger import GrindrLogHandler
from Grindr.client.web.web_settings import DEFAULT_REQUEST_PARAMS, DEFAULT_REQUEST_HEADERS

OKHTTP_4_ANDROID_10_JA3 = okhttp4_android10_ja3 = ",".join(
    [
        "771",
        "4865-4866-4867-49195-49196-52393-49199-49200-52392-49171-49172-156-157-47-53",
        "0-23-65281-10-11-35-16-5-13-51-45-43-21",
        "29-23-24",
        "0",
    ]
)

OKHTTP_4_ANDROID_10_AKAMAI = "4:16777216|16711681|0|m,p,a,s"

extra_fp = {
    "tls_signature_algorithms": [
        "ecdsa_secp256r1_sha256",
        "rsa_pss_rsae_sha256",
        "rsa_pkcs1_sha256",
        "ecdsa_secp384r1_sha384",
        "rsa_pss_rsae_sha384",
        "rsa_pkcs1_sha384",
        "rsa_pss_rsae_sha512",
        "rsa_pkcs1_sha512",
        "rsa_pkcs1_sha1",
    ]
}


class GrindrHTTPClient:

    def __init__(
            self,
            proxy: Optional[str] = None,
            session_kwargs: Optional[dict] = None
    ):
        """
        Create an HTTP client for interacting with the various APIs

        :param proxy: An optional proxy for the HTTP client
        :param session_kwargs: Additional kwargs

        """

        self._session: AsyncSession = self._create_libcurl_client(
            proxy=proxy,
            session_kwargs=session_kwargs or dict(),
        )

        self._session_token: Optional[str] = None

    @property
    def http_client(self) -> AsyncSession:
        return self._session

    def _create_libcurl_client(
            self,
            proxy: Optional[str],
            session_kwargs: Dict[str, Any]
    ) -> AsyncSession:
        self.headers = {**session_kwargs.pop("headers", {}), **DEFAULT_REQUEST_HEADERS}
        self.params: Dict[str, Any] = {**session_kwargs.pop("params", {}), **DEFAULT_REQUEST_PARAMS}
        self.headers['L-Device-Info'] = self.generate_device_info()

        return AsyncSession(
            proxy=proxy,
            **session_kwargs
        )

    async def request(
            self,
            method: Literal["GET", "POST", "PUT", "DELETE"],
            url: str,
            extra_params: dict = None,
            extra_headers: dict = None,
            client: Optional[AsyncSession] = None,
            base_params: bool = True,
            base_headers: bool = True,
            **kwargs
    ) -> curl_cffi.requests.Response:
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
    def generate_device_info(cls):
        """iOS device info generator"""
        return f"{str(uuid.uuid4()).upper()};appStore;2;2107621376;1334x750"

    @classmethod  # Not used anymore
    def _android_deprecated_generate_device_info(cls):
        identifier = uuid.uuid4()
        hex_identifier = identifier.hex
        random_integer = random.randint(1000000000, 9999999999)
        return f"{hex_identifier};GLOBAL;2;{random_integer};2277x1080;{identifier}"


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
        :param url_template: The URL acting as a template

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
        d = self._url.format(**data)
        return d


# Define a TypeVar that can be any subclass of BaseModel
Method = TypeVar('Method', bound=Literal["GET", "POST", "PUT", "DELETE"])
Url = TypeVar('Url', bound=URLTemplate)
Params = TypeVar('Params')
Body = TypeVar('Body')
Response = TypeVar('Response')


class ClientRoute(
    Generic[
        Method,
        Url,
        Params,
        Body,
        Response
    ]
):

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

    async def __call__(
            self,
            params: Params = None,
            body: Body = None,
            **kwargs: Any
    ) -> Optional[Response]:
        """
        Method used for calling the route as a function

        :param kwargs: Arguments to be overridden
        :return: Return to be overridden

        """

        # Add the body
        if body is not None:
            kwargs['json'] = kwargs.get('json', body.model_dump())

        response: curl_cffi.requests.Response = await self._web.request(
            method=self.method,
            url=self.url % (params.model_dump() if params else {}),
            **kwargs
        )

        if os.environ.get("G_DEBUG_JSON"):
            self._logger.debug(f"Sent Payload to {response.request.url}: " + json.dumps(kwargs.get('json', {})))

        if response.status_code == 403:
            try:
                data = response.json()
                if data.get('code') == 4:
                    logging.error("Failed login attempt. Invalid account credentials (wrong user/pass)." + str(data))
                    raise LoginFailedResponse("Invalid account credentials (wrong user/pass).")
                else:
                    raise LoginFailedResponse("Failed login attempt. Something went wrong: " + str(data))

            except JSONDecodeError:
                raise CloudflareWAFResponse("Blocked by the Grindr Cloudflare WAF!")

        if response.status_code != 200:
            self._logger.debug("Request Failed: " + str(response.status_code) + response.content.decode())
            return None

        # Build the payload reply
        try:
            data: dict = response.json() if response.content else {}
            if os.environ.get("G_DEBUG_JSON"):
                self._logger.debug("Received JSON: " + json.dumps(data))
            return self.response(**data)
        except ValidationError:
            self._logger.error(f"Failed due to ValidationError: {response.status_code} {response.url}\n" + traceback.format_exc())
            return None
