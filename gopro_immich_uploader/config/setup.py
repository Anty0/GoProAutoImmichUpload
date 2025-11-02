from typing import Optional

from pydantic.v1 import Field

from .common import CommonConfig


class SetupConfig(CommonConfig):
    wifi_ssid: str = Field(
        description="WiFi SSID for camera connection"
    )
    wifi_password: str = Field(
        description="WiFi password for camera connection"
    )

    identifier: Optional[str] = Field(
        default=None,
        description="Camera identifier (optional - for targeting specific camera)"
    )

    no_pair: bool = Field(
        default=False,
        description="Disable Bluetooth pairing during setup"
    )
