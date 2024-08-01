import uuid
from abc import ABC, abstractmethod
from typing import Union, Type

from pydantic import BaseModel

from Grindr.models.message import SendMessageType, MessageType


class WSMessagePayloadTarget(BaseModel):
    type: str = "Direct"
    targetId: int


class WSMessagePayloadBody(ABC):

    @classmethod
    @abstractmethod
    def from_defaults(cls, **kwargs) -> "WSMessagePayloadBody":
        raise NotImplementedError


class WSTextPayloadBody(BaseModel, WSMessagePayloadBody):
    text: str

    @classmethod
    def from_defaults(cls, text: str) -> "WSTextPayloadBody":
        return cls(text=text)


class WSImagePayloadBody(BaseModel, WSMessagePayloadBody):
    mediaId: int

    @classmethod
    def from_defaults(cls, media_id: str) -> "WSImagePayloadBody":
        return cls(media_id=media_id)


class WSGifPayloadBody(BaseModel, WSMessagePayloadBody):
    stillPath: str
    urlPath: str
    id: str
    previewPath: str
    imageHash: str
    width: int
    height: int

    @classmethod
    def from_defaults(
            cls,
            image_url: str,
            image_id: str,
            width: int = 1080,
            height: int = 1920
    ) -> "WSGifPayloadBody":
        return cls(
            stillPath=image_url,
            urlPath=image_url,
            id=image_id,
            previewPath=image_url,
            imageHash=f"giphy/{image_id}",
            width=width,
            height=height
        )


SendPayloadBody: Type = Union[WSTextPayloadBody, WSImagePayloadBody, WSGifPayloadBody]


class WSMessagePayload(BaseModel):
    type: SendMessageType
    target: WSMessagePayloadTarget
    body: SendPayloadBody
    ref: str

    @classmethod
    def from_defaults(
            cls,
            target_id: int,
            message_type: SendMessageType,
            message_body: SendPayloadBody
    ) -> "WSMessagePayload":
        ref: str = str(uuid.uuid4())

        return cls(
            type=message_type,
            target=WSMessagePayloadTarget(targetId=target_id),
            body=message_body,
            ref=ref
        )


class WSMessage(BaseModel):
    payload: WSMessagePayload
    ref: str
    token: str
    type: str = "chat.v1.message.send"

    @classmethod
    def from_defaults(
            cls,
            payload: WSMessagePayload
    ) -> "WSMessage":
        return cls(
            payload=payload,
            ref=payload.ref,
            token=payload.ref
        )
