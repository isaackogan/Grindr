from curl_cffi.requests import Response, Request
from pydantic import BaseModel


class QueryParams(BaseModel):
    """Query parameters"""
    pass


class BodyParams(BaseModel):
    """Body parameters"""

    pass


class ImageBody(BodyParams):
    """Image body data"""

    image_data: bytes
    image_mimetype: str


class CredentialsMissingError(RuntimeError):
    pass


class GrindrRequestError(RuntimeError):

    def __init__(self, response: Response | None, *args):
        super().__init__(*args)
        self._response = response

    @property
    def response(self) -> Response | None:
        return self._response

    @property
    def request(self) -> Request | None:
        return self._response.request


class LoginFailedResponse(GrindrRequestError):
    pass


class AccountBannedError(LoginFailedResponse):
    pass


class CloudflareWAFResponse(LoginFailedResponse):
    pass
