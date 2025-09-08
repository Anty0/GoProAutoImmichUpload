import logging
import environ


@environ.config(prefix="")
class Config:
    immich_server_url: str = environ.var(default="http://127.0.0.1:2283/api")
    immich_api_key: str = environ.var()

    wifi_ssid: str = environ.var()
    wifi_password: str = environ.var()

    delete_after_upload: bool = environ.bool_var(default=False)
    scan_interval_sec: int = environ.var(
        default=30,
        converter=int,
        validator=lambda v: v > 0,
    )
    camera_power_off: bool = environ.bool_var(default=False)

    log_level: int = environ.var(
        default="INFO",
        converter=lambda v: logging.getLevelNamesMapping()[v.strip().upper()],
    )


def load_config() -> Config:
    return environ.to_config(Config)
