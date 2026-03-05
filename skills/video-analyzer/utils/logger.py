"""
Logger - Structured logging utility
"""

import logging
from datetime import datetime


class SkillLogger:
    """Custom logger for the skill."""

    def __init__(self, name: str = "video-analyzer"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # Console handler
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)s | %(message)s", datefmt="%H:%M:%S"
            )
        )
        self.logger.addHandler(handler)

    def info(self, msg: str, **kwargs):
        """Log info message."""
        self.logger.info(msg)
        if kwargs:
            self.logger.info("  " + " | ".join(f"{k}: {v}" for k, v in kwargs.items()))

    def error(self, msg: str, **kwargs):
        """Log error message."""
        self.logger.error(msg)
        if kwargs:
            self.logger.error("  " + " | ".join(f"{k}: {v}" for k, v in kwargs.items()))

    def warning(self, msg: str, **kwargs):
        """Log warning message."""
        self.logger.warning(msg)
        if kwargs:
            self.logger.warning(
                "  " + " | ".join(f"{k}: {v}" for k, v in kwargs.items())
            )


# Global logger instance
logger = SkillLogger()
