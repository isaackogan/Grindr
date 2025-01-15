import enum

from pydantic import BaseModel

from Grindr.client.web.web_base import ClientRoute, URLTemplate, BodyParams
from Grindr.client.web.web_settings import GRINDR_V2


class TapType(int, enum.Enum):
    NULL = 0
    FIRE = 1
    DEVIL = 2
    HI = 3


class SetSendTapRouteResponse(BaseModel):
    isMutual: bool


class SetSendTapRoutePayload(BodyParams):
    recipientId: int
    tapType: TapType


class SetSendTapRoute(
    ClientRoute[
        "POST",
        URLTemplate(GRINDR_V2, "/taps/add"),
        None,
        SetSendTapRoutePayload,
        SetSendTapRouteResponse
    ]
):
    """
    Retrieve a session from the API

    """
