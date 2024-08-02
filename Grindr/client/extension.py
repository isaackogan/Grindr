import typing
from abc import ABC
from typing import Awaitable, Type, Optional

from pydantic import BaseModel, PrivateAttr

from Grindr.client.emitter import GrindrEmitter
from Grindr.events import Event

if typing.TYPE_CHECKING:
    from Grindr import GrindrClient


class Extension(BaseModel, ABC):
    """
    Extensions that can be added to client instances to perform tasks.

    """

    _listeners: dict[Type[Event], str] = PrivateAttr(default_factory=dict)
    _client: Optional[GrindrEmitter] = PrivateAttr(default=None)
    _instance_id: Optional[str] = PrivateAttr(default=None)

    def _add_decorated_listeners(self) -> None:
        """Add listeners to the client"""

        for attr in dir(self):

            try:
                if not callable(getattr(self, attr)):
                    continue
            except AttributeError:
                continue

            if not hasattr(getattr(self, attr), "is_event_listener"):
                continue

            event_listener = getattr(self, attr)
            event_type = list(getattr(event_listener, "__annotations__").values())[0]

            self._listeners[event_type] = event_listener
            self._client.add_listener(event_type, event_listener)

    def _unload_decorated_listeners(self) -> None:
        """Clear listeners on unload"""

        for event, attr in self._listeners.items():
            self._client.remove_listener(event, getattr(self, attr))

    async def load(self, instance_id: str, client: "GrindrClient") -> None:
        """Load the extension"""

        await self.on_load()
        self._client = client
        self._instance_id = instance_id
        self._add_decorated_listeners()

    async def unload(self) -> None:
        """Unload the extension"""

        await self.on_unload()
        self._unload_decorated_listeners()
        self._instance_id = None
        self._client = None

    @property
    def client(self) -> "GrindrClient":
        """Get the client instance"""

        # noinspection PyTypeChecker
        return self._client

    async def on_load(self) -> Awaitable[None]:
        """Client-defined method for handling extension load"""
        pass

    async def on_unload(self) -> Awaitable[None]:
        """Client-defined method for handling extension unload"""
        pass

    @property
    def instance_id(self):
        return self._instance_id


# noinspection PyPep8Naming
def ExtensionListener(func):
    setattr(func, "is_event_listener", True)
    return func
