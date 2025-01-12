from typing import Any

from pydantic import BaseModel

from Grindr.client.web.web_base import ClientRoute, URLTemplate, BodyParams
from Grindr.client.web.web_settings import GRINDR_V1


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
