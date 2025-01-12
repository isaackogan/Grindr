from pydantic import BaseModel

from pydantic import BaseModel

from Grindr.client.web.web_base import ClientRoute, URLTemplate
from Grindr.client.web.web_settings import GRINDR_V3


class FetchPrefsRouteResponse(BaseModel):
    profileId: int | None = None
    locationSearchOptOut: bool | None = None
    incognito: bool | None = None
    hideViewedMe: bool | None = None
    approximateDistance: bool | None = None


class FetchPrefsRoute(
    ClientRoute[
        "GET",
        URLTemplate(GRINDR_V3, "/me/prefs/settings"),
        None,
        None,
        FetchPrefsRouteResponse
    ]
):
    pass
