from requests_toolbelt import StreamingIterator


class StreamingIteratorFixed(StreamingIterator):
    def read(self, size=-1):
        chunk: bytes = super().read(size)
        self.len -= chunk.__len__()
        if self.len <= 0:
            self.len = 0
        return chunk
