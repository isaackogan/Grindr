import uuid
from typing import List

from pydantic import BaseModel, Field

from Grindr.client.web.web_base import ClientRoute, URLTemplate, QueryParams, BodyParams
from Grindr.client.web.web_settings import GRINDR_V1


class SetSendAlbumRouteParams(QueryParams):
    albumId: int


class SetSendAlbumRouteBodyProfile(BaseModel):
    profileId: int
    shareId: str = Field(default_factory=lambda: str(uuid.uuid4()))


class SetSendAlbumRouteBody(BodyParams):
    profiles: List[SetSendAlbumRouteBodyProfile]


class SetSendAlbumRoute(
    ClientRoute[
        "POST",
        URLTemplate(GRINDR_V1, "/albums/{albumId}/shares"),
        SetSendAlbumRouteParams,
        SetSendAlbumRouteBody,
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
    ) -> SetSendAlbumRouteBody:
        return SetSendAlbumRouteBody(
            profiles=[
                SetSendAlbumRouteBodyProfile(
                    profileId=profile_id
                )
            ]
        )
