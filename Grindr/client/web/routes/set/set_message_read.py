from typing import Optional

from pydantic import BaseModel

from Grindr.client.web.web_base import ClientRoute, URLTemplate, QueryParams
from Grindr.client.web.web_settings import GRINDR_V3, GRINDR_V4


class SetMessageReadRouteParams(QueryParams):
    conversationId: str
    messageId: str


class SetMessageReadRoute(
    ClientRoute[
        "POST",
        URLTemplate(GRINDR_V4, "/chat/conversation/{conversationId}/read/{messageId}"),
        SetMessageReadRouteParams,
        None,
        None
    ]
):
    """
    Retrieve a session from the API

    """
