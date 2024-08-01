from typing import List, Optional

from pydantic import PrivateAttr

from Grindr.client.web.routes.fetch_inbox import FetchInboxRouteResponse, FetchInboxRouteParams, InboxConversationData
from Grindr.models.context import GrindrModel, Context


class Inbox(GrindrModel):
    _currentPage: Optional[int] = PrivateAttr(default=1)
    _entries: List[InboxConversationData] = PrivateAttr(default_factory=list)

    @classmethod
    def from_defaults(cls, context: Context) -> "Inbox":
        return cls(context=context)

    @property
    def entries(self) -> List[InboxConversationData]:
        return self._entries

    async def retrieve_next_page(self) -> List[InboxConversationData]:

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

    async def retrieve_pages(self, page_limit: int = 1) -> List[InboxConversationData]:
        for _ in range(page_limit):
            await self.retrieve_next_page()
            if self._currentPage is None:
                break

        return self.entries

    async def retrieve_all(self) -> "Inbox":
        await self.retrieve_pages()
        return self
