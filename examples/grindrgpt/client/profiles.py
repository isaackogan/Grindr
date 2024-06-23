from typing import Dict, Optional

from Grindr.client.web.routes.fetch_profile import DetailedProfile, FetchProfileRouteParams, FetchProfileRouteResponse
from Grindr.client.web.web_client import GrindrWebClient


class ProfileManager:

    def __init__(
            self,
            web: GrindrWebClient,
    ):
        self._web: GrindrWebClient = web
        self._profile_cache: Dict[int, DetailedProfile] = {}

    async def get_profile(self, profile_id: int) -> Optional[DetailedProfile]:

        if profile_id not in self._profile_cache:

            try:
                response: FetchProfileRouteResponse = await self._web.fetch_profile(params=FetchProfileRouteParams(profileId=profile_id))
                profile: DetailedProfile = response.profiles[0]
            except:
                return None

            self._profile_cache[profile_id] = profile

        return self._profile_cache[profile_id]
