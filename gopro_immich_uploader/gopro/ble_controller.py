from typing import Callable

from bleak import BLEDevice as BleakDevice, BleakClient, BleakScanner
from open_gopro.network.ble import BleakWrapperController

from gopro_immich_uploader.gopro.manufacturer_data_structs import manuf_data_struct

MANUFACTURER_ID = 0x02F2

ENABLE_PAIRING = False
ONLY_POWERED_ON = False


class DeviceNotPoweredOn(BaseException):
    pass


class BLEController(BleakWrapperController):
    async def pair(self, handle: BleakClient) -> None:
        """Optionally enable pairing - it is broken on recent Linux and macOS."""
        if ENABLE_PAIRING:
            await super().pair(handle)
        else:
            pass

    async def connect(self, disconnect_cb: Callable, device: BleakDevice, timeout: int = 15) -> BleakClient:
        """Optionally allow connection only if the device is powered on - avoid waking up the GoPro."""

        if not ONLY_POWERED_ON:
            return await super().connect(disconnect_cb, device, timeout)

        address = device.address
        is_powered = False

        async with BleakScanner() as scanner:
            async for found, advertisement_data in scanner.advertisement_data():
                if found.address.upper() != address.upper():
                    continue
                manuf_data = manuf_data_struct.parse(advertisement_data.manufacturer_data[MANUFACTURER_ID])
                is_powered = manuf_data.camera_status.reserved03
                break

        if is_powered:
            return await super().connect(disconnect_cb, device, timeout)
        else:
            raise DeviceNotPoweredOn("Device is not powered on.")

    @staticmethod
    def set_enable_pairing(enable: bool) -> None:
        global ENABLE_PAIRING
        ENABLE_PAIRING = enable

    @staticmethod
    def set_only_powered_on(enable: bool) -> None:
        global ONLY_POWERED_ON
        ONLY_POWERED_ON = enable
