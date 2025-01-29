from __future__ import annotations

import json
import uuid
from abc import ABC
from typing import Any, ClassVar

from pydantic import BaseModel, Field

from Grindr.client.schemas.message import MessageType


class WebSocketResponse(BaseModel):
    """WebSocket response from Grindr"""

    # Type of item
    type: str | None = None

    # Reference to the item
    ref: Any | None = None

    # Raw event payload
    payload: dict | None = None

    # If the event is associated with a notification, the ID of it
    notificationId: str | None = None

    # If the event is associated with the response to an outgoing event, the status of the sent event
    status: int | None = None

    @classmethod
    def from_bytes(cls, data: bytes) -> WebSocketResponse:
        """Decode a WebSocket response from bytes"""
        return cls(**json.loads(data.decode("utf-8")))


class MessagePayloadTarget(BaseModel):
    """The target of a message payload"""

    type: str = "Direct"
    targetId: int


type MessagePayloadBodyType = TextPayloadBody | ImagePayloadBody | GifPayloadBody


class MessagePayload[T: MessageType, B: MessagePayloadBodyType](BaseModel):
    """A message payload sent to the Grindr WebSocket"""

    type: T
    target: MessagePayloadTarget
    body: B
    ref: uuid.UUID = Field(default_factory=uuid.uuid4)

    def to_message(
            self,
            session_id: str,
            ref: uuid.UUID | None = None,
    ) -> Message[MessagePayload]:
        """Create a message from the payload"""

        return Message(
            payload=self,
            token=session_id,
            **{"ref": ref} if ref else {}
        )


class Message[T: MessagePayload](BaseModel):
    """A message sent to the Grindr WebSocket"""

    # Message payload
    payload: T

    # Ref for the message
    ref: uuid.UUID = Field(default_factory=uuid.uuid4)

    # Current session ID
    token: str

    # Outgoing event type
    type: str = "chat.v1.message.send"


class MessagePayloadBody(BaseModel, ABC):
    """The body of a message payload"""

    # The type of message
    _message_type: ClassVar[MessageType] = NotImplemented

    def to_message(
            self,
            session_id: str,
            target_profile_id: int
    ) -> MessagePayload:
        """Convert a payload body to a Message"""

        # Create the payload
        payload: MessagePayload = MessagePayload(
            type=self._message_type,
            target=MessagePayloadTarget(targetId=target_profile_id),
            body=self
        )

        # Create the message object
        return payload.to_message(
            session_id=session_id,
            ref=payload.ref
        )


class TextPayloadBody(MessagePayloadBody):
    """Text Payload"""
    _message_type = MessageType.TEXT

    text: str


class ImagePayloadBody(MessagePayloadBody):
    """Image Payload"""
    _message_type = MessageType.IMAGE

    mediaId: int


class GifPayloadBody(MessagePayloadBody):
    """GIF Payload"""
    _message_type = MessageType.GIPHY

    stillPath: str
    urlPath: str
    id: str
    previewPath: str
    imageHash: str
    width: int
    height: int

    @classmethod
    def from_data(
            cls,
            image_url: str,
            image_id: str,
            width: int = 1080,
            height: int = 1920
    ) -> "GifPayloadBody":
        """Create a GIF payload body from defaults"""

        return cls(
            stillPath=image_url,
            urlPath=image_url,
            id=image_id,
            previewPath=image_url,
            imageHash=f"giphy/{image_id}",
            width=width,
            height=height
        )


