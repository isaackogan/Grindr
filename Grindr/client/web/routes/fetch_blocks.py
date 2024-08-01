from typing import Optional, List

from pydantic import BaseModel

from Grindr.client.web.web_base import ClientRoute, URLTemplate, BodyParams
from Grindr.client.web.web_settings import GRINDR_V3_1


class BlockedProfile(BaseModel):
    profileId: int
    blockedTime: int


class FetchBlocksRouteResponse(BaseModel):
    blocking: BlockedProfile


class FetchBlocksRoute(
    ClientRoute[
        "POST",
        URLTemplate(GRINDR_V3_1, "/me/blocks"),
        None,
        None,
        FetchBlocksRouteResponse
    ]
):
    """
    Retrieve blocked accounts

    """
