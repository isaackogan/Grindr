from Grindr.client.web.routes.fetch.fetch_album import FetchAlbumRoute
from Grindr.client.web.routes.fetch.fetch_albums import FetchAlbumsRoute
from Grindr.client.web.routes.fetch.fetch_blocks import FetchBlocksRoute
from Grindr.client.web.routes.fetch.fetch_cascade import FetchCascadeRoute
from Grindr.client.web.routes.fetch.fetch_eyeball import FetchEyeballRoute
from Grindr.client.web.routes.fetch.fetch_favorites import FetchFavoritesRoute
from Grindr.client.web.routes.fetch.fetch_inbox import FetchInboxRoute
from Grindr.client.web.routes.fetch.fetch_messages import FetchMessagesRoute
from Grindr.client.web.routes.fetch.fetch_profile import FetchProfileRoute
from Grindr.client.web.routes.fetch.fetch_profiles import FetchProfilesRoute
from Grindr.client.web.routes.fetch.fetch_session import FetchSessionNewRoute, FetchSessionRefreshRoute
from Grindr.client.web.routes.fetch.fetch_shared_albums import FetchSharedAlbumsRoute
from Grindr.client.web.routes.fetch.fetch_taps import FetchTapsRoute
from Grindr.client.web.routes.fetch.fetch_views import FetchViewsRoute
from Grindr.client.web.routes.set.set_active import SetActiveRoute
from Grindr.client.web.routes.set.set_block_user import SetBlockUserRoute
from Grindr.client.web.routes.set.set_location import SetLocationRoute
from Grindr.client.web.routes.set.set_media_upload import SetMediaUploadRoute
from Grindr.client.web.routes.set.set_message_read import SetMessageReadRoute
from Grindr.client.web.routes.set.set_profile_details import SetProfileDetailsRoute
from Grindr.client.web.routes.set.set_profile_image import SetProfileImageRoute
from Grindr.client.web.routes.set.set_profile_images import SetProfileImagesRoute
from Grindr.client.web.routes.set.set_send_album import SetSendAlbumRoute
from Grindr.client.web.routes.set.set_send_reaction import SetSendReactionRoute
from Grindr.client.web.routes.set.set_send_tap import SetSendTapRoute
from Grindr.client.web.routes.set.set_typing import SetTypingRoute
from Grindr.client.web.routes.set.set_unblock_user import SetUnblockUserRoute
from .routes.fetch.fetch_albums_red_dot import FetchAlbumsRedDotRoute
from .routes.fetch.fetch_boost_sessions import FetchBoostSessionsRoute
from .routes.fetch.fetch_genders import FetchGendersRoute
from .routes.fetch.fetch_google_play_products import FetchGooglePlayProductsRoute
from .routes.fetch.fetch_legal_agreements import FetchLegalAgreementsRoute
from .routes.fetch.fetch_my_profile import FetchMyProfileRoute
from .routes.fetch.fetch_offers_eligible import FetchOffersEligibleRoute
from .routes.fetch.fetch_opt_out import FetchOptOutRoute
from .routes.fetch.fetch_prefs import FetchPrefsRoute
from .routes.fetch.fetch_rewarded_chats import FetchRewardedChatsRoute
from .routes.fetch.fetch_taps_sent import FetchTapsSentRoute
from .routes.fetch.fetch_warnings import FetchWarningsRoute
from .routes.set.set_gcm_push_tokens import SetGcmPushTokensRoute
from .routes.set.set_mobile_logs import SetMobileLogsRoute
from .routes.set.set_notifications_ack import SetNotificationsAckRoute
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
        self.fetch_eyeball: FetchEyeballRoute = FetchEyeballRoute(self)
        self.fetch_albums_red_dot: FetchAlbumsRedDotRoute = FetchAlbumsRedDotRoute(self)
        self.fetch_boost_sessions: FetchBoostSessionsRoute = FetchBoostSessionsRoute(self)
        self.fetch_eyeball: FetchEyeballRoute = FetchEyeballRoute(self)
        self.fetch_genders: FetchGendersRoute = FetchGendersRoute(self)
        self.getch_google_play_products: FetchGooglePlayProductsRoute = FetchGooglePlayProductsRoute(self)
        self.fetch_legal_agreements: FetchLegalAgreementsRoute = FetchLegalAgreementsRoute(self)
        self.fetch_my_profile: FetchMyProfileRoute = FetchMyProfileRoute(self)
        self.fetch_offers_eligible: FetchOffersEligibleRoute = FetchOffersEligibleRoute(self)
        self.fetch_opt_out: FetchOptOutRoute = FetchOptOutRoute(self)
        self.fetch_prefs: FetchPrefsRoute = FetchPrefsRoute(self)
        self.fetch_rewarded_chats: FetchRewardedChatsRoute = FetchRewardedChatsRoute(self)
        self.fetch_taps_sent: FetchTapsSentRoute = FetchTapsSentRoute(self)
        self.fetch_warnings: FetchWarningsRoute = FetchWarningsRoute(self)

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
        self.set_profile_image: SetProfileImageRoute = SetProfileImageRoute(self)
        self.set_profile_images: SetProfileImagesRoute = SetProfileImagesRoute(self)
        self.set_notifications_ack: SetNotificationsAckRoute = SetNotificationsAckRoute(self)
        self.set_gcm_push_tokens: SetGcmPushTokensRoute = SetGcmPushTokensRoute(self)
        self.set_mobile_logs: SetMobileLogsRoute = SetMobileLogsRoute(self)
