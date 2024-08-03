import enum
from typing import Optional, List

from pydantic import BaseModel, Field
from pygeohash import geohash

from Grindr.client.web.web_base import ClientRoute, URLTemplate, QueryParams
from Grindr.client.web.web_settings import GRINDR_V1


class FetchCascadeRouteParams(QueryParams):
    geohash: str
    pageNumber: int = 1
    onlineOnly: bool = False
    photoOnly: bool = False
    faceOnly: bool = False
    notRecentlyChatted: bool = False
    fresh: bool = False
    favorites: bool = False


class Ethnicity(int, enum.Enum):
    ASIAN = 1
    BLACK = 2
    LATINO = 3
    MIDDLE_EASTERN = 4
    MIXED = 5
    NATIVE_AMERICAN = 6
    WHITE = 7
    _UNKNOWN = 8
    SOUTH_ASIAN = 9


class CascadeProfileData(BaseModel):
    type: Optional[str] = Field(None, alias='@type')
    profileId: Optional[int] = None
    lastOnline: Optional[int] = None
    onlineUntil: Optional[int] = None
    distanceMeters: Optional[int] = None
    displayName: Optional[str] = None
    aboutMe: Optional[str] = None
    age: Optional[int] = None
    photoMediaHashes: Optional[List[str]] = None
    heightCm: Optional[int] = None
    lookingFor: Optional[List[int]] = None
    tribes: Optional[List[int]] = None
    meetAt: Optional[List[int]] = None
    vaccines: Optional[List[int]] = None
    genders: Optional[List[int]] = None
    pronouns: Optional[List[int]] = None
    relationshipStatus: Optional[int] = None
    ethnicity: Optional[Ethnicity] = None
    bodyType: Optional[int] = None
    acceptsNsfwPics: Optional[int] = None
    hivStatus: Optional[int] = None
    approximateDistance: Optional[bool] = None
    tags: Optional[List[str]] = None
    isFavorite: Optional[bool] = None
    socialNetworks: Optional[list[dict]] = None
    isBoosting: Optional[bool] = None
    hasChattedInLast24Hrs: Optional[bool] = None
    hasUnviewedSpark: Optional[bool] = None
    isTeleporting: Optional[bool] = None
    isRoaming: Optional[bool] = None
    isRightNow: Optional[bool] = None
    unreadCount: Optional[int] = None
    rightNow: Optional[str] = None
    isPopular: Optional[bool] = None


class CascadeProfile(BaseModel):
    type: str
    data: CascadeProfileData


class FetchCascadeRouteResponse(BaseModel):
    items: List[CascadeProfile]
    nextPage: Optional[int] = None


class FetchCascadeRoute(
    ClientRoute[
        "GET",
        URLTemplate(
            GRINDR_V1,
            "/cascade"
            "?nearbyGeoHash={geohash}"
            "&onlineOnline={onlineOnly}"
            "&photoOnly={photoOnly}"
            "&faceOnly={faceOnly}"
            "&notRecentlyChatted={notRecentlyChatted}"
            "&fresh={fresh}"
            "&pageNumber={pageNumber}"
            "&favorites={favorites}"
        ),
        FetchCascadeRouteParams,
        None,
        FetchCascadeRouteResponse
    ]
):
    """
    Get profiles in an area

    """

    @classmethod
    def generate_hash(cls, lat: float, lon: float) -> str:
        return geohash.encode(lat, lon, precision=12)
