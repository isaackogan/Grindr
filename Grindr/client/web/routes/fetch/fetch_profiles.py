from typing import Optional, List

from pydantic import BaseModel

from Grindr.client.web.web_base import ClientRoute, URLTemplate, BodyParams
from Grindr.client.web.web_settings import GRINDR_V3


class ProfileData(BaseModel):
    profileId: int | None = None
    displayName: str | None = None
    profileImageMediaHash: str | None = None
    distance: float | None = None
    isFavorite: bool | None = None
    timestamp: int | None = None
    tapType: int | None = None
    lastOnline: int | None = None
    isBoosting: bool | None = None
    isMutual: bool | None = None
    rightNowType: str | None = None
    isViewable: bool | None = None


class FetchProfilesRouteResponse(BaseModel):
    profiles: list[ProfileData]


class FetchProfilesRoutePayload(BodyParams):
    targetProfileIds: list[str]


class FetchProfilesRoute(
    ClientRoute[
        "POST",
        URLTemplate(GRINDR_V3, "/profiles"),
        None,
        FetchProfilesRoutePayload,
        FetchProfilesRouteResponse
    ]
):
    """
    Retrieve a session from the API

    """
