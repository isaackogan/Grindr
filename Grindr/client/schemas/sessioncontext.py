from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel, PrivateAttr

from Grindr.client.ext.client_emitter import GrindrEventEmitter
from Grindr.web.web_client import GrindrWebClient
from Grindr.ws.ws_client import GrindrWebSocketClient


class SessionContext:

    def __init__(
            self,
            web: GrindrWebClient,
            ws: GrindrWebSocketClient,
            emitter: GrindrEventEmitter
    ):
        self.ws: GrindrWebSocketClient = ws
        self.web: GrindrWebClient = web
        self.emitter: GrindrEventEmitter = emitter

    @property
    def profile_id(self) -> int:
        if not self.web.auth_session.profile_id:
            raise ValueError("No profile ID available, authenticate!")

        return int(self.web.auth_session.profile_id)


class GrindrModel(BaseModel, ABC):
    _context: SessionContext = PrivateAttr()

    def __init__(self, context: SessionContext, **data):
        super().__init__(**data)
        self._context = context

    @property
    def context(self) -> SessionContext:
        return self._context

    @abstractmethod
    async def retrieve_all(self) -> "GrindrModel":
        raise NotImplementedError
