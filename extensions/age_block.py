import os
from profile import Profile

from pydantic import PrivateAttr

from Grindr.client.extension import Extension, ExtensionListener
from Grindr.events import MessageEvent


class AgeBlock(Extension):
    """
    Extension to block users who are too old or too young

    """

    min_age: int = int(os.environ.get("G_MIN_AGE", "18"))
    max_age: int = int(os.environ.get("G_MAX_AGE", "24"))

    # Private parts
    _profiles: dict[int, Profile] = PrivateAttr(default_factory=dict)

    @ExtensionListener
    async def on_message(self, event: MessageEvent) -> None:
        """Block users who are too old or too young when they message."""

        if self.client.session.profileId == event.senderId:
            return

        # Get the profile
        if not (profile := self._profiles.get(event.senderId)):
            profile = self._profiles[event.senderId] = await self.client.retrieve_profile(profile_id=event.senderId)

        # If no age is set, return, can't do anything
        if not profile.age:
            return

        # If too old or too young
        if not profile.age <= self.min_age <= self.max_age:
            self.client.logger.debug(f"Blocking {profile.name} ({profile.id})")
            await profile.send_block()

        self.client.logger.debug(f"Received message from {profile.name} ({profile.id}) within age parameters")

    async def on_unload(self) -> None:
        """Clear the cache when the extension is unloaded."""
        self._profiles.clear()
