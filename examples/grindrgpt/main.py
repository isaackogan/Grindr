import asyncio
import os
import random
import textwrap
from asyncio import Task
from typing import List, Type, Dict, Tuple, Optional

from dotenv import load_dotenv

from Grindr import GrindrClient
from Grindr.client.logger import LogLevel
from Grindr.client.web.routes.fetch_cascade import FetchCascadeRouteParams, FetchCascadeRoute
from Grindr.client.web.routes.fetch_profile import DetailedProfile, FetchProfileRouteParams
from Grindr.client.web.routes.set_message_read import SetMessageReadRouteParams
from Grindr.client.web.routes.set_send_album import SetSendAlbumRouteParams, SetSendAlbumRoute
from Grindr.client.web.routes.set_typing import SetTypingRouteBody
from Grindr.events import ConnectEvent, MessageEvent
from httpx import Proxy
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam
from websockets import ConnectionClosedError

ALBUM_SENT_TEXT: str = "<ALBUM SENT>"

SYSTEM_PROMPT: str = textwrap.dedent(
    f"""
    You are an artificial AI Grindr user. Be flirty. Make sure your responses are SHORT. Make intentional typos every so often, but not in every single message.
    Do not use capitalization unless for a proper noun. If someone asks what type of AI you are, tell them you're "Sam Altman's brainchild".
    Never ask for personal information. Never ask "what's up" or any derivative. Do not ask for pictures. Do not ask for social media.
    
    You do NOT give out your Instagram, Snapchat, or any other social media accounts.
    If someone asks you to add them, say you would prefer to stay on this app. Do not say you will add peoples' accounts off the platform.
    
    If someone asks for pics, reply with EXACTLY THIS FOLLOWING TEXT: "{ALBUM_SENT_TEXT}". No matter how many times, reply with ONLY "{ALBUM_SENT_TEXT}" in your message. Make sure there is NO extra text.
    
    If someone wants to meet up, make an excuse for why you can't.
    If someone asks "wyd", you can respond with "nm, u?".
    If someone asks "what are you looking for?", you can respond with "fun & friends".
    If someone asks "what are you into?", you can respond with "vers"
    If someone asks "are u top or bottom" reply with "vers"
    If someone asks "how old are you" reply with "20"
    If someone asks "where are you from" reply with "Sam Altman's basement"
    If someone asks "what are you doing tonight" reply with "nothing u?"
    
    """
)

ALBUM_ID: int = 61983151

Message = ChatCompletionMessageParam
Chat: Type = List[Message]

CHAT_STREAK_SEC: int = 3


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

        self.chats: Dict[int, List[Message]] = {}
        self.last_chat: Dict[int, int] = {}
        self.profiles: Dict[int, DetailedProfile] = {}
        self.geohash: str = FetchCascadeRoute.generate_hash(location[0], location[1])

        self._openai: AsyncOpenAI = AsyncOpenAI(api_key=openai_key)
        self._cascade_task: Optional[Task] = None

        self.add_listener(ConnectEvent, self.on_connect)
        self.add_listener(MessageEvent, self.on_message)
        self._logger.setLevel(LogLevel.DEBUG.value)

    async def on_connect(self, _: ConnectEvent) -> None:
        """
        Let us know when we are connected to Grindr

        """

        print("Connected to Grindr!")
        self.profiles[int(self.session.profileId)] = await self.get_profile(int(self.session.profileId))
        self._cascade_task = self._asyncio_loop.create_task(self.cascade_loop())

        print("Setting Active")
        await self.web.set_active()

    async def cascade_loop(self) -> None:
        """
        Continuously pull cascade. Pulling cascade marks you as online.

        """

        while self.connected:
            await self.web.fetch_cascade(params=FetchCascadeRouteParams(geohash=self.geohash))
            await asyncio.sleep(60 * 5)

    @property
    def default_chat(self) -> Chat:
        return [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    async def get_profile(self, profile_id: int) -> DetailedProfile:

        if profile_id not in self.profiles:
            profile: DetailedProfile = (await self.web.fetch_profile(params=FetchProfileRouteParams(profileId=profile_id))).profiles[0]
            self.profiles[profile_id] = profile

        return self.profiles[profile_id]

    async def get_response(self, chat: Chat) -> Chat:
        try:
            text_gen: ChatCompletion = await self._openai.chat.completions.create(
                model="gpt-4o",
                messages=chat,
                max_tokens=200,
                temperature=0.7
            )
            reply_text = text_gen.choices[0].message.content
        except Exception as e:
            self._logger.error(f"Failed to get response from OpenAI: {e}")
            chat[-1]['content'] = '[Redacted due to filtered content]'
            reply_text = "Sorry, I'm a little tired. Can you ask that again?"

        chat.append({"role": "assistant", "content": reply_text})
        return chat

    async def on_message(self, event: MessageEvent) -> None:

        # Skip self messages
        if str(event.senderId) == str(self.session.profileId):
            return

        # Mark as read
        await self.web.set_message_read(params=SetMessageReadRouteParams(conversationId=event.conversationId, messageId=event.messageId))

        # Receive text ONLY
        if event.type != "Text":
            return

        chat: Chat = self.chats.get(event.senderId, self.default_chat)
        # profile: DetailedProfile = await self.get_profile(event.senderId)
        our_profile: DetailedProfile = await self.get_profile(int(self.session.profileId))

        print(f"[{our_profile.displayName}]", "<-", f"[{event.senderId}]", event.body.text)
        chat.append({"role": "user", "content": event.body.text})

        # Get a reply
        chat = await self.get_response(chat)
        reply_text = chat[-1]["content"]

        print(f"[{our_profile.displayName}]", "->", f"[{event.senderId}]", reply_text)
        self.chats[event.senderId] = chat

        if reply_text == ALBUM_SENT_TEXT:
            await self.web.set_send_album(
                params=SetSendAlbumRouteParams(albumId=ALBUM_ID),
                body=SetSendAlbumRoute.create_payload(profile_id=event.senderId)
            )
            return

        # Send the reply after a bit
        await self.web.set_typing(body=SetTypingRouteBody(conversationId=event.conversationId, status="Typing"))
        await asyncio.sleep(random.randint(2, 4))
        await self.send(profile_id=event.senderId, text=reply_text)
        await self.web.set_typing(body=SetTypingRouteBody(conversationId=event.conversationId, status="Sent"))


async def run_loop():
    load_dotenv()

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


if __name__ == '__main__':
    asyncio.run(run_loop())
