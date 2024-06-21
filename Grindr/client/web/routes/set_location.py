from pygeohash import geohash

from Grindr.client.web.web_base import ClientRoute, URLTemplate, BodyParams
from Grindr.client.web.web_settings import GRINDR_V3


class SetLocationRouteBody(BodyParams):
    geohash: str


class SetLocationRoute(
    ClientRoute[
        "PUT",
        URLTemplate(GRINDR_V3, "/me/location"),
        None,
        SetLocationRouteBody,
        None
    ]
):
    """
    Set the user's location

    """

    @classmethod
    def generate_body(cls, lat: float, lon: float) -> SetLocationRouteBody:
        return SetLocationRouteBody(
            geohash=geohash.encode(lat, lon, precision=12)
        )
