from typing import Any

from pydantic import BaseModel

from Grindr.web.routes.fetch.fetch_profiles import ProfileData
from Grindr.web.routes.set.set_profile_details import SexualPosition, SocialNetworks
from Grindr.web.web_schemas import BodyParams
from Grindr.web.web_base import URLTemplate
from Grindr.web.web_route import ClientRoute
from Grindr.web.web_settings import GRINDR_V4


class DetailedProfileData(ProfileData):
    aboutMe: str | None = None
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
    socialNetworks: SocialNetworks | None = None
    approximateDistance: bool | None = None
    identity: Any | None = None
    meetAt: list[int] | None = None
    hashtags: list[str] | None = None
    profileTags: list[str] | None = None
    genders: list[int] | None = None
    pronouns: list[int] | None = None
    tapped: bool | None = None
    isTeleporting: bool | None = None
    isRoaming: bool | None = None
    arrivalDays: int | None = None
    foundVia: int | None = None
    unreadCount: int | None = None
    lastThrobTimestamp: int | None = None
    sexualHealth: list[int] | None = None


class FetchProfileRouteResponse(BaseModel):
    profiles: list[DetailedProfileData]


if __name__ == '__main__':
    d = print(FetchProfileRouteResponse(profiles=[DetailedProfileData()]).model_dump_json())
    exit()


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
