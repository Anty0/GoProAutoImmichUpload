import urllib.parse
from typing import Iterator, Callable, Coroutine

from open_gopro import WirelessGoPro
from open_gopro.models import MediaItem
from open_gopro.models.constants import Toggle

from gopro_immich_uploader.exit_handler import should_exit
from gopro_immich_uploader.config import Config
from gopro_immich_uploader.logger import get_logger
from gopro_immich_uploader.progress_reporting_iterator import ProgressReportingIterator

log = get_logger(__name__)


async def download_files(
        cfg: Config,
        camera: WirelessGoPro,
        handle_file: Callable[
            [MediaItem, Iterator[bytes], int],
            Coroutine[None, None, None]
        ]
) -> tuple[int, int]:
    total_count = -1
    done_count = 0

    try:
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
                    await camera.http_command.delete_file(path=file.filename)

                done_count += 1
            except Exception as e:
                log.error(f"Error handling file {file.filename}: {e}")

        return done_count, total_count - done_count
    finally:
        await camera.http_command.set_turbo_mode(mode=Toggle.DISABLE)
