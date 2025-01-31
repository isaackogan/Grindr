from pydantic import BaseModel

from Grindr.web.web_base import URLTemplate
from Grindr.web.web_route import ClientRoute
from Grindr.web.web_settings import GRINDR_V6


class MostRecentEyeballView(BaseModel):
    profileId: str | None = None
    photoHash: str | None = None
    timestamp: int | None = None


class FetchEyeballRouteResponse(BaseModel):
    viewedCount: int | None = None
    mostRecent: MostRecentEyeballView | None = None


class FetchEyeballRoute(
    ClientRoute[
        "GET",
        URLTemplate(GRINDR_V6, "/views/eyeball"),
        None,
        None,
        FetchEyeballRouteResponse
    ]
):
    pass
