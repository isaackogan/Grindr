import os
import random
from typing import Union

from curl_cffi import requests

from Grindr.client.tls_match import tls_match

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

DEFAULT_REQUEST_PARAMS: dict[str, Union[int, bool, str]] = {}

# Not validated, but if they start validating it, it becomes a bit more of a pain
BUILD_NUMBER: str = "132462"

LATEST_APP: str = (
    requests.get("https://itunes.apple.com/lookup?id=319881193").json()["results"][0]["version"]
    if os.environ.get('USE_LATEST_VERSION') else "24.19.0"
)

DEFAULT_REQUEST_HEADERS: dict[str, str] = {
    "requireRealDeviceInfo": "true",
    "L-Time-Zone": "America/Toronto",
    "L-Grindr-Roles": "[]",
    "L-Device-Info": "",  # Supplied by the web client
    "Accept": "application/json",
    "User-Agent": tls_match.user_agent().replace("24.19.0", LATEST_APP).replace("132462", BUILD_NUMBER),
    "L-Locale": "en_US",
    "Accept-language": "en-US",
    "Content-Type": "application/json; charset=UTF-8",
    "Host": GRINDR_HOST,
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip",
}

DEVICE_MANUFACTURER_LIST: list[tuple[str, str]] = [
    ("Galaxy S21", "Samsung"),
    ("Xperia 1 III", "Sony"),
    ("Mi 11", "Xiaomi"),
    ("OnePlus 9", "OnePlus"),
    ("Nokia 8.3", "Nokia"),
    ("Moto G Power", "Motorola"),
    ("P40 Pro", "Huawei"),
    ("Find X3", "Oppo"),
    ("V60 ThinQ", "LG"),
    ("Redmi Note 10", "Xiaomi"),
    ("Reno 6", "Oppo"),
    ("Pixel 5", "Google"),
    ("Galaxy Note 20", "Samsung"),
    ("ROG Phone 5", "Asus"),
    ("Magic 3", "Honor"),
]


def generate_user_agent() -> str:
    """Generate user agent"""

    device, manufacturer = random.choice(DEVICE_MANUFACTURER_LIST)
    user_agent = f"grindr3/{LATEST_APP}.{BUILD_NUMBER};{BUILD_NUMBER};Free;Android {random.randint(12, 14)};{device};{manufacturer}"
    return user_agent
