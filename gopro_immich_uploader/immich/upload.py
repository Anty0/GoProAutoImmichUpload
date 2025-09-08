# This file is just an example how to upload to immich
# We need to reimplement this properly to allow streaming the file directly from the camera to the immich
# probably using the requests_toolbelt library
from typing import Iterator

import requests

from open_gopro.models import MediaItem

from gopro_immich_uploader.config import Config
from gopro_immich_uploader.logger import get_logger

log = get_logger(__name__)


async def upload_file(cfg: Config, file: MediaItem, stream: Iterator[bytes]):
    headers = {
        'Accept': 'application/json',
        'x-api-key': cfg.immich_api_key
    }

    # TODO: test compatibility of creation_timestamp with datetime.fromtimestamp
    data = {
        'deviceAssetId': f'{file}-{file.creation_timestamp}', # TODO: better id
        'deviceId': 'python',
        'fileCreatedAt': file.creation_timestamp,
        'fileModifiedAt': file.creation_timestamp,
        'isFavorite': 'false',
    }

    files = {
        'assetData': stream # FIXME: expects SupportsRead[str | bytes] - won't work with Iterator[bytes]
    }

    response = requests.post(
        f'{cfg.immich_server_url}/assets', headers=headers, data=data, files=files)

    try:
        resp = response.json()
    except Exception:
        log.error("Failed to parse response: %s", response.text)
        raise
    log.info("Uploaded asset: %s", resp)
    # {'id': 'ef96f635-61c7-4639-9e60-61a11c4bbfba', 'duplicate': False}
