from pydantic.v1 import Field

from .common import CommonConfig


class ServiceConfig(CommonConfig):
    immich_server_url: str = Field(
        default="http://127.0.0.1:2283/api",
        description="Immich server API URL"
    )
    immich_api_key: str = Field(
        description="Immich API key for authentication"
    )

    identifier: str = Field(
        description="Camera identifier (BLE MAC address or name)"
    )
    cohn_credentials: str = Field(
        description="Base64-encoded COHN credentials from setup"
    )

    delete_after_upload: bool = Field(
        default=False,
        description="Delete media from camera after successful upload"
    )
    scan_interval_sec: int = Field(
        default=30,
        gt=0,
        description="Interval between scans in seconds"
    )
    camera_sleep: bool = Field(
        default=True,
        description="Put camera to sleep after uploading all media"
    )
    min_battery_level: int = Field(
        default=20,
        ge=0,
        le=100,
        description="Minimum battery level percentage to continue operation"
    )
