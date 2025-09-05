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


def set_global_memory_storage_as_default():
    """
    Set the global memory storage as the default storage.
    """
    TinyDB.default_storage_class = GlobalMemoryStorage
