import logging

from pydantic.v1 import BaseSettings, Field, validator


class CommonConfig(BaseSettings):
    log_level: str = Field(
        default="INFO", description=f"Logging level ({', '.join(logging.getLevelNamesMapping().keys())})"
    )

    # noinspection PyMethodParameters
    @validator("log_level")
    def validate_log_level(cls, v: str) -> str:  # noqa: N805
        normalized = v.strip().upper()
        if normalized not in logging.getLevelNamesMapping():
            raise ValueError(
                f"Invalid log level: {v}. Must be one of: {', '.join(logging.getLevelNamesMapping().keys())}"
            )
        return normalized

    def get_log_level_int(self) -> int:
        return logging.getLevelNamesMapping()[self.log_level]
