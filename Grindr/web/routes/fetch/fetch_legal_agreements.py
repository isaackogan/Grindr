from typing import Any, Literal

from pydantic import BaseModel

from Grindr.web.web_schemas import QueryParams, URLTemplate
from Grindr.web.web_route import ClientRoute
from Grindr.web.web_settings import GRINDR_V4


class FetchLegalAgreementsRouteParams(QueryParams):
    agreement: Literal["right-now", "top-picks"]


class FetchLegalAgreementsRouteResponse(BaseModel):
    agreement: Any | None = None


class FetchLegalAgreementsRoute(
    ClientRoute[
        "GET",
        URLTemplate(GRINDR_V4, "/legal-agreements/{agreement}"),
        FetchLegalAgreementsRouteParams,
        None,
        FetchLegalAgreementsRouteResponse
    ]
):
    pass
