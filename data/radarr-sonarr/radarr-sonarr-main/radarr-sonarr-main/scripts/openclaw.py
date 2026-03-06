"""
OpenClaw Skill Integration

Integrates Radarr-Sonarr with OpenClaw's skill system.
"""

import os
import sys
import logging

# Add skill directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.radarr import RadarrClient
from scripts.sonarr import SonarrClient
from scripts.parser import NLParser, MovieRequest, SeriesRequest

logger = logging.getLogger(__name__)


class RadarrSonarrSkill:
    """OpenClaw skill for Radarr and Sonarr operations."""

    def __init__(self):
        """Initialize the skill."""
        self.parser = NLParser()
        self._radarr_client = None
        self._sonarr_client = None

    @property
    def radarr(self) -> RadarrClient:
        """Get Radarr client (lazy initialization)."""
        if self._radarr_client is None:
            try:
                self._radarr_client = RadarrClient()
            except ValueError as e:
                logger.error(f"Radarr not configured: {e}")
                return None
        return self._radarr_client

    @property
    def sonarr(self) -> SonarrClient:
        """Get Sonarr client (lazy initialization)."""
        if self._sonarr_client is None:
            try:
                self._sonarr_client = SonarrClient()
            except ValueError as e:
                logger.error(f"Sonarr not configured: {e}")
                return None
        return self._sonarr_client

    def handle(self, message: str, context: dict = None) -> str:
        """
        Handle a user message.

        Args:
            message: User message (natural language)
            context: Additional context (optional)

        Returns:
            Response message
        """
        message = message.strip()

        # Handle status/queue queries
        lower_msg = message.lower()

        if any(kw in lower_msg for kw in ["status", "queue", "downloading", "downloads"]):
            if "radarr" in lower_msg or "movie" in lower_msg:
                return self._radarr_status()
            elif "sonarr" in lower_msg or "series" in lower_msg or "tv" in lower_msg:
                return self._sonarr_status()
            else:
                return self._all_status()

        if "wanted" in lower_msg or "missing" in lower_msg:
            if "radarr" in lower_msg or "movie" in lower_msg:
                return self._radarr_wanted()
            elif "sonarr" in lower_msg or "series" in lower_msg or "tv" in lower_msg:
                return self._sonarr_wanted()

        # Parse natural language request
        movie_req, series_req, req_type = self.parser.parse(message)

        if req_type == "movie":
            return self._download_movie(movie_req)
        else:
            return self._download_series(series_req)

    def _download_movie(self, request: MovieRequest) -> str:
        """Download/add a movie."""
        if not self.radarr:
            return "❌ Radarr is not configured. Please set RADARR_URL and RADARR_API_KEY."

        # Search for the movie
        results = self.radarr.search(request.title)
        if not results:
            return f"❌ Movie not found: {request.title}"

        movie = results[0]
        tmdb_id = movie.get('tmdbId')
        title = movie.get('title')
        year = movie.get('year', '')

        # Add to Radarr
        result = self.radarr.add(tmdb_id)
        if "error" in result:
            return f"❌ Error adding movie: {result['error']}"

        response = f"✅ Added to download queue: {title} ({year})\n"
        response += f"   Quality: {request.quality}\n"
        response += f"   Language: {request.language}\n"
        response += "   Radarr will search and download the best available quality."
        return response

    def _download_series(self, request: SeriesRequest) -> str:
        """Download/add a TV series."""
        if not self.sonarr:
            return "❌ Sonarr is not configured. Please set SONARR_URL and SONARR_API_KEY."

        # Search for the series
        results = self.sonarr.search(request.title)
        if not results:
            return f"❌ Series not found: {request.title}"

        series = results[0]
        tvdb_id = series.get('tvdbId')
        title = series.get('title')
        year = series.get('year', '')

        # Add to Sonarr
        result = self.sonarr.add(tvdb_id)
        if "error" in result:
            return f"❌ Error adding series: {result['error']}"

        response = f"✅ Added to download queue: {title} ({year})\n"
        response += f"   Quality: {request.quality}\n"
        response += f"   Language: {request.language}\n"
        if request.season:
            response += f"   Season: {request.season}\n"
        if request.episode:
            response += f"   Episode: {request.episode}\n"
        response += "   Sonarr will search and download the best available quality."
        return response

    def _radarr_status(self) -> str:
        """Get Radarr status and queue."""
        if not self.radarr:
            return "❌ Radarr is not configured."

        queue = self.radarr.get_queue()
        if "error" in queue:
            return f"❌ Error fetching queue: {queue['error']}"

        records = queue.get("records", [])
        if not records:
            return "📥 Radarr queue is empty. 🎉"

        response = "📥 Radarr Download Queue:\n\n"
        for item in records[:5]:
            title = item.get('title', 'Unknown')
            status = item.get('status', 'N/A')
            progress = item.get('progress', 0)
            response += f"• {title}\n"
            response += f"  Status: {status} | Progress: {progress:.0f}%\n\n"

        if len(records) > 5:
            response += f"... and {len(records) - 5} more items"

        return response

    def _sonarr_status(self) -> str:
        """Get Sonarr status and queue."""
        if not self.sonarr:
            return "❌ Sonarr is not configured."

        queue = self.sonarr.get_queue()
        if "error" in queue:
            return f"❌ Error fetching queue: {queue['error']}"

        records = queue.get("records", [])
        if not records:
            return "📥 Sonarr queue is empty. 🎉"

        response = "📥 Sonarr Download Queue:\n\n"
        for item in records[:5]:
            title = item.get('title', 'Unknown')
            status = item.get('status', 'N/A')
            progress = item.get('progress', 0)
            response += f"• {title}\n"
            response += f"  Status: {status} | Progress: {progress:.0f}%\n\n"

        if len(records) > 5:
            response += f"... and {len(records) - 5} more items"

        return response

    def _all_status(self) -> str:
        """Get status for both Radarr and Sonarr."""
        radarr_status = self._radarr_status()
        sonarr_status = self._sonarr_status()

        return f"{radarr_status}\n\n{sonarr_status}"

    def _radarr_wanted(self) -> str:
        """Get wanted/missing Radarr movies."""
        if not self.radarr:
            return "❌ Radarr is not configured."

        wanted = self.radarr.get_wanted()
        if "error" in wanted:
            return f"❌ Error fetching wanted: {wanted['error']}"

        records = wanted.get("records", [])
        if not records:
            return "🎉 No wanted movies! Everything is downloaded."

        response = "🎬 Wanted/Missing Movies:\n\n"
        for movie in records[:5]:
            title = movie.get('title', 'Unknown')
            year = movie.get('year', '')
            response += f"• {title} ({year})\n"

        if len(records) > 5:
            response += f"\n... and {len(records) - 5} more"

        return response

    def _sonarr_wanted(self) -> str:
        """Get wanted/missing Sonarr episodes."""
        if not self.sonarr:
            return "❌ Sonarr is not configured."

        wanted = self.sonarr.get_wanted()
        if "error" in wanted:
            return f"❌ Error fetching wanted: {wanted['error']}"

        records = wanted.get("records", [])
        if not records:
            return "🎉 No wanted episodes! Everything is downloaded."

        response = "📺 Wanted/Missing Episodes:\n\n"
        for ep in records[:5]:
            title = ep.get('title', 'Unknown')
            season = ep.get('seasonNumber', 0)
            episode = ep.get('episodeNumber', 0)
            response += f"• {title} S{season:02d}E{episode:02d}\n"

        if len(records) > 5:
            response += f"\n... and {len(records) - 5} more"

        return response


# OpenClaw skill entry point
def skill_entry(message: str, context: dict = None) -> str:
    """
    OpenClaw skill entry point.

    Args:
        message: User message
        context: Additional context

    Returns:
        Response message
    """
    skill = RadarrSonarrSkill()
    return skill.handle(message, context)


if __name__ == "__main__":
    # Test the skill
    import sys

    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
    else:
        message = input("Enter message: ")

    print(f"\nYou: {message}\n")
    print(f"Bot: {skill_entry(message)}")
