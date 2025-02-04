from pydantic import BaseModel

from Grindr.web.web_schemas import QueryParams, ImageBody
from Grindr.web.web_base import URLTemplate
from Grindr.web.web_route import ClientRoute
from Grindr.web.web_settings import GRINDR_V3


class SetProfileImageRouteParams(QueryParams):
    """Parameters for the SetProfileImageRoute route"""

    thumbCoords: str

    @classmethod
    def from_crop_coordinates(cls, x1: int, y1: int, x2: int, y2: int) -> "SetProfileImageRouteParams":
        """Convert crop coordinates to a string for the Grindr API"""

        # Y-BOTTOM,X-LEFT,X-RIGHT,Y-TOP
        comma_escape: str = "%2C"
        raw_coords: str = f"{y2},{x1},{x2},{y1}"

        # URL encode the coordinates
        return cls(
            thumbCoords=raw_coords.replace(",", comma_escape)
        )


class ProfilePhoto(BaseModel):
    size: int | None = None
    fullUrl: str | None = None
    thumbnail: bool | None = None
    state: str | None = None
    mediaHash: str | None = None
    rejectionReason: str | None = None


class SetProfileImageRouteResponse(BaseModel):
    hash: str | None = None
    imageSizes: list[ProfilePhoto] = None
    mediaId: int


class SetProfileImageRoute(
    ClientRoute[
        "POST",
        URLTemplate(GRINDR_V3, "/me/profile/images?thumbCoords={thumbCoords}"),
        SetProfileImageRouteParams,
        ImageBody,
        SetProfileImageRouteResponse
    ]
):
    """
    Upload a profile photo image to the Grindr API & receive a result

    """
