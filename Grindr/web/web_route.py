import json
import logging
import os
import traceback
from functools import cached_property
from json import JSONDecodeError
from typing import Literal, Any, ForwardRef, Type

import curl_cffi.requests
from pydantic import TypeAdapter, BaseModel, ValidationError

from Grindr.web.web_base import GrindrHTTPClient, URLTemplate
from Grindr.web.web_schemas import ImageBody, BodyParams, GrindrRequestError, CloudflareWAFResponse, LoginFailedResponse, AccountBannedError


class ClientRoute[Method: Literal["GET", "POST", "PUT", "DELETE"], Url: URLTemplate, Params: BodyParams, Body: BodyParams, Response: Any]:
    """
    Base class for abstract URL route definitions for accessing the Grindr API

    """

    def __init__(self, web: GrindrHTTPClient):
        """
        Initialize the route with the web client

        :param web: An instance of the web request client

        """

        self._logger: logging.Logger = web.logger
        self._web: GrindrHTTPClient = web

    @classmethod
    def _extract_generic_parameter(cls, index: int) -> Any:
        """Extract the pertinent generic parameter from the class definition"""

        base = getattr(cls, "__orig_bases__")[0]
        generics = base.__args__
        method = generics[index]

        if isinstance(method, ForwardRef):
            return method.__forward_arg__

        return method

    @property
    def method(self) -> Method:
        """Return the method of the route"""
        return self._extract_generic_parameter(0)

    @property
    def url(self) -> Url:
        """Route URL Template"""
        return self._extract_generic_parameter(1)

    @property
    def params(self) -> Type[Params]:
        """Route parameters"""
        return self._extract_generic_parameter(2)

    @property
    def body(self) -> Type[Body]:
        """Route body data"""
        return self._extract_generic_parameter(3)

    @property
    def response(self) -> Type[Response]:
        """Response body"""
        return self._extract_generic_parameter(4)

    @cached_property
    def adapter(self) -> TypeAdapter:
        """Type adapter for responses"""
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
            base_url=url,
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

            self._logger.debug(f"A {response.request.method} request to Grindr failed ({response.status_code}): Payload: {payload_preview} - URL: {url} - Response: {(response.content or b'').decode('utf-8')}")
            raise GrindrRequestError(response, f"A {response.request.method} request to Grindr at {response.url} failed with status code {response.status_code}!")

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
