from typing import Any

from pydantic import BaseModel

from Grindr.web.web_base import URLTemplate
from Grindr.web.web_route import ClientRoute
from Grindr.web.web_settings import GRINDR_V1


class SetActiveRouteResponse(BaseModel):
    post: Any | None


class SetActiveRoute(
    ClientRoute[
        "GET",
        URLTemplate(GRINDR_V1, "/rightnow/active-post"),
        None,
        None,
        SetActiveRouteResponse
    ]
):
    """
    Retrieve a session from the API

    """
