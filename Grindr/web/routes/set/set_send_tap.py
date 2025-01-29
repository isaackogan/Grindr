import enum

from pydantic import BaseModel

from Grindr.web.web_schemas import BodyParams, URLTemplate
from Grindr.web.web_route import ClientRoute
from Grindr.web.web_settings import GRINDR_V2


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
