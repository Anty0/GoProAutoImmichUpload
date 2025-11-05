import base64
import json
from typing import Any, override

from tinydb import TinyDB
from tinydb.storages import Storage

MEMORY: dict[str, dict[str, Any]] | None = None


class GlobalMemoryStorage(Storage):
    """
    Store the data as JSON in memory as a global variable.
    """

    def __init__(self, *args: Any, **kwargs: Any):  # noqa: ARG002
        super().__init__()

    @override
    def read(self) -> dict[str, dict[str, Any]] | None:
        return MEMORY

    @override
    def write(self, data: dict[str, dict[str, Any]]) -> None:
        global MEMORY  # noqa: PLW0603
        MEMORY = data

    @staticmethod
    def set_as_default() -> None:
        """
        Set the global memory storage as the default storage.
        """
        TinyDB.default_storage_class = GlobalMemoryStorage  # type: ignore

    @staticmethod
    def serialize() -> str:
        if MEMORY is None:
            return ""
        json_str = json.dumps(MEMORY)
        return base64.b64encode(json_str.encode()).decode()

    @staticmethod
    def restore(credentials: str) -> None:
        global MEMORY  # noqa: PLW0603
        if not credentials:
            MEMORY = None
            return
        json_str = base64.b64decode(credentials.encode()).decode()
        MEMORY = json.loads(json_str)
