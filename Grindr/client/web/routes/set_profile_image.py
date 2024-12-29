from typing import Optional, List

from pydantic import BaseModel

from Grindr.client.web.web_base import ClientRoute, URLTemplate, ImageBody, QueryParams
from Grindr.client.web.web_settings import GRINDR_V3


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
    size: Optional[int] = None
    fullUrl: Optional[str] = None
    thumbnail: Optional[bool] = None
    state: Optional[str] = None
    mediaHash: Optional[str] = None
    rejectionReason: Optional[str] = None


class SetProfileImageRouteResponse(BaseModel):
    hash: Optional[str] = None
    imageSizes: List[ProfilePhoto] = None
    mediaId: int


class SetProfileImageRoute(
    ClientRoute[
        "POST",
        URLTemplate(GRINDR_V3, "/me/profile/images"),
        SetProfileImageRouteParams,
        ImageBody,
        SetProfileImageRouteResponse
    ]
):
    """
    Upload a profile photo image to the Grindr API & receive a result

    """
