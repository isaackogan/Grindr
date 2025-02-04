import json
import traceback
from typing import Any

from pydantic import BaseModel, ValidationError

from Grindr.web.web_base import URLTemplate
from Grindr.web.web_route import ClientRoute
from Grindr.web.web_settings import GRINDR_V4


class SetMediaUploadRouteResponse(BaseModel):
    mediaId: int
    mediaHash: str
    url: str


class SetMediaUploadRoutePayload(BaseModel):
    image_bytes: bytes


class SetMediaUploadRoute(
    ClientRoute[
        "POST",
        URLTemplate(GRINDR_V4, "/chat/media/upload"),
        None,
        SetMediaUploadRoutePayload,
        SetMediaUploadRouteResponse
    ]
):
    """
    Retrieve a session from the API
    """

    async def __call__(
            self,
            params: None = None,
            body: SetMediaUploadRoutePayload = None,
            **kwargs: Any
    ) -> SetMediaUploadRouteResponse | None:

        response = await self._web.request(
            method="POST",
            base_url=self.url % {},
            extra_headers={"Content-Type": "image/jpeg"},
            content=body.image_bytes,
            **kwargs
        )

        if response.status_code != 200:
            self._logger.debug("Image Upload Failed: " + str(response.status_code) + response.content.decode())
            return None

        # Build the payload reply
        try:
            data: dict = response.json() if response.content else {}
            self._logger.debug("Received JSON: " + json.dumps(data))
            return self.response(**data)
        except ValidationError:
            self._logger.error(f"Failed due to ValidationError: {response.status_code} {response.url}\n" + traceback.format_exc())
            return None
