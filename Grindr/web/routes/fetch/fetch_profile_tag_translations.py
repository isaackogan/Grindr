from pydantic import BaseModel

from Grindr.web.web_schemas import URLTemplate
from Grindr.web.web_route import ClientRoute
from Grindr.web.web_settings import GRINDR_V5


class TranslationCategory(BaseModel):
    key: str
    localized: str


class FetchProfileTagTranslationsRouteResponse(BaseModel):
    categories: list[TranslationCategory]


class FetchProfileTagTranslationsRoute(
    ClientRoute[
        "GET",
        URLTemplate(GRINDR_V5, "/profile-tags/translations"),
        None,
        None,
        FetchProfileTagTranslationsRouteResponse
    ]
):
    pass
