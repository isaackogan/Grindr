from pydantic import Field

from Grindr.client.web.web_base import ClientRoute, URLTemplate, BodyParams
from Grindr.client.web.web_settings import GRINDR_V3


class SetProfileImagesRouteBody(BodyParams):
    """Set profile images body"""

    primaryImageHash: str  # Only one primary image, obviously
    secondaryImageHashes: list[str] = Field(max_length=4)  # Max 4 secondary images


class SetProfileImageRoute(
    ClientRoute[
        "PUT",
        URLTemplate(GRINDR_V3, "/me/profile/images"),
        None,
        SetProfileImagesRouteBody,
        None
    ]
):
    """
    Set the current profile images. The 'primaryImageHash' signifies the main image (your profile cover photo).
    The secondary image hashes are your other photos.

    """
