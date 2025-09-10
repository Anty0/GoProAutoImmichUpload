from open_gopro import WirelessGoPro

from gopro_immich_uploader.gopro.streaming_download_mixin import GoProStreamingDownloadMixin


class StreamingWirelessGoPro(WirelessGoPro, GoProStreamingDownloadMixin):
    pass
