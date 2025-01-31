from __future__ import annotations

from abc import ABC
from typing import Any, ClassVar

from pydantic import BaseModel, ValidationError

from Grindr.client.schemas.message import Message
from Grindr.ws.events.base import WebSocketEvent, WSEventMap
from Grindr.ws.ws_schemas import WebSocketResponse


class BaseWebSocketEventPayload(BaseModel, ABC):
    _event_name: ClassVar[str] = NotImplemented

    @classmethod
    def event_name(cls) -> str:
        return cls._event_name


class ViewedEventMostRecent(BaseModel):
    profileId: str | None = None
    photoHash: str | None = None
    timestamp: int | None = None


@WebSocketEvent("ws.ext.unknown")
class UnknownEvent(BaseWebSocketEventPayload):
    """An Unknown Event"""
    raw_data: Any


@WebSocketEvent("ws.connection.established")
class ConnectEvent(BaseWebSocketEventPayload):
    """WebSocket connect event"""


@WebSocketEvent("chat.v1.message_sent")
class MessageEvent(Message, BaseWebSocketEventPayload):
    """WebSocket Message Event"""


@WebSocketEvent("tap.v1.tap_sent")
class TapEvent(BaseWebSocketEventPayload):
    """Tap Event"""

    timestamp: int | None = None
    senderId: int | None = None
    recipientId: int | None = None
    tapType: int | None = None
    senderProfileImageHash: str | None = None
    senderDisplayName: str | None = None
    isMutual: bool | None = None


@WebSocketEvent("viewed_me.v1.new_view_received")
class ViewedEvent(BaseWebSocketEventPayload):
    """View Received Event"""

    viewedCount: int | None = None
    mostRecent: ViewedEventMostRecent | None = None


@WebSocketEvent("ws.ext.disconnect")
class DisconnectEvent(BaseWebSocketEventPayload):
    """Disconnect Event"""


class Event[T: BaseWebSocketEventPayload](WebSocketResponse):
    """A mobile log event sent to the Grindr API"""

    type: str | None = None
    payload: T | None = None

    def __init__(self, /, **data: Any):
        name: str = data.get('type', 'ws.ext.unknown')

        if name not in WSEventMap:
            name = 'ws.ext.unknown'
            data['payload'] = {'raw_data': data.get('payload', None)}

        try:
            super().__init__(**data)
        except ValidationError as ex:
            ex.add_note(f"Variant: Event[\"{name}\", {WSEventMap.get(name).__name__}]")
            raise ex


__all__ = [
    "ConnectEvent",
    "MessageEvent",
    "TapEvent",
    "ViewedEvent",
    "DisconnectEvent",
    "UnknownEvent",

]
