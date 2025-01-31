from typing import Any

from pydantic import BaseModel

from Grindr.web.web_base import URLTemplate
from Grindr.web.web_route import ClientRoute
from Grindr.web.web_settings import GRINDR_V2


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
