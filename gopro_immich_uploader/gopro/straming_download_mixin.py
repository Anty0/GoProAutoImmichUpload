from typing import Any

from open_gopro.gopro_base import GoProBase, enforce_message_rules
from open_gopro.domain.communicator_interface import (
    HttpMessage,
    MessageRules,
)
from open_gopro.models import GoProResp
from open_gopro.models.constants import ErrorCode

from gopro_immich_uploader.logger import get_logger

log = get_logger(__name__)


class GoProStramingDownloadMixin(GoProBase):

    @enforce_message_rules
    async def _get_stream(
        self,
        message: HttpMessage,
        *,
        timeout: int = GoProBase.HTTP_TIMEOUT,
        rules: MessageRules = MessageRules(),
        **kwargs: Any,
    ) -> GoProResp:
        url = self._base_url + message.build_url(path=kwargs["camera_file"])
        callback = kwargs["stream_callback"]
        log.debug(f"Sending:  {url}")
        with self._requests_session.get(
            url,
            stream=True,
            timeout=timeout,
            **self._build_http_request_args(message),
        ) as request:
            request.raise_for_status()
            await callback(request.iter_content(chunk_size=8192))
        return GoProResp(protocol=GoProResp.Protocol.HTTP, status=ErrorCode.SUCCESS, data=request, identifier=url)
