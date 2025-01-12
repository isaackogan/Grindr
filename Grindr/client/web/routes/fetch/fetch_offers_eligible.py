from typing import Any

from pydantic import BaseModel

from Grindr.client.web.web_base import ClientRoute, URLTemplate
from Grindr.client.web.web_settings import GRINDR_V2


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
