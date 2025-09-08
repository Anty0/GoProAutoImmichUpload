from open_gopro import WirelessGoPro
from open_gopro.models.general import CohnInfo
from open_gopro.models.proto import EnumCOHNNetworkState

from gopro_immich_uploader.config import Config
from gopro_immich_uploader.gopro.streamin_download import StreamingWirelessGoPro
from gopro_immich_uploader.logger import get_logger

log = get_logger(__name__)


def ble_camera(cfg: Config) -> WirelessGoPro:
    return StreamingWirelessGoPro(
        interfaces={WirelessGoPro.Interface.BLE},
    )


def cohn_camera(cfg: Config, identifier: str = None) -> WirelessGoPro:
    return StreamingWirelessGoPro(
        interfaces={WirelessGoPro.Interface.COHN},
        target=identifier,
    )


async def provision_cohn(cfg: Config, camera: WirelessGoPro) -> None:
    status = camera.cohn.status
    connected = status.state == EnumCOHNNetworkState.COHN_STATE_NetworkConnected
    correct_ssid = status.ssid == cfg.wifi_ssid
    if not connected or not correct_ssid:
        await camera.access_point.connect(cfg.wifi_ssid, cfg.wifi_password)

    if await camera.cohn.is_configured:
        log.info("COHN is already configured")
        return

    try:
        log.info("Checking for existing COHN certificate")
        cert = (await camera.ble_command.cohn_get_certificate()).data.cert
        credentials = CohnInfo(
            ip_address=status.ipaddress,
            username=status.username,
            password=status.password,
            certificate=cert,
        )
        camera.cohn.credentials = credentials
        log.info("Successfully retrieved existing certificate")
    except Exception as e:
        log.error("COHN get existing certificate failed: %s", e)

        log.info("Initiating full COHN onboarding")
        await camera.cohn.configure()
