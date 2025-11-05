from typing import override

from bleak import BleakClient
from open_gopro.network.ble import BleakWrapperController

MANUFACTURER_ID = 0x02F2

ENABLE_PAIRING = False
ONLY_POWERED_ON = False


class DeviceNotPoweredOn(BaseException):
    pass


class BLEController(BleakWrapperController):
    @override
    async def pair(self, handle: BleakClient) -> None:
        """Optionally enable pairing - it is broken on recent Linux and macOS."""
        if ENABLE_PAIRING:
            await super().pair(handle)
        else:
            pass

    @staticmethod
    def set_enable_pairing(enable: bool) -> None:
        global ENABLE_PAIRING  # noqa: PLW0603
        ENABLE_PAIRING = enable
