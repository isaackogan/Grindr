from typing import Optional

from pydantic import BaseModel

from Grindr.client.web.web_base import ClientRoute, URLTemplate, QueryParams
from Grindr.client.web.web_settings import GRINDR_V3


class SetBlockUserRouteParams(QueryParams):
    profileId: int


class SetBlockUserRouteResponse(BaseModel):
    updateTime: Optional[int] = None


class SetBlockUserRoute(
    ClientRoute[
        "POST",
        URLTemplate(GRINDR_V3, "/me/blocks/{profileId}"),
        SetBlockUserRouteParams,
        None,
        SetBlockUserRouteResponse
    ]
):
    """
    Retrieve a session from the API

    """
