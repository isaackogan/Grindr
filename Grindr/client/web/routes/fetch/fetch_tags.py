from pydantic import BaseModel

from Grindr.client.web.web_base import ClientRoute, URLTemplate
from Grindr.client.web.web_settings import GRINDR_V1


class Tag(BaseModel):
    tagId: int
    text: str
    key: str


class TagCollection(BaseModel):
    text: str
    possessiveText: str
    tags: list[Tag]


class FetchTagsRouteResponse(BaseModel):
    language: str
    categoryCollection: list[TagCollection]


class FetchTagsRoute(
    ClientRoute[
        "GET",
        URLTemplate(GRINDR_V1, "/tags"),
        None,
        None,
        FetchTagsRouteResponse
    ]
):
    pass
