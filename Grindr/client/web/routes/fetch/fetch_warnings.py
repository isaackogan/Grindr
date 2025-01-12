from typing import Any

from pydantic import BaseModel

from Grindr.client.web.web_base import ClientRoute, URLTemplate
from Grindr.client.web.web_settings import GRINDR_V2


class FetchWarningsRouteResponse(BaseModel):
    warnings: list[Any] = None


class FetchWarningsRoute(
    ClientRoute[
        "GET",
        URLTemplate(GRINDR_V2, "/warnings"),
        None,
        None,
        FetchWarningsRouteResponse
    ]
):
    pass
