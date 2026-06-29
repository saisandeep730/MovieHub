import logging
import logging.handlers
import sys
from pathlib import Path

from app.config import settings


def setup_logging() -> None:
    """Configure the root logger with console and rotating file handlers."""

    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    log_format = (
        "[%(asctime)s] %(levelname)-8s %(name)s:%(lineno)d — %(message)s"
    )

    root = logging.getLogger()
    root.setLevel(log_level)

    # Remove any pre-existing handlers
    root.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(log_format))
    root.addHandler(console_handler)

    # File handler with rotation
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "moviehub.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging.Formatter(log_format))
    root.addHandler(file_handler)

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("motor").setLevel(logging.WARNING)
    logging.getLogger("pymongo").setLevel(logging.WARNING)
