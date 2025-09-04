# This file is just an example how to upload to immich
# We need to reimplement this properly to allow streaming the file directly from the camera to the immich
# probably using the requests_toolbelt library

import requests
import os
from datetime import datetime

from gopro_immich_uploader.config import Config
from gopro_immich_uploader.logger import get_logger

log = get_logger(__name__)


def upload(file: str, cfg: Config):
    stats = os.stat(file)

    headers = {
        'Accept': 'application/json',
        'x-api-key': cfg.immich_api_key
    }

    data = {
        'deviceAssetId': f'{file}-{stats.st_mtime}',
        'deviceId': 'python',
        'fileCreatedAt': datetime.fromtimestamp(stats.st_mtime),
        'fileModifiedAt': datetime.fromtimestamp(stats.st_mtime),
        'isFavorite': 'false',
    }

    files = {
        'assetData': open(file, 'rb')
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
