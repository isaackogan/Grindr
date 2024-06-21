from .routes.fetch_cascade import FetchCascadeRoute
from .routes.fetch_conversation import FetchConversationRoute
from .routes.fetch_inbox import FetchInboxRoute
from .routes.fetch_profile import FetchProfileRoute
from .routes.fetch_profiles import FetchProfilesRoute
from .routes.fetch_session import FetchSessionRoute
from .routes.fetch_taps import FetchTapsRoute
from .routes.set_block_user import SetBlockUserRoute
from .routes.set_location import SetLocationRoute
from .web_base import GrindrHTTPClient


class GrindrWebClient(GrindrHTTPClient):
    """
    Wrapper for the HTTP client to add web routes

    """

    def __init__(self, **kwargs):
        """
        Create a web client with registered TikTok routes

        :param kwargs: Arguments to pass to the super-class

        """

        super().__init__(**kwargs)

        self.fetch_session: FetchSessionRoute = FetchSessionRoute(self)
        self.fetch_inbox: FetchInboxRoute = FetchInboxRoute(self)
        self.fetch_taps: FetchTapsRoute = FetchTapsRoute(self)
        self.fetch_conversation: FetchConversationRoute = FetchConversationRoute(self)
        self.fetch_profiles: FetchProfilesRoute = FetchProfilesRoute(self)
        self.fetch_profile: FetchProfileRoute = FetchProfileRoute(self)
        self.fetch_cascade: FetchCascadeRoute = FetchCascadeRoute(self)

        self.set_block_user: SetBlockUserRoute = SetBlockUserRoute(self)
        self.set_location: SetLocationRoute = SetLocationRoute(self)