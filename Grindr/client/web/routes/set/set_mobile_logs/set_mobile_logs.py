from Grindr.client.web.web_base import ClientRoute, URLTemplate, BodyParams
from Grindr.client.web.web_settings import GRINDR_V3
from .event_schemas import *


class SetMobileLogsRoutePayload(BodyParams):
    events: list[MobileLogEvent]


class SetMobileLogsRoute(
    ClientRoute[
        "GET",
        URLTemplate(GRINDR_V3, "/logging/mobile/logs"),
        None,
        SetMobileLogsRoutePayload,
        None
    ]
):
    pass
