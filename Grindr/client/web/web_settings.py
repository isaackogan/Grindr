import os
from typing import Dict, Union

import httpx

GRINDR_HOST: str = os.getenv("GRINDR_HOST", "grindr.mobi")
GRINDR_BASE: str = os.getenv("GRINDR_API_BASE", f"https://{GRINDR_HOST}")
GRINDR_WS: str = os.getenv("GRINDR_API_WS", f"wss://{GRINDR_HOST}/v1/ws")

GRINDR_V1: str = GRINDR_BASE + "/v1"
GRINDR_V2: str = GRINDR_BASE + "/v2"
GRINDR_V3: str = GRINDR_BASE + "/v3"
GRINDR_V3_1: str = GRINDR_BASE + "/v3.1"
GRINDR_V4: str = GRINDR_BASE + "/v4"
GRINDR_V5: str = GRINDR_BASE + "/v5"
GRINDR_V6: str = GRINDR_BASE + "/v6"

DEFAULT_REQUEST_PARAMS: Dict[str, Union[int, bool, str]] = {}

# Not validated, but if they start validating it, it becomes a bit more of a pain
BUILD_NUMBER: str = "57276.231185624.99"

LATEST_APP: str = (
    httpx.get("https://itunes.apple.com/lookup?id=319881193").json()["results"][0]["version"]
    if os.environ.get('USE_LATEST_VERSION') else "24.19.0"
)

DEFAULT_REQUEST_HEADERS: Dict[str, str] = {
    "requireRealDeviceInfo": "true",
    "L-Time-Zone": "America/Toronto",
    "L-Grindr-Roles": "[]",
    "L-Device-Info": "",  # Supplied by the web client
    "Accept": "application/json",
    "User-Agent": f"Grindr3/{LATEST_APP}.{BUILD_NUMBER} ({BUILD_NUMBER}; iPhone10,3; iOS 16.6.1)",
    "L-Locale": "en_US",
    "Accept-language": "en-US",
    "Content-Type": "application/json; charset=UTF-8",
    "Host": GRINDR_HOST,
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip",
}
