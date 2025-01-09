from pydantic import BaseModel

from Grindr.client.web.web_base import ClientRoute, URLTemplate
from Grindr.client.web.web_settings import GRINDR_V5


class FavoriteProfile(BaseModel):
    profileId: str
    distance: float
    lastUpdatedTime: int
    lastSeen: int
    hasAlbum: bool
    isOnline: bool
    rightNow: str


class FetchFavoritesRouteResponse(BaseModel):
    favorites: list[FavoriteProfile] | None = None


class FetchFavoritesRoute(
    ClientRoute[
        "GET",
        URLTemplate(GRINDR_V5, "/favorites"),
        None,
        None,
        FetchFavoritesRouteResponse
    ]
):
    """
    Retrieve favorite profiles

    """
