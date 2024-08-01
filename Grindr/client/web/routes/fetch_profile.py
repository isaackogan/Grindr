from typing import List, Optional, Dict, Any

from pydantic import BaseModel

from Grindr.client.web.routes.fetch_profiles import ProfileData
from Grindr.client.web.web_base import ClientRoute, URLTemplate, BodyParams
from Grindr.client.web.web_settings import GRINDR_V4


class Media(BaseModel):
    mediaHash: Optional[str] = None
    type: Optional[int] = None
    state: Optional[int] = None
    reason: Optional[Any] = None


class DetailedProfileData(ProfileData):
    aboutMe: Optional[str] = None
    age: Optional[int] = None
    showAge: Optional[bool] = None
    ethnicity: Optional[int] = None
    relationshipStatus: Optional[int] = None
    grindrTribes: Optional[List[int]] = None
    lookingFor: Optional[List[int]] = None
    vaccines: Optional[List[int]] = None
    bodyType: Optional[int] = None
    sexualPosition: Optional[int] = None
    hivStatus: Optional[int] = None
    lastTestedDate: Optional[int] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    socialNetworks: Optional[Any] = None
    showDistance: Optional[bool] = None
    approximateDistance: Optional[bool] = None
    seen: Optional[int] = None
    medias: Optional[List[Media]] = None
    identity: Optional[Any] = None
    lastChatTimestamp: Optional[int] = None
    isNew: Optional[bool] = None
    lastViewed: Optional[int] = None
    meetAt: Optional[List[int]] = None
    nsfw: Optional[int] = None
    hashtags: Optional[List[str]] = None
    profileTags: Optional[List[str]] = None
    lastUpdatedTime: Optional[int] = None
    genders: Optional[List[int]] = None
    pronouns: Optional[List[int]] = None
    tapped: Optional[bool] = None
    isTeleporting: Optional[bool] = None
    isRoaming: Optional[bool] = None
    arrivalDays: Optional[int] = None
    foundVia: Optional[int] = None
    unreadCount: Optional[int] = None
    rightNow: Optional[str] = None
    rightNowText: Optional[str] = None
    rightNowPosted: Optional[int] = None
    rightNowDistance: Optional[float] = None
    verifiedInstagramId: Optional[str] = None


class FetchProfileRouteResponse(BaseModel):
    profiles: List[DetailedProfileData]


class FetchProfileRouteParams(BodyParams):
    profileId: int


class FetchProfileRoute(
    ClientRoute[
        "GET",
        URLTemplate(GRINDR_V4, "/profiles/{profileId}"),
        FetchProfileRouteParams,
        None,
        FetchProfileRouteResponse
    ]
):
    """
    Retrieve a session from the API

    """
