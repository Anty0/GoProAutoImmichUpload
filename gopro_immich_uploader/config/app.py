from typing import Optional

from pydantic.v1 import BaseModel, Field

from gopro_immich_uploader.config import SetupConfig, ServiceConfig


class AppConfig(BaseModel):
    setup: Optional[SetupConfig] = Field(description="Setup GoPro camera via BLE for COHN (Camera On the Home Network)")
    run: Optional[ServiceConfig] = Field(description="Service Mode - automatic upload of media to Immich")
