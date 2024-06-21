from typing import Dict, Union

GRINDR_BASE: str = "https://grindr.mobi"
GRINDR_WS: str = "wss://grindr.mobi/v1/ws"

GRINDR_V1: str = GRINDR_BASE + "/v1"
GRINDR_V2: str = GRINDR_BASE + "/v2"
GRINDR_V3: str = GRINDR_BASE + "/v3"
GRINDR_V4: str = GRINDR_BASE + "/v4"
GRINDR_V5: str = GRINDR_BASE + "/v5"
GRINDR_V6: str = GRINDR_BASE + "/v6"

DEFAULT_REQUEST_PARAMS: Dict[str, Union[int, bool, str]] = {}

DEFAULT_REQUEST_HEADERS: Dict[str, str] = {
    "requireRealDeviceInfo": "true",
    "L-Time-Zone": "America/Toronto",
    "L-Device-Info": "dd0703f136406de3;GLOBAL;2;3109244928;2891x1440;d6fcd76c-a0e4-4a99-97a9-29b109bc1042",
    "Accept": "application/json",
    "User-Agent": "grindr3/24.2.2.122427;122427;Free;Android 13;sdk_gphone64_arm64;Google",
    "L-Locale": "en_US",
    "Accept-language": "en-US",
    "Content-Type": "application/json; charset=UTF-8",
    "Host": "grindr.mobi",
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip"
}
