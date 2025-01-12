from pydantic import BaseModel

from Grindr.client.web.web_base import ClientRoute, URLTemplate
from Grindr.client.web.web_settings import GRINDR_V3


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
