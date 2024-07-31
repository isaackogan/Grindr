import asyncio
import random
import textwrap
from typing import List, Optional, Tuple

import openai
from httpx import Response
from openai import AsyncOpenAI
from openai.types import ImagesResponse
from openai.types.chat import ChatCompletion

from Grindr.client.web.routes.set_media_upload import SetMediaUploadRouteBody, SetMediaUploadRouteResponse
from Grindr.client.web.routes.set_send_album import SetSendAlbumRouteParams, SetSendAlbumRoute
from Grindr.client.web.routes.set_send_reaction import SetSendReactionRouteBody
from Grindr.client.web.web_client import GrindrWebClient
from Grindr.client.ws.ws_client import GrindrWSClient
from Grindr.client.ws.ws_objects import WSMessage
from Grindr.events import MessageEvent, MediaType
from gpt.gpt_tools import Tool, pick_tool, Chat

ALBUM_CODE = "{USER_ASKED_FOR_ALBUM}"
PICS_CODE = "{USER_ASKED_FOR_PICS}"
LIKE_MESSAGE_CODE = "{LIKE_USER_MESSAGE}"
NO_REPLY_CODE = "{NO_REPLY}"

SYNC_TOOLS: List[Tool] = [
    {"id": 1, "description": "Use this if someone asks for **MORE / ADDITIONAL** pics, an album, or nudes", "fn_code": ALBUM_CODE},
    {"id": 2, "description": "Use this if someone asks for pics/photos", "fn_code": PICS_CODE},
    {"id": 3, "description": "Use this if someone says bye, goodnight, or is otherwise leaving the conversation.", "fn_code": NO_REPLY_CODE},
    {"id": 4, "description": "Use this for all other requests that do not fit any other tool", "fn_code": None},
]

ASYNC_TOOLS: List[Tool] = [
    {"id": 1, "description": "Use this if the message sounds like it's horny", "fn_code": LIKE_MESSAGE_CODE},
    {"id": 2, "description": "Use this for all other requests that do not fit any other tool", "fn_code": None},
]

SELF_IMAGE_PROMPT = textwrap.dedent(
    """
    Generate an image of a computer datacenter. The image should be a realistic, high-quality image of a computer datacenter.
    It should be a datacenter specializing in artificial intelligence like ChatGPT or Llama-3.
    """
)

ALBUM_TOKEN = "<Album Sent>"
NO_REPLY_TOKEN = "<No Reply>"


