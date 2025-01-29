from pydantic import Field

from Grindr.web.web_schemas import BodyParams, URLTemplate
from Grindr.web.web_route import ClientRoute
from Grindr.web.web_settings import GRINDR_V3


class SetProfileImagesRoutePayload(BodyParams):
    """Set profile images body"""

    primaryImageHash: str | None  # Only one primary image, obviously
    secondaryImageHashes: list[str] = Field(max_length=4)  # Max 4 secondary images


class SetProfileImagesRoute(
    ClientRoute[
        "PUT",
        URLTemplate(GRINDR_V3, "/me/profile/images"),
        None,
        SetProfileImagesRoutePayload,
        None
    ]
):
    """
    Set the current profile images. The 'primaryImageHash' signifies the main image (your profile cover photo).
    The secondary image hashes are your other photos.

    """
