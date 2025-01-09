import json
import os
import re
import ssl
import sys
from pathlib import Path
from ssl import SSLContext

import httpx
from packaging.version import Version

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

CURRENT_OPEN_SSL_VERSION: str = ssl.OPENSSL_VERSION.split(' ')[1]

if Version(CURRENT_OPEN_SSL_VERSION) < Version("3.4.0"):
    GrindrLogHandler.get_logger().warning(
        f"Your OpenSSL version is {CURRENT_OPEN_SSL_VERSION}, which is less than 3.4.0. "
        f"Please upgrade to 3.4.0 or higher to ensure the best compatibility with the Grindr client. You may run into SSL cipher issues."
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

    context: PatchedSSLContext = PatchedSSLContext(ssl.PROTOCOL_TLS)
    context.verify_mode = verify_mode
    context.check_hostname = True

    if context.verify_mode != ssl.CERT_NONE:
        context.load_default_certs(purpose=ssl.Purpose.SERVER_AUTH)

    if hasattr(context, 'keylog_filename'):
        keylogfile = os.environ.get('SSLKEYLOGFILE')
        if keylogfile and not sys.flags.ignore_environment:
            context.keylog_filename = keylogfile

    # Set the ciphers to JUST TLS_AES_128_GCM_SHA256. That is the *actual* cipher_suite in the tls.browserleaks.com/tls dump.
    # Then for other *preferred* cipher options, the default behaviour of OpenSSL will be to fall back to the
    # default ciphers in openssl.cnf. If this throws an error that it could not find a cipher name, your openssl.cnf is not loaded
    # context.set_ciphers("TLS_AES_128_GCM_SHA256")

    # Min version MUST be 1.2, max version MUST be 1.3. Because the set of ciphers is a COMBINATION of 1.2 and 1.3 ciphers.
    # context.minimum_version = ssl.TLSVersion.TLSv1_2
    # context.maximum_version = ssl.TLSVersion.TLSv1_3
    context.set_ciphers("TLS_FALLBACK_SCSV")

    # Disable/Enable TLS extensions required to match the ja3 fingerprint
    context.check_hostname = False
    context.verify_mode = False

    # |= <- Turns ON
    # &= ~ <- Turns OFF

    # Set options (extensions config)
    context.options |= 0x00080000  # SSL_OP_NO_ENCRYPT_THEN MAC
    context.options &= ~0x00004000  # SSL_OP_NO_TICKET (aka 35)
    context.options |= 0x00040000
    context.options |= ssl.OP_ENABLE_KTLS

    CACHED_CONTEXT = context
    assert_ja3_match()
    return context


def print_difference(measured, blueprint, label: str) -> str:
    items_measured = measured.split('-')
    items_blueprint = blueprint.split('-')

    # Extra items in measured
    extra_items = set(items_measured) - set(items_blueprint)

    # Missing items in measured
    missing_items = set(items_blueprint) - set(items_measured)

    # Check if it's a difference in orders
    if len(extra_items) == 0 and len(missing_items) == 0:
        return f"Mismatch in the JA3 Fingerprint Order {label}:\n- Measured: {measured}\n- Blueprint: {blueprint}"

    # Print the diffmerge
    return (
            f"Mismatch in the JA3 Fingerprint >>{label}<<:\n" +
            (f"-" * 50 + "Raw" + "-" * 50) +
            f"\n- Measured: {measured}" +
            f"\n- Blueprint: {blueprint}\n" +
            (f"-" * 50 + "Int" + "-" * 50) +
            f"\n- Missing Items ({len(missing_items)}): {sorted(missing_items)}" +
            f"\n- Extra Items ({len(extra_items)}): {sorted(extra_items)}\n" +
            (f"-" * 50 + "Hex" + "-" * 50) +
            f"\n- Missing Items ({len(missing_items)}): {sorted([hex(int(item)) for item in missing_items])}" +
            f"\n- Extra Items ({len(extra_items)}): {sorted(extra_items)}\n"
    )


def assert_ja3_match():
    """Confirm the JA3 matches what it needs to"""

    # Sync check
    response: httpx.Response = httpx.get(
        url="https://tls.browserleaks.com/tls",
        verify=patched_ssl_context()
    )

    ja3_text_blueprint = JA3_BLUEPRINT_JSON['ja3_text']
    ja3_text_measured = response.json()['ja3_text']

    # Split the JA3 fingerprint into its components
    tls_version_sample, ciphers_sample, extensions_sample, curves_sample, curve_formats_sample = ja3_text_measured.split(',')

    # Confirm the JA3 fingerprint matches the blueprint
    tls_version_blueprint, ciphers_blueprint, extensions_blueprint, curves_blueprint, curve_formats_blueprint = ja3_text_blueprint.split(',')

    # We must REMOVE the TLS_EMPTY_RENEGOTIATION_INFO_SCSV from the blueprint & renegotiation_info from the sample
    # This is because it is an unchangeable attribute that was replaced by OpenSSL in April 2022
    # See https://github.com/openssl/openssl/discussions/26349 for me breaking down over this
    # Also, different users may have different OpenSSL's so handle both conditions
    ciphers_blueprint = re.sub(r'-?255-?', '', ciphers_blueprint)
    ciphers_sample = re.sub(r'-?255-?', '', ciphers_sample)
    extensions_sample = re.sub(r'-?65281-?', '', extensions_sample)
    extensions_blueprint = re.sub(r'-?65281-?', '', extensions_blueprint)

    assert tls_version_blueprint == tls_version_sample, print_difference(tls_version_sample, tls_version_blueprint, "TLS Version")
    assert ciphers_blueprint == ciphers_sample, print_difference(ciphers_sample, ciphers_blueprint, "Ciphers")
    assert extensions_blueprint == extensions_sample, print_difference(extensions_sample, extensions_blueprint, "Extensions")
    assert curves_blueprint == curves_sample, print_difference(curves_sample, curves_blueprint, "Curves")
    assert curve_formats_blueprint == curve_formats_sample, print_difference(curve_formats_sample, curve_formats_blueprint, "Curve Formats")


def user_agent() -> str:
    """Dynamically retrieve the user agent from the blueprint"""
    return JA3_BLUEPRINT_JSON['user_agent']


__all__ = [
    "patched_ssl_context",
    "assert_ja3_match"
]
