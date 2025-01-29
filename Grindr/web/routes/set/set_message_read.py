from Grindr.web.web_schemas import QueryParams, URLTemplate
from Grindr.web.web_route import ClientRoute
from Grindr.web.web_settings import GRINDR_V4


class SetMessageReadRouteParams(QueryParams):
    conversationId: str
    messageId: str


class SetMessageReadRoute(
    ClientRoute[
        "POST",
        URLTemplate(GRINDR_V4, "/chat/conversation/{conversationId}/read/{messageId}"),
        SetMessageReadRouteParams,
        None,
        None
    ]
):
    """
    Retrieve a session from the API

    """
