from typing import Any, Literal

from pydantic import BaseModel

from Grindr.client.web.web_base import ClientRoute, URLTemplate, QueryParams
from Grindr.client.web.web_settings import GRINDR_V4


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
