"""
Screenshot Extractor - Extract video frames at specific timestamps using ffmpeg
"""

import subprocess
from pathlib import Path
from typing import List, Optional
import logging

from models import ScreenshotResult


logger = logging.getLogger(__name__)


class ScreenshotExtractor:
    """Extract screenshots from video at specified timestamps."""

    def extract(
        self, video_path: str, timestamps: List[float], output_dir: str
    ) -> ScreenshotResult:
        """
        Extract screenshots from video at specified timestamps.

        Args:
            video_path: Path to video file
            timestamps: List of timestamps in seconds (e.g., [10.5, 125.3, 240.0])
            output_dir: Directory to save screenshot files

        Returns:
            ScreenshotResult containing:
            - file_paths: List of successfully extracted screenshot paths
            - timestamps: Corresponding timestamps for successful extractions
            - success: True if at least one screenshot extracted, False if all failed
            - error_message: Error details if all extractions failed

        Note:
            Non-fatal errors: If individual screenshots fail, they are skipped
            with a warning, and the operation continues with remaining timestamps.
        """
        # Validate inputs
        video_file = Path(video_path)
        if not video_file.exists():
            error_msg = f"Video file not found: {video_path}"
            logger.error(error_msg)
            return ScreenshotResult(
                file_paths=[], timestamps=[], success=False, error_message=error_msg
            )

        if not timestamps:
            error_msg = "No timestamps provided for screenshot extraction"
            logger.warning(error_msg)
            return ScreenshotResult(
                file_paths=[], timestamps=[], success=False, error_message=error_msg
            )

        # Ensure output directory exists
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Extract screenshots
        successful_paths = []
        successful_timestamps = []
        failed_count = 0

        for timestamp in timestamps:
            screenshot_path = self._extract_single_screenshot(
                video_path, timestamp, output_dir
            )

            if screenshot_path:
                successful_paths.append(screenshot_path)
                successful_timestamps.append(timestamp)
            else:
                failed_count += 1
                logger.warning(
                    f"Failed to extract screenshot at {timestamp}s, continuing with remaining timestamps"
                )

        # Determine overall success
        if not successful_paths:
            error_msg = f"All {len(timestamps)} screenshot extractions failed"
            logger.error(error_msg)
            return ScreenshotResult(
                file_paths=[],
                timestamps=[],
                success=False,
                error_message=error_msg,
            )

        # Partial success or full success
        if failed_count > 0:
            logger.info(
                f"Extracted {len(successful_paths)}/{len(timestamps)} screenshots "
                f"({failed_count} failed)"
            )

        return ScreenshotResult(
            file_paths=successful_paths,
            timestamps=successful_timestamps,
            success=True,
            error_message=None,
        )

    def _extract_single_screenshot(
        self, video_path: str, timestamp: float, output_dir: str
    ) -> Optional[str]:
        """
        Extract a single screenshot at the specified timestamp.

        Args:
            video_path: Path to video file
            timestamp: Timestamp in seconds
            output_dir: Directory to save screenshot

        Returns:
            Absolute path to screenshot file if successful, None if failed
        """
        # Deterministic output path
        output_filename = f"screenshot_{timestamp:.1f}s.jpg"
        output_path = Path(output_dir) / output_filename

        # ffmpeg command:
        # -ss: seek to timestamp (before -i for faster seek)
        # -i: input video
        # -frames:v 1: extract only 1 frame
        # -q:v 2: high quality JPEG (1-31 scale, lower = better quality)
        # -y: overwrite output file if exists
        cmd = [
            "ffmpeg",
            "-ss",
            str(timestamp),
            "-i",
            video_path,
            "-frames:v",
            "1",
            "-q:v",
            "2",
            "-y",
            str(output_path),
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                check=True,
                text=True,
                timeout=30,  # 30 second timeout per screenshot
            )

            # Verify output file was created
            if output_path.exists():
                return str(output_path.absolute())
            else:
                logger.warning(
                    f"ffmpeg completed but output file not found: {output_path}"
                )
                return None

        except subprocess.TimeoutExpired:
            logger.warning(f"Screenshot extraction timed out at timestamp {timestamp}s")
            return None
        except subprocess.CalledProcessError as e:
            logger.warning(
                f"ffmpeg failed at timestamp {timestamp}s: {e.stderr.strip() if e.stderr else 'unknown error'}"
            )
            return None
        except Exception as e:
            logger.warning(
                f"Unexpected error extracting screenshot at {timestamp}s: {e}"
            )
            return None
