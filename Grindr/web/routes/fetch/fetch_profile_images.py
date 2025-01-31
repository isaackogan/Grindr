from pydantic import BaseModel

from Grindr.web.routes.fetch.fetch_profiles import Media
from Grindr.web.web_schemas import QueryParams
from Grindr.web.web_base import URLTemplate
from Grindr.web.web_route import ClientRoute
from Grindr.web.web_settings import GRINDR_V3_1


class FetchProfileImagesRouteParams(QueryParams):
    """Get all images associated with profile photos on the account"""
    selected: bool


class FetchProfileImagesRouteResponse(BaseModel):
    medias: list[Media]


class FetchProfileImagesRoute(
    ClientRoute[
        "GET",
        URLTemplate(GRINDR_V3_1, "/me/profile/images?selected={selected}"),
        FetchProfileImagesRouteParams,
        None,
        FetchProfileImagesRouteResponse
    ]
):
    """
    Get the current profile images. The 'primaryImageHash' signifies the main image (your profile cover photo).
    The secondary image hashes are your other photos.

    """
