"""Guardian core package."""

from .api import GuardianScanner, ScanResult, scan

__version__ = "2.0.0"

__all__ = ["scan", "GuardianScanner", "ScanResult"]
