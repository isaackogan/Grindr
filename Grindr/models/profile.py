import typing
from typing import List

from Grindr.client.web.routes.fetch_albums import Album
from Grindr.client.web.routes.fetch_profile import DetailedProfileData
from Grindr.client.web.routes.fetch_shared_albums import FetchSharedAlbumsRouteParams, FetchSharedAlbumsRouteResponse
from Grindr.client.web.routes.set_block_user import SetBlockUserRouteResponse, SetBlockUserRouteParams
from Grindr.client.web.routes.set_send_tap import SetSendTapRouteBody, SetSendTapRouteResponse
from Grindr.client.web.routes.set_unblock_user import SetUnblockUserRouteParams, SetUnblockUserRouteResponse
from Grindr.models.context import GrindrModel, Context

if typing.TYPE_CHECKING:
    pass


class Profile(DetailedProfileData, GrindrModel):
    albums: List[Album] = []

    async def retrieve_albums(self) -> List[Album]:
        """
        Retrieve the albums for the profile
        :return: The albums for the profile
        """

        response: FetchSharedAlbumsRouteResponse = await self.context.web.fetch_shared_albums(
            params=FetchSharedAlbumsRouteParams(
                profileId=str(self.profileId)
            )
        )

        self.albums = response.albums
        return self.albums

    @classmethod
    def from_data(cls, context: Context, data: DetailedProfileData):
        return cls(
            context=context,
            **data.model_dump()
        )

    async def retrieve_all(self) -> "Profile":
        await self.retrieve_albums()
        return self

    async def send_tap(self) -> SetSendTapRouteResponse:
        return await self.context.web.set_send_tap(
            body=SetSendTapRouteBody(
                profileId=self.profileId
            )
        )

    async def send_block(self) -> SetBlockUserRouteResponse:
        return await self.context.web.set_block_user(
            params=SetBlockUserRouteParams(
                profileId=self.profileId
            )
        )

    async def send_unblock(self) -> SetUnblockUserRouteResponse:
        return await self.context.web.set_unblock_user(
            params=SetUnblockUserRouteParams(
                profileId=self.profileId
            )
        )
