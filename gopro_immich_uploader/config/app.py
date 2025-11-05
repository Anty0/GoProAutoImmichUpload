from pydantic.v1 import BaseModel, Field

from .service import ServiceConfig
from .setup import SetupConfig


class AppConfig(BaseModel):
    setup: SetupConfig | None = Field(description="Setup GoPro camera via BLE for COHN (Camera On the Home Network)")
    run: ServiceConfig | None = Field(description="Service Mode - automatic upload of media to Immich")
