import enum

from pydantic import BaseModel, Field
from pygeohash import geohash

from Grindr.client.web.web_base import ClientRoute, URLTemplate, QueryParams
from Grindr.client.web.web_settings import GRINDR_V1, GRINDR_V3


class FetchCascadeRouteParams(QueryParams):
    geohash: str
    pageNumber: int = 1
    onlineOnly: bool = False
    photoOnly: bool = False
    faceOnly: bool = False
    notRecentlyChatted: bool = False
    favorites: bool = False
    showSponsoredProfiles: bool = False
    shuffle: bool = False


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
    type: str | None = Field(None, alias='@type')
    profileId: int | None = None
    lastOnline: int | None = None
    onlineUntil: int | None = None
    distanceMeters: int | None = None
    displayName: str | None = None
    aboutMe: str | None = None
    age: int | None = None
    photoMediaHashes: list[str] | None = None
    heightCm: int | None = None
    lookingFor: list[int] | None = None
    tribes: list[int] | None = None
    meetAt: list[int] | None = None
    vaccines: list[int] | None = None
    genders: list[int] | None = None
    pronouns: list[int] | None = None
    relationshipStatus: int | None = None
    ethnicity: Ethnicity | None = None
    bodyType: int | None = None
    acceptsNsfwPics: int | None = None
    hivStatus: int | None = None
    approximateDistance: bool | None = None
    tags: list[str] | None = None
    isFavorite: bool | None = None
    socialNetworks: list[dict] | None = None
    isBoosting: bool | None = None
    hasChattedInLast24Hrs: bool | None = None
    hasUnviewedSpark: bool | None = None
    isTeleporting: bool | None = None
    isRoaming: bool | None = None
    isRightNow: bool | None = None
    unreadCount: int | None = None
    rightNow: str | None = None
    isPopular: bool | None = None


class CascadeProfile(BaseModel):
    type: str
    data: CascadeProfileData


class FetchCascadeRouteResponse(BaseModel):
    items: list[CascadeProfile]
    nextPage: int | None = None


class FetchCascadeRoute(
    ClientRoute[
        "GET",
        URLTemplate(
            GRINDR_V3,
            "/cascade"
            "?nearbyGeoHash={geohash}"
            "&onlineOnline={onlineOnly}"
            "&photoOnly={photoOnly}"
            "&faceOnly={faceOnly}"
            "&notRecentlyChatted={notRecentlyChatted}"
            "&pageNumber={pageNumber}"
            "&favorites={favorites}"
            "&showSponsoredProfiles={showSponsoredProfiles}"
            "&shuffle={shuffle}"
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
