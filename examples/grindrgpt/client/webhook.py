import os
from typing import Optional

import aiohttp
from discord import Webhook

from Grindr.client.web.routes.fetch_profile import DetailedProfile
from client.profiles import ProfileManager


class WebhookLogger:

    def __init__(
            self,
            profile_manager: ProfileManager,
            print_messages: bool = True
    ):
        self._profiles: ProfileManager = profile_manager
        self._aiohttp: aiohttp.ClientSession = aiohttp.ClientSession()
        self._webhook: Webhook = Webhook.from_url(os.environ['DISCORD_WEBHOOK'], session=self._aiohttp)
        self._print_messages: bool = print_messages

    async def send_message(
            self,
            sender_id: int,
            recipient_id: int,
            prompt: str,
            reply: str
    ) -> None:
        chat_id: int = abs(hash(f"{sender_id}{recipient_id}")) % (10 ** 8)

        recipient_profile: Optional[DetailedProfile] = await self._profiles.get_profile(recipient_id)
        sender_profile: Optional[DetailedProfile] = await self._profiles.get_profile(sender_id)

        recipient_image: Optional[str] = f"https://cdns.grindr.com/images/thumb/320x320/{recipient_profile.profileImageMediaHash}" if recipient_profile else None
        sender_image: Optional[str] = f"https://cdns.grindr.com/images/thumb/320x320/{sender_profile.profileImageMediaHash}" if sender_profile else None

        recipient_name: str = (recipient_profile.displayName or str(recipient_id)) if recipient_profile else str(recipient_id)
        sender_name: str = (sender_profile.displayName or str(sender_id)) if sender_profile else str(sender_id)

        if self._print_messages:
            print(f"[{recipient_name}]", "<-", f"[{sender_name}]", prompt)
            print(f"[{recipient_name}]", "->", f"[{sender_name}]", reply)

        await self._webhook.send(
            content=reply,
            avatar_url=recipient_image,
            username=recipient_name + f" - Chat #{chat_id}"
        )

        await self._webhook.send(
            content=prompt,
            avatar_url=sender_image,
            username=sender_name + f" - Chat #{chat_id}"
        )


