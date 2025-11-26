# src/logger.py
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# --------------------------------------------------------------------------- #
# Centralized Logger Configuration (used across the entire project)
# --------------------------------------------------------------------------- #

def get_logger(
    name: str | None = None,
    log_level: str = "INFO",
    log_file: str | Path | None = None,
) -> logging.Logger:
    """
    Returns a configured logger that logs to both console and file (optional).

    Args:
        name (str, optional): Name of the logger (usually __name__). Defaults to root.
        log_level (str): Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL
        log_file (str | Path | None): Path to log file. If None, logs only to console.

    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name or "GeminiRetailAgent")
    
    # Prevent adding handlers multiple times (important when importing in many modules)
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, log_level.upper()))

    # Formatter (professional look)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(name)s | %(levelname)8s | %(filename)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console Handler (with colors on Windows/macOS/Linux)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Optional File Handler with rotation (max 5MB, keep 5 backups)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=5_000_000,      # 5 MB
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# --------------------------------------------------------------------------- #
# Default project logger (most modules will just do: from logger import logger)
# --------------------------------------------------------------------------- #

# This is the logger you'll import everywhere
logger = get_logger(
    name="Gemini_Retail_Agent",
    log_level="INFO",
    log_file="logs/app.log"   # Creates logs/app.log automatically
)

# Create logs directory on import
Path("logs").mkdir(exist_ok=True)