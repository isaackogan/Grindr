from typing import Any

from pydantic import BaseModel

from Grindr.web.routes.fetch.fetch_profiles import ProfileData, Media
from Grindr.web.routes.set.set_profile_details import SexualPosition
from Grindr.web.web_base import URLTemplate
from Grindr.web.web_route import ClientRoute
from Grindr.web.web_settings import GRINDR_V6


class ViewedProfilePreview(BaseModel):
    distance: float | None = None
    lastViewed: int | None = None
    profileImageMediaHash: str | None = None
    seen: int | None = None
    sexualPosition: SexualPosition | None = None
    foundVia: Any | None = None
    rightNow: str | None = None
    inBadNeighborhood: bool | None = None
    secretAdmirer: bool | None = None
    viewedMeFreshFace: bool | None = None
    favorite: bool | None = None


class ViewedProfile(ViewedProfilePreview):
    profileId: int | None = None
    displayName: str | None = None
    age: int | None = None
    showAge: bool | None = None
    showDistance: bool | None = None
    approximateDistance: bool | None = None
    lastChatTimestamp: int | None = None
    hasFaceRecognition: bool | None = None
    medias: list[Media] | None = None
    lastUpdatedTime: int | None = None
    boosting: bool | None = None
    profileTags: list[str] | None = None
    incognito: bool | None = None
    new: bool | None = None


class FetchViewsRouteResponse(BaseModel):
    totalViewers: int
    profiles: list[ProfileData]
    previews: list[ViewedProfilePreview]
    ttl: int


class FetchViewsRoute(
    ClientRoute[
        "GET",
        URLTemplate(GRINDR_V6, "/views/list"),
        None,
        None,
        FetchViewsRouteResponse
    ]
):
    pass
