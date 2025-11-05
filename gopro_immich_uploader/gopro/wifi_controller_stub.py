from typing import override

from open_gopro.network.wifi import SsidState, WifiController


class WifiControllerStub(WifiController):
    @override
    async def connect(self, ssid: str, password: str, timeout: float = 15) -> bool:
        return False

    @override
    async def disconnect(self) -> bool:
        return False

    @override
    def current(self) -> tuple[str | None, SsidState]:
        return None, SsidState.DISCONNECTED

    @override
    def available_interfaces(self) -> list[str]:
        return ["stub0"]

    @override
    def power(self, power: bool) -> bool:
        return False

    @override
    @property
    def is_on(self) -> bool:
        return False
