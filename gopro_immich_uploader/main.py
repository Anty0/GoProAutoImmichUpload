import asyncio
import signal

from pydantic_argparse import ArgumentParser

from gopro_immich_uploader.config import AppConfig
from gopro_immich_uploader.exit_handler import exit_handler
from gopro_immich_uploader.logger import configure_logging
from gopro_immich_uploader.service import service
from gopro_immich_uploader.setup import setup
from gopro_immich_uploader.tinydb import GlobalMemoryStorage


def main() -> None:
    init()

    # noinspection PyTypeChecker
    parser = ArgumentParser(model=AppConfig, prog="gopro-immich-uploader", description="GoPro Auto Immich Uploader")
    cfg: AppConfig = parser.parse_typed_args()

    if cfg.setup:
        configure_logging(cfg.setup.get_log_level_int())
        asyncio.run(setup(cfg.setup))
    elif cfg.run:
        configure_logging(cfg.run.get_log_level_int())
        asyncio.run(service(cfg.run))


def init() -> None:
    # Register the signal handler for SIGINT and SIGTERM
    asyncio.get_event_loop().add_signal_handler(signal.SIGINT, exit_handler, "SIGINT")
    asyncio.get_event_loop().add_signal_handler(signal.SIGTERM, exit_handler, "SIGTERM")

    # OpenGoPro uses TinyDB as a storage backend for COHN info.
    # We need multiple instances of GoPro cameras to be able to use this COHN info, but
    # there is no reason to store it in a file system.
    GlobalMemoryStorage.set_as_default()


if __name__ == "__main__":
    main()
