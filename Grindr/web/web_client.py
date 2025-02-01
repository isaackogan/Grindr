from pathlib import Path
from typing import Literal

from curl_cffi.requests import AsyncSession, Response
from pydantic import BaseModel

from Grindr.web.routes.fetch.fetch_album import FetchAlbumRoute
from Grindr.web.routes.fetch.fetch_albums import FetchAlbumsRoute
from Grindr.web.routes.fetch.fetch_blocks import FetchBlocksRoute
from Grindr.web.routes.fetch.fetch_cascade import FetchCascadeRoute
from Grindr.web.routes.fetch.fetch_eyeball import FetchEyeballRoute
from Grindr.web.routes.fetch.fetch_favorites import FetchFavoritesRoute
from Grindr.web.routes.fetch.fetch_inbox import FetchInboxRoute
from Grindr.web.routes.fetch.fetch_messages import FetchMessagesRoute
from Grindr.web.routes.fetch.fetch_profile import FetchProfileRoute
from Grindr.web.routes.fetch.fetch_profiles import FetchProfilesRoute
from Grindr.web.routes.fetch.fetch_session import FetchSessionRoute, FetchSessionRefreshRoutePayload, FetchSessionNewRoutePayload, FetchSessionRouteResponse, SessionCredentials
from Grindr.web.routes.fetch.fetch_shared_albums import FetchSharedAlbumsRoute
from Grindr.web.routes.fetch.fetch_taps import FetchTapsRoute
from Grindr.web.routes.fetch.fetch_views import FetchViewsRoute
from Grindr.web.routes.set.set_active import SetActiveRoute
from Grindr.web.routes.set.set_block_user import SetBlockUserRoute
from Grindr.web.routes.set.set_location import SetLocationRoute
from Grindr.web.routes.set.set_media_upload import SetMediaUploadRoute
from Grindr.web.routes.set.set_message_read import SetMessageReadRoute
from Grindr.web.routes.set.set_profile_details import SetProfileDetailsRoute
from Grindr.web.routes.set.set_profile_image import SetProfileImageRoute
from Grindr.web.routes.set.set_profile_images import SetProfileImagesRoute
from Grindr.web.routes.set.set_send_album import SetSendAlbumRoute
from Grindr.web.routes.set.set_send_reaction import SetSendReactionRoute
from Grindr.web.routes.set.set_send_tap import SetSendTapRoute
from Grindr.web.routes.set.set_typing import SetTypingRoute
from Grindr.web.routes.set.set_unblock_user import SetUnblockUserRoute
from .routes.fetch.fetch_albums_red_dot import FetchAlbumsRedDotRoute
from .routes.fetch.fetch_assignments import FetchAssignmentsRoute
from .routes.fetch.fetch_boost_sessions import FetchBoostSessionsRoute
from .routes.fetch.fetch_chat_media import FetchChatMediaRoute
from .routes.fetch.fetch_genders import FetchGendersRoute
from .routes.fetch.fetch_google_play_products import FetchGooglePlayProductsRoute
from .routes.fetch.fetch_legal_agreements import FetchLegalAgreementsRoute
from .routes.fetch.fetch_my_profile import FetchMyProfileRoute
from .routes.fetch.fetch_offers_eligible import FetchOffersEligibleRoute
from .routes.fetch.fetch_opt_out import FetchOptOutRoute
from .routes.fetch.fetch_prefs import FetchPrefsRoute
from .routes.fetch.fetch_profile_images import FetchProfileImagesRoute
from .routes.fetch.fetch_profile_tag_translations import FetchProfileTagTranslationsRoute
from .routes.fetch.fetch_rewarded_chats import FetchRewardedChatsRoute
from .routes.fetch.fetch_tags import FetchTagsRoute
from .routes.fetch.fetch_taps_sent import FetchTapsSentRoute
from .routes.fetch.fetch_videos_expiring_status import FetchVideosExpiringStatusRoute
from .routes.fetch.fetch_warnings import FetchWarningsRoute
from .routes.set.set_delete_profile_images import SetDeleteProfileImagesRoute
from .routes.set.set_gcm_push_tokens import SetGcmPushTokensRoute
from .routes.set.set_mobile_logs import SetMobileLogsRoute
from .routes.set.set_notifications_ack import SetNotificationsAckRoute
from .web_base import GrindrHTTPClient
from .web_logger import GrindrWebFileLogger
from .web_schemas import GrindrRequestError, CredentialsMissingError


