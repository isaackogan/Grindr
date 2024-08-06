import asyncio
import json
import struct
from typing import AsyncGenerator

import curl_cffi.requests
from curl_cffi import CurlWsFlag, CurlError
from curl_cffi.requests import WsCloseCode, WebSocketError
from pydantic import BaseModel

from Grindr.client.logger import GrindrLogHandler


class WebsocketClosedError(Exception):

    def __init__(self, code: int, *args):
        super().__init__(code, *args)
        self.code = code


class AsyncWebSocket(curl_cffi.requests.WebSocket):
    logger = GrindrLogHandler.get_logger()

    async def asend(self, payload: bytes | dict | str | BaseModel, flags: CurlWsFlag = CurlWsFlag.TEXT):

        if isinstance(payload, dict):
            payload: bytes = json.dumps(payload).encode('utf-8')

        if isinstance(payload, BaseModel):
            payload: bytes = payload.model_dump_json().encode('utf-8')

        if isinstance(payload, str):
            payload: bytes = payload.encode('utf-8')

        self.logger.debug(f"Sending payload: {payload}")
        await super().asend(payload, flags)

    async def __aexit__(self, exc_type, exc, tb):
        await self.aclose()

    async def __aiter__(self) -> AsyncGenerator[bytes, None]:

        while self.keep_running:
            try:
                msg, flags = await self.arecv()
                await asyncio.sleep(0.25)

                self.logger.debug(f"Received payload [w/ Flag(s) {flags}]: {msg}")

                if not flags & CurlWsFlag.CLOSE:
                    yield msg
                    continue

                self.keep_running = False

                if len(msg) < 2:
                    code = WsCloseCode.UNKNOWN
                    reason = ""
                else:
                    try:
                        code = struct.unpack_from("!H", msg)[0]
                        reason = msg[2:].decode()
                    except UnicodeDecodeError as e:
                        raise WebSocketError(
                            "Invalid close message", WsCloseCode.INVALID_DATA
                        ) from e
                    except Exception as e:
                        raise WebSocketError(
                            "Invalid close frame", WsCloseCode.PROTOCOL_ERROR
                        ) from e
                    else:
                        if code < 3000 and (code not in WsCloseCode or code == 1005):
                            raise WebSocketError(
                                "Invalid close code", WsCloseCode.PROTOCOL_ERROR
                            )
                raise WebsocketClosedError(code, reason)
            except WebSocketError as e:
                await self.aclose(e.code)
                raise WebsocketClosedError(e.code, str(e))
            except CurlError as e:
                raise WebsocketClosedError(e.code, str(e))
