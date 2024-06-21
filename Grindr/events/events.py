from __future__ import annotations

from typing import Any, Optional, Literal, Union, List

from pydantic import BaseModel


class Event(BaseModel):
    """
    Base event emitted from the TikTokLiveClient

    """

    @property
    def event_type(self) -> str:
        """
        String representation of the class type

        :return: Class name

        """

        return self.get_event_type()

    @classmethod
    def get_event_type(cls) -> str:
        """
        String representation of the class type

        :return: Class name

        """

        return cls.__name__


class WebsocketResponse(BaseModel):
    type: Optional[str] = None
    ref: Optional[Any] = None
    payload: Optional[dict] = None


class UnknownEvent(Event):
    """
    Triggered when a message is received that is NOT tracked yet.

    """

    data: dict
    payload: Optional[dict] = None


class ConnectEvent(Event):
    """
    Manually thrown whenever a connection is started

    """


class TextMedia(BaseModel):
    text: str


class ImageMedia(BaseModel):
    mediaId: int
    url: str
    imageHash: str
    width: int
    height: int
    expiresAt: int


MediaType = Literal["Text", "Image", "ProfilePhotoReply", "Album", "AlbumContentReply"]
MediaBody = Union[TextMedia, ImageMedia, dict]


class MessageEventReplyPreview(BaseModel):
    senderId: int
    type: Optional[MediaType] = None
    chat1Type: Optional[str] = None
    previewMessageId: str
    text: Optional[str]
    lat: Optional[Any]
    lon: Optional[Any]
    albumId: Optional[Any]
    duration: Optional[Any]


class MessageEvent(Event):
    messageId: Optional[str] = None
    conversationId: Optional[str] = None
    senderId: Optional[int] = None
    timestamp: Optional[int] = None
    unsent: Optional[bool] = None
    reactions: Optional[List[Any]] = None
    type: Optional[MediaType] = None
    body: Optional[MediaBody] = None
    replyToMessage: Optional[Any] = None
    dynamic: Optional[bool] = None
    chat1Type: Optional[str] = None
    replyPreview: Optional[MessageEventReplyPreview] = None


class TapEvent(Event):
    timestamp: Optional[int] = None
    senderId: Optional[int] = None
    recipientId: Optional[int] = None
    tapType: Optional[int] = None
    senderProfileImageHash: Optional[str] = None
    senderDisplayName: Optional[str] = None
    isMutual: Optional[bool] = None


class ViewedEventMostRecent(BaseModel):
    profileId: Optional[str] = None
    photoHash: Optional[str] = None
    timestamp: Optional[int] = None


class ViewedEvent(Event):
    viewedCount: Optional[int] = None
    mostRecent: Optional[ViewedEventMostRecent] = None


class DisconnectEvent(Event):
    """
    Thrown when disconnecting from a stream

    """
