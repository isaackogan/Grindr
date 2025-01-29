from pydantic import BaseModel

from Grindr.web.web_schemas import URLTemplate
from Grindr.web.web_route import ClientRoute
from Grindr.web.web_settings import GRINDR_V1


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
