from typing import Optional, List, Any

from pydantic import BaseModel

from Grindr.client.web.web_base import ClientRoute, URLTemplate, BodyParams
from Grindr.client.web.web_settings import GRINDR_V3_1


class SocialNetworks(BaseModel):
    twitter: Optional[dict] = None
    facebook: Optional[dict] = None
    instagram: Optional[dict] = None


class SetProfileDetailsRouteBody(BaseModel):
    aboutMe: Optional[str] = None
    nsfw: Optional[int] = None
    age: Optional[int] = None
    approximateDistance: Optional[bool] = None
    bodyType: Optional[int] = None
    displayName: Optional[str] = None
    ethnicity: Optional[int] = None
    genders: Optional[List[int]] = None
    grindrTribes: Optional[List[int]] = None
    hashtags: Optional[List[str]] = None
    height: Optional[float] = None
    hivStatus: Optional[int] = None
    lastTestedDate: Optional[int] = None
    lookingFor: Optional[List[int]] = None
    meetAt: Optional[List[int]] = None
    profileTags: Optional[List[str]] = None
    pronouns: Optional[List[int]] = None
    relationshipStatus: Optional[int] = None
    sexualPosition: Optional[int] = None
    showAge: Optional[bool] = None
    showDistance: Optional[bool] = None
    socialNetworks: Optional[SocialNetworks] = None
    vaccines: Optional[List[int]] = None
    weight: Optional[float] = None


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
