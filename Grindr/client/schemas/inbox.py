from pydantic import PrivateAttr

from Grindr.client.schemas.sessioncontext import GrindrModel, SessionContext
from Grindr.web.routes.fetch.fetch_inbox import FetchInboxRouteResponse, InboxConversationData, FetchInboxRouteParams


class Inbox(GrindrModel):
    _currentPage: int | None = PrivateAttr(default=1)
    _entries: list[InboxConversationData] = PrivateAttr(default_factory=list)

    @classmethod
    def from_defaults(cls, context: SessionContext) -> "Inbox":
        return cls(context=context)

    @property
    def entries(self) -> list[InboxConversationData]:
        return self._entries

    async def retrieve_next_page(self) -> list[InboxConversationData]:

        # If there are no further pages to retrieve
        if self._currentPage is None:
            return []

        # Fetch the next page
        response: FetchInboxRouteResponse = await self.context.web.fetch_inbox(
            params=FetchInboxRouteParams(page=self._currentPage)
        )

        response.entries.reverse()
        self._entries = [*response.entries, *self._entries]
        self._currentPage = response.nextPage

        return response.entries

    async def retrieve_pages(self, page_limit: int = 1) -> list[InboxConversationData]:
        for _ in range(page_limit):
            await self.retrieve_next_page()
            if self._currentPage is None:
                break

        return self.entries

    async def retrieve_all(self) -> "Inbox":
        await self.retrieve_pages()
        return self
