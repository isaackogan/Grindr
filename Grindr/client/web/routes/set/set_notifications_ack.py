from Grindr.client.web.web_base import ClientRoute, URLTemplate, BodyParams
from Grindr.client.web.web_settings import GRINDR_PUBLIC_V1


class SetNotificationsAckRoutePayload(BodyParams):
    notificationId: str | None = None
    source: str | None = None


class SetNotificationsAckRoute(
    ClientRoute[
        "POST",
        URLTemplate(GRINDR_PUBLIC_V1, "/notifications/ack"),
        None,
        SetNotificationsAckRoutePayload,
        None
    ]
):
    pass
