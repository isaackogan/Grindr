from .routes.fetch_album import FetchAlbumRoute
from .routes.fetch_albums import FetchAlbumsRoute
from .routes.fetch_blocks import FetchBlocksRoute
from .routes.fetch_cascade import FetchCascadeRoute
from .routes.fetch_messages import FetchMessagesRoute
from .routes.fetch_favorites import FetchFavoritesRoute
from .routes.fetch_inbox import FetchInboxRoute
from .routes.fetch_profile import FetchProfileRoute
from .routes.fetch_profiles import FetchProfilesRoute
from .routes.fetch_session import FetchSessionNewRoute, FetchSessionRefreshRoute
from .routes.fetch_shared_albums import FetchSharedAlbumsRoute
from .routes.fetch_taps import FetchTapsRoute
from .routes.fetch_views import FetchViewsRoute
from .routes.set_active import SetActiveRoute
from .routes.set_block_user import SetBlockUserRoute
from .routes.set_location import SetLocationRoute
from .routes.set_media_upload import SetMediaUploadRoute
from .routes.set_message_read import SetMessageReadRoute
from .routes.set_profile_details import SetProfileDetailsRoute
from .routes.set_send_album import SetSendAlbumRoute
from .routes.set_send_reaction import SetSendReactionRoute
from .routes.set_send_tap import SetSendTapRoute
from .routes.set_typing import SetTypingRoute
from .routes.set_unblock_user import SetUnblockUserRoute
from .web_base import GrindrHTTPClient


class GrindrWebClient(GrindrHTTPClient):
    """
    Wrapper for the HTTP client to add web routes

    """

    def __init__(self, **kwargs):
        """
        Create a web client with registered Grindr routes

        :param kwargs: Arguments to pass to the super-class

        """

        super().__init__(**kwargs)

        self.fetch_session_new: FetchSessionNewRoute = FetchSessionNewRoute(self)
        self.fetch_session_refresh: FetchSessionRefreshRoute = FetchSessionRefreshRoute(self)

        self.fetch_inbox: FetchInboxRoute = FetchInboxRoute(self)
        self.fetch_taps: FetchTapsRoute = FetchTapsRoute(self)
        self.fetch_views: FetchViewsRoute = FetchViewsRoute(self)
        self.fetch_messages: FetchMessagesRoute = FetchMessagesRoute(self)
        self.fetch_profiles: FetchProfilesRoute = FetchProfilesRoute(self)
        self.fetch_profile: FetchProfileRoute = FetchProfileRoute(self)
        self.fetch_cascade: FetchCascadeRoute = FetchCascadeRoute(self)
        self.fetch_albums: FetchAlbumsRoute = FetchAlbumsRoute(self)
        self.fetch_album: FetchAlbumRoute = FetchAlbumRoute(self)
        self.fetch_shared_albums: FetchSharedAlbumsRoute = FetchSharedAlbumsRoute(self)
        self.fetch_favorites: FetchFavoritesRoute = FetchFavoritesRoute(self)
        self.fetch_blocks: FetchBlocksRoute = FetchBlocksRoute(self)

        self.set_block_user: SetBlockUserRoute = SetBlockUserRoute(self)
        self.set_unblock_user: SetUnblockUserRoute = SetUnblockUserRoute(self)
        self.set_location: SetLocationRoute = SetLocationRoute(self)
        self.set_message_read: SetMessageReadRoute = SetMessageReadRoute(self)
        self.set_typing: SetTypingRoute = SetTypingRoute(self)
        self.set_active: SetActiveRoute = SetActiveRoute(self)
        self.set_send_album: SetSendAlbumRoute = SetSendAlbumRoute(self)
        self.set_send_reaction: SetSendReactionRoute = SetSendReactionRoute(self)
        self.set_send_tap: SetSendTapRoute = SetSendTapRoute(self)
        self.set_media_upload: SetMediaUploadRoute = SetMediaUploadRoute(self)
        self.set_profile_details: SetProfileDetailsRoute = SetProfileDetailsRoute(self)
