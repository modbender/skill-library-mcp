"""
Temporary File Manager - Auto-cleanup on exit
"""

import atexit
from pathlib import Path
from typing import List


class TempFileManager:
    """Manage temporary files with auto-cleanup."""

    _instance = None
    _files: List[str] = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            atexit.register(cls._instance.cleanup)
        return cls._instance

    def add(self, file_path: str):
        """Add a temp file to cleanup list."""
        self._files.append(file_path)

    def cleanup(self):
        """Remove all temp files."""
        for file_path in self._files:
            try:
                Path(file_path).unlink(missing_ok=True)
            except Exception:
                pass
        self._files.clear()


# Global instance
temp_manager = TempFileManager()
