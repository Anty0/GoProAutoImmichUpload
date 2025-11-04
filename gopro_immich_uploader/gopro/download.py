import asyncio
from typing import Iterator, Callable, Coroutine

from open_gopro import WirelessGoPro
from open_gopro.models import MediaItem
from open_gopro.models.constants import Toggle

from gopro_immich_uploader.exit_handler import should_exit
from gopro_immich_uploader.config import ServiceConfig
from gopro_immich_uploader.logger import get_logger
from gopro_immich_uploader.progress_reporting_iterator import ProgressReportingIterator

log = get_logger(__name__)


async def try_delete_file(camera: WirelessGoPro, file: MediaItem) -> bool:
    try:
        response = await camera.http_command.delete_file(path=file.filename)
        if response.ok:
            return True
        log.warning("Delete for %s failed", file.filename)
    except Exception as e:
        log.exception(f"Delete for %s threw exception: %s", file.filename, e, exc_info=e)
    return False

async def check_media_list(camera: WirelessGoPro, file: MediaItem):
    files = (await camera.http_command.get_media_list()).data.files
    found_file = file.filename in [f.filename for f in files]
    if not found_file:
        log.warning("File %s no longer found in media list", file.filename)
    else:
        log.warning("File %s still found in media list", file.filename)


async def delete_file(camera: WirelessGoPro, file: MediaItem):
    # Give time for the camera to realize the file is no longer in use,
    # no idea if it really helps
    await asyncio.sleep(1)
    if await try_delete_file(camera, file):
        return

    # We probably got a 400: Requested delete path was not found in the media list.
    # This should not happen, yet it happens regularly...
    # Let's try to fetch the media list again, maybe that will fix it
    await asyncio.sleep(1)
    log.warning("Retry delete for %s: Fetch media list before delete", file.filename)
    await check_media_list(camera, file)
    if await try_delete_file(camera, file):
        return

    try:
        # Still nothing? Fuggin GoPro...
        # Try one more time with turbo mode disabled
        log.warning("Retry delete for %s: Without turbo mode", file.filename)
        await camera.http_command.set_turbo_mode(mode=Toggle.DISABLE)
        await asyncio.sleep(1)
        if await try_delete_file(camera, file):
            return
    finally:
        await camera.http_command.set_turbo_mode(mode=Toggle.ENABLE)

    # Last try before we give up
    # Maybe rebooting the camera will help?
    log.warning("Retry delete for %s: Rebooting camera", file.filename)
    try:
        await camera.http_command.reboot()
        await asyncio.sleep(30)  # Give the camera time to reboot and reconnect (I hope this works)
        if await try_delete_file(camera, file):
            return

        # Maybe media again?
        log.warning("Retry delete for %s: Rebooting camera: Fetch media list before delete", file.filename)
        await check_media_list(camera, file)
        if await try_delete_file(camera, file):
            return
    finally:
        # Re-enable turbo mode after rebooting
        await camera.http_command.set_turbo_mode(mode=Toggle.ENABLE)

    log.error("Delete for %s failed: I give up, delete the file manually", file.filename)


async def download_files(
        cfg: ServiceConfig,
        camera: WirelessGoPro,
        handle_file: Callable[
            [MediaItem, Iterator[bytes], int],
            Coroutine[None, None, None]
        ]
) -> tuple[int, int]:
    try:
        done_count = 0
        await camera.http_command.set_turbo_mode(mode=Toggle.ENABLE)

        files = (await camera.http_command.get_media_list()).data.files
        total_count = len(files)

        for file in files:
            if should_exit():
                break

            async def stream_callback(stream: Iterator[bytes], size: int):
                progress_stream = ProgressReportingIterator(file.filename, stream, size)
                await handle_file(file, progress_stream, size)

            try:
                # Lil hack here - we abuse the local_file arg to pass the callback instead
                # this callback will get picked up by the GoProStreamingDownloadMixin
                # noinspection PyTypeChecker
                await camera.http_command.download_file(camera_file=file.filename, local_file=stream_callback)

                if cfg.delete_after_upload:
                    await delete_file(camera, file)

                done_count += 1
            except Exception as e:
                log.error(f"Error handling file {file.filename}: {e}")

        return done_count, total_count - done_count
    finally:
        await camera.http_command.set_turbo_mode(mode=Toggle.DISABLE)
