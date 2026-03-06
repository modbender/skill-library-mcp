"""Utility functions for tsend"""

from pathlib import Path


def get_file_type(file_path: Path) -> str:
    """Determine file type for Telegram sending

    Args:
        file_path: Path to the file

    Returns:
        'photo' for images, 'document' for other files
    """
    # Image extensions that Telegram treats as photos
    photo_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}

    if file_path.suffix.lower() in photo_extensions:
        return "photo"
    return "document"


def format_bytes(size: int) -> str:
    """Format bytes to human readable string"""
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"
