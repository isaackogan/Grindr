import asyncio
import json

from curl_cffi import CurlWsFlag, CurlError, CurlECode, CurlInfo
from curl_cffi.aio import CURL_SOCKET_BAD
from curl_cffi.requests import AsyncWebSocket, WebSocketError
from curl_cffi.requests.websockets import aselect
from pydantic import BaseModel

from Grindr.client.ext.client_logger import GrindrLogHandler


class AsyncGrindrWS(AsyncWebSocket):
    logger = GrindrLogHandler.get_logger()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.close_event = asyncio.Event()

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def send(self, payload: bytes | dict | str | BaseModel, flags: CurlWsFlag = CurlWsFlag.TEXT):
        """Send anything over the WS"""

        if isinstance(payload, dict):
            payload: bytes = json.dumps(payload).encode('utf-8')

        if isinstance(payload, BaseModel):
            payload: bytes = payload.model_dump_json().encode('utf-8')

        if isinstance(payload, str):
            payload: bytes = payload.encode('utf-8')

        self.logger.debug(f"Sending payload: {payload}")
        await super().send(payload, flags)

    async def recv(self, *, timeout: float | None = None) -> tuple[bytes, int]:
        """
        Receive a frame as bytes. Whoever designed this is mentally deficient.
        We had to rework it because aselect hangs when the socket is closed.

        """
        loop = self.loop
        chunks = []
        # noinspection PyUnusedLocal
        flags = 0

        sock_fd = await loop.run_in_executor(None, self.curl.getinfo, CurlInfo.ACTIVESOCKET)
        if sock_fd == CURL_SOCKET_BAD:
            raise WebSocketError("Invalid active socket", CurlECode.NO_CONNECTION_AVAILABLE)
        while True:
            try:
                # Should never be more than 0.5 seconds
                rlist = await aselect(sock_fd, loop=loop, timeout=min(timeout if timeout else 0.5, 0.5))
                if rlist:
                    chunk, frame = await self.recv_fragment(timeout=timeout)
                    flags = frame.flags
                    chunks.append(chunk)
                    if frame.bytesleft == 0 and flags & CurlWsFlag.CONT == 0:
                        break
            except CurlError as e:
                if e.code == CurlECode.AGAIN:
                    pass
                else:
                    raise
            except OSError as ex:
                if ex.errno == 9:
                    return b'Closed (Patched close)', CurlWsFlag.CLOSE

        return b"".join(chunks), flags
