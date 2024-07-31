from typing import Dict, Union

GRINDR_BASE: str = "https://grindr.mobi"
GRINDR_WS: str = "wss://grindr.mobi/v1/ws"

GRINDR_V1: str = GRINDR_BASE + "/v1"
GRINDR_V2: str = GRINDR_BASE + "/v2"
GRINDR_V3: str = GRINDR_BASE + "/v3"
GRINDR_V3_1: str = GRINDR_BASE + "/v3.1"
GRINDR_V4: str = GRINDR_BASE + "/v4"
GRINDR_V5: str = GRINDR_BASE + "/v5"
GRINDR_V6: str = GRINDR_BASE + "/v6"

DEFAULT_REQUEST_PARAMS: Dict[str, Union[int, bool, str]] = {}

DEFAULT_REQUEST_HEADERS: Dict[str, str] = {
    "requireRealDeviceInfo": "true",
    "L-Time-Zone": "America/Toronto",
    "L-Grindr-Roles": "[]",
    "L-Device-Info": "",
    "Accept": "application/json",
    "User-Agent": "Grindr3/24.8.0.55320.047817240.99 (55320.047817240.99; iPhone8,1; iOS 15.8.2)",
    "L-Locale": "en_US",
    "Accept-language": "en-US",
    "Content-Type": "application/json; charset=UTF-8",
    "Host": "grindr.mobi",
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip",
}
