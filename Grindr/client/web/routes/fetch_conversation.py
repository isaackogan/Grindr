from typing import Optional, List

from pydantic import BaseModel

from Grindr.client.web.web_base import ClientRoute, URLTemplate, QueryParams
from Grindr.client.web.web_settings import GRINDR_V4
from Grindr.events import MediaType, MediaBody


class FetchConversationRouteParams(QueryParams):
    conversationId: str


class Message(BaseModel):
    messageId: Optional[str] = None
    conversationId: Optional[str] = None
    senderId: Optional[int] = None
    timestamp: Optional[int] = None
    unsent: Optional[bool] = None
    reactions: Optional[List] = None
    type: MediaType = None
    body: Optional[MediaBody] = None
    replyToMessage: Optional[str] = None
    dynamic: Optional[bool] = None
    chat1Type: Optional[str] = None
    replyPreview: Optional[str] = None


class Metadata(BaseModel):
    translate: Optional[bool] = None
    hasSharedAlbums: Optional[bool] = None


class FetchConversationRouteResponse(BaseModel):
    lastReadTimestamp: Optional[str] = None
    messages: Optional[List[Message]] = None
    metadata: Optional[Metadata] = None


class FetchConversationRoute(
    ClientRoute[
        "GET",
        URLTemplate(GRINDR_V4, "/chat/conversation/{conversationId}/message"),
        FetchConversationRouteParams,
        None,
        FetchConversationRouteResponse
    ]
):
    """
    Retrieve a session from the API

    """
