import enum
from typing import Optional, Literal

from pydantic import BaseModel

from Grindr.client.web.web_base import ClientRoute, URLTemplate, QueryParams
from Grindr.client.web.web_settings import GRINDR_V3, GRINDR_V4


class TypingStatus(str, enum.Enum):
    TYPING = "Typing"
    CLEARED = "Cleared"
    SENT = "Sent"


class SetTypingRouteBody(QueryParams):
    conversationId: str
    status: TypingStatus


class SetTypingRoute(
    ClientRoute[
        "POST",
        URLTemplate(GRINDR_V4, "/chatstatus/typing"),
        None,
        SetTypingRouteBody,
        None
    ]
):
    """
    Retrieve a session from the API

    """
