from typing import Generator, Any

from Grindr.client.ws.AsyncWS.client import AsyncWebSocket
from Grindr.client.ws.AsyncWS.session import AsyncWebSocketSession


class AsyncWebSocketConnect:
    """
    Wrapper to allow for easy connection through async generators.
    Copies the format of the websockets library, because it's cool.

    """

    def __init__(
            self,
            url: str,
            *args,
            **kwargs
    ):
        """
        Initialize the AsyncWebSocketConnect object

        :param url: URL to connect to
        :param args: Args to pass to the connection
        :param kwargs: Kwargs to pass to the connection

        """

        self._url: str = url
        self._args = args
        self._kwargs = kwargs
        self._ws = None

    async def __call__(self) -> AsyncWebSocket:
        """
        Initialize the custom WS session with an async context manager

        :return: The WebSocket connection

        """

        async with AsyncWebSocketSession() as session:
            self._ws = await session.ws_connect(
                url=self._url,
                *self._args,
                **self._kwargs
            )

            return self._ws

    def __await__(self) -> Generator[Any, None, AsyncWebSocket]:
        """
        Initialize the custom WS session with an async generator

        :return: Async web socket from generator

        """

        # Create a suitable iterator by calling __await__ on a coroutine.
        return self().__await__()

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        When exiting, close the connection

        :param exc_type: Type of exception
        :param exc_val: The exception value
        :param exc_tb: The traceback
        :return: None

        """

        return await self._ws.aclose()

    async def __aenter__(self) -> AsyncWebSocket:
        """
        When entering the context, create & return the connection
        :return: The WebSocket connection

        """

        return await self


connect = AsyncWebSocketConnect

__all__ = ["connect"]
