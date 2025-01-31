from Grindr.web.web_schemas import BodyParams
from Grindr.web.web_base import URLTemplate
from Grindr.web.web_route import ClientRoute
from Grindr.web.web_settings import GRINDR_V5


class FetchRewardedChatsRouteResponse(BodyParams):
    remainingChats: int | None = None


class FetchRewardedChatsRoute(
    ClientRoute[
        "GET",
        URLTemplate(GRINDR_V5, "/rewarded-chats"),
        None,
        None,
        FetchRewardedChatsRouteResponse
    ]
):
    """
    Retrieve a session from the API

    """
