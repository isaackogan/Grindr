from typing import Any

from pydantic import BaseModel

from Grindr.client.web.web_base import ClientRoute, URLTemplate
from Grindr.client.web.web_settings import GRINDR_V1


class FetchBoostSessionsRouteResponse(BaseModel):
    boostSessions: list[Any] = None


class FetchBoostSessionsRoute(
    ClientRoute[
        "GET",
        URLTemplate(GRINDR_V1, "/boost/sessions"),
        None,
        None,
        FetchBoostSessionsRouteResponse
    ]
):
    pass
