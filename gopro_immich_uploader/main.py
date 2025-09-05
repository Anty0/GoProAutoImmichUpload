import signal
import asyncio

from gopro_immich_uploader.exit_handler import exit_handler
from gopro_immich_uploader.tinydb import set_global_memory_storage_as_default
from gopro_immich_uploader.logger import configure_logging, get_logger
from gopro_immich_uploader.config import load_config
from gopro_immich_uploader.loop import loop_main


def main():
    # Register the signal handler for SIGINT
    asyncio.get_event_loop().add_signal_handler(signal.SIGINT, exit_handler)

    # OpenGoPro uses TinyDB as a storage backend for COHN info.
    # We need multiple instances of GoPro cameras to be able to use this COHN info, but
    # there is no reason to store it in a file system.
    set_global_memory_storage_as_default()

    cfg = load_config()
    configure_logging(cfg.log_level)
    log = get_logger(__name__)

    log.info("Starting GoPro Immich Uploader")
    log.debug("Using config: %s", cfg)

    # Start the asynchronous main loop
    asyncio.run(loop_main(cfg))


if __name__ == '__main__':
    main()
