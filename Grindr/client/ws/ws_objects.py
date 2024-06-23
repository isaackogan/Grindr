import uuid
from typing import Optional, Union

from pydantic import BaseModel


class WSMessagePayloadTarget(BaseModel):
    type: str = "Direct"
    targetId: int


class WSTextPayloadBody(BaseModel):
    text: str


class WSImagePayloadBody(BaseModel):
    mediaId: int


class WSMessagePayload(BaseModel):
    type: str = "Text"
    target: WSMessagePayloadTarget
    body: Union[WSTextPayloadBody, WSImagePayloadBody]
    ref: str


class WSMessage(BaseModel):
    payload: WSMessagePayload
    ref: str
    token: str
    type: str = "chat.v1.message.send"

    @classmethod
    def text_from_defaults(
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
                body=WSTextPayloadBody(text=text),
                ref=ref
            ),
            token=token
        )

    @classmethod
    def image_from_defaults(
            cls,
            token: str,
            profile_id: int,
            media_id: int
    ):
        ref = str(uuid.uuid4())

        return cls(
            ref=ref,
            payload=WSMessagePayload(
                type="Image",
                target=WSMessagePayloadTarget(targetId=profile_id),
                body=WSImagePayloadBody(mediaId=media_id),
                ref=ref
            ),
            token=token
        )
