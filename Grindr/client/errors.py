import httpx


class AlreadyConnectedError(RuntimeError):
    pass


class AuthenticationDetailsMissingError(RuntimeError):
    pass


class GrindrRequestError(RuntimeError):

    def __init__(self, response: httpx.Response | None, *args):
        self.response = response
        super().__init__(*args)


class LoginFailedResponse(GrindrRequestError):

    def __init__(self, response: httpx.Response | None, *args):
        self.response = response
        super().__init__(*args)


class CloudflareWAFResponse(LoginFailedResponse):
    pass
