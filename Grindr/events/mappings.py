from .events import MessageEvent, TapEvent, ViewedEvent, ConnectEvent, Event, WebsocketResponse, UnknownEvent

EventMappings: dict = {
    "ws.connection.established": ConnectEvent,
    "viewed_me.v1.new_view_received": ViewedEvent,
    "chat.v1.message_sent": MessageEvent,
    "tap.v1.tap_sent": TapEvent
}


def get_event(data: WebsocketResponse) -> Event:
    mapping = EventMappings.get(data.type)

    # If no mapping found
    if mapping is None:
        return UnknownEvent(data=data.model_dump(), payload=data.payload)

    # If mapping found
    return mapping(**(data.payload or {}))
