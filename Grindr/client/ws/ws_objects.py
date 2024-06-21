import uuid
from typing import Optional

from pydantic import BaseModel


class WSMessagePayloadTarget(BaseModel):
    type: str = "Direct"
    targetId: int


class WSMessagePayloadBody(BaseModel):
    text: str


class WSMessagePayload(BaseModel):
    type: str = "Text"
    target: WSMessagePayloadTarget
    body: WSMessagePayloadBody
    ref: str


class WSMessage(BaseModel):
    payload: WSMessagePayload
    ref: str
    token: str
    type: str = "chat.v1.message.send"

    @classmethod
    def from_defaults(
            cls,
            token: str,
            profile_id: int,
            text: str
    ) -> "WSMessage":
        ref = str(uuid.uuid4())

        return cls(
            ref=ref,
            payload=WSMessagePayload(
                target=WSMessagePayloadTarget(targetId=profile_id),
                body=WSMessagePayloadBody(text=text),
                ref=ref
            ),
            token=token
        )
