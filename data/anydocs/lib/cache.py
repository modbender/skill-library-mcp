"""Caching layer for anydocs. Handles TTL-based cache expiration and storage."""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
import hashlib
from typing import Optional, Dict, Any, List


class CacheManager:
    """Manages file-based caching with TTL support."""
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize cache manager.
        
        Args:
            cache_dir: Cache directory. Defaults to ~/.anydocs/cache
        """
        if cache_dir is None:
            cache_dir = os.path.expanduser("~/.anydocs/cache")
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.pages_dir = self.cache_dir / "pages"
        self.pages_dir.mkdir(exist_ok=True)
        self.index_dir = self.cache_dir / "indexes"
        self.index_dir.mkdir(exist_ok=True)
        self.metadata_file = self.cache_dir / "metadata.json"
    
    def _get_cache_key(self, url: str) -> str:
        """Generate a unique cache key for a URL."""
        return hashlib.sha256(url.encode()).hexdigest()
    
    def save_page(self, url: str, title: str, content: str, 
                  metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Save a scraped page to cache.
        
        Args:
            url: Page URL
            title: Page title
            content: Page content (HTML or text)
            metadata: Optional metadata dict (tags, etc.)
        
        Returns:
            Cache key
        """
        cache_key = self._get_cache_key(url)
        page_data = {
            "url": url,
            "title": title,
            "content": content,
            "metadata": metadata or {},
            "cached_at": datetime.now().isoformat(),
        }
        
        page_file = self.pages_dir / f"{cache_key}.json"
        with open(page_file, "w") as f:
            json.dump(page_data, f, indent=2)
        
        return cache_key
    
    def get_page(self, url: str, ttl_days: int = 7) -> Optional[Dict[str, Any]]:
        """
        Retrieve a cached page if still valid (within TTL).
        
        Args:
            url: Page URL
            ttl_days: Cache TTL in days
        
        Returns:
            Page data dict or None if expired/missing
        """
        cache_key = self._get_cache_key(url)
        page_file = self.pages_dir / f"{cache_key}.json"
        
        if not page_file.exists():
            return None
        
        try:
            with open(page_file, "r") as f:
                page_data = json.load(f)
            
            cached_at = datetime.fromisoformat(page_data["cached_at"])
            age = datetime.now() - cached_at
            
            if age > timedelta(days=ttl_days):
                # Expired
                page_file.unlink()
                return None
            
            return page_data
        except Exception:
            return None
    
    def save_index(self, profile: str, index_data: Dict[str, Any]) -> None:
        """Save search index for a profile."""
        index_file = self.index_dir / f"{profile}_index.json"
        index_data["indexed_at"] = datetime.now().isoformat()
        with open(index_file, "w") as f:
            json.dump(index_data, f, indent=2)
    
    def get_index(self, profile: str, ttl_days: int = 7) -> Optional[Dict[str, Any]]:
        """Retrieve cached search index if valid."""
        index_file = self.index_dir / f"{profile}_index.json"
        
        if not index_file.exists():
            return None
        
        try:
            with open(index_file, "r") as f:
                index_data = json.load(f)
            
            indexed_at = datetime.fromisoformat(index_data["indexed_at"])
            age = datetime.now() - indexed_at
            
            if age > timedelta(days=ttl_days):
                index_file.unlink()
                return None
            
            return index_data
        except Exception:
            return None
    
    def clear_cache(self, profile: Optional[str] = None) -> int:
        """
        Clear cache. If profile is specified, only clear that profile's data.
        
        Returns:
            Number of files deleted
        """
        deleted = 0
        
        if profile:
            # Clear specific profile index
            index_file = self.index_dir / f"{profile}_index.json"
            if index_file.exists():
                index_file.unlink()
                deleted += 1
        else:
            # Clear everything
            for f in self.pages_dir.glob("*.json"):
                f.unlink()
                deleted += 1
            for f in self.index_dir.glob("*.json"):
                f.unlink()
                deleted += 1
        
        return deleted
    
    def get_cache_size(self) -> Dict[str, Any]:
        """Get cache size stats."""
        pages = list(self.pages_dir.glob("*.json"))
        indexes = list(self.index_dir.glob("*.json"))
        
        total_size = sum(f.stat().st_size for f in pages + indexes) / (1024 * 1024)  # MB
        
        return {
            "pages_count": len(pages),
            "indexes_count": len(indexes),
            "total_size_mb": round(total_size, 2),
            "cache_dir": str(self.cache_dir),
        }
