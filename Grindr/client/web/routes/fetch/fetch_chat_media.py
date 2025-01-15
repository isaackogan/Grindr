from pydantic import BaseModel

from Grindr.client.web.web_base import ClientRoute, URLTemplate, QueryParams
from Grindr.client.web.web_settings import GRINDR_V4


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
