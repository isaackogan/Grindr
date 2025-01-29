import os
import random
from typing import Union

from curl_cffi import requests

from Grindr.web.tls_match import tls_match

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

GRINDR_PUBLIC_V1: str = GRINDR_BASE + "/public/v1"
GRINDR_PUBLIC_V2: str = GRINDR_BASE + "/public/v2"

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

DEVICE_SCREEN_DIMENSIONS: list[str] = [
    "1080x2400",  # Galaxy S21
    "1644x3840",  # Xperia 1 III
    "1440x3200",  # Mi 11
    "1080x2400",  # OnePlus 9
    "1080x2400",  # Nokia 8.3
    "1080x2300",  # Moto G Power
    "1200x2640",  # P40 Pro
    "1440x3216",  # Find X3
    "2460x1080",  # V60 ThinQ
    "1080x2400",  # Redmi Note 10
    "1080x2400",  # Reno 6
    "1080x2340",  # Pixel 5
    "1440x3088",  # Galaxy Note 20
    "1080x2448",  # ROG Phone 5
    "1344x2772",  # Magic 3
]

DESKTOP_USER_AGENTS: list[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:114.0) Gecko/20100101 Firefox/114.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:113.0) Gecko/20100101 Firefox/113.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.2 Safari/605.1.15"
]

ANDROID_VERSION_API_LEVEL_MAP: dict[int, list[int]] = {
    15: [35],  # Android 15
    14: [34],  # Android 14
    13: [33],  # Android 13
    12: [31, 32],  # Android 12 (API levels 31 and 32)
    11: [30],  # Android 11
    10: [29],  # Android 10
    9: [28],  # Android 9
    8: [26, 27],  # Android 8 (API levels 26 and 27)
    7: [25],  # Android 7
}


def get_desktop_user_agent() -> str:
    """
    Get a random desktop user agent string.

    Returns:
        str: A random desktop user agent string.
    """
    return random.choice(DESKTOP_USER_AGENTS)


def get_mobile_user_agent() -> str:
    """Generate user agent"""

    device, manufacturer = random.choice(DEVICE_MANUFACTURER_LIST)
    user_agent = f"grindr3/{LATEST_APP}.{BUILD_NUMBER};{BUILD_NUMBER};Free;Android {random.randint(12, 14)};{device};{manufacturer}"
    return user_agent
