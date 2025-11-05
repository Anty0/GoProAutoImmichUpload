from open_gopro import WirelessGoPro

from gopro_immich_uploader.gopro.ble_controller import BLEController
from gopro_immich_uploader.gopro.streaming_download import StreamingWirelessGoPro
from gopro_immich_uploader.gopro.wifi_controller_stub import WifiControllerStub
from gopro_immich_uploader.logger import get_logger

log = get_logger(__name__)


def ble_camera() -> WirelessGoPro:
    return StreamingWirelessGoPro(
        wifi_adapter=WifiControllerStub,
        ble_adapter=BLEController,
        interfaces={WirelessGoPro.Interface.BLE},
    )


def cohn_camera(identifier: str | None = None) -> WirelessGoPro:
    return StreamingWirelessGoPro(
        wifi_adapter=WifiControllerStub,
        ble_adapter=BLEController,
        interfaces={WirelessGoPro.Interface.COHN},
        target=identifier,
    )
