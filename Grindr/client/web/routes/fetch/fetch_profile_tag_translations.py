from pydantic import BaseModel

from Grindr.client.web.web_base import ClientRoute, URLTemplate
from Grindr.client.web.web_settings import GRINDR_V5


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
