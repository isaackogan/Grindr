from typing import Callable, Any

from pydantic import Field, PrivateAttr

from Grindr.client.schemas.profile import Profile
from Grindr.client.schemas.sessioncontext import SessionContext, GrindrModel
from Grindr.web.routes.fetch.fetch_messages import FetchMessagesRouteParams, FetchMessagesRouteResponse, Message
from Grindr.web.routes.fetch.fetch_profile import FetchProfileRouteResponse, FetchProfileRouteParams
from Grindr.web.routes.set.set_message_read import SetMessageReadRouteParams
from Grindr.web.routes.set.set_send_album import SetSendAlbumRouteParams, SetSendAlbumRoute
from Grindr.web.routes.set.set_send_reaction import SetSendReactionRoutePayload
from Grindr.ws.events.events import MessageEvent
from Grindr.ws.ws_schemas import MessagePayloadBodyType


class Conversation(GrindrModel):
    # Format [TargetID:YourID]
    id: str = Field(pattern=r"^\d+:\d+$")

    profile: Profile | None = None
    messages: list[Message] | None = None

    _on_message: Callable[[...], Any] | None = PrivateAttr(default=None)

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
    def from_defaults(cls, target_id: int, context: SessionContext, profile: Profile | None = None) -> "Conversation":
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

    async def retrieve_messages(self, page_limit: int | None = 1) -> list[Message]:

        current_page: int = 0
        page_key: str = ""
        continue_pagination: Callable[[], bool] = (lambda: (current_page < max(1, page_limit)) if page_limit is not None else True)
        messages: list[Message] = []

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

    async def send_message(self, message: MessagePayloadBodyType) -> None:
        """
        Send a message to the conversation

        :param message: The body of the message to send
        :return: None

        """

        await self.context.ws.send(
            body=message,
            target_profile_id=self.target_id,
        )

    async def send_album(self, album_id: int) -> None:

        await self.context.web.set_send_album(
            params=SetSendAlbumRouteParams(albumId=album_id),
            body=SetSendAlbumRoute.create_payload(profile_id=self.target_id)
        )

    async def send_like(self, message_id: str) -> None:

        await self._web.set_send_reaction(
            body=SetSendReactionRoutePayload(messageId=message_id, conversationId=self.id)
        )
