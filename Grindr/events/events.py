from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel

from Grindr.client.web.routes.fetch.fetch_messages import Message
from Grindr.models.message import MessageType


class Event(BaseModel):
    """
    Base event emitted from the Grindr client

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
    type: str | None = None
    ref: Any | None = None
    payload: dict | None = None

    @classmethod
    def from_bytes(cls, data: bytes) -> WebsocketResponse:
        return cls(**json.loads(data.decode("utf-8")))


class UnknownEvent(Event):
    """
    Triggered when a message is received that is NOT tracked yet.

    """

    data: dict
    payload: dict | None = None


class ConnectEvent(Event):
    """
    Manually thrown whenever a connection is started

    """


class MessageEventReplyPreview(BaseModel):
    senderId: int
    type: MessageType | None = None
    chat1Type: str | None = None
    previewMessageId: str
    text: str | None
    lat: Any | None
    lon: Any | None
    albumId: Any | None
    duration: Any | None


class MessageEvent(Message, Event):
    pass


class TapEvent(Event):
    timestamp: int | None = None
    senderId: int | None = None
    recipientId: int | None = None
    tapType: int | None = None
    senderProfileImageHash: str | None = None
    senderDisplayName: str | None = None
    isMutual: bool | None = None


class ViewedEventMostRecent(BaseModel):
    profileId: str | None = None
    photoHash: str | None = None
    timestamp: int | None = None


class ViewedEvent(Event):
    viewedCount: int | None = None
    mostRecent: ViewedEventMostRecent | None = None


class DisconnectEvent(Event):
    """
    Thrown when disconnecting from a stream

    """
