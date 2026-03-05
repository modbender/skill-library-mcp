"""
Natural Language Parser

Parses user requests into structured commands for Radarr/Sonarr.
"""

import re
from dataclasses import dataclass
from typing import Optional, Tuple, List


@dataclass
class MovieRequest:
    """Structured movie download request."""
    title: str
    quality: str = "1080p"
    language: str = "english"
    year: Optional[str] = None
    action: str = "download"


@dataclass
class SeriesRequest:
    """Structured series download request."""
    title: str
    season: Optional[int] = None
    episode: Optional[int] = None
    quality: str = "1080p"
    language: str = "english"
    action: str = "download"


# Quality mapping (name -> display name)
QUALITY_MAP = {
    # 4K
    "4k": "4K",
    "uhd": "4K",
    "ultra": "4K",
    "ultra hd": "4K",
    "2160p": "4K",
    # 1080p
    "1080p": "1080p",
    "hd 1080p": "1080p",
    "full hd": "1080p",
    "fullhd": "1080p",
    # 720p
    "720p": "720p",
    "hd 720p": "720p",
    "hd": "720p",
    # SD
    "480p": "480p",
    "sd": "SD",
}

# Language mapping (name -> display name)
LANGUAGE_MAP = {
    # English
    "english": "English",
    "en": "English",
    "eng": "English",
    "vo": "English",
    "original": "English",
    # French
    "french": "French",
    "fr": "French",
    "fra": "French",
    "vf": "French",
    # Spanish
    "spanish": "Spanish",
    "es": "Spanish",
    "esp": "Spanish",
    # German
    "german": "German",
    "de": "German",
    "ger": "German",
    # Multi
    "multi": "Multi",
    "multilingual": "Multi",
}

# Actions
ACTIONS = {
    "download": "download",
    "add": "add",
    "get": "get",
    "search": "search",
    "find": "find",
    "look": "look",
    "show": "show",
    "status": "status",
    "queue": "queue",
}


