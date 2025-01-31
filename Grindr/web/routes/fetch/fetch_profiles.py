from typing import Any

from pydantic import BaseModel

from Grindr.web.web_schemas import BodyParams
from Grindr.web.web_base import URLTemplate
from Grindr.web.web_route import ClientRoute
from Grindr.web.web_settings import GRINDR_V3


class Media(BaseModel):
    mediaHash: str | None = None
    type: int | None = None
    state: int | None = None
    reason: Any | None = None


class ProfileData(BaseModel):
    profileId: int | None = None
    seen: int | None = None
    isFavorite: bool | None = None
    displayName: str | None = None
    profileImageMediaHash: str | None = None
    age: int | None = None
    showDistance: bool | None = None
    isNew: bool | None = None
    distance: float | None = None
    lastChatTimestamp: int | None = None
    medias: list[Media] | None = None
    lastUpdatedTime: int | None = None
    lastViewed: int | None = None
    rightNow: str | None = None
    rightNowText: str | None = None
    rightNowPosted: int | None = None
    rightNowDistance: float | None = None
    nsfw: int | None = None
    acceptNSFWPics: bool | None = None
    verifiedInstagramId: str | None = None
    isBlockable: bool | None = None


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
