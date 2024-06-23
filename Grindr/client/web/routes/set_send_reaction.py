import uuid
from typing import List

from pydantic import BaseModel, Field

from Grindr.client.web.web_base import ClientRoute, URLTemplate, QueryParams, BodyParams
from Grindr.client.web.web_settings import GRINDR_V1, GRINDR_V4


class SetSendReactionRouteBody(BodyParams):
    conversationId: str
    messageId: str
    reactionType: int = 1


class SetSendReactionRoute(
    ClientRoute[
        "POST",
        URLTemplate(GRINDR_V4, "/chat/message/reaction"),
        None,
        SetSendReactionRouteBody,
        None
    ]
):
    """
    Retrieve a session from the API

    """
