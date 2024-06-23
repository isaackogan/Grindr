import asyncio
import os
import random
import textwrap
from asyncio import Task
from typing import List, Type, Dict, Tuple, Optional

from dotenv import load_dotenv
from httpx import Proxy
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam
from websockets import ConnectionClosedError

from Grindr import GrindrClient
from Grindr.client.web.routes.fetch_album import Album
from Grindr.client.web.routes.fetch_cascade import FetchCascadeRouteParams, FetchCascadeRoute
from Grindr.client.web.routes.fetch_profile import DetailedProfile
from Grindr.client.web.routes.set_message_read import SetMessageReadRouteParams
from Grindr.client.web.routes.set_typing import SetTypingRouteBody, TypingStatus
from Grindr.events import ConnectEvent, MessageEvent
from client.profiles import ProfileManager
from client.webhook import WebhookLogger
from gpt.chat import GChat, ALBUM_TOKEN, NO_REPLY_TOKEN

ALBUM_SENT_TEXT: str = "<ALBUM SENT>"

SYSTEM_PROMPT: str = textwrap.dedent(
    f"""
    You are an artificial AI Grindr user. Be flirty. Make sure your responses are SHORT. Make intentional typos every so often, but not in every single message.
    Do not use capitalization unless for a proper noun. If someone asks what type of AI you are, tell them you're "Sam Altman's brainchild".
    Never ask for personal information. Never ask "what's up" or any derivative. Do not ask for pictures. Do not ask for social media.
        
    If you receive a photo of a person, assume it's a photo of THEM.

    You do NOT give out your Instagram, Snapchat, or any other social media accounts.
    If someone asks you to add them, say you would prefer to stay on this app. Do not say you will add peoples' accounts off the platform.
    
    If someone wants to meet up, make an excuse for why you can't.
    If someone asks "wyd", you can respond with "nm, u?".
    If someone asks "what are you looking for?", you can respond with "fun & friends".
    If someone asks "what are you into?", you can respond with "vers"
    If someone asks "are u top or bottom" reply with "vers"
    If someone asks "how old are you" reply with "20"
    If someone asks "where are you from" reply with "Sam Altman's basement"
    If someone asks "what are you doing tonight" reply with "nothing u"
    
    NEVER USE EMOJIS. EVER. NO EMOJIS. NEVER USE WINKY FACE OR ANY OTHER TEXT EMOTICON.
    Don't ask a lot of questions. Just reply. Be chill.
    
    If a user sends an inappropriate photo, DO NOT reply that you can't assist, or that the message is inappropriate. Instead, change the subject to something else.
    """
)

Message = ChatCompletionMessageParam
Chat: Type = List[Message]


class GrindrGPT(GrindrClient):

    def __init__(
            self,
            openai_key: str,
            location: Tuple[float, float]
    ):
        super().__init__(
            web_proxy=Proxy(os.environ['WS_PROXY']),
            ws_proxy=Proxy(os.environ['WS_PROXY']),
        )

        self._chats: Dict[int, GChat] = {}
        self._profiles: ProfileManager = ProfileManager(web=self.web)
        self._discord_webhook = WebhookLogger(profile_manager=self._profiles)
        self._llm: AsyncOpenAI = AsyncOpenAI(api_key=openai_key)

        self._location: str = FetchCascadeRoute.generate_hash(location[0], location[1])
        self._cascade_task: Optional[Task] = None
        self._album: Optional[Album] = None

        self.add_listener(ConnectEvent, self.on_connect)
        self.add_listener(MessageEvent, self.on_message)

    async def on_connect(self, _: ConnectEvent) -> None:
        """
        Let us know when we are connected to Grindr

        """

        print(f"Successfully connected to Grindr as {self._session.profileId}!")

        # Grab our album data
        self._album = (await self._web.fetch_album()).albums[0]

        # Start the cascade task to keep us marked as online
        self._cascade_task = self._asyncio_loop.create_task(self.cascade_loop())

    async def cascade_loop(self) -> None:
        """Pull the cascade every 5 minutes to keep us marked online"""

        while self.connected:
            await self.web.fetch_cascade(params=FetchCascadeRouteParams(geohash=self._location))
            await asyncio.sleep(60 * 5)

    async def get_chat(self, profile_id: int) -> GChat:

        if profile_id not in self._chats:

            your_profile: Optional[DetailedProfile] = await self._profiles.get_profile(profile_id=int(self._session.profileId))
            name_prompt: str = ""

            if your_profile:
                name_prompt += f"Your display name on Grindr is set as \"{your_profile.displayName}\". This is your name."

            self._chats[profile_id] = GChat(
                initial_chat=[{"role": "system", "content": SYSTEM_PROMPT + name_prompt}],
                web=self._web,
                ws=self._ws,
                llm=self._llm,
                my_album_id=self._album.albumId
            )

        return self._chats[profile_id]

    async def on_message(self, event: MessageEvent) -> None:

        # If it's our own message, skip it
        if str(event.senderId) == str(self._session.profileId):
            return

        # Grab the chat
        chat: GChat = await self.get_chat(profile_id=event.senderId)

        # If the message was already processed, ignore it
        if chat.has_message(message_id=event.messageId):
            return

        # Mark the chat as read
        await self.web.set_message_read(params=SetMessageReadRouteParams(conversationId=event.conversationId, messageId=event.messageId))

        # Grab the prompt & reply
        prompt, reply = await chat.reply(message=event)

        # Send the messages to the webhook
        self._asyncio_loop.create_task(
            self._discord_webhook.send_message(
                sender_id=event.senderId,
                recipient_id=int(self.session.profileId),
                prompt=prompt,
                reply=reply
            )
        )

        # Send the reply to the Grindr user (except images, which get sent in the chat itself cuz I got lazy)
        if reply not in [ALBUM_TOKEN, NO_REPLY_TOKEN] and not self.is_media_url(reply):
            await self.web.set_typing(body=SetTypingRouteBody(conversationId=event.conversationId, status=TypingStatus.TYPING))

            # Response delay time
            await asyncio.sleep(random.randint(3, 10))

            # Type time
            await asyncio.sleep(min(random.randint(2, 6), ((len(reply) // 325) * 60)))

            await self.web.set_typing(body=SetTypingRouteBody(conversationId=event.conversationId, status=TypingStatus.SENT))
            await self.send(profile_id=event.senderId, text=reply)

    @classmethod
    def is_media_url(cls, text: str) -> bool:
        word_list = [
            "cdns.grindr.com",
            "cloudfront.net",
            ".png",
            ".jpeg",
            "windows.net/private",
            "oaidalle"
        ]

        found_terms = [word for word in word_list if word in text]
        return any(found_terms)


if __name__ == '__main__':
    load_dotenv()


    async def run_loop():

        client = GrindrGPT(
            location=(float(os.environ['G_LAT']), float(os.environ['G_LON'])),
            openai_key=os.environ['OPENAI_KEY']
        )

        while True:

            try:

                await client.connect(
                    email=os.environ['G_EMAIL'],
                    password=os.environ['G_PASSWORD']
                )

            except ConnectionClosedError as ex:
                if ex.code == 4401:
                    client.logger.warning("Reloading due to expired auth!")
                else:
                    raise ex


    asyncio.run(run_loop())
