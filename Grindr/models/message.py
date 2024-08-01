from __future__ import annotations

import enum
from typing import Optional, List, Union

from pydantic import BaseModel


class SendMessageType(str, enum.Enum):
    TEXT = "Text"
    IMAGE = "Image"
    GIPHY = "Giphy"


class MessageType(str, enum.Enum):
    TEXT = "Text"
    IMAGE = "Image"
    GIPHY = "Giphy"
    PROFILE_PHOTO_REPLY = "ProfilePhotoReply"
    ALBUM = "Album"
    ALBUM_CONTENT_REPLY = "AlbumContentReply"


class TextMedia(BaseModel):
    text: str


class ImageMedia(BaseModel):
    mediaId: int
    url: str
    imageHash: str
    width: int
    height: int
    expiresAt: int


class ProfilePhotoReplyMedia(BaseModel):
    imageHash: str
    photoContentReply: str


class AlbumContentReplyMedia(BaseModel):
    albumId: Optional[int] = None
    ownerProfileId: Optional[int] = None
    albumContentId: Optional[int] = None
    albumContentReply: Optional[str] = None
    previewUrl: Optional[str] = None
    expiresAt: Optional[int] = None


MediaBody = Union[TextMedia, ImageMedia, ProfilePhotoReplyMedia, AlbumContentReplyMedia, dict]


class Message(BaseModel):
    messageId: Optional[str] = None
    conversationId: Optional[str] = None
    senderId: Optional[int] = None
    timestamp: Optional[int] = None
    unsent: Optional[bool] = None
    reactions: Optional[List] = None
    type: MessageType = None
    body: Optional[MediaBody] = None
    replyToMessage: Optional[Message] = None
    dynamic: Optional[bool] = None
    chat1Type: Optional[str] = None
    replyPreview: Optional[dict] = None