class GChat:

    def __init__(
            self,
            initial_chat: Chat,
            web: GrindrWebClient,
            ws: GrindrWSClient,
            llm: AsyncOpenAI,
            my_album_id: int,
    ):
        self._ws: GrindrWSClient = ws
        self._web: GrindrWebClient = web
        self._llm: AsyncOpenAI = llm
        self._chat: Chat = initial_chat
        self._my_album_id: int = my_album_id
        self._logged_chats: List[str] = []

    def has_message(self, message_id: str) -> bool:
        return message_id in self._logged_chats

    async def reply(self, message: MessageEvent) -> Tuple[str, str]:
        """
        Reply to a message event

        :param message: The message event to reply to
        :return: The AI's response

        """

        self._logged_chats.append(message.messageId)

        match message.type:
            case MediaType.ALBUM:
                prompt, reply = await self._reply_album(message)
            case MediaType.IMAGE:
                prompt, reply = await self._reply_image(message)
            case MediaType.ALBUM_CONTENT_REPLY:
                prompt, reply = await self._reply_album_content_reply(message)
            case MediaType.TEXT:
                prompt, reply = await self._reply_text(message)
            case _:
                prompt, reply = await self._reply_other(message)

        return prompt, reply.strip()

    @classmethod
    def _get_reply_text(cls, message: MessageEvent) -> str:

        if message.replyToMessage is None:
            return ''

        if message.replyToMessage.type == MediaType.TEXT:
            return f"You sent a message \"{message.replyToMessage.body.text}\" earlier. This is a reply to that message:\n"

        return ''

    async def _reply_text(self, message: MessageEvent) -> Tuple[str, str]:
        user_prompt: str = self._get_reply_text(message) + message.body.text

        sync_tool_response: Optional[str] = await pick_tool(prompt=user_prompt, tools=SYNC_TOOLS, llm=self._llm)
        async_tool_response: Optional[str] = await pick_tool(prompt=user_prompt, tools=ASYNC_TOOLS, llm=self._llm)

        if async_tool_response == LIKE_MESSAGE_CODE and random.randint(1, 3) == 4:
            await self._send_reaction_width_random_delay(message_id=message.messageId, conversation_id=message.conversationId)

        chat: Chat = [*self._chat, {"role": "user", "content": user_prompt}]
        return_message: Optional[str] = None

        if sync_tool_response == ALBUM_CODE:
            await self._web.set_send_album(
                params=SetSendAlbumRouteParams(albumId=self._my_album_id),
                body=SetSendAlbumRoute.create_payload(profile_id=message.senderId)
            )

            if random.randint(1, 4) == 2:
                await self._send_reaction_width_random_delay(message_id=message.messageId, conversation_id=message.conversationId)

            chat.append({"role": "assistant", "content": ALBUM_TOKEN})

        elif sync_tool_response == NO_REPLY_CODE:
            chat.append({"role": "assistant", "content": NO_REPLY_TOKEN})

        elif sync_tool_response == PICS_CODE:

            llm_response: ImagesResponse = await self._llm.images.generate(
                prompt=SELF_IMAGE_PROMPT,
                response_format="url",
            )

            image_response: Response = await self._web.http_client.get(url=llm_response.data[0].url, headers={"Accept": "image/png"})
            image_data: bytes = image_response.read()

            media_upload_response: SetMediaUploadRouteResponse = await self._web.set_media_upload(
                body=SetMediaUploadRouteBody(image_bytes=image_data)
            )

            await self._ws.ws.asend(
                WSMessage.image_from_defaults(
                    token=self._web.session_token,
                    profile_id=message.senderId,
                    media_id=media_upload_response.mediaId
                ).model_dump_json()
            )

            chat.append({"role": "assistant", "content": "<Generated image of myself>"})
            return_message = llm_response.data[0].url
        else:

            # Like their message randomly (1/10 chance)
            if random.randint(1, 10) == 5:
                await self._send_reaction_width_random_delay(message_id=message.messageId, conversation_id=message.conversationId)

            response, exception = await self._llm_text_response(chat=chat)
            chat.append({"role": "assistant", "content": response})

        self._chat = chat
        return user_prompt, return_message if return_message else chat[-1]["content"]

    async def _send_reaction_width_random_delay(self, message_id: str, conversation_id: str) -> None:

        async def _send_reaction():
            await asyncio.sleep(min(random.randint(2, 12), 60))

            await self._web.set_send_reaction(
                body=SetSendReactionRouteBody(messageId=message_id, conversationId=conversation_id)
            )

        asyncio.get_running_loop().create_task(_send_reaction())

    async def _reply_other(self, message: MessageEvent) -> Tuple[str, str]:
        """Tap the message if there's nothing to say because it's an unhandled message type"""

        await self._send_reaction_width_random_delay(message_id=message.messageId, conversation_id=message.conversationId)

        response: str = "<Liked the message>"

        self._chat = [
            *self._chat,
            {"role": "user", "content": f"<User sent a message of type {message.type.name}>"},
            {"role": "assistant", "content": response}
        ]

        return '<User sent a message that was not handled>', response

    async def _reply_image(self, message: MessageEvent) -> Tuple[str, str]:

        chat: Chat = [
            *self._chat,
            {"role": "user", "content": [{"type": "image_url", "image_url": {"url": message.body.url}}]}
        ]

        response, exception = await self._llm_text_response(chat=chat)

        if exception == openai.BadRequestError and "content filter" in str(exception):
            chat[-1] = {"role": "user", "content": "<NSFW Image>"}

        chat.append({"role": "assistant", "content": response})
        self._chat = chat

        return "<User sent an image>", response

    async def _reply_album_content_reply(self, message: MessageEvent) -> Tuple[str, str]:

        user_prompt: str = "<In response to our Grindr album>" + message.body.albumContentReply

        chat: Chat = [
            *self._chat,
            {"role": "user", "content": user_prompt}
        ]

        response, exception = await self._llm_text_response(chat=chat)
        chat.append({"role": "assistant", "content": response})

        self._chat = chat
        return user_prompt, response

    async def _reply_album(self, _: MessageEvent) -> Tuple[str, str]:

        chat: Chat = [
            *self._chat,
            {"role": "system", "content": "<The user sent their Grindr album. Reply to this message as if the album contained photos of them."}
        ]

        user_message: str = "<Album Sent>"
        response, exception = await self._llm_text_response(chat=chat)
        chat[-1] = {"role": "user", "content": user_message}
        chat.append({"role": "assistant", "content": response})

        self._chat = chat
        return user_message, response

    async def _llm_text_response(self, chat: Chat) -> Tuple[str, Optional[Exception]]:
        """
        Generic LLM response query

        :param chat: The chat history to reply to
        :return: The response from the LLM

        """

        # Ask for a reply
        try:

            text_gen: ChatCompletion = await self._llm.chat.completions.create(
                model="gpt-4o",
                messages=chat,
                temperature=0.7
            )

            return text_gen.choices[0].message.content, None

        # Handle content filtered
        except openai.BadRequestError as e:

            if "content filter" not in str(e):
                raise e

            response: ChatCompletion = await self._llm.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "Someone sent an inappropriate message. Reply in a flirty way that they should keep it clean."}],
                temperature=0.4
            )

            return response.choices[0].message.content, None
