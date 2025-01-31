from typing import Any

from pydantic import BaseModel

from Grindr.web.web_schemas import BodyParams
from Grindr.web.web_base import URLTemplate
from Grindr.web.web_route import ClientRoute
from Grindr.web.web_settings import GRINDR_V1


class GooglePlayProductTrial(BaseModel):
    interval: str
    duration: int


class GooglePlayProduct(BaseModel):
    vendorProductId: str | None = None
    type: str | None = None
    duration: int | None = None
    interval: str | None = None
    trial: GooglePlayProductTrial | None = None
    consumable: Any | None = None
    roles: list[str]  # e.g. ["XTRA"]


class FetchGoogleProductsRouteResponse(BodyParams):
    name: str | None
    products: list[GooglePlayProduct] | None = None


class FetchGooglePlayProductsRoute(
    ClientRoute[
        "GET",
        URLTemplate(GRINDR_V1, "/store/googleplay/products/store"),
        None,
        None,
        FetchGoogleProductsRouteResponse
    ]
):
    pass
