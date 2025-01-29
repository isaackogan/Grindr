from pydantic import BaseModel, Field

from Grindr.web.routes.fetch.fetch_profile import DetailedProfileData
from Grindr.web.web_schemas import URLTemplate
from Grindr.web.web_route import ClientRoute
from Grindr.web.web_settings import GRINDR_V4


class FetchMyProfileRouteResponse(BaseModel):
    profiles: list[DetailedProfileData] | None = Field(max_length=1)


class FetchMyProfileRoute(
    ClientRoute[
        "GET",
        URLTemplate(GRINDR_V4, "/me/profile"),
        None,
        None,
        FetchMyProfileRouteResponse
    ]
):
    """
    Set profile details

    """
