from typing import AsyncIterator

from .events.events import Event
from .ws_base import BaseGrindrWebSocketClient
from .ws_schemas import MessagePayloadBodyType
from ..web.web_client import GrindrWebClientAuthSession


class GrindrWebSocketClient(BaseGrindrWebSocketClient):
    """High-level abstraction around BaseGrindrWSClient to parse events"""

    def __init__(
            self,
            auth_session: GrindrWebClientAuthSession,
            **kwargs
    ):
        """
        Create a WS Client

        :param auth: Instance of a shared ClientAuth object
        :param kwargs: Other arguments (ws_base and ws_proxy)

        """

        self._auth_session: GrindrWebClientAuthSession = auth_session
        super().__init__(**kwargs)

    async def connect(
            self,
            url: str,
            headers: dict[str, str]
    ) -> AsyncIterator[Event]:
        """Connect to the Grindr client & parse events"""

        async for message in super().connect(url, headers):
            yield Event.from_bytes(data=message)

    async def send(
            self,
            body: MessagePayloadBodyType,
            target_profile_id: int
    ) -> None:
        """Send a message to the Grindr client"""

        await self.ws.send(
            payload=body.to_message(
                target_profile_id=target_profile_id,
                session_id=self._auth_session.session_id
            )
        )
