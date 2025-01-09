import enum
from typing import Optional, List

from pydantic import BaseModel

from Grindr.client.web.web_base import ClientRoute, URLTemplate
from Grindr.client.web.web_settings import GRINDR_V3_1


class SocialNetworks(BaseModel):
    twitter: dict | None = None
    facebook: dict | None = None
    instagram: dict | None = None


class SexualPosition(int, enum.Enum):
    TOP = 1
    BOTTOM = 2
    VERSATILE = 3
    VERS_BOTTOM = 4
    VERS_TOP = 5
    SIDE = 6


class SetProfileDetailsRouteBody(BaseModel):
    aboutMe: str | None = None
    nsfw: int | None = None
    age: int | None = None
    approximateDistance: bool | None = None
    bodyType: int | None = None
    displayName: str | None = None
    ethnicity: int | None = None
    genders: list[int] | None = None
    grindrTribes: list[int] | None = None
    hashtags: list[str] | None = None
    height: float | None = None
    hivStatus: int | None = None
    lastTestedDate: int | None = None
    lookingFor: list[int] | None = None
    meetAt: list[int] | None = None
    profileTags: list[str] | None = None
    pronouns: list[int] | None = None
    relationshipStatus: int | None = None
    sexualPosition: SexualPosition | None = None
    showAge: bool | None = None
    showDistance: bool | None = None
    socialNetworks: SocialNetworks | None = None
    vaccines: list[int] | None = None
    weight: float | None = None


class SetProfileDetailsRoute(
    ClientRoute[
        "PUT",
        URLTemplate(GRINDR_V3_1, "/me/profile"),
        None,
        SetProfileDetailsRouteBody,
        None
    ]
):
    """
    Set profile details

    """
