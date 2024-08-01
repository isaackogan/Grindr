from typing import Optional, List

from pydantic import BaseModel

from Grindr.client.web.web_base import ClientRoute, URLTemplate, BodyParams
from Grindr.client.web.web_settings import GRINDR_V3


class ProfileData(BaseModel):
    profileId: Optional[int] = None
    displayName: Optional[str] = None
    profileImageMediaHash: Optional[str] = None
    distance: Optional[float] = None
    isFavorite: Optional[bool] = None
    timestamp: Optional[int] = None
    tapType: Optional[int] = None
    lastOnline: Optional[int] = None
    isBoosting: Optional[bool] = None
    isMutual: Optional[bool] = None
    rightNowType: Optional[str] = None
    isViewable: Optional[bool] = None


class FetchProfilesRouteResponse(BaseModel):
    profiles: list[ProfileData]


class FetchProfilesRouteBody(BodyParams):
    targetProfileIds: List[str]


class FetchProfilesRoute(
    ClientRoute[
        "POST",
        URLTemplate(GRINDR_V3, "/profiles"),
        None,
        FetchProfilesRouteBody,
        FetchProfilesRouteResponse
    ]
):
    """
    Retrieve a session from the API

    """
