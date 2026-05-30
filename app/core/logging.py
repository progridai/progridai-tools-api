import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler()]
    )
    # Ensure we don't log raw text or PII in this setup
    logger = logging.getLogger("progridai-tools")
    return logger

logger = setup_logging()
