from typing import Optional, List, Any

from pydantic import BaseModel

from Grindr.client.web.routes.fetch_profile import Media
from Grindr.client.web.routes.fetch_profiles import ProfileData
from Grindr.client.web.web_base import ClientRoute, URLTemplate
from Grindr.client.web.web_settings import GRINDR_V6


class ViewedProfilePreview(BaseModel):
    distance: Optional[float] = None
    lastViewed: Optional[int] = None
    profileImageMediaHash: Optional[str] = None
    seen: Optional[int] = None
    sexualPosition: Optional[int] = None
    foundVia: Optional[Any] = None
    rightNow: Optional[str] = None
    inBadNeighborhood: Optional[bool] = None
    secretAdmirer: Optional[bool] = None
    viewedMeFreshFace: Optional[bool] = None
    favorite: Optional[bool] = None


class ViewedProfile(ViewedProfilePreview):
    profileId: Optional[int] = None
    displayName: Optional[str] = None
    age: Optional[int] = None
    showAge: Optional[bool] = None
    showDistance: Optional[bool] = None
    approximateDistance: Optional[bool] = None
    lastChatTimestamp: Optional[int] = None
    hasFaceRecognition: Optional[bool] = None
    medias: Optional[List[Media]] = None
    lastUpdatedTime: Optional[int] = None
    boosting: Optional[bool] = None
    profileTags: Optional[List[str]] = None
    incognito: Optional[bool] = None
    new: Optional[bool] = None


class FetchViewsRouteResponse(BaseModel):
    totalViewers: int
    profiles: List[ProfileData]
    previews: List[ViewedProfilePreview]
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
