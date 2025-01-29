from pydantic import BaseModel

from Grindr.web.web_schemas import URLTemplate
from Grindr.web.web_route import ClientRoute
from Grindr.web.web_settings import GRINDR_V3


class SetGcmPushTokensRoutePayload(BaseModel):
    vendorProvidedIdentifier: str | None = None
    token: str | None = None


class SetGcmPushTokensRoute(
    ClientRoute[
        "POST",
        URLTemplate(GRINDR_V3, "/gcm-push-tokens"),
        None,
        SetGcmPushTokensRoutePayload,
        None
    ]
):
    pass
