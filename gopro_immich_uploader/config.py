import logging
import environ


@environ.config(prefix="")
class Config:
    # Based on README
    immich_server_url: str = environ.var(default="http://127.0.0.1:2283/api")
    immich_api_key: str = environ.var()

    wifi_ssid: str = environ.var()
    wifi_password: str = environ.var()

    delete_after_upload: bool = environ.bool_var(default=False)
    scan_interval_sec: int = environ.int_var(default=30)
    camera_power_off: bool = environ.bool_var(default=False)

    log_level: int = environ.var(
        default="INFO",
        converter=lambda v: logging.getLevelNamesMapping()[v.strip().upper()],
    )


def _validate(cfg: Config) -> None:
    # Required: api key
    if not cfg.immich_api_key or cfg.immich_api_key.strip() == "":
        raise environ.MissingEnvValueError("IMMICH_API_KEY")

    # Required: wifi ssid and password
    if not cfg.wifi_ssid or cfg.wifi_ssid.strip() == "":
        raise environ.MissingEnvValueError("WIFI_SSID")
    if not cfg.wifi_password or cfg.wifi_password.strip() == "":
        raise environ.MissingEnvValueError("WIFI_PASSWORD")

    # Minimal sanity checks
    if not isinstance(cfg.scan_interval_sec, int) or cfg.scan_interval_sec <= 0:
        raise ValueError("SCAN_INTERVAL_SEC must be an integer > 0")


def load_config() -> Config:
    cfg = environ.to_config(Config)
    _validate(cfg)
    return cfg
