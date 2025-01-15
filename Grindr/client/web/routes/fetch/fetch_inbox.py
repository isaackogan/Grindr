from typing import Any

from pydantic import BaseModel

from Grindr.client.web.web_base import ClientRoute, URLTemplate, QueryParams
from Grindr.client.web.web_settings import GRINDR_V1


class Participant(BaseModel):
    profileId: int | None = None
    primaryMediaHash: str | None = None
    lastOnline: int | None = None
    distanceMetres: float | None = None


class Preview(BaseModel):
    conversationId: dict | None = None
    messageId: str | None = None
    chat1MessageId: str | None = None
    senderId: int | None = None
    type: str | None = None
    chat1Type: str | None = None
    text: str | None = None
    url: str | None = None
    lat: float | None = None
    lon: float | None = None
    albumId: int | None = None
    albumContentId: int | None = None
    albumContentReply: str | None = None
    duration: int | None = None
    imageHash: str | None = None
    photoContentReply: str | None = None


class InboxConversationData(BaseModel):
    conversationId: str | None = None
    name: str | None = None
    participants: list[Participant] | None = None
    lastActivityTimestamp: int | None = None
    unreadCount: int | None = None
    preview: Preview | None = None
    muted: bool | None = None
    pinned: bool | None = None
    favorite: bool | None = None
    context: str | None = None
    onlineUntil: int | None = None
    translatable: bool | None = None
    rightNow: str | None = None


class FetchInboxRouteResponse(BaseModel):
    entries: list[InboxConversationData] | None = []
    nextPage: int | None = None


class FetchInboxRouteParams(QueryParams):
    page: int


class FetchInboxRoutePayload(QueryParams):
    unreadOnly: bool

    def model_dump(
            self,
            **kwargs
    ) -> dict[str, Any]:
        kwargs['exclude_none'] = True
        return super().model_dump(**kwargs)


class FetchInboxRoute(
    ClientRoute[
        "POST",
        URLTemplate(GRINDR_V1, "/inbox?page={page}"),
        FetchInboxRouteParams,
        FetchInboxRoutePayload,
        FetchInboxRouteResponse
    ]
):
    """
    Retrieve a session from the API

    """
