from functools import partial

from open_gopro import WirelessGoPro
from open_gopro.models.general import CohnInfo
from open_gopro.models.proto import EnumCOHNNetworkState

from gopro_immich_uploader.config import SetupConfig
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


def cohn_camera(identifier: str = None) -> WirelessGoPro:
    return StreamingWirelessGoPro(
        wifi_adapter=WifiControllerStub,
        ble_adapter=BLEController,
        interfaces={WirelessGoPro.Interface.COHN},
        target=identifier,
    )


async def provision_cohn(cfg: SetupConfig, camera: WirelessGoPro) -> None:
    status = camera.cohn.status
    connected = status.state == EnumCOHNNetworkState.COHN_STATE_NetworkConnected
    correct_ssid = status.ssid == cfg.wifi_ssid

    log.warning("Connecting to COHN; SSID: %s, Connected: %s, Correct SSID: %s", status.ssid, connected, cfg.wifi_ssid)
    log.warning("Password: %s", cfg.wifi_password)
    if not connected or not correct_ssid:
        await camera.access_point.connect(cfg.wifi_ssid, cfg.wifi_password)

    if await camera.cohn.is_configured:
        log.warning("COHN is already configured")
        return

    try:
        log.warning("Checking for existing COHN certificate")
        cert = (await camera.ble_command.cohn_get_certificate()).data.cert
        credentials = CohnInfo(
            ip_address=status.ipaddress,
            username=status.username,
            password=status.password,
            certificate=cert,
        )
        camera.cohn.credentials = credentials
        log.warning("Successfully retrieved existing certificate")
    except Exception as e:
        log.error("COHN get existing certificate failed: %s", e, exc_info=e)

        log.warning("Initiating full COHN onboarding")
        await camera.cohn.configure()
