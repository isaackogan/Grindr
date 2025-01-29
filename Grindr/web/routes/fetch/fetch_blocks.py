from pydantic import BaseModel

from Grindr.web.web_schemas import URLTemplate
from Grindr.web.web_route import ClientRoute
from Grindr.web.web_settings import GRINDR_V3_1


class BlockedProfile(BaseModel):
    profileId: int
    blockedTime: int  # Always 0


class FetchBlocksRouteResponse(BaseModel):
    blocking: list[BlockedProfile]


class FetchBlocksRoute(
    ClientRoute[
        "GET",
        URLTemplate(GRINDR_V3_1, "/me/blocks"),
        None,
        None,
        FetchBlocksRouteResponse
    ]
):
    """
    Retrieve blocked accounts

    """
