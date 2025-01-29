from __future__ import annotations

from pydantic import BaseModel

from Grindr.client.schemas.message import Message
from Grindr.ws.events.base import WebSocketEvent, BaseEventPayload


class ViewedEventMostRecent(BaseModel, BaseEventPayload):
    profileId: str | None = None
    photoHash: str | None = None
    timestamp: int | None = None


@WebSocketEvent("ws.ext.unknown")
class UnknownEvent(dict, BaseEventPayload):
    """An Unknown Event"""


@WebSocketEvent("ws.connection.established")
class ConnectEvent(BaseModel, BaseEventPayload):
    """WebSocket connect event"""


@WebSocketEvent("chat.v1.message_sent")
class MessageEvent(Message, BaseEventPayload):
    """WebSocket Message Event"""


@WebSocketEvent("tap.v1.tap_sent")
class TapEvent(BaseModel, BaseEventPayload):
    """Tap Event"""

    timestamp: int | None = None
    senderId: int | None = None
    recipientId: int | None = None
    tapType: int | None = None
    senderProfileImageHash: str | None = None
    senderDisplayName: str | None = None
    isMutual: bool | None = None


@WebSocketEvent("viewed_me.v1.new_view_received")
class ViewedEvent(BaseModel, BaseEventPayload):
    """View Received Event"""

    viewedCount: int | None = None
    mostRecent: ViewedEventMostRecent | None = None


@WebSocketEvent("ws.ext.disconnect")
class DisconnectEvent(BaseModel, BaseEventPayload):
    """Disconnect Event"""


__all__ = [
    "ConnectEvent",
    "MessageEvent",
    "TapEvent",
    "ViewedEvent",
    "DisconnectEvent",
    "UnknownEvent"
]
