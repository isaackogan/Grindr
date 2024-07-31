class AlreadyConnectedError(RuntimeError):
    pass


class LoginFailedResponse(RuntimeError):
    pass


class CloudflareWAFResponse(RuntimeError):
    pass


class AuthenticationDetailsMissingError(RuntimeError):
    pass
