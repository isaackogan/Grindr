from Grindr.client.web.web_base import ClientRoute, URLTemplate, BodyParams
from Grindr.client.web.web_settings import GRINDR_V3


class SetDeleteProfileImagesRoutePayload(BodyParams):
    """Get all images associated with profile photos on the account"""
    media_hashes: list[str]


class SetDeleteProfileImagesRoute(
    ClientRoute[
        "DELETE",
        URLTemplate(GRINDR_V3, "/me/profile/images"),
        None,
        SetDeleteProfileImagesRoutePayload,
        None
    ]
):
    """
    Get the current profile images. The 'primaryImageHash' signifies the main image (your profile cover photo).
    The secondary image hashes are your other photos.

    """
