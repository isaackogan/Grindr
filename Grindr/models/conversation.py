import asyncio
from typing import List, Optional, Callable

from pydantic import Field, PrivateAttr

from Grindr.client.web.routes.fetch_messages import FetchMessagesRouteParams, FetchMessagesRouteResponse, Message
from Grindr.client.web.routes.fetch_profile import FetchProfileRouteParams, FetchProfileRouteResponse
from Grindr.client.web.routes.set_message_read import SetMessageReadRouteParams
from Grindr.client.web.routes.set_send_album import SetSendAlbumRouteParams, SetSendAlbumRoute
from Grindr.client.web.routes.set_send_reaction import SetSendReactionRouteBody
from Grindr.client.ws.ws_objects import SendPayloadBody, WSTextPayloadBody, WSImagePayloadBody, WSGifPayloadBody, WSMessage, WSMessagePayload
from Grindr.events import MessageEvent
from Grindr.models.context import Context, GrindrModel
from Grindr.models.message import SendMessageType
from Grindr.models.profile import Profile


class Conversation(GrindrModel):
    # Format [TargetID:YourID]
    id: str = Field(pattern=r"^\d+:\d+$")

    profile: Optional[Profile] = None
    messages: Optional[List[Message]] = None

    _on_message: Optional[Callable] = PrivateAttr(default=None)

    async def retrieve_all(self) -> "Conversation":
        await self.retrieve_messages()
        await self.retrieve_profile()
        return self

    def track(self, mark_read: bool = False) -> bool:
        """
        Add new messages to the messages as they are received on the WS

        :return: None

        """

        if self._on_message is not None:
            return False

        async def _on_message(e: MessageEvent):
            if e.conversationId == self.id:
                self.messages.append(Message(**e.model_dump()))

                if mark_read:
                    await self.set_read(message_id=e.messageId)

        self.context.emitter.on(MessageEvent, _on_message)
        self._on_message = _on_message
        return True

    def untrack(self) -> bool:
        """
        Remove the tracking function from the emitter

        :return: None

        """

        if self._on_message is None:
            return False

        self.context.emitter.remove_listener(MessageEvent, self._on_message)
        self._on_message = None
        return True

    async def set_read(self, message_id: str) -> None:
        """
        Read the conversation & track messages

        :return: None

        """

        await self.web.set_message_read(
            params=SetMessageReadRouteParams(
                conversationId=self.id,
                messageId=message_id
            )
        )

    async def set_typing(self) -> None:
        """
        Set typing status

        :return: None

        """

        await self.web.set_typing(params=None, body=None)

    @classmethod
    def get_conversation_id(cls, profile_id: int, target_id: int) -> str:
        return f"{target_id}:{profile_id}"

    @classmethod
    def from_defaults(cls, target_id: int, context: Context, profile: Optional[Profile] = None) -> "Conversation":
        return cls(
            context=context,
            id=cls.get_conversation_id(profile_id=context.profile_id, target_id=target_id),
            profile=profile
        )

    @property
    def target_id(self) -> int:
        return int(self.id.split(":")[0])

    async def retrieve_profile(self) -> Profile:
        response: FetchProfileRouteResponse = await self.context.web.fetch_profile(
            params=FetchProfileRouteParams(
                profileId=self.target_id
            )
        )

        profile = self.profile = Profile.from_data(
            context=self.context,
            data=response.profiles[0]
        )

        await profile.retrieve_all()
        return profile

    async def retrieve_messages(self, page_limit: Optional[int] = 1) -> List[Message]:

        current_page: int = 0
        page_key: str = ""
        continue_pagination: Callable[[], bool] = (lambda: (current_page < max(1, page_limit)) if page_limit is not None else True)
        messages: List[Message] = []

        while continue_pagination():
            current_page += 1

            response: FetchMessagesRouteResponse = await self.context.web.fetch_messages(
                params=FetchMessagesRouteParams(
                    conversationId=self.id,
                    pageKey=page_key
                )
            )

            messages.extend(response.messages)

            # Reached the end of the pagination
            if len(messages) == 0:
                break

            # The oldest message is the last message in the list
            page_key = messages[-1].messageId

        messages.reverse()
        self.messages = messages
        return self.messages

    async def send(
            self,
            message_type: SendMessageType,
            message_body: SendPayloadBody
    ) -> None:
        """
        Send a message to the conversation

        :param message_type: The type of message to send
        :param message_body: The body of the message to send
        :return: None

        """

        await self.context.ws.ws.asend(
            payload=WSMessage.from_defaults(
                payload=WSMessagePayload.from_defaults(
                    target_id=self.target_id,
                    message_type=message_type,
                    message_body=message_body
                )
            )
        )

    async def send_text(
            self,
            text: str,
            send_typing: bool = True,
            wpm: Optional[int] = 60
    ) -> None:
        await self.set_typing()

        if send_typing and wpm is not None and wpm > 0:
            await asyncio.sleep((len(text.split()) / wpm) * 60)

        payload: WSTextPayloadBody = WSTextPayloadBody.from_defaults(text=text)
        await self.send(message_type=SendMessageType.TEXT, message_body=payload)

    async def send_image(
            self,
            media_id: str
    ) -> None:
        payload: WSImagePayloadBody = WSImagePayloadBody.from_defaults(media_id=media_id)
        await self.send(message_type=SendMessageType.IMAGE, message_body=payload)

    async def send_gif(
            self,
            image_url: str,
            image_id: str
    ) -> None:
        payload: WSGifPayloadBody = WSGifPayloadBody.from_defaults(image_url=image_url, image_id=image_id)
        await self.send(message_type=SendMessageType.GIPHY, message_body=payload)

    async def send_album(self, album_id: int) -> None:

        await self.context.web.set_send_album(
            params=SetSendAlbumRouteParams(albumId=album_id),
            body=SetSendAlbumRoute.create_payload(profile_id=self.target_id)
        )

    async def send_like(self, message_id: str) -> None:

        await self._web.set_send_reaction(
            body=SetSendReactionRouteBody(messageId=message_id, conversationId=self.id)
        )
