from pydantic import BaseModel

from Grindr.client.web.web_base import ClientRoute, URLTemplate, BodyParams
from Grindr.client.web.web_settings import GRINDR_V1


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
