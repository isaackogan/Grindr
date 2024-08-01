from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel, PrivateAttr

from Grindr.client.emitter import GrindrEmitter
from Grindr.client.web.web_client import GrindrWebClient
from Grindr.client.ws.ws_client import GrindrWSClient


class Context(BaseModel):
    profile_id: int
    _web: GrindrWebClient = PrivateAttr()
    _ws: GrindrWSClient = PrivateAttr()
    _emitter: GrindrEmitter = PrivateAttr()

    def __init__(
            self,
            _web: GrindrWebClient,
            _ws: GrindrWSClient,
            _emitter: GrindrEmitter,
            **data
    ):
        super().__init__(**data)
        self._web = _web
        self._ws = _ws
        self._emitter = _emitter

    @property
    def web(self) -> GrindrWebClient:
        return self._web

    @property
    def ws(self) -> GrindrWSClient:
        return self._ws

    @property
    def emitter(self) -> GrindrEmitter:
        return self._emitter


class GrindrModel(BaseModel, ABC):
    context: Context

    @abstractmethod
    async def retrieve_all(self) -> "GrindrModel":
        raise NotImplementedError
