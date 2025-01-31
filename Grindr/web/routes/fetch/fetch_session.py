from pydantic import BaseModel, EmailStr

from Grindr.web.web_route import ClientRoute
from Grindr.web.web_schemas import BodyParams
from Grindr.web.web_base import URLTemplate
from Grindr.web.web_settings import GRINDR_V4


class FetchSessionRouteBasePayload(BodyParams):
    # Account e-mail address
    email: EmailStr

    # Firebase token on Android, timestamp on IOS (leave default for iOS)
    token: str


class FetchSessionNewRoutePayload(FetchSessionRouteBasePayload):
    password: str


class FetchSessionRefreshRoutePayload(FetchSessionRouteBasePayload):
    authToken: str


EmailPasswordCredentials = FetchSessionNewRoutePayload
AuthTokenCredentials = FetchSessionRefreshRoutePayload
type SessionCredentials = EmailPasswordCredentials | AuthTokenCredentials


class FetchSessionRouteResponse(BaseModel):
    sessionId: str
    profileId: str
    authToken: str

    @property
    def session_id(self) -> str:
        return self.sessionId

    @property
    def profile_id(self) -> str:
        return self.profileId

    @property
    def auth_token(self) -> str:
        return self.authToken


class FetchSessionRoute(
    ClientRoute[
        "POST",
        URLTemplate(GRINDR_V4, "/sessions"),
        None,
        FetchSessionNewRoutePayload | FetchSessionRefreshRoutePayload,
        FetchSessionRouteResponse
    ]
):
    """
    Retrieve a session from the API

    """
