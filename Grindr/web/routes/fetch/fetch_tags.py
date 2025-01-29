from pydantic import BaseModel

from Grindr.web.web_schemas import URLTemplate
from Grindr.web.web_route import ClientRoute
from Grindr.web.web_settings import GRINDR_V1


class Tag(BaseModel):
    tagId: int | None = None
    text: str | None = None
    key: str | None = None


class TagCollection(BaseModel):
    text: str | None = None
    possessiveText: str | None = None
    tags: list[Tag] | None = None


class TagCategory(BaseModel):
    language: str | None = None  # 2 letter language code
    categoryCollection: list[TagCollection] | None = None


type FetchTagsRouteResponse = list[TagCategory]


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
