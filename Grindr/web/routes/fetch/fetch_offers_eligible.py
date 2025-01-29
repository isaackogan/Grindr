from typing import Any

from pydantic import BaseModel

from Grindr.web.web_schemas import URLTemplate
from Grindr.web.web_route import ClientRoute
from Grindr.web.web_settings import GRINDR_V2


class FetchOffersEligibleRouteResponse(BaseModel):
    offerTypes: list[Any] = None
    hasExistingOffer: bool = None


class FetchOffersEligibleRoute(
    ClientRoute[
        "GET",
        URLTemplate(GRINDR_V2, "/offers/eligible"),
        None,
        None,
        FetchOffersEligibleRouteResponse
    ]
):
    pass
