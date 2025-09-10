import asyncio
import threading

from open_gopro import WirelessGoPro
from open_gopro.models.constants import StatusId

from gopro_immich_uploader.exit_handler import should_exit, on_exit
from gopro_immich_uploader.gopro.ble_controller_no_pair import DeviceNotPoweredOn
from gopro_immich_uploader.logger import get_logger
from gopro_immich_uploader.config import Config
from gopro_immich_uploader.gopro import ble_camera, provision_cohn, cohn_camera
from gopro_immich_uploader.upload import upload_media

log = get_logger(__name__)


async def loop_main(cfg: Config) -> None:
    log.info("Starting main loop (scan interval: %ss)", cfg.scan_interval_sec)
    while not should_exit():
        try:
            async with ble_camera(cfg) as camera_ble:
                log.info("Found BLE camera: %s", camera_ble)

                status = await camera_ble.ble_command.get_camera_statuses()
                battery_level = int(status.data[StatusId.INTERNAL_BATTERY_PERCENTAGE])
                log.info("Battery level: %d%%", battery_level)
                if battery_level < cfg.min_battery_level:
                    log.info("Battery level below threshold, exiting")
                    break

                await provision_cohn(cfg, camera_ble)
                identifier = camera_ble.identifier

                async with cohn_camera(cfg, identifier=identifier) as camera_cohn:
                    log.info("Connected to camera over COHN: %s", camera_cohn)
                    success_count, failed_count = await upload_media(cfg, camera_cohn)
                    log.info("Uploads complete: %d success, %d failed", success_count, failed_count)

                if cfg.camera_power_off and failed_count == 0:
                    await camera_ble.ble_command.power_down()
        except DeviceNotPoweredOn:
            log.info("Found camera is powered off, ignoring")
        except Exception as e:
            log.exception("Error in main loop: %s", e)
        finally:
            if should_exit():
                break
            await asyncio.sleep(cfg.scan_interval_sec)