class GrindrWebClientAuthSession(BaseModel):
    """Auth Context Object"""

    # The current credentials
    credentials: SessionCredentials | None = None

    # Current session data
    session_data: FetchSessionRouteResponse | None = None

    @property
    def auth_token(self) -> str | None:
        """The current auth token"""

        if self.session_data is not None and self.session_data.auth_token is not None:
            return self.session_data.auth_token

        if isinstance(self.credentials, FetchSessionRefreshRoutePayload) and self.credentials.authToken:
            return self.credentials.authToken

        return None

    @property
    def profile_id(self) -> int | None:
        """The current profile ID"""

        if self.session_data is not None and self.session_data.profile_id is not None:
            return self.session_data.profile_id

        return None


class GrindrWebClient(GrindrHTTPClient):
    """
    Wrapper for the HTTP client to add web routes

    """

    def __init__(
            self,
            web_credentials: GrindrWebClientAuthSession,
            web_max_auth_retries: int = 2,
            web_request_dump_directory: str | None = None,
            web_curl_proxy: str | None = None,
            web_curl_kwargs: dict | None = None
    ):
        """
        Create a web client with registered Grindr routes

        :param web_max_auth_retries: The maximum number of times to retry authentication
        :param web_curl_kwargs: Arguments to pass to the base HTTP client

        """

        super().__init__(
            web_curl_proxy=web_curl_proxy,
            web_curl_kwargs=web_curl_kwargs
        )

        self._max_auth_retries: int = web_max_auth_retries
        self._auth_session: GrindrWebClientAuthSession = GrindrWebClientAuthSession(credentials=web_credentials)
        self._file_logger: GrindrWebFileLogger | None = GrindrWebFileLogger(Path(web_request_dump_directory), self._auth_session) if web_request_dump_directory else None
        self._user_agent: str | None = None

        self.fetch_session: FetchSessionRoute = FetchSessionRoute(self)
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
        self.fetch_profile_tag_translations: FetchProfileTagTranslationsRoute = FetchProfileTagTranslationsRoute(self)
        self.fetch_my_profile: FetchMyProfileRoute = FetchMyProfileRoute(self)
        self.fetch_offers_eligible: FetchOffersEligibleRoute = FetchOffersEligibleRoute(self)
        self.fetch_opt_out: FetchOptOutRoute = FetchOptOutRoute(self)
        self.fetch_prefs: FetchPrefsRoute = FetchPrefsRoute(self)
        self.fetch_rewarded_chats: FetchRewardedChatsRoute = FetchRewardedChatsRoute(self)
        self.fetch_taps_sent: FetchTapsSentRoute = FetchTapsSentRoute(self)
        self.fetch_warnings: FetchWarningsRoute = FetchWarningsRoute(self)
        self.fetch_profile_images: FetchProfileImagesRoute = FetchProfileImagesRoute(self)
        self.fetch_assignments: FetchAssignmentsRoute = FetchAssignmentsRoute(self)
        self.fetch_tags: FetchTagsRoute = FetchTagsRoute(self)
        self.fetch_videos_expiring_status: FetchVideosExpiringStatusRoute = FetchVideosExpiringStatusRoute(self)
        self.fetch_chat_media: FetchChatMediaRoute = FetchChatMediaRoute(self)

        self.set_delete_profile_images: SetDeleteProfileImagesRoute = SetDeleteProfileImagesRoute(self)
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

    async def refresh_session_data(self, use_auth_token: bool = True) -> GrindrWebClientAuthSession:
        """
        Authenticate with Grindr using the current session credentials

        :param use_auth_token: Use the session refresh endpoint with the auth token IF one is available, otherwise default to email-pass if available
        :return: The updated session data

        """

        self.logger.debug("Logging into Grindr...")

        if not self.auth_session.credentials:
            raise CredentialsMissingError("Authentication details must be set! Either username/password, or session_token.")

        # Attempt to refresh the session
        if use_auth_token and self.auth_session.auth_token:
            try:
                self.update_session_data(
                    session_data=await self.fetch_session(
                        body=FetchSessionRefreshRoutePayload(
                            email=self.auth_session.credentials.email,
                            authToken=self.auth_session.auth_token,
                            token=self.auth_session.credentials.token
                        )
                    )
                )
            except GrindrRequestError as ex:
                if ex.response.status_code == 401:  # 401 means it expired, so retry with a new session
                    return await self.refresh_session_data(use_auth_token=False)
                raise ex
        # Fetch a NEW session
        else:
            self.update_session_data(
                session_data=await self.fetch_session(
                    body=FetchSessionNewRoutePayload(
                        email=self.auth_session.credentials.email,
                        password=self.auth_session.credentials.password,
                        token=self.auth_session.credentials.token
                    )
                )
            )

    async def request(
            self,
            method: Literal["GET", "POST", "PUT", "DELETE"],
            base_url: str,
            *,
            extra_params: dict = None,
            extra_headers: dict = None,
            web_client: AsyncSession | None = None,
            base_params: bool = True,
            base_headers: bool = True,
            __retries_remaining: int = None,
            **kwargs
    ) -> Response:
        """
        Make a request to the Grindr API, re-authenticating when necessary

        """

        try:

            return await super().request(
                method=method,
                base_url=base_url,
                extra_params=extra_params,
                extra_headers=extra_headers,
                web_client=web_client,
                base_params=base_params,
                base_headers=base_headers,
                file_logger=self._file_logger,
                **kwargs
            )

        except GrindrRequestError as ex:
            if ex.response.status_code == 401:
                self.logger.warning(f"Auth error for {self.auth_session.credentials.email} - refreshing session...")
                await self.refresh_session_data(use_auth_token=True)
                return await self.request(
                    method=method,
                    base_url=base_url,
                    extra_params=extra_params,
                    extra_headers=extra_headers,
                    web_client=web_client,
                    base_params=base_params,
                    base_headers=base_headers,
                    __retries_remaining=__retries_remaining - 1 if __retries_remaining is not None else self._max_auth_retries,
                    **kwargs
                )

            raise ex

    def update_session_credentials(
            self,
            *,
            details: FetchSessionNewRoutePayload | FetchSessionRefreshRoutePayload
    ) -> GrindrWebClientAuthSession:
        """Update the credentials attached to a session object"""

        self._auth_session.credentials = details
        return self._auth_session

    def update_session_data(
            self,
            *,
            session_data: FetchSessionRouteResponse,
    ) -> GrindrWebClientAuthSession:
        """Update the current session data used by the client"""

        self._auth_session.session_data = session_data
        self.headers['Authorization'] = f'Grindr3 {session_data.session_id}'

        return self._auth_session

    @property
    def auth_session(self) -> GrindrWebClientAuthSession:
        """The current auth session"""
        return self._auth_session

    async def fetch_data(self, route, params=None, body=None, url_override=None, header_override=None, **kwargs):
        """
        Fetch data from a specified route with error handling.

        :param route: The route to fetch data from.
        :param params: Optional parameters for the route.
        :param body: Optional body for the route.
        :param url_override: Optional URL override for the route.
        :param header_override: Optional header override for the route.
        :param kwargs: Additional arguments for the route.
        :return: The response data.
        """
        try:
            return await route(params=params, body=body, url_override=url_override, header_override=header_override, **kwargs)
        except GrindrRequestError as ex:
            self.logger.error(f"Failed to fetch data from {route}: {ex}")
            raise

    async def set_data(self, route, params=None, body=None, url_override=None, header_override=None, **kwargs):
        """
        Set data to a specified route with error handling.

        :param route: The route to set data to.
        :param params: Optional parameters for the route.
        :param body: Optional body for the route.
        :param url_override: Optional URL override for the route.
        :param header_override: Optional header override for the route.
        :param kwargs: Additional arguments for the route.
        :return: The response data.
        """
        try:
            return await route(params=params, body=body, url_override=url_override, header_override=header_override, **kwargs)
        except GrindrRequestError as ex:
            self.logger.error(f"Failed to set data to {route}: {ex}")
            raise
