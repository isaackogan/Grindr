from typing import Optional, List, Any

from pydantic import BaseModel

from Grindr.client.web.web_base import ClientRoute, BodyParams, URLTemplate
from Grindr.client.web.web_settings import GRINDR_V4, GRINDR_V3, GRINDR_V1


class AlbumContent(BaseModel):
    contentId: Optional[int] = None
    contentType: Optional[str] = None
    url: Optional[str] = None
    processing: Optional[bool] = None
    thumbUrl: Optional[str] = None
    coverUrl: Optional[str] = None
    statusId: Optional[int] = None
    rejectionId: Optional[Any] = None


class Album(BaseModel):
    albumId: Optional[int] = None
    albumName: Optional[str] = None
    profileId: Optional[int] = None
    sharedCount: Optional[int] = None
    version: Optional[int] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
    content: Optional[List[AlbumContent]] = None
    isShareable: Optional[bool] = None


class FetchAlbumsRouteResponse(BaseModel):
    albums: Optional[List[Album]] = None


class FetchAlbumRoute(
    ClientRoute[
        "GET",
        URLTemplate(GRINDR_V1, "/albums"),
        None,
        None,
        FetchAlbumsRouteResponse
    ]
):
    pass
