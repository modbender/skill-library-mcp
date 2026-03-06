"""
Radarr API Wrapper

Provides a clean interface for Radarr operations.
"""

import os
import json
import urllib.request
import urllib.parse
import urllib.error
import logging

logger = logging.getLogger(__name__)


class RadarrClient:
    """Client for Radarr API operations."""

    def __init__(
        self,
        url: str = None,
        api_key: str = None,
        root_folder: str = None,
        quality_profile: str = None,
        language_profile: str = None,
    ):
        """
        Initialize Radarr client.

        Args:
            url: Radarr server URL (default: RADARR_URL env var)
            api_key: Radarr API key (default: RADARR_API_KEY env var)
            root_folder: Default root folder for movies
            quality_profile: Default quality profile name
            language_profile: Default language profile name
        """
        self.url = url or os.environ.get("RADARR_URL", "http://localhost:7878")
        self.api_key = api_key or os.environ.get("RADARR_API_KEY")
        self.root_folder = root_folder or os.environ.get(
            "RADARR_ROOT_FOLDER", "/data/movies"
        )
        self.quality_profile = quality_profile or os.environ.get(
            "RADARR_QUALITY_PROFILE", "HD-1080p"
        )
        self.language_profile = language_profile or os.environ.get(
            "RADARR_LANGUAGE_PROFILE", "English"
        )

        if not self.api_key:
            raise ValueError("RADARR_API_KEY is required")

    def _request(self, endpoint: str, method: str = "GET", data: dict = None):
        """Make API request to Radarr."""
        url = f"{self.url}/api/v3{endpoint}&apikey={self.api_key}" if "?" in endpoint else f"{self.url}/api/v3{endpoint}?apikey={self.api_key}"
        
        headers = {"X-Api-Key": self.api_key}
        
        req = urllib.request.Request(url, headers=headers, method=method)
        if data:
            req.data = json.dumps(data).encode('utf-8')
            req.add_header('Content-Type', 'application/json')
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                content = response.read().decode('utf-8')
                return json.loads(content) if content else {"status": "ok"}
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else ""
            logger.error(f"Radarr HTTP {e.code}: {e.reason} - {error_body}")
            return {"error": f"HTTP {e.code}: {e.reason}"}
        except Exception as e:
            logger.error(f"Radarr API error: {e}")
            return {"error": str(e)}

    def test_connection(self) -> dict:
        """Test connection to Radarr."""
        return self._request("/system/status")

    def search(self, query: str, limit: int = 10):
        """
        Search for movies.

        Args:
            query: Search query
            limit: Maximum results to return

        Returns:
            List of matching movies
        """
        endpoint = f"/movie/lookup?term={urllib.parse.quote(query)}"
        results = self._request(endpoint)
        return results[:limit] if isinstance(results, list) else []

    def get_movie(self, tmdb_id: int):
        """Get movie details by TMDB ID."""
        return self._request(f"/movie/lookup?term=tmdb:{tmdb_id}")

    def add(
        self,
        tmdb_id: int,
        quality_profile_id: int = None,
        language_profile_id: int = None,
        search: bool = True,
    ):
        """
        Add a movie to Radarr.

        Args:
            tmdb_id: The Movie Database ID
            quality_profile_id: Quality profile ID (optional, uses default)
            language_profile_id: Language profile ID (optional, uses default)
            search: Whether to search for the movie after adding

        Returns:
            Added movie data or error
        """
        # Get movie info first
        movie_info = self.get_movie(tmdb_id)
        if isinstance(movie_info, list) and movie_info:
            movie = movie_info[0]
        else:
            return {"error": f"Movie not found: TMDB {tmdb_id}"}

        data = {
            "tmdbId": tmdb_id,
            "qualityProfileId": quality_profile_id or self._get_quality_profile_id(),
            "languageProfileId": language_profile_id or self._get_language_profile_id(),
            "rootFolderPath": self.root_folder,
            "monitored": True,
            "addOptions": {"searchForMovie": search},
        }

        return self._request("/movie", method="POST", data=data)

    def get_queue(self, page: int = 1):
        """Get download queue."""
        return self._request(f"/queue?page={page}")

    def get_wanted(self, page: int = 1):
        """Get missing/wanted movies."""
        return self._request(f"/wanted/missing?page={page}")

    def delete(self, movie_id: int, delete_files: bool = False):
        """Delete a movie from Radarr."""
        return self._request(
            f"/movie/{movie_id}?deleteFiles={str(delete_files).lower()}",
            method="DELETE",
        )

    def _get_quality_profiles(self):
        """Get available quality profiles."""
        return self._request("/qualityprofile")

    def _get_quality_profile_id(self, name: str = None):
        """Get quality profile ID by name."""
        profiles = self._get_quality_profiles()
        name = name or self.quality_profile
        if isinstance(profiles, list):
            for p in profiles:
                if p.get("name", "").lower() == name.lower():
                    return p.get("id")
        return 1  # Default to first profile

    def _get_language_profiles(self):
        """Get available language profiles."""
        return self._request("/languageprofile")

    def _get_language_profile_id(self, name: str = None):
        """Get language profile ID by name."""
        profiles = self._get_language_profiles()
        name = name or self.language_profile
        if isinstance(profiles, list):
            for p in profiles:
                if p.get("name", "").lower() == name.lower():
                    return p.get("id")
        return 1  # Default to English
