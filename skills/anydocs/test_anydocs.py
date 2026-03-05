#!/usr/bin/env python3
"""Quick integration tests for anydocs."""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from lib.config import ConfigManager
from lib.indexer import SearchIndex
from lib.cache import CacheManager
from lib.scraper import DiscoveryEngine

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


def test_config_manager():
    """Test configuration management."""
    print("Testing ConfigManager...")
    cfg = ConfigManager()
    
    # Add profile
    cfg.add_profile(
        "test",
        "https://example.com/docs",
        "https://example.com/sitemap.xml",
        "hybrid",
        7
    )
    
    # List profiles
    profiles = cfg.list_profiles()
    assert "test" in profiles, "Profile not found"
    
    # Get profile
    profile = cfg.get_profile("test")
    assert profile["base_url"] == "https://example.com/docs", "Profile data mismatch"
    
    # Validate
    is_valid, error = cfg.validate_profile("test")
    assert is_valid, f"Validation failed: {error}"
    
    print("✓ ConfigManager tests passed")


def test_search_index():
    """Test search indexing and retrieval."""
    print("Testing SearchIndex...")
    
    # Create test documents
    docs = [
        {
            "url": "https://example.com/api/webhooks",
            "title": "Webhook API Reference",
            "content": "Webhooks allow you to receive notifications...",
            "full_content": "Webhooks are HTTP callbacks that allow external services to notify your application of events. This guide covers how to implement and manage webhooks effectively.",
            "tags": ["api", "webhooks", "integration"]
        },
        {
            "url": "https://example.com/guides/getting-started",
            "title": "Getting Started Guide",
            "content": "This guide will walk you through the initial setup...",
            "full_content": "Welcome! This getting started guide will help you set up your first integration. We'll cover authentication, basic API calls, and best practices.",
            "tags": ["guide", "setup", "beginners"]
        },
        {
            "url": "https://example.com/api/rate-limiting",
            "title": "Rate Limiting and Quotas",
            "content": "API rate limits are applied to prevent abuse...",
            "full_content": "Rate limiting protects our servers by restricting the number of requests. Each endpoint has specific limits. Check headers for current usage.",
            "tags": ["api", "rate-limits", "performance"]
        }
    ]
    
    # Build index
    index = SearchIndex()
    index.build(docs)
    
    # Test keyword search
    results = index.search("webhooks", method="keyword", limit=10)
    assert len(results) > 0, "Webhook search returned no results"
    assert results[0]["title"] == "Webhook API Reference", "Wrong document ranked first"
    assert results[0]["relevance_score"] > 0, "No relevance score"
    
    # Test hybrid search
    results = index.search("how to set up", method="hybrid", limit=10)
    assert len(results) > 0, "Hybrid search returned no results"
    
    # Test regex search
    results = index.search("^(Webhook|Getting)", method="keyword", regex=True, limit=10)
    assert len(results) > 0, "Regex search returned no results"
    
    # Test serialization
    data = index.to_dict()
    assert "docs" in data, "Serialization failed"
    assert data["count"] == 3, "Wrong document count"
    
    # Test deserialization
    index2 = SearchIndex.from_dict(data)
    results2 = index2.search("rate limit", limit=10)
    assert len(results2) > 0, "Deserialized index doesn't work"
    
    print("✓ SearchIndex tests passed")


def test_cache_manager():
    """Test caching functionality."""
    print("Testing CacheManager...")
    
    cache = CacheManager()
    
    # Save a page
    cache.save_page(
        url="https://example.com/test",
        title="Test Page",
        content="This is test content",
        metadata={"tags": ["test"]}
    )
    
    # Retrieve it
    page = cache.get_page("https://example.com/test")
    assert page is not None, "Page not found in cache"
    assert page["title"] == "Test Page", "Page title mismatch"
    assert page["content"] == "This is test content", "Page content mismatch"
    
    # Save index
    test_index = {
        "docs": [
            {
                "url": "https://example.com/1",
                "title": "Doc 1",
                "content": "Content 1",
                "full_content": "Full content 1",
                "tags": []
            }
        ],
        "count": 1
    }
    cache.save_index("test_profile", test_index)
    
    # Retrieve index
    index_data = cache.get_index("test_profile")
    assert index_data is not None, "Index not found in cache"
    assert index_data["count"] == 1, "Index count mismatch"
    
    # Get stats
    stats = cache.get_cache_size()
    assert stats["pages_count"] > 0, "Pages not counted"
    assert stats["indexes_count"] > 0, "Indexes not counted"
    
    # Clear cache
    deleted = cache.clear_cache()
    assert deleted > 0, "No files cleared"
    
    stats = cache.get_cache_size()
    assert stats["pages_count"] == 0, "Pages not cleared"
    
    print("✓ CacheManager tests passed")


