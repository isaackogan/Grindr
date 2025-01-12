from pydantic import BaseModel, Field

from Grindr.client.web.routes.fetch.fetch_profile import DetailedProfileData
from Grindr.client.web.web_base import ClientRoute, URLTemplate
from Grindr.client.web.web_settings import GRINDR_V4


class FetchMyProfileRouteResponse(BaseModel):
    profile: list[DetailedProfileData] | None = Field(max_length=1)


class FetchMyProfileRoute(
    ClientRoute[
        "PUT",
        URLTemplate(GRINDR_V4, "/me/profile"),
        None,
        None,
        FetchMyProfileRouteResponse
    ]
):
    """
    Set profile details

    """
