from pydantic import BaseModel

from Grindr.web.web_schemas import QueryParams
from Grindr.web.web_base import URLTemplate
from Grindr.web.web_route import ClientRoute
from Grindr.web.web_settings import GRINDR_V3


class SetUnblockUserRouteParams(QueryParams):
    profileId: str = ""


class SetUnblockUserRouteResponse(BaseModel):
    updateTime: int | None = None


class SetUnblockUserRoute(
    ClientRoute[
        "DELETE",
        URLTemplate(GRINDR_V3, "/me/blocks/{profileId}"),
        SetUnblockUserRouteParams,
        None,
        SetUnblockUserRouteResponse
    ]
):
    """
    Unblock a user. Set profileId to an empty string to unblock all users

    """
