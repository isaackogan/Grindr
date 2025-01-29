from pydantic import BaseModel

from Grindr.web.web_schemas import QueryParams, URLTemplate
from Grindr.web.web_route import ClientRoute
from Grindr.web.web_settings import GRINDR_V4


class FetchChatMediaRouteResponseMedia(BaseModel):
    id: int
    url: str  # Signed url, expires
    contentType: str
    createdTs: int  # millis
    used: bool


type FetchChatMediaRouteResponse = list[FetchChatMediaRouteResponseMedia]


class FetchChatMediaRouteParams(QueryParams):
    conversationId: str


class FetchChatMediaRoute(
    ClientRoute[
        "GET",
        URLTemplate(GRINDR_V4, "/chat/media/drawer/{conversationId}"),
        FetchChatMediaRouteParams,
        None,
        FetchChatMediaRouteResponse
    ]
):
    pass
