from pydantic import BaseModel

from Grindr.client.web.web_base import ClientRoute, BodyParams, URLTemplate
from Grindr.client.web.web_settings import GRINDR_V4, GRINDR_V3


class FetchSessionRoutePayload(BodyParams):
    email: str
    password: str
    token: str = ""


class FetchSessionRouteResponse(BaseModel):
    sessionId: str
    profileId: str
    authToken: str
    xmppToken: str


SessionData = FetchSessionRouteResponse


class FetchSessionNewRoute(
    ClientRoute[
        "POST",
        URLTemplate(GRINDR_V3, "/sessions"),
        None,
        FetchSessionRoutePayload,
        FetchSessionRouteResponse
    ]
):
    """
    Retrieve a session from the API

    """


class FetchSessionRefreshRoutePayload(BodyParams):
    email: str
    token: str
    authToken: str


class FetchSessionRefreshRoute(
    ClientRoute[
        "POST",
        URLTemplate(GRINDR_V4, "/sessions"),
        None,
        FetchSessionRefreshRoutePayload,
        FetchSessionRouteResponse
    ]
):
    """
    Retrieve a session from the API

    """
