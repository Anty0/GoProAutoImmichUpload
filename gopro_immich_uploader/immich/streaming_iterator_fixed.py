from typing import override

from requests_toolbelt import StreamingIterator


class StreamingIteratorFixed(StreamingIterator):
    len: int

    @override
    def read(self, size: int = -1) -> bytes:
        chunk: bytes = super().read(size)
        self.len -= chunk.__len__()
        self.len = max(0, self.len)
        return chunk
