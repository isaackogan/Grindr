from typing import Optional, List

from pydantic import BaseModel

from Grindr.client.web.web_base import ClientRoute, URLTemplate, QueryParams
from Grindr.client.web.web_settings import GRINDR_V4
from Grindr.models.message import Message


class FetchMessagesRouteParams(QueryParams):
    conversationId: str
    pageKey: str = ""


class Metadata(BaseModel):
    translate: Optional[bool] = None
    hasSharedAlbums: Optional[bool] = None


class FetchMessagesRouteResponse(BaseModel):
    lastReadTimestamp: Optional[int] = None
    messages: Optional[List[Message]] = None
    metadata: Optional[Metadata] = None


class FetchMessagesRoute(
    ClientRoute[
        "GET",
        URLTemplate(GRINDR_V4, "/chat/conversation/{conversationId}/message?pageKey={pageKey}"),
        FetchMessagesRouteParams,
        None,
        FetchMessagesRouteResponse
    ]
):
    """
    Retrieve messages from a conversation.
    If no page key is specified you are grabbing the FIRST page.
    All successive requests should use the page key from the previous response.
    The page key is the OLDEST message in the response.

    """
