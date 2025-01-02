import httpx


class AlreadyConnectedError(RuntimeError):
    pass


class AuthenticationDetailsMissingError(RuntimeError):
    pass


class GrindrRequestError(RuntimeError):

    def __init__(self, response: httpx.Response | None, *args):
        super().__init__(*args)
        self._response = response

    @property
    def response(self) -> httpx.Response | None:
        return self._response

    @property
    def request(self) -> httpx.Request | None:
        return self._response.request


class LoginFailedResponse(GrindrRequestError):
    pass


class AccountBannedError(LoginFailedResponse):
    pass


class CloudflareWAFResponse(LoginFailedResponse):
    pass
