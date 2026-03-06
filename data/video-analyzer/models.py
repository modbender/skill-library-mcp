"""
Video Analyzer Models - Type contracts for analysis results
"""

from enum import Enum
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class TranscriptSegment:
    """
    Represents a single segment of transcribed audio with timing information.

    Attributes:
        start: Start time in seconds
        end: End time in seconds
        text: Transcribed text for this segment
    """

    start: float
    end: float
    text: str


class SummaryStyle(Enum):
    """Summary style options for video analysis output."""

    BRIEF_POINTS = "brief_points"  # Brief bullet points
    DEEP_LONGFORM = "deep_longform"  # In-depth long-form analysis
    SOCIAL_MEDIA = "social_media"  # Social media copywriting
    STUDY_NOTES = "study_notes"  # Study notes format

    @property
    def display_name(self) -> str:
        """Get human-readable display name."""
        names = {
            "brief_points": "Brief Points",
            "deep_longform": "Deep Longform",
            "social_media": "Social Media",
            "study_notes": "Study Notes",
        }
        return names.get(self.value, self.value)

    @property
    def chinese_name(self) -> str:
        """Get Chinese display name."""
        names = {
            "brief_points": "Brief Points",
            "deep_longform": "Deep Longform",
            "social_media": "Social Media",
            "study_notes": "Study Notes",
        }
        return names.get(self.value, self.value)


def get_default_summary_style() -> SummaryStyle:
    """
    Get the default summary style for video analysis.

    Returns:
        SummaryStyle.DEEP_LONGFORM - Default style for in-depth analysis
    """
    return SummaryStyle.DEEP_LONGFORM


@dataclass
class KeyNode:
    """
    Represents a key moment/node in the video timeline.

    Attributes:
        timestamp_seconds: Position in video (seconds from start)
        title: Brief title/description of this key moment
        importance_score: Relevance score (0.0-1.0)
    """

    timestamp_seconds: float
    title: str
    importance_score: float


@dataclass
class ScreenshotSpec:
    """
    Specification for screenshot extraction from video.

    Attributes:
        key_nodes: List of selected key moments to capture
        screenshot_count: Total number of screenshots to extract
        duration_seconds: Video duration for context
    """

    key_nodes: List[KeyNode]
    screenshot_count: int
    duration_seconds: float


@dataclass
class ScreenshotResult:
    """
    Result of screenshot extraction operation.

    Attributes:
        file_paths: List of absolute paths to saved screenshot files
        timestamps: Corresponding timestamps (seconds) for each screenshot
        success: Whether extraction succeeded
        error_message: Error details if failed
    """

    file_paths: List[str]
    timestamps: List[float]
    success: bool
    error_message: Optional[str] = None


def calculate_screenshot_count(duration_seconds: float) -> int:
    """
    Calculate recommended screenshot count based on video duration.

    Duration ranges:
    - < 5 minutes: 3 screenshots
    - 5-20 minutes: 5 screenshots
    - 20-60 minutes: 8 screenshots
    - > 60 minutes: 12 screenshots

    Args:
        duration_seconds: Video duration in seconds

    Returns:
        Recommended number of screenshots to extract
    """
    duration_minutes = duration_seconds / 60.0

    if duration_minutes < 5:
        return 3
    elif duration_minutes < 20:
        return 5
    elif duration_minutes < 60:
        return 8
    else:
        return 12
