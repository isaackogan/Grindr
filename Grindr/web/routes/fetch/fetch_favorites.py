from pydantic import BaseModel

from Grindr.web.web_schemas import URLTemplate
from Grindr.web.web_route import ClientRoute
from Grindr.web.web_settings import GRINDR_V6


class FavoriteProfile(BaseModel):
    profileId: str | None = None
    distance: float | None = None
    lastUpdatedTime: int | None = None
    lastSeen: int | None = None
    hasAlbum: bool | None = None
    isOnline: bool | None = None
    rightNow: str | None = None
    displayName: str | None = None
    photohash: str | None = None


class FetchFavoritesRouteResponse(BaseModel):
    favorites: list[FavoriteProfile] | None = None


class FetchFavoritesRoute(
    ClientRoute[
        "GET",
        URLTemplate(GRINDR_V6, "/favorites"),
        None,
        None,
        FetchFavoritesRouteResponse
    ]
):
    """
    Retrieve favorite profiles

    """
