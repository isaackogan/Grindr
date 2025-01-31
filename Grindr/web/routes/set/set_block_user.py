from pydantic import BaseModel

from Grindr.web.web_schemas import QueryParams
from Grindr.web.web_base import URLTemplate
from Grindr.web.web_route import ClientRoute
from Grindr.web.web_settings import GRINDR_V3


class SetBlockUserRouteParams(QueryParams):
    profileId: int


class SetBlockUserRouteResponse(BaseModel):
    updateTime: int | None = None


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
