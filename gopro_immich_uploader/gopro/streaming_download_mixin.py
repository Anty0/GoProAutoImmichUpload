from collections.abc import Callable, Coroutine, Iterator
from typing import Any, override

from open_gopro.domain.communicator_interface import (
    HttpMessage,
    MessageRules,
)
from open_gopro.gopro_base import GoProBase
from open_gopro.models import GoProResp
from open_gopro.models.constants import ErrorCode

from gopro_immich_uploader.logger import get_logger

log = get_logger(__name__)


# noinspection PyAbstractClass
class GoProStreamingDownloadMixin(GoProBase):
    @override
    async def _get_stream(
        self,
        message: HttpMessage,
        *,
        timeout: int = GoProBase.HTTP_TIMEOUT,
        rules: MessageRules = MessageRules(),  # noqa: B008
        **kwargs: Any,
    ) -> GoProResp:
        url = self._base_url + message.build_url(path=kwargs["camera_file"])
        # We abuse existing local_file kwarg to pass in callback
        callback: Callable[[Iterator[bytes], int], Coroutine[None, None, None]] = kwargs["local_file"]
        log.debug(f"Sending:  {url}")
        with self._requests_session.get(
            url,
            stream=True,
            timeout=timeout,
            **self._build_http_request_args(message),
        ) as request:
            request.raise_for_status()
            content_length = int(request.headers["Content-Length"])
            await callback(request.iter_content(chunk_size=1_048_576), content_length)
        return GoProResp(protocol=GoProResp.Protocol.HTTP, status=ErrorCode.SUCCESS, data=request, identifier=url)
