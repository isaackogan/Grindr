from pydantic import BaseModel

from Grindr.web.web_schemas import BodyParams
from Grindr.web.web_base import URLTemplate
from Grindr.web.web_route import ClientRoute
from Grindr.web.web_settings import GRINDR_V1


class Assignment(BaseModel):
    key: str
    value: str
    payload: dict
    type: str


class FetchAssignmentsRouteResponse(BaseModel):
    assignments: list[Assignment]


class FetchAssignmentsRouteParams(BodyParams):
    geohash: str


class FetchAssignmentsRoute(
    ClientRoute[
        "GET",
        URLTemplate(GRINDR_V1, "/assignment?geohash={geohash}"),
        FetchAssignmentsRouteParams,
        None,
        FetchAssignmentsRouteResponse
    ]
):
    pass
