from pydantic import BaseModel

from Grindr.web.routes.set.set_send_tap import TapType
from Grindr.web.web_base import URLTemplate
from Grindr.web.web_route import ClientRoute
from Grindr.web.web_settings import GRINDR_V2


class TapProfileData(BaseModel):
    profileId: int | None = None
    displayName: str | None = None
    profileImageMediaHash: str | None = None
    distance: float | None = None
    isFavorite: bool | None = None
    timestamp: int | None = None
    tapType: TapType | None = None
    lastOnline: int | None = None
    isBoosting: bool | None = None
    isMutual: bool | None = None
    rightNowType: str | None = None
    isViewable: bool | None = None
    onlineUntil: int | None = None


class FetchTapsRouteResponse(BaseModel):
    profiles: list[TapProfileData] | None


class FetchTapsRoute(
    ClientRoute[
        "GET",
        URLTemplate(GRINDR_V2, "/taps/received"),
        None,
        None,
        FetchTapsRouteResponse
    ]
):
    """
    Retrieve a session from the API

    """
