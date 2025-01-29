from pygeohash import geohash

from Grindr.web.web_schemas import BodyParams, URLTemplate
from Grindr.web.web_route import ClientRoute
from Grindr.web.web_settings import GRINDR_V3


class SetLocationRoutePayload(BodyParams):
    geohash: str


class SetLocationRoute(
    ClientRoute[
        "PUT",
        URLTemplate(GRINDR_V3, "/me/location"),
        None,
        SetLocationRoutePayload,
        None
    ]
):
    """
    Set the user's location

    """

    @classmethod
    def generate_body(cls, lat: float, lon: float) -> SetLocationRoutePayload:
        return SetLocationRoutePayload(
            geohash=geohash.encode(lat, lon, precision=12)
        )
