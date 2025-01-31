import uuid

from pydantic import BaseModel, Field

from Grindr.web.web_schemas import QueryParams, BodyParams
from Grindr.web.web_base import URLTemplate
from Grindr.web.web_route import ClientRoute
from Grindr.web.web_settings import GRINDR_V1


class SetSendAlbumRouteParams(QueryParams):
    albumId: int


class SetSendAlbumRoutePayloadProfile(BaseModel):
    profileId: int
    shareId: str = Field(default_factory=lambda: str(uuid.uuid4()))


class SetSendAlbumRoutePayload(BodyParams):
    profiles: list[SetSendAlbumRoutePayloadProfile]


class SetSendAlbumRoute(
    ClientRoute[
        "POST",
        URLTemplate(GRINDR_V1, "/albums/{albumId}/shares"),
        SetSendAlbumRouteParams,
        SetSendAlbumRoutePayload,
        None
    ]
):
    """
    Retrieve a session from the API

    """

    @classmethod
    def create_payload(
            cls,
            profile_id: int
    ) -> SetSendAlbumRoutePayload:
        return SetSendAlbumRoutePayload(
            profiles=[
                SetSendAlbumRoutePayloadProfile(
                    profileId=profile_id
                )
            ]
        )