class NLParser:
    """Natural language parser for movie/TV requests."""

    def __init__(self):
        """Initialize parser."""
        # Compile patterns for better performance
        self._patterns = {
            "season": re.compile(
                r"(?:season|seasons|s)(\s*)(\d+)",
                re.IGNORECASE
            ),
            "episode": re.compile(
                r"(?:episode|episodes|ep|e)(\s*)(\d+)",
                re.IGNORECASE
            ),
            # Year pattern: only match years between 1900-2025, with word boundary
            "year": re.compile(
                r"\b(19\d{2}|20[0-2]\d)\b|\((\d{4})\)",
                re.IGNORECASE
            ),
        }

    def parse_movie(self, text: str) -> MovieRequest:
        """
        Parse a movie download request.

        Examples:
            - "Download Inception in 4K English"
            - "Find Dune 2020 in 1080p"
            - "Add Matrix in HD"

        Args:
            text: Natural language request

        Returns:
            MovieRequest with parsed components
        """
        text = text.lower().strip()

        # Detect action
        action = "download"
        for act in ACTIONS:
            if text.startswith(act):
                action = ACTIONS[act]
                text = text[len(act):].strip()
                break

        # Remove action words that might be in the middle
        for act in ["download", "add", "search", "find", "get"]:
            if text.startswith(act):
                text = text[len(act):].strip()

        # Extract year
        year_match = self._patterns["year"].search(text)
        year = None
        if year_match:
            year = year_match.group(1) or year_match.group(2)
            text = self._patterns["year"].sub("", text)

        # Extract quality (handle 720p, 1080p, 4K patterns first)
        quality = "1080p"  # Default
        text_lower = text.lower()
        
        # Quality patterns with special handling for numbers+p
        quality_patterns = [
            (r'\b4k\b', '4K'),
            (r'\buhd\b', '4K'),
            (r'\bultra\s*hd\b', '4K'),
            (r'\b2160p\b', '4K'),
            (r'\b1080p\b', '1080p'),
            (r'\bhd\s*1080p\b', '1080p'),
            (r'\bfull\s*hd\b', '1080p'),
            (r'\b720p\b', '720p'),
            (r'\bhd\s*720p\b', '720p'),
            (r'\b480p\b', '480p'),
        ]
        
        for pattern, q_display in quality_patterns:
            if re.search(pattern, text_lower):
                quality = q_display
                text = re.sub(pattern, "", text, flags=re.IGNORECASE).strip()
                break

        # Extract language
        language = "English"  # Default
        for lang_name, lang_display in sorted(
            LANGUAGE_MAP.items(), key=lambda x: len(x[0]), reverse=True
        ):
            pattern = rf'\b{re.escape(lang_name)}\b'
            if re.search(pattern, text_lower):
                language = lang_display
                text = re.sub(pattern, "", text, flags=re.IGNORECASE).strip()
                break

        # Clean up the remaining text (movie title)
        # Remove common words at start, middle, or end
        title = text
        for word in ["in", "with", "the", "a", "an", "movie", "film"]:
            # Remove at start
            title = re.sub(rf"^{word}\s+", " ", title, flags=re.IGNORECASE).strip()
            # Remove at end
            title = re.sub(rf"\s+{word}$", " ", title, flags=re.IGNORECASE).strip()
            # Remove in middle
            title = re.sub(rf"\s+{word}\s+", " ", title, flags=re.IGNORECASE).strip()

        # Clean up extra whitespace and trailing punctuation
        title = re.sub(r'[^\w\s\-]', '', title)  # Remove special chars except - and space
        title = " ".join(title.split())

        return MovieRequest(
            title=title,
            quality=quality,
            language=language,
            year=year,
            action=action,
        )

    def parse_series(self, text: str) -> SeriesRequest:
        """
        Parse a TV series download request.

        Examples:
            - "Download Supernatural season 4"
            - "Add Breaking Bad season 1 episode 3"
            - "Find Stranger Things in 4K"

        Args:
            text: Natural language request

        Returns:
            SeriesRequest with parsed components
        """
        text = text.lower().strip()

        # Detect action
        action = "download"
        for act in ACTIONS:
            if text.startswith(act):
                action = ACTIONS[act]
                text = text[len(act):].strip()
                break

        # Extract season
        season = None
        season_match = self._patterns["season"].search(text)
        if season_match:
            season = int(season_match.group(2))
            text = self._patterns["season"].sub("", text)

        # Extract episode
        episode = None
        episode_match = self._patterns["episode"].search(text)
        if episode_match:
            episode = int(episode_match.group(2))
            text = self._patterns["episode"].sub("", text)

        # Extract quality
        quality = "1080p"  # Default
        text_lower = text.lower()
        for q_name, q_display in sorted(
            QUALITY_MAP.items(), key=lambda x: len(x[0]), reverse=True
        ):
            if q_name in text_lower:
                quality = q_display
                text = re.sub(rf"\b{re.escape(q_name)}\b", "", text, flags=re.IGNORECASE).strip()
                break

        # Extract language
        language = "English"  # Default
        for lang_name, lang_display in sorted(
            LANGUAGE_MAP.items(), key=lambda x: len(x[0]), reverse=True
        ):
            if lang_name in text_lower:
                language = lang_display
                text = re.sub(rf"\b{re.escape(lang_name)}\b", "", text, flags=re.IGNORECASE).strip()
                break

        # Clean up the remaining text (series title)
        title = text
        for word in ["in", "with", "the", "a", "an", "tv", "show", "series"]:
            title = re.sub(rf"^{word}\s+|\s+{word}\s+", " ", title, flags=re.IGNORECASE).strip()

        title = " ".join(title.split())

        return SeriesRequest(
            title=title,
            season=season,
            episode=episode,
            quality=quality,
            language=language,
            action=action,
        )

    def is_series_request(self, text: str) -> bool:
        """Check if the request is likely for a TV series."""
        text_lower = text.lower()
        series_keywords = ["season", "seasons", "episode", "episodes", "tv show", "tv series"]
        return any(kw in text_lower for kw in series_keywords)

    def parse(self, text: str) -> Tuple[MovieRequest, SeriesRequest, str]:
        """
        Parse any request and return the appropriate type.

        Args:
            text: Natural language request

        Returns:
            Tuple of (movie_request, series_request, request_type)
        """
        if self.is_series_request(text):
            series_req = self.parse_series(text)
            return None, series_req, "series"
        else:
            movie_req = self.parse_movie(text)
            return movie_req, None, "movie"


# Convenience function
def parse_request(text: str) -> Tuple[MovieRequest, SeriesRequest, str]:
    """Parse a natural language request."""
    parser = NLParser()
    return parser.parse(text)
