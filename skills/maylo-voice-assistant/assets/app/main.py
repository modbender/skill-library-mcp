#!/usr/bin/env python3
"""Entry point for the Maylo voice assistant.

For the actual implementation see: maylo_assistant/core.py

This wrapper keeps the historical `python main.py` workflow intact.
"""

from maylo_assistant.core import cli


if __name__ == "__main__":
    cli()
