from __future__ import annotations

from typing import Type, Union, Literal, ClassVar

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

        return cls

    return decorator


__all__ = ['WebSocketEvent', 'WSEventMap']
