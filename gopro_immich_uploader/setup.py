from gopro_immich_uploader.config import SetupConfig
from gopro_immich_uploader.gopro import ble_camera, provision_cohn, BLEController
from gopro_immich_uploader.logger import get_logger
from gopro_immich_uploader.tinydb.storage import GlobalMemoryStorage

log = get_logger(__name__)


async def setup(cfg: SetupConfig) -> None:
    log.warning("Searching for camera")

    try:
        BLEController.set_enable_pairing(not cfg.no_pair)
        async with ble_camera() as camera_ble:
            log.warning("Found BLE camera: %s", camera_ble)

            await camera_ble.ble_command.cohn_clear_certificate()
            await camera_ble.access_point.connect(cfg.wifi_ssid, cfg.wifi_password)
            await camera_ble.cohn.configure()

            # Serialize COHN credentials
            credentials = GlobalMemoryStorage.serialize()

            log.warning("Setup complete!")
            print("Set the following environment variables for the service mode:")
            print(f"IDENTIFIER={camera_ble.identifier}")
            print(f"COHN_CREDENTIALS={credentials}")

    except Exception as e:
        log.exception("Error during camera setup: %s", e, exc_info=e)
        raise
