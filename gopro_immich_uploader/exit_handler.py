from gopro_immich_uploader.logger import get_logger

log = get_logger(__name__)

SHOULD_EXIT = False


def exit_handler(signal, frame):
    log.info("Caught SIGINT. Exiting... (running uploads will finish)")
    global SHOULD_EXIT
    SHOULD_EXIT = True


def should_exit() -> bool:
    return SHOULD_EXIT
