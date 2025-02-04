from pydantic import BaseModel

from Grindr.web.routes.fetch.fetch_albums import Album
from Grindr.web.web_base import URLTemplate
from Grindr.web.web_route import ClientRoute
from Grindr.web.web_settings import GRINDR_V2


class FetchSharedAlbumsRouteResponse(BaseModel):
    albums: list[Album] | None = None


class FetchSharedAlbumsRouteParams(BaseModel):
    profileId: str = ""


class FetchSharedAlbumsRoute(
    ClientRoute[
        "GET",
        URLTemplate(GRINDR_V2, "/albums/shares/{profileId}"),
        FetchSharedAlbumsRouteParams,
        None,
        FetchSharedAlbumsRouteResponse
    ]
):
    """
    Fetch shared albums or albums for a specific profile

    If profileId is set to an EMPTY string, all albums will be retrieved.
    if it is set to ANY value, it will retrieve the albums for the profile ID entered.

    """
