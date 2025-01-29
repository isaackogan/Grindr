from pydantic import BaseModel

from Grindr.web.routes.fetch.fetch_albums import Album
from Grindr.web.web_schemas import QueryParams, URLTemplate
from Grindr.web.web_route import ClientRoute
from Grindr.web.web_settings import GRINDR_V2


class FetchAlbumRouteResponse(Album, BaseModel):
    pass


class FetchAlbumRouteParams(QueryParams):
    albumId: int


class FetchAlbumRoute(
    ClientRoute[
        "GET",
        URLTemplate(GRINDR_V2, "/albums/{albumId}"),
        FetchAlbumRouteParams,
        None,
        FetchAlbumRouteResponse
    ]
):
    pass
