
from gopro_immich_uploader.config import load_config
from gopro_immich_uploader.logger import configure_logging, get_logger


def main():
    cfg = load_config()
    configure_logging(cfg.log_level)
    log = get_logger(__name__)

    log.info("Starting GoPro Immich Uploader")
    log.debug(f"Using config: %s", cfg)

    # TODO: wire the rest of the application using cfg
    # For now, just a placeholder

if __name__ == '__main__':
    main()
