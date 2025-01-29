from pydantic import BaseModel

from Grindr.web.web_schemas import QueryParams, URLTemplate
from Grindr.web.web_route import ClientRoute
from Grindr.web.web_settings import GRINDR_V4
from Grindr.client.schemas.message import Message


class FetchMessagesRouteParams(QueryParams):
    conversationId: str
    pageKey: str = ""


class Metadata(BaseModel):
    translate: bool | None = None
    hasSharedAlbums: bool | None = None


class FetchMessagesRouteResponse(BaseModel):
    lastReadTimestamp: int | None = None
    messages: list[Message] | None = None
    metadata: Metadata | None = None


class FetchMessagesRoute(
    ClientRoute[
        "GET",
        URLTemplate(GRINDR_V4, "/chat/conversation/{conversationId}/message?pageKey={pageKey}"),
        FetchMessagesRouteParams,
        None,
        FetchMessagesRouteResponse
    ]
):
    """
    Retrieve messages from a conversation.
    If no page key is specified you are grabbing the FIRST page.
    All successive requests should use the page key from the previous response.
    The page key is the OLDEST message in the response.

    """
