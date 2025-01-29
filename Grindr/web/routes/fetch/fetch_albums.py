from typing import Any

from pydantic import BaseModel

from Grindr.web.web_schemas import URLTemplate
from Grindr.web.web_route import ClientRoute
from Grindr.web.web_settings import GRINDR_V1


class AlbumContent(BaseModel):
    contentId: int | None = None
    contentType: str | None = None
    url: str | None = None
    processing: bool | None = None
    thumbUrl: str | None = None
    coverUrl: str | None = None
    statusId: int | None = None
    rejectionId: Any | None = None


class Album(BaseModel):
    albumId: int | None = None
    albumName: str | None = None
    profileId: int | None = None
    sharedCount: int | None = None
    version: int | None = None
    createdAt: str | None = None
    updatedAt: str | None = None
    content: AlbumContent | None = None
    isShareable: bool | None = None


class FetchAlbumsRouteResponse(BaseModel):
    albums: list[Album] | None = None


class FetchAlbumsRoute(
    ClientRoute[
        "GET",
        URLTemplate(GRINDR_V1, "/albums"),
        None,
        None,
        FetchAlbumsRouteResponse
    ]
):
    pass
