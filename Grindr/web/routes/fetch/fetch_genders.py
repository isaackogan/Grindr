from pydantic import BaseModel

from Grindr.web.web_schemas import URLTemplate
from Grindr.web.web_route import ClientRoute
from Grindr.web.web_settings import GRINDR_PUBLIC_V2


class Gender(BaseModel):
    genderId: int | None = None
    gender: str | None = None
    displayGroup: int | None = None
    sortProfile: int | None = None
    sortFilter: int | None = None
    genderPlural: str | None = None
    excludeOnProfileSelection: list[int] | None = None
    excludeOnFilterSelection: list[int] | None = None
    alsoClassifiedAs: list[int] | None = None


type FetchGendersRouteResponse = list[Gender]


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
