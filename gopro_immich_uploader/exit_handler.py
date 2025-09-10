from gopro_immich_uploader.logger import get_logger

log = get_logger(__name__)

SHOULD_EXIT = False


def exit_handler():
    log.info("Caught SIGINT. Exiting... (running uploads will finish)")
    log.info("Press Ctrl+C again to force exit")
    if SHOULD_EXIT:
        raise KeyboardInterrupt()
    on_exit()


def on_exit():
    global SHOULD_EXIT
    SHOULD_EXIT = True


def should_exit() -> bool:
    return SHOULD_EXIT
