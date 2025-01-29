import textwrap

from curl_cffi.requests import Response, Request
from pydantic import BaseModel

from Grindr.web.routes.fetch.fetch_session import FetchSessionRouteResponse, SessionCredentials, FetchSessionRefreshRoutePayload


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


class GrindrHTTPClientAuthSession(BaseModel):
    """Auth Context Object"""

    # The current credentials
    credentials: SessionCredentials | None = None

    # Current session data
    session_data: FetchSessionRouteResponse | None = None

    @property
    def auth_token(self) -> str | None:
        """The current auth token"""

        if self.session_data is not None and self.session_data.auth_token is not None:
            return self.session_data.auth_token

        if isinstance(self.credentials, FetchSessionRefreshRoutePayload) and self.credentials.authToken:
            return self.credentials.authToken

        return None


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
