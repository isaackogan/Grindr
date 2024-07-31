from curl_cffi import CurlOpt
from curl_cffi.requests import AsyncSession

from Grindr.client.ws.AsyncWS.client import AsyncWebSocket


class AsyncWebSocketSession(AsyncSession):
    """
    Override the default curl_cffi AsyncSession to provide a custom instance of the WebSocket connection

    """

    async def ws_connect(self, url, *args, **kwargs):
        """
        Connect to a WebSocket server

        :param url: URL to connect to
        :param args: Args to pass to the connection
        :param kwargs: Kwargs to pass to the connection
        :return: AsyncWebSocket instance

        """

        # Connect to the server
        self._check_session_closed()
        curl = await self.pop_curl()
        self._set_curl_options(curl, "GET", url, *args, **kwargs)
        curl.setopt(CurlOpt.CONNECT_ONLY, 2)
        await self.loop.run_in_executor(None, curl.perform)

        # Return the WebSocket connection
        return AsyncWebSocket(self, curl)
