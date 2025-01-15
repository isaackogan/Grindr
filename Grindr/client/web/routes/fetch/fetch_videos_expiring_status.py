from pydantic import BaseModel

from Grindr.client.web.web_base import ClientRoute, URLTemplate
from Grindr.client.web.web_settings import GRINDR_V4


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
