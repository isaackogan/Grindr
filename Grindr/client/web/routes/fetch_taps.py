from typing import Optional, List

from pydantic import BaseModel

from Grindr.client.web.routes.fetch_profiles import Profile
from Grindr.client.web.web_base import ClientRoute, URLTemplate
from Grindr.client.web.web_settings import GRINDR_V2


class FetchTapsRouteResponse(BaseModel):
    profiles: Optional[List[Profile]]


class FetchTapsRoute(
    ClientRoute[
        "GET",
        URLTemplate(GRINDR_V2, "/taps/received"),
        None,
        None,
        FetchTapsRouteResponse
    ]
):
    """
    Retrieve a session from the API

    """
