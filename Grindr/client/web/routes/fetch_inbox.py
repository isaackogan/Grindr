from typing import Optional, List

from pydantic import BaseModel

from Grindr.client.web.web_base import ClientRoute, URLTemplate, QueryParams
from Grindr.client.web.web_settings import GRINDR_V1


class Participant(BaseModel):
    profileId: Optional[int] = None
    primaryMediaHash: Optional[str] = None
    lastOnline: Optional[int] = None
    distanceMetres: Optional[float] = None


class Preview(BaseModel):
    conversationId: Optional[dict] = None
    messageId: Optional[str] = None
    chat1MessageId: Optional[str] = None
    senderId: Optional[int] = None
    type: Optional[str] = None
    chat1Type: Optional[str] = None
    text: Optional[str] = None
    url: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    albumId: Optional[int] = None
    albumContentId: Optional[int] = None
    albumContentReply: Optional[str] = None
    duration: Optional[int] = None
    imageHash: Optional[str] = None
    photoContentReply: Optional[str] = None


class InboxConversationData(BaseModel):
    conversationId: Optional[str] = None
    name: Optional[str] = None
    participants: Optional[List[Participant]] = None
    lastActivityTimestamp: Optional[int] = None
    unreadCount: Optional[int] = None
    preview: Optional[Preview] = None
    muted: Optional[bool] = None
    pinned: Optional[bool] = None
    favorite: Optional[bool] = None
    context: Optional[str] = None
    onlineUntil: Optional[int] = None
    translatable: Optional[bool] = None
    rightNow: Optional[str] = None


class FetchInboxRouteResponse(BaseModel):
    entries: Optional[List[InboxConversationData]] = []
    nextPage: Optional[int] = None


class FetchInboxRouteParams(QueryParams):
    page: int


class FetchInboxRoute(
    ClientRoute[
        "GET",
        URLTemplate(GRINDR_V1, "/inbox?page={page}"),
        FetchInboxRouteParams,
        None,
        FetchInboxRouteResponse
    ]
):
    """
    Retrieve a session from the API

    """
