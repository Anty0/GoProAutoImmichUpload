from typing import Iterator, Callable, Coroutine

from open_gopro import WirelessGoPro
from open_gopro.models import MediaItem

from gopro_immich_uploader.config import Config
from gopro_immich_uploader.logger import get_logger

log = get_logger(__name__)


async def download_files(
        cfg: Config,
        camera: WirelessGoPro,
        handle_file: Callable[[MediaItem, Iterator[bytes]],
        Coroutine[None, None, None]]
) -> tuple[int, int]:
    total_count = 0
    error_count = 0

    try:
        await camera.http_command.set_turbo_mode(True)

        files = (await camera.http_command.get_media_list()).data.files
        total_count = len(files)

        for file in files:
            async def stream_callback(stream: Iterator[bytes]):
                nonlocal error_count
                try:
                    await handle_file(file, stream)
                except Exception as e:
                    error_count += 1
                    log.error(f"Error handling file {file.filename}: {e}")

            await camera.http_command.download_file(camera_file=file.filename, stream_callback=stream_callback)
    finally:
        await camera.http_command.set_turbo_mode(False)

    return total_count - error_count, error_count
