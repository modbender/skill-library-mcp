"""
Sonarr API Wrapper

Provides a clean interface for Sonarr operations.
"""

import os
import json
import urllib.request
import urllib.parse
import urllib.error
import logging

logger = logging.getLogger(__name__)


class SonarrClient:
    """Client for Sonarr API operations."""

    def __init__(
        self,
        url: str = None,
        api_key: str = None,
        root_folder: str = None,
        quality_profile: str = None,
        language_profile: str = None,
    ):
        """
        Initialize Sonarr client.

        Args:
            url: Sonarr server URL (default: SONARR_URL env var)
            api_key: Sonarr API key (default: SONARR_API_KEY env var)
            root_folder: Default root folder for TV shows
            quality_profile: Default quality profile name
            language_profile: Default language profile name
        """
        self.url = url or os.environ.get("SONARR_URL", "http://localhost:8989")
        self.api_key = api_key or os.environ.get("SONARR_API_KEY")
        self.root_folder = root_folder or os.environ.get(
            "SONARR_ROOT_FOLDER", "/data/tv"
        )
        self.quality_profile = quality_profile or os.environ.get(
            "SONARR_QUALITY_PROFILE", "HD-1080p"
        )
        self.language_profile = language_profile or os.environ.get(
            "SONARR_LANGUAGE_PROFILE", "English"
        )

        if not self.api_key:
            raise ValueError("SONARR_API_KEY is required")

    def _request(self, endpoint: str, method: str = "GET", data: dict = None):
        """Make API request to Sonarr."""
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
            logger.error(f"Sonarr HTTP {e.code}: {e.reason} - {error_body}")
            return {"error": f"HTTP {e.code}: {e.reason}"}
        except Exception as e:
            logger.error(f"Sonarr API error: {e}")
            return {"error": str(e)}

    def test_connection(self) -> dict:
        """Test connection to Sonarr."""
        return self._request("/system/status")

    def search(self, query: str, limit: int = 10):
        """
        Search for TV series.

        Args:
            query: Search query
            limit: Maximum results to return

        Returns:
            List of matching series
        """
        endpoint = f"/series/lookup?term={urllib.parse.quote(query)}"
        results = self._request(endpoint)
        return results[:limit] if isinstance(results, list) else []

    def get_series(self, tvdb_id: int):
        """Get series details by TVDB ID."""
        return self._request(f"/series/lookup?term=tvdb:{tvdb_id}")

    def add(
        self,
        tvdb_id: int,
        quality_profile_id: int = None,
        language_profile_id: int = None,
        search: bool = True,
        monitored: bool = True,
        season_folder: bool = True,
    ):
        """
        Add a TV series to Sonarr.

        Args:
            tvdb_id: The TV Database ID
            quality_profile_id: Quality profile ID (optional, uses default)
            language_profile_id: Language profile ID (optional, uses default)
            search: Whether to search for episodes after adding
            monitored: Whether to monitor the series
            season_folder: Whether to create season folders

        Returns:
            Added series data or error
        """
        # Get series info first
        series_info = self.get_series(tvdb_id)
        if isinstance(series_info, list) and series_info:
            series = series_info[0]
        else:
            return {"error": f"Series not found: TVDB {tvdb_id}"}

        data = {
            "tvdbId": tvdb_id,
            "qualityProfileId": quality_profile_id or self._get_quality_profile_id(),
            "languageProfileId": language_profile_id or self._get_language_profile_id(),
            "rootFolderPath": self.root_folder,
            "monitored": monitored,
            "seasonFolder": season_folder,
            "addOptions": {"searchForMissingEpisodes": search},
        }

        return self._request("/series", method="POST", data=data)

    def add_season(self, series_id: int, season_number: int, search: bool = True):
        """
        Add a specific season to an existing series.

        Args:
            series_id: Sonarr series ID
            season_number: Season number to add
            search: Whether to search for episodes

        Returns:
            Response data
        """
        data = {
            "seriesId": series_id,
            "seasonNumber": season_number,
            "monitored": True,
            "addOptions": {"searchForMissingEpisodes": search},
        }
        return self._request("/season", method="POST", data=data)

    def get_queue(self, page: int = 1):
        """Get download queue."""
        return self._request(f"/queue?page={page}")

    def get_wanted(self, page: int = 1):
        """Get missing/wanted episodes."""
        return self._request(f"/wanted/missing?page={page}")

    def delete(self, series_id: int, delete_files: bool = False):
        """Delete a series from Sonarr."""
        return self._request(
            f"/series/{series_id}?deleteFiles={str(delete_files).lower()}",
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
