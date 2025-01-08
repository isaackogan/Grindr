import json
import os
import ssl
import sys
from pathlib import Path
from ssl import SSLContext

import httpx

from Grindr.client.logger import GrindrLogHandler

# Generated via POST to https://tls.browserleaks.com/tls from the Grindr HTTP client
JA3_BLUEPRINT_JSON: dict = json.load(open(Path(__file__).parent.resolve().absolute().joinpath('./ja3_blueprint.json')))
OPEN_SSL_CONF_PATH: str = str(Path(__file__).parent.resolve().absolute().joinpath('./openssl.cnf'))

if 'OPENSSL_CONF' not in os.environ:
    GrindrLogHandler.get_logger().warning(
        f"You MUST pass the OPENSSL_CONF environment variable BEFORE initializing Python, and it must be set to {OPEN_SSL_CONF_PATH}."
        f"If you do not, your ja3 fingerprint WILL be wrong and Cloudflare WILL block you.\n"
        f"This is because we must monkey-patch the openssl configuration in a way that cannot be done in Python due to limited support.\n"
        f"You can also dynamically load this with \"str(Path(importlib.util.find_spec('Grindr').origin).parent.joinpath('./web/tls_patch/openssl.cnf'))\""
    )


class PatchedSSLContext(ssl.SSLContext):

    def set_alpn_protocols(self, alpn_protocols):
        """Disable ALPN protocol (extension 16) by preventing the function from calling the clib"""
        return None


CACHED_CONTEXT: SSLContext | None = None


# Must be indented
def patched_ssl_context(verify_mode: ssl.VerifyMode = ssl.VerifyMode.CERT_REQUIRED) -> SSLContext:
    """
    Patch the SSL Context to override data affecting the ja3 fingerprint.

    JA3 fingerprint is made up of the following:
    tls_version, ciphers, extensions, curves, curve_formats

    Only "curves" is set in patch_open_ssl_config, manually. The others are done here.

    :return: The patched SSL Context object

    """

    global CACHED_CONTEXT

    if CACHED_CONTEXT is not None:
        return CACHED_CONTEXT

    context: PatchedSSLContext = PatchedSSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.verify_mode = verify_mode
    context.check_hostname = True

    if context.verify_mode != ssl.CERT_NONE:
        context.load_default_certs(purpose=ssl.Purpose.SERVER_AUTH)

    if hasattr(context, 'keylog_filename'):
        keylogfile = os.environ.get('SSLKEYLOGFILE')
        if keylogfile and not sys.flags.ignore_environment:
            context.keylog_filename = keylogfile

    # Set the ciphers to EMPTY, because the default behaviour of OpenSSL will be to fall back to the
    # default ciphers in openssl.cnf. If this throws an error that it could not find a cipher name, your openssl.cnf is not loaded
    context.set_ciphers("")

    # Disable/Enable TLS extensions required to match the ja3 fingerprint
    context.check_hostname = False
    context.verify_mode = False

    # Set options (extensions config)
    context.options |= 0x00080000  # SSL_OP_NO_ENCRYPT_THEN MAC
    context.options &= ~0x00004000  # SSL_OP_NO_TICKET (aka 35)
    context.options |= 0x00040000
    context.options |= ssl.OP_ENABLE_KTLS

    CACHED_CONTEXT = context
    assert_ja3_match()
    return context


def assert_ja3_match():
    """Confirm the JA3 matches what it needs to"""

    # Sync check
    response: httpx.Response = httpx.get(
        url="https://localhost:4443/",
        verify=patched_ssl_context()
    )

    ja3_text_blueprint = JA3_BLUEPRINT_JSON['ja3_text']
    ja3_text_measured = response.json()['ja3_text']

    assert ja3_text_blueprint == ja3_text_measured, f"Mismatch in the JA3 Fingerprints:\n- Measured:  {ja3_text_measured}\n- Blueprint: {ja3_text_blueprint}"


def user_agent() -> str:
    """Dynamically retrieve the user agent from the blueprint"""
    return JA3_BLUEPRINT_JSON['user_agent']


__all__ = [
    "patched_ssl_context",
    "assert_ja3_match"
]
