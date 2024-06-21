from typing import Optional, Any

from pydantic import BaseModel

from Grindr.client.web.web_base import ClientRoute, URLTemplate
from Grindr.client.web.web_settings import GRINDR_V1


class SetActiveRouteResponse(BaseModel):
    post: Optional[Any]


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
