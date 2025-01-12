from pydantic import BaseModel

from Grindr.client.web.web_base import ClientRoute, URLTemplate
from Grindr.client.web.web_settings import GRINDR_V2, GRINDR_V1


class TapData(BaseModel):
    senderId: str | None = None
    receiverId: str | None = None
    tapType: int | None = None
    sentOn: int | None = None
    deleted: bool | None = None
    readOn: int | None = None


type FetchTapsRouteResponse = list[TapData] | None


class FetchTapsSentRoute(
    ClientRoute[
        "GET",
        URLTemplate(GRINDR_V1, "/interactions/taps/sent"),
        None,
        None,
        FetchTapsRouteResponse
    ]
):
    """
    Retrieve a session from the API

    """
