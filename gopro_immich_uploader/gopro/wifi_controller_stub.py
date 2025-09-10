from typing import Optional

from open_gopro.network.wifi import WifiController, SsidState


class WifiControllerStub(WifiController):
    async def connect(self, ssid: str, password: str, timeout: float = 15) -> bool:
        return False

    async def disconnect(self) -> bool:
        return False

    def current(self) -> tuple[Optional[str], SsidState]:
        return None, SsidState.DISCONNECTED

    def available_interfaces(self) -> list[str]:
        return ["stub0"]

    def power(self, power: bool) -> bool:
        return False

    @property
    def is_on(self) -> bool:
        return False