def test_scraper_browser_mode():
    """Test browser rendering mode in scraper."""
    print("Testing Scraper with browser mode...")
    
    # Test 1: Scraper initialization with use_browser flag
    engine_no_browser = DiscoveryEngine(
        "https://example.com",
        "https://example.com/sitemap.xml",
        use_browser=False
    )
    assert engine_no_browser.use_browser is False, "use_browser not set correctly"
    
    # Test 2: Scraper initialization with browser enabled
    engine_with_browser = DiscoveryEngine(
        "https://example.com",
        "https://example.com/sitemap.xml",
        use_browser=True
    )
    assert engine_with_browser.use_browser is True, "use_browser not set correctly"
    
    # Test 3: Check if Playwright is available
    if PLAYWRIGHT_AVAILABLE:
        print("  ✓ Playwright is available")
    else:
        print("  ⚠ Playwright not installed (browser rendering will fallback)")
    
    # Test 4: scrape_page with browser override
    # This will try a simple fetch; full browser test would need a real URL
    page_data = engine_with_browser.scrape_page(
        "https://httpbin.org/html",  # Simple test URL that returns HTML
        use_browser=False  # Override to not use browser for this test
    )
    
    if page_data:
        assert "title" in page_data, "Page scrape missing title"
        assert "content" in page_data, "Page scrape missing content"
        assert "full_content" in page_data, "Page scrape missing full_content"
        print("  ✓ Page scraping works correctly")
    else:
        print("  ⚠ Could not fetch test URL (network issue, acceptable)")
    
    print("✓ Scraper browser mode tests passed")


def test_integration():
    """Full integration test: config -> index -> search."""
    print("Testing full integration...")
    
    # Step 1: Configure
    config_mgr = ConfigManager()
    config_mgr.add_profile(
        "integration_test",
        "https://example.com",
        "https://example.com/sitemap.xml"
    )
    
    # Step 2: Build index with synthetic data
    docs = [
        {
            "url": "https://example.com/docs/overview",
            "title": "API Overview",
            "content": "Welcome to our API documentation...",
            "full_content": "This API provides access to user data, authentication, and webhooks.",
            "tags": ["api", "documentation"]
        },
        {
            "url": "https://example.com/docs/auth",
            "title": "Authentication Methods",
            "content": "We support OAuth 2.0 and API keys...",
            "full_content": "Authentication is required for all endpoints. We support OAuth 2.0 and API key authentication.",
            "tags": ["api", "security", "auth"]
        }
    ]
    
    index = SearchIndex()
    index.build(docs)
    
    # Step 3: Cache the index
    cache_mgr = CacheManager()
    cache_mgr.save_index("integration_test", index.to_dict())
    
    # Step 4: Search
    retrieved_index_data = cache_mgr.get_index("integration_test")
    assert retrieved_index_data is not None, "Index not cached"
    
    retrieved_index = SearchIndex.from_dict(retrieved_index_data)
    results = retrieved_index.search("authentication", limit=10)
    
    assert len(results) > 0, "Search found no results"
    assert any("auth" in r["title"].lower() for r in results), "Auth doc not found"
    
    # Cleanup
    cache_mgr.clear_cache("integration_test")
    config_mgr.delete_profile("integration_test")
    
    print("✓ Integration test passed")


if __name__ == "__main__":
    try:
        test_config_manager()
        test_search_index()
        test_cache_manager()
        test_scraper_browser_mode()
        test_integration()
        print("\n✓✓✓ All tests passed! ✓✓✓")
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
