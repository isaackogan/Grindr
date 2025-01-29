import random
import time
import uuid

from Grindr.web.web_settings import ANDROID_VERSION_API_LEVEL_MAP, DEVICE_SCREEN_DIMENSIONS


def android_api_level(
        mobile_user_agent: str
) -> list[int]:
    """Get the Android API Level from a UA string"""
    app_version, build, free, android_version, device, manufacturer = mobile_user_agent.split(";")
    return ANDROID_VERSION_API_LEVEL_MAP[int(android_version.split(" ")[1])]


def generate_device_info_android(
        android_device_id: str | None = None,
) -> str:
    android_advertising_id: str = str(uuid.uuid4())  # Not validated

    # How much memory does the phone have, in bytes. Should be some multiple of 1024 (i.e. Some # of megabytes summing to some # of gigabytes)
    memory_on_phone: int = (
            random.randint(2800, 3600)  # Mb
            * 1024  # Kb
            * 1024  # Bytes
    )

    # The value "2" represents the follow code from the Grindr APK: "x86".equals(Build.CPU_ABI) ? 1 : 2
    # The value "GLOBAL" is statically set in the APK. No clue what it does.
    return f"{android_device_id or f'{random.getrandbits(64):016x}'};GLOBAL;2;{memory_on_phone};{random.choice(DEVICE_SCREEN_DIMENSIONS)};{android_advertising_id}"


def generate_device_info_ios() -> str:
    """iOS device info generator"""

    return f"{str(uuid.uuid4()).upper()};appStore;2;2107621376;1334x750"


def generate_ios_token() -> str:
    """On IOS, the "token attribute is the current timestamp since there's no Firebase"""
    return f"{time.time() * 1000:.3f}"