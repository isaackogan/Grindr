from pydantic import BaseModel

from Grindr.client.web.web_base import ClientRoute, URLTemplate, BodyParams
from Grindr.client.web.web_settings import GRINDR_V1


class FetchOptOutRouteResponse(BaseModel):
    isOptedOut: bool | None = None


class FetchOptOutRoutePayload(BodyParams):
    optOutType: str  # e.g. TOP_PICKS


class FetchOptOutRoute(
    ClientRoute[
        "POST",
        URLTemplate(GRINDR_V1, "/opt-out"),
        None,
        FetchOptOutRoutePayload,
        FetchOptOutRouteResponse
    ]
):
    pass
