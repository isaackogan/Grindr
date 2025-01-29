from __future__ import annotations

from typing import Type, Union, Literal, Any, ClassVar

from pydantic import ValidationError, Field

from Grindr.ws.ws_schemas import WebSocketResponse


class _WSEventMap(dict):
    """A map of WebSocket events to their respective classes"""

    @property
    def payload_types(self) -> Type:
        return Union[tuple(self.values())]

    @property
    def event_names(self) -> Type:
        # Get the keys as a list of strings
        keys = list(self.keys())

        # Create a dynamic Union of Literal types using type hints
        # noinspection PyTypeHints
        return Union[tuple(Literal[key] for key in keys)]


WSEventMap: _WSEventMap = _WSEventMap()


# noinspection PyPep8Naming
def WebSocketEvent[T](name: str):
    """Register the mapping of the event name to the class"""

    def decorator(cls: T) -> object:
        cls._event_name = name

        # This way subclasses don't override the base class
        if name not in WSEventMap:
            WSEventMap[name] = cls

        class WebSocketEventResponse(WebSocketResponse):
            payload: cls

        return WebSocketEventResponse

    return decorator


class BaseEventPayload:
    _event_name: ClassVar[str] = NotImplemented

    @classmethod
    def get_type(cls) -> str:
        return cls._event_name


class Event[T: WSEventMap.event_names, Z: WSEventMap.payload_types](WebSocketResponse):
    """A mobile log event sent to the Grindr API"""

    type: T = Field(union_mode='left_to_right')
    payload: Z = Field(union_mode='left_to_right')

    def __init__(self, /, **data: Any):
        name: str = data.get('type', 'ws.ext.unknown')

        if name not in WSEventMap:
            name = 'ws.ext.unknown'

        try:
            super().__init__(**data)
        except ValidationError as ex:
            ex.add_note(f"Variant: Event[\"{name}\", {WSEventMap.get(name).__name__}]")
            raise ex


__all__ = ['Event', 'WebSocketEvent', 'WSEventMap', 'BaseEventPayload']
