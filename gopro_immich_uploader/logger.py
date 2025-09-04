import logging
from typing import Optional


def configure_logging(level: int) -> None:
    logging.basicConfig(
        format='%(asctime)s [%(levelname)s] %(message)s',
        level=level,
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def get_logger(name: Optional[str] = None) -> logging.Logger:
    return logging.getLogger(name)
