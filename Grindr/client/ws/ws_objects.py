import uuid
from typing import Union

from pydantic import BaseModel

from Grindr.events import MediaType


class WSMessagePayloadTarget(BaseModel):
    type: str = "Direct"
    targetId: int


class WSTextPayloadBody(BaseModel):
    text: str


class WSImagePayloadBody(BaseModel):
    mediaId: int


class WSGifPayloadBody(BaseModel):
    stillPath: str
    urlPath: str
    id: str
    previewPath: str
    imageHash: str
    width: int
    height: int


class WSMessagePayload(BaseModel):
    type: str = "Text"
    target: WSMessagePayloadTarget
    body: Union[WSTextPayloadBody, WSImagePayloadBody, WSGifPayloadBody]
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
                type=MediaType.IMAGE.value,
                target=WSMessagePayloadTarget(targetId=profile_id),
                body=WSImagePayloadBody(mediaId=media_id),
                ref=ref
            ),
            token=token
        )

    @classmethod
    def gif_from_defaults(
            cls,
            token: str,
            profile_id: int,
            image_url: str,
            image_id: str
    ):
        ref = str(uuid.uuid4())

        return cls(
            ref=ref,
            payload=WSMessagePayload(
                type=MediaType.GIPHY.value,
                target=WSMessagePayloadTarget(targetId=profile_id),
                body=WSGifPayloadBody(
                    stillPath=image_url,
                    urlPath=image_url,
                    id=image_id,
                    previewPath=image_url,
                    imageHash=f"giphy/{image_id}",
                    width=30,
                    height=60
                ),
                ref=ref
            ),
            token=token
        )
