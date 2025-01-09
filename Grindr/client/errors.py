from curl_cffi.requests import Response, Request


class AlreadyConnectedError(RuntimeError):
    pass


class AuthenticationDetailsMissingError(RuntimeError):
    pass


class GrindrRequestError(RuntimeError):

    def __init__(self, response: Response | None, *args):
        super().__init__(*args)
        self._response = response

    @property
    def response(self) -> Response | None:
        return self._response

    @property
    def request(self) -> Request | None:
        return self._response.request


class LoginFailedResponse(GrindrRequestError):
    pass


class AccountBannedError(LoginFailedResponse):
    pass


class CloudflareWAFResponse(LoginFailedResponse):
    pass
