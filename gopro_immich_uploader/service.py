import asyncio

from open_gopro import WirelessGoPro
from open_gopro.domain.communicator_interface import HttpMessage, MessageRules
from open_gopro.models.constants import StatusId, Toggle
from requests import ConnectTimeout

from gopro_immich_uploader.exit_handler import should_exit
from gopro_immich_uploader.logger import get_logger
from gopro_immich_uploader.config import ServiceConfig
from gopro_immich_uploader.gopro import cohn_camera
from gopro_immich_uploader.tinydb import GlobalMemoryStorage
from gopro_immich_uploader.upload import upload_media

log = get_logger(__name__)


async def service(cfg: ServiceConfig) -> None:
    if not cfg.cohn_credentials:
        log.error("No COHN credentials provided.")
        return
    GlobalMemoryStorage.restore(cfg.cohn_credentials)

    log.warning("GoPro Immich Uploader")
    log.debug("Using config: %s", cfg)
    await loop_main(cfg)


async def loop_main(cfg: ServiceConfig) -> None:
    log.warning("Starting main loop (scan interval: %ss)", cfg.scan_interval_sec)

    while not should_exit():
        try:
            async with cohn_camera(identifier=cfg.identifier) as camera_cohn:
                await test_connection(camera_cohn)

                log.warning("Connected to camera over COHN: %s", camera_cohn)

                # Make sure the camera is not in turbo mode
                await camera_cohn.http_command.set_turbo_mode(mode=Toggle.DISABLE)

                await check_battery_level(cfg, camera_cohn)

                success_count, failed_count = await upload_media(cfg, camera_cohn)
                log.warning("Uploads complete: %d success, %d failed", success_count, failed_count)

                if cfg.camera_sleep and failed_count == 0:
                    await camera_sleep(camera_cohn)
        except InitialConnectionFailed:
            continue
        except LowBatteryError:
            continue
        except Exception as e:
            log.exception("Error in main loop: %s", e, exc_info=e)
        finally:
            if should_exit():
                break
            log.info("Waiting %ss before next scan", cfg.scan_interval_sec)
            await asyncio.sleep(cfg.scan_interval_sec)


async def test_connection(camera: WirelessGoPro) -> None:
    try:
        response = await camera.http_command.set_keep_alive()
    except ConnectTimeout as e:
        raise InitialConnectionFailed() from e
    if not response.ok:
        raise InitialConnectionFailed()


async def camera_sleep(camera_cohn: WirelessGoPro) -> None:
    """
    Sends a command to a GoPro camera to put it into sleep mode.

    This endpoint is undocumented and is missing from the ` WirelessGoPro.http_command ` interface,
    so we use the low-level `_get_json` method to invoke it directly.
    """
    message = HttpMessage(endpoint="gp/gpControl/command/system/sleep", identifier=None)
    await camera_cohn._get_json(message, rules=MessageRules(fastpass_analyzer=MessageRules.always_true))


async def check_battery_level(cfg: ServiceConfig, camera_cohn: WirelessGoPro) -> None:
    status = await camera_cohn.http_command.get_camera_state()
    battery_level = int(status.data[StatusId.INTERNAL_BATTERY_PERCENTAGE])
    log.warning("Battery level: %d%%", battery_level)

    if battery_level < cfg.min_battery_level:
        log.warning("Battery level below threshold (%d%% < %d%%), exiting", battery_level, cfg.min_battery_level)
        raise LowBatteryError()


class LowBatteryError(Exception):
    pass


class InitialConnectionFailed(Exception):
    pass
