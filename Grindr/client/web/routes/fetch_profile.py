from typing import List, Optional, Any

from pydantic import BaseModel

from Grindr.client.web.routes.fetch_profiles import ProfileData
from Grindr.client.web.routes.set_profile_details import SexualPosition
from Grindr.client.web.web_base import ClientRoute, URLTemplate, BodyParams
from Grindr.client.web.web_settings import GRINDR_V4


class Media(BaseModel):
    mediaHash: str | None = None
    type: int | None = None
    state: int | None = None
    reason: Any | None = None


class DetailedProfileData(ProfileData):
    aboutMe: str | None = None
    age: int | None = None
    showAge: bool | None = None
    ethnicity: int | None = None
    relationshipStatus: int | None = None
    grindrTribes: list[int] | None = None
    lookingFor: list[int] | None = None
    vaccines: list[int] | None = None
    bodyType: int | None = None
    sexualPosition: SexualPosition | None = None
    hivStatus: int | None = None
    lastTestedDate: int | None = None
    height: float | None = None
    weight: float | None = None
    socialNetworks: Any | None = None
    showDistance: bool | None = None
    approximateDistance: bool | None = None
    seen: int | None = None
    medias: list[Media] | None = None
    identity: Any | None = None
    lastChatTimestamp: int | None = None
    isNew: bool | None = None
    lastViewed: int | None = None
    meetAt: list[int] | None = None
    nsfw: int | None = None
    hashtags: list[str] | None = None
    profileTags: list[str] | None = None
    lastUpdatedTime: int | None = None
    genders: list[int] | None = None
    pronouns: list[int] | None = None
    tapped: bool | None = None
    isTeleporting: bool | None = None
    isRoaming: bool | None = None
    arrivalDays: int | None = None
    foundVia: int | None = None
    unreadCount: int | None = None
    rightNow: str | None = None
    rightNowText: str | None = None
    rightNowPosted: int | None = None
    rightNowDistance: float | None = None
    verifiedInstagramId: str | None = None


class FetchProfileRouteResponse(BaseModel):
    profiles: list[DetailedProfileData]


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
