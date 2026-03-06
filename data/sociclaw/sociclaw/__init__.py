"""SociClaw skill package."""

import logging

# Centralized logging configuration
# This prevents conflicts from multiple basicConfig calls in submodules
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
