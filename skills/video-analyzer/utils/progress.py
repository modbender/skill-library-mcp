"""
Progress Bar - Display progress during long operations
"""

try:
    from tqdm import tqdm

    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False


class ProgressBar:
    """Progress bar wrapper."""

    @staticmethod
    def transcribe(audio_path: str, total_duration: float = None):
        """Create transcription progress bar."""
        if HAS_TQDM and total_duration:
            return tqdm(total=total_duration, desc="Transcribing", unit="秒")
        return None

    @staticmethod
    def download(total: int = None):
        """Create download progress bar."""
        if HAS_TQDM and total:
            return tqdm(total=total, desc="Downloading", unit="文件")
        return None

    @staticmethod
    def analyze(total: int = None):
        """Create analysis progress bar."""
        if HAS_TQDM and total:
            return tqdm(total=total, desc="Analyzing", unit="个")
        return None
