import enum

from Grindr.web.web_schemas import QueryParams
from Grindr.web.web_base import URLTemplate
from Grindr.web.web_route import ClientRoute
from Grindr.web.web_settings import GRINDR_V4


class TypingStatus(str, enum.Enum):
    TYPING = "Typing"
    CLEARED = "Cleared"
    SENT = "Sent"


class SetTypingRoutePayload(QueryParams):
    conversationId: str
    status: TypingStatus


class SetTypingRoute(
    ClientRoute[
        "POST",
        URLTemplate(GRINDR_V4, "/chatstatus/typing"),
        None,
        SetTypingRoutePayload,
        None
    ]
):
    """
    Retrieve a session from the API

    """
