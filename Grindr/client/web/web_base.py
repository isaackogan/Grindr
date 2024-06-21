import json
import random
import textwrap
import traceback
import uuid
from typing import Optional, Any, Dict, Literal, TypeVar, Generic, ForwardRef, Type

import httpx
from httpx import AsyncClient, Proxy, URL
from pydantic import BaseModel, ValidationError

from Grindr.client.errors import CloudflareWAFResponse
from Grindr.client.logger import GrindrLogHandler
from Grindr.client.web.web_settings import DEFAULT_REQUEST_PARAMS, DEFAULT_REQUEST_HEADERS


class GrindrHTTPClient:

    def __init__(
            self,
            proxy: Optional[Proxy] = None,
            httpx_kwargs: Optional[dict] = None
    ):
        """
        Create an HTTP client for interacting with the various APIs

        :param proxy: An optional proxy for the HTTP client
        :param httpx_kwargs: Additional httpx k

        """

        self._httpx: AsyncClient = self._create_httpx_client(
            proxy=proxy,
            httpx_kwargs=httpx_kwargs or dict()
        )

    def _create_httpx_client(
            self,
            proxy: Optional[Proxy],
            httpx_kwargs: Dict[str, Any]
    ) -> AsyncClient:
        """
        Initialize a new `httpx.AsyncClient`, called internally on object creation

        :param proxy: An optional HTTP proxy to initialize the client with
        :return: An instance of the `httpx.AsyncClient`

        """

        self.headers = {**httpx_kwargs.pop("headers", {}), **DEFAULT_REQUEST_HEADERS}
        self.params: Dict[str, Any] = {**httpx_kwargs.pop("params", {}), **DEFAULT_REQUEST_PARAMS}

        return AsyncClient(proxies=proxy, **httpx_kwargs)

    async def request(
            self,
            method: Literal["GET", "POST", "PUT", "DELETE"],
            url: str,
            extra_params: dict = None,
            extra_headers: dict = None,
            client: Optional[httpx.AsyncClient] = None,
            base_params: bool = True,
            base_headers: bool = True,
            **kwargs
    ) -> httpx.Response:
        headers: dict = {
            **(self.headers if base_headers else {}),
            **(extra_headers or {}),
        }

        if kwargs.get('json') is not None:
            headers['Content-Length'] = str(len(json.dumps(kwargs['json']).encode('utf-8')))

        # Make the request
        return await (client or self._httpx).request(
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

        await self._httpx.aclose()

    def set_session(self, session_token: str) -> None:
        """
        Set the session for the HTTP client

        :param session_token: The (must be valid) session token
        :return: None

        """

        self.headers['Authorization'] = f'Grindr3 {session_token}'
        self.headers['L-Device-Info'] = self.generate_device_info()

    @classmethod
    def generate_device_info(cls):
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

    def __mod__(self, data: dict) -> URL:
        """
        Overload modulus operator to allow formatting
        :param data: The data to format the URL with
        :return: The filled template

        """

        return httpx.URL(
            self._url.format(**data)
        )


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

        # Get response
        response: httpx.Response = await self._web.request(
            method=self.method,
            url=self.url % (params.model_dump() if params else {}),
            **kwargs
        )

        if response.status_code == 403:
            raise CloudflareWAFResponse("Blocked by the Grindr Cloudflare WAF!")

        if response.status_code != 200:
            self._logger.debug("Request Failed: " + str(response.status_code) + response.content.decode())
            return None

        # Build the payload reply
        try:
            data: dict = response.json() if response.content else {}
            self._logger.debug("Received JSON: " + json.dumps(data))
            return self.response(**data)
        except ValidationError:
            self._logger.error(f"Failed due to ValidationError: {response.status_code} {response.url}\n" + traceback.format_exc())
            return None
