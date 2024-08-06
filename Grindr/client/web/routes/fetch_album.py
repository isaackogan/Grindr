from pydantic import BaseModel

from pydantic import BaseModel

from Grindr.client.web.routes.fetch_albums import Album
from Grindr.client.web.web_base import ClientRoute, URLTemplate, QueryParams
from Grindr.client.web.web_settings import GRINDR_V2


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
