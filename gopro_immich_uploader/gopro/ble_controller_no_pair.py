from typing import Callable

from bleak import BLEDevice as BleakDevice, BleakClient, BleakScanner
from open_gopro.network.ble import BleakWrapperController

from gopro_immich_uploader.gopro.manufacturer_data_structs import manuf_data_struct

MANUFACTURER_ID = 0x02F2


class DeviceNotPoweredOn(BaseException):
    pass


class BLEControllerNoPair(BleakWrapperController):

    async def pair(self, handle: BleakClient) -> None:
        """Disable pairing - it is broken."""
        pass

    async def connect(self, disconnect_cb: Callable, device: BleakDevice, timeout: int = 15) -> BleakClient:
        """Allow connection only if the device is powered on - avoid waking up the GoPro."""

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
