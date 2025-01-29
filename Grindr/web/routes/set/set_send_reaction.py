from Grindr.web.web_schemas import BodyParams, URLTemplate
from Grindr.web.web_route import ClientRoute
from Grindr.web.web_settings import GRINDR_V4


class SetSendReactionRoutePayload(BodyParams):
    conversationId: str
    messageId: str
    reactionType: int = 1


class SetSendReactionRoute(
    ClientRoute[
        "POST",
        URLTemplate(GRINDR_V4, "/chat/message/reaction"),
        None,
        SetSendReactionRoutePayload,
        None
    ]
):
    """
    Retrieve a session from the API

    """
