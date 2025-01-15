from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel

from Grindr.client.web.web_base import ClientRoute, URLTemplate
from Grindr.client.web.web_settings import GRINDR_V1


class FetchBoostSessionsRouteResponse(BaseModel):
    boostSessions: list[Any] = None


class FetchBoostSessionsRoute(
    ClientRoute[
        "GET",
        URLTemplate(GRINDR_V1, "/boost/sessions"),
        None,
        None,
        FetchBoostSessionsRouteResponse
    ]
):

    def __call__(
            self,
            if_modified_since: str | None = None,
            **kwargs
    ):
        if_modified_since = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
        kwargs['headers'] = kwargs.get('extra_headers', {})
        kwargs['headers']['If-Modified-Since'] = if_modified_since
        return super().__call__(**kwargs)
