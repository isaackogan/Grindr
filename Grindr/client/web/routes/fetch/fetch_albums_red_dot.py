from pydantic import BaseModel

from Grindr.client.web.web_base import ClientRoute, URLTemplate
from Grindr.client.web.web_settings import GRINDR_V1


class FetchAlbumsRedDotRouteResponse(BaseModel):
    hasUnseen: bool | None = None


class FetchAlbumsRedDotRoute(
    ClientRoute[
        "GET",
        URLTemplate(GRINDR_V1, "/albums/red-dot"),
        None,
        None,
        FetchAlbumsRedDotRouteResponse
    ]
):
    pass
