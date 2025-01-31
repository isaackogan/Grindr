from pydantic import BaseModel

from Grindr.web.web_base import URLTemplate
from Grindr.web.web_route import ClientRoute
from Grindr.web.web_settings import GRINDR_V4


class VideosExpiringStatusRouteResponse(BaseModel):
    total: int
    available: int


class FetchVideosExpiringStatusRoute(
    ClientRoute[
        "GET",
        URLTemplate(GRINDR_V4, "/videos/expiring/status"),
        None,
        None,
        VideosExpiringStatusRouteResponse
    ]
):
    pass
