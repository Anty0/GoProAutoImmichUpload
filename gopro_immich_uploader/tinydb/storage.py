import base64
import json
from typing import Any, Dict, Optional

from tinydb import TinyDB
from tinydb.storages import Storage


MEMORY: Optional[Dict[str, Dict[str, Any]]] = None

class GlobalMemoryStorage(Storage):
    """
    Store the data as JSON in memory as a global variable.
    """

    def __init__(self, *args, **kwargs):
        super().__init__()

    def read(self) -> Optional[Dict[str, Dict[str, Any]]]:
        global MEMORY
        return MEMORY

    def write(self, data: Dict[str, Dict[str, Any]]):
        global MEMORY
        MEMORY = data

    @staticmethod
    def set_as_default():
        """
        Set the global memory storage as the default storage.
        """
        TinyDB.default_storage_class = GlobalMemoryStorage

    @staticmethod
    def serialize() -> str:
        global MEMORY
        if MEMORY is None:
            return ""
        json_str = json.dumps(MEMORY)
        return base64.b64encode(json_str.encode()).decode()

    @staticmethod
    def restore(credentials: str) -> None:
        global MEMORY
        if not credentials:
            MEMORY = None
            return
        json_str = base64.b64decode(credentials.encode()).decode()
        MEMORY = json.loads(json_str)
