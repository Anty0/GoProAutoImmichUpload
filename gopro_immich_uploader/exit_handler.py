from gopro_immich_uploader.logger import get_logger

log = get_logger(__name__)

SHOULD_EXIT = False


def exit_handler(signame: str) -> None:
    log.error(f"Caught {signame}. Exiting... (running uploads will finish)")
    log.error("Press Ctrl+C again to force exit")
    if SHOULD_EXIT:
        raise KeyboardInterrupt()
    on_exit()


def on_exit() -> None:
    global SHOULD_EXIT  # noqa: PLW0603
    SHOULD_EXIT = True


def should_exit() -> bool:
    return SHOULD_EXIT
