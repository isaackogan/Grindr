from pydantic import BaseModel

from Grindr.client.web.web_base import ClientRoute, URLTemplate
from Grindr.client.web.web_settings import GRINDR_PUBLIC_V2


class FetchGendersRouteResponse(BaseModel):
    genderId: int | None = None
    gender: str | None = None
    displayGroup: int | None = None
    sortProfile: int | None = None
    sortFilter: int | None = None
    genderPlural: str | None = None
    excludeOnProfileSelection: bool | None = None
    excludeOnFilterSelection: list[int] | None = None
    alsoClassifiedAs: list[int] | None = None


class FetchGendersRoute(
    ClientRoute[
        "GET",
        URLTemplate(GRINDR_PUBLIC_V2, "/genders"),
        None,
        None,
        FetchGendersRouteResponse
    ]
):
    pass
