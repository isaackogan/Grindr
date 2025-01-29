import difflib
import json
import os
from pathlib import Path
from typing import Callable

from curl_cffi import requests
from curl_cffi.requests import AsyncSession, Response, ExtraFingerprints

from Grindr.client.ext.client_logger import GrindrLogHandler

# Load the ja3 blueprint
JA3_BLUEPRINT: dict = (
    json.load(Path(__file__).parent.joinpath('./ja3_blueprint.json').open('r'))
    if 'G_JA3_API_URL' not in os.environ else
    json.load(Path(os.environ['G_JA3_API_URL']).open('r')).json()
)

JA3_BLUEPRINT_CERT_NAMES: list[str] = [suite["name"] for suite in JA3_BLUEPRINT["cipher_suites"]]
JA3_SIGNATURE_ALGORITHMS_EXTENSION: dict = [ext for ext in JA3_BLUEPRINT["extensions"] if ext["name"] == "signature_algorithms"][0]
JA3_SIGNATURE_ALGORITHMS: list[str] = [algo['name'] for algo in JA3_SIGNATURE_ALGORITHMS_EXTENSION['data']['algorithms']]
RED: Callable[[str], str] = lambda text: f"\u001b[31m{text}\033\u001b[0m"
GREEN: Callable[[str], str] = lambda text: f"\u001b[32m{text}\033\u001b[0m"


def has_diff(old: dict, new: dict) -> bool:
    """
    Check if there are differences between two dictionaries.

    Args:
        old (dict): The original dictionary.
        new (dict): The updated dictionary.

    Returns:
        bool: True if there are differences, False otherwise.
    """
    old_json = json.dumps(old, indent=4, sort_keys=True)
    new_json = json.dumps(new, indent=4, sort_keys=True)

    return old_json != new_json


def print_diff(old: dict, new: dict) -> str:
    """Print the diff between"""
    result = ""

    old_str: str = json.dumps(old, indent=4, sort_keys=True)
    new_str: str = json.dumps(new, indent=4, sort_keys=True)

    lines = difflib.ndiff(old_str.splitlines(keepends=True), new_str.splitlines(keepends=True))
    for line in lines:
        line = line.rstrip()
        if line.startswith("+"):
            result += GREEN(line) + "\n"
        elif line.startswith("-"):
            result += RED(line) + "\n"
        elif line.startswith("?"):
            continue
        else:
            result += line + "\n"

    return "JA3 Mismatch!\n\n" + result


def assert_client_ja3(client_kwargs, raise_error: bool = False) -> None:
    """
    Test that the JA3 client matches the blueprint.
    >>> assert_client_ja3(client_kwargs=create_client_kwargs(), raise_error=True)

    """

    # Get the json
    client_kwargs = client_kwargs.copy()
    client_kwargs.pop('proxy')
    response: Response = requests.get(url=os.environ.get('G_JA3_API_URL', "https://tls.browserleaks.com/tls"), **client_kwargs)
    response_json: dict = response.json()

    # Check there's no diff, throw a warning if there is
    try:
        assert not has_diff(JA3_BLUEPRINT, response_json), print_diff(JA3_BLUEPRINT, response_json)
    except AssertionError as ex:
        if raise_error:
            raise
        else:
            GrindrLogHandler.get_logger().warning("TLS Mismatch:", exc_info=True)


def create_client_kwargs(**base_kwargs) -> dict:
    """Create kwargs to feed to the curl cffi client to make the fingerprint (hopefully) match"""

    base_headers: dict = base_kwargs.pop("headers", {})
    base_headers['User-Agent'] = user_agent()

    return {
        **base_kwargs,
        "headers": base_headers,
        "ja3": JA3_BLUEPRINT['ja3_text'],
        "extra_fp": ExtraFingerprints(
            tls_grease="GREASE" in JA3_BLUEPRINT_CERT_NAMES,
            tls_signature_algorithms=JA3_SIGNATURE_ALGORITHMS
        )
    }


def create_async_client(**extra_kwargs) -> AsyncSession:
    """Create the async client"""

    # Create the kwargs
    client_kwargs: dict = create_client_kwargs(**extra_kwargs)

    # Check that the kwargs match the required
    assert_client_ja3(client_kwargs)

    # Generate a session
    return AsyncSession(**client_kwargs)


def user_agent() -> str:
    """TLS User Agent"""

    return JA3_BLUEPRINT['user_agent']
