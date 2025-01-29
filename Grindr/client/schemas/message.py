from __future__ import annotations

import enum
from typing import List, Union

from pydantic import BaseModel


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
    albumId: int | None = None
    ownerProfileId: int | None = None
    albumContentId: int | None = None
    albumContentReply: str | None = None
    previewUrl: str | None = None
    expiresAt: int | None = None


MediaBody = Union[TextMedia, ImageMedia, ProfilePhotoReplyMedia, AlbumContentReplyMedia, dict]


class Message(BaseModel):
    messageId: str | None = None
    conversationId: str | None = None
    senderId: int | None = None
    timestamp: int | None = None
    unsent: bool | None = None
    reactions: List | None = None
    type: MessageType = None
    body: MediaBody | None = None
    replyToMessage: Message | None = None
    dynamic: bool | None = None
    chat1Type: str | None = None
    replyPreview: dict | None = None
