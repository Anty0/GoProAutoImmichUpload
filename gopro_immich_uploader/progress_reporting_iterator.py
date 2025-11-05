import time
from collections.abc import Iterator

from gopro_immich_uploader.logger import get_logger

log = get_logger(__name__)


class ProgressReportingIterator(Iterator[bytes]):
    def __init__(self, name: str, stream: Iterator[bytes], size: int, min_delay: float = 10.0):
        self.name = name
        self.stream = stream
        self.size = size
        self.min_delay = min_delay
        self.read_so_far = 0
        self.last_report = 0.0

    def __next__(self) -> bytes:
        try:
            chunk = next(self.stream)
            self.read_so_far += len(chunk)
            now = time.time()
            if now - self.last_report > self.min_delay:
                log.info("%s: %d%% (%d/%d)", self.name, self.read_so_far / self.size * 100, self.read_so_far, self.size)
                self.last_report = now
            return chunk
        except StopIteration:
            log.info("%s: 100%% (%d/%d) - Done", self.name, self.read_so_far, self.size)
            raise
