from typing import Optional

from pydantic import BaseModel

from Grindr.client.web.web_base import ClientRoute, URLTemplate, QueryParams
from Grindr.client.web.web_settings import GRINDR_V3


class SetUnblockUserRouteParams(QueryParams):
    profileId: str = ""


class SetUnblockUserRouteResponse(BaseModel):
    updateTime: Optional[int] = None


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
