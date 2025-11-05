import logging


def configure_logging(level: int) -> None:
    logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=level, datefmt="%Y-%m-%d %H:%M:%S")


def get_logger(name: str | None = None) -> logging.Logger:
    return logging.getLogger(name)
