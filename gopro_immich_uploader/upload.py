from collections.abc import Iterator

from open_gopro import WirelessGoPro
from open_gopro.models import MediaItem

from gopro_immich_uploader.config import ServiceConfig
from gopro_immich_uploader.gopro import download_files
from gopro_immich_uploader.immich import upload_file
from gopro_immich_uploader.logger import get_logger

log = get_logger(__name__)


async def upload_media(cfg: ServiceConfig, camera: WirelessGoPro) -> tuple[int, int]:
    async def handle_file(file: MediaItem, stream: Iterator[bytes], size: int) -> None:
        await upload_file(cfg, file, stream, size)

    return await download_files(cfg, camera, handle_file)
