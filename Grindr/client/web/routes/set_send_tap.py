import enum

from pydantic import BaseModel

from Grindr.client.web.web_base import ClientRoute, URLTemplate, BodyParams
from Grindr.client.web.web_settings import GRINDR_V2


class TapType(int, enum.Enum):
    FIRE = 1
    DEVIL = 2
    HI = 3


class SetSendTapRouteResponse(BaseModel):
    isMutual: bool


class SetSendTapRouteBody(BodyParams):
    recipientId: int
    tapType: TapType


class SetSendTapRoute(
    ClientRoute[
        "POST",
        URLTemplate(GRINDR_V2, "/taps/add"),
        None,
        SetSendTapRouteBody,
        SetSendTapRouteResponse
    ]
):
    """
    Retrieve a session from the API

    """
