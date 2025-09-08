from open_gopro import WirelessGoPro

from gopro_immich_uploader.gopro.straming_download_mixin import GoProStramingDownloadMixin


class StreamingWirelessGoPro(WirelessGoPro, GoProStramingDownloadMixin):
    pass
