import mimetypes
from collections.abc import Iterator
from datetime import datetime
from typing import Any

import requests
from open_gopro.models import MediaItem
from requests_toolbelt.multipart.encoder import MultipartEncoder

from gopro_immich_uploader.config import ServiceConfig
from gopro_immich_uploader.immich.streaming_iterator_fixed import StreamingIteratorFixed
from gopro_immich_uploader.logger import get_logger

log = get_logger(__name__)


async def upload_file(cfg: ServiceConfig, file: MediaItem, stream: Iterator[bytes], size: int) -> None:
    """Stream-upload a GoPro media file to Immich without storing it locally.

    The data is read progressively from the provided `stream` iterator and sent
    as multipart/form-data using requests_toolbelt's MultipartEncoder.
    """
    device_asset_id = f"-{file.filename}-{file.creation_timestamp}"
    creating_at = str(datetime.fromtimestamp(int(file.creation_timestamp)))
    data_fields = {
        "deviceAssetId": str(device_asset_id),
        "deviceId": "gopro",
        "fileCreatedAt": creating_at,
        "fileModifiedAt": creating_at,
        "isFavorite": "false",
    }

    content_type, _ = mimetypes.guess_type(file.filename)
    if not content_type:
        content_type = "application/octet-stream"

    streaming_file = StreamingIteratorFixed(size, stream)

    # Build the multipart encoder with both text fields and the streaming file
    fields: list[tuple[str, Any]] = list(data_fields.items())
    fields.append(("assetData", (file.filename, streaming_file, content_type)))

    encoder = MultipartEncoder(fields=fields)

    headers = {
        "Accept": "application/json",
        "x-api-key": cfg.immich_api_key,
        "Content-Type": encoder.content_type,
    }

    url = f"{cfg.immich_server_url}/assets"
    response = requests.post(url, headers=headers, data=encoder)
    response.raise_for_status()

    try:
        resp = response.json()
    except Exception as e:
        log.error("Failed to parse response: %s", response.text, exc_info=e)
        raise
    log.warning("Uploaded asset: %s", resp)
