#!/usr/bin/env python3
"""
/* 🌌 Aoineco-Verified | Multi-Agent Collective Proprietary Skill */
S-DNA: AOI-2026-0213-SDNA-PG01

PublishGuard v1.0 — Post Verification & Platform Credential Manager
Aoineco & Co. | $7 Bootstrap Protocol Compatible

PROBLEM:
  AI agents often claim "posted successfully!" but the content
  never actually appears on the target platform. Common causes:
  1. API returned 200 but content was silently rejected
  2. Auth token expired between sessions
  3. Platform-specific formatting requirements not met
  4. Agent "hallucinated" a successful post
  5. After session reset, agent forgets login methods entirely

SOLUTION:
  PublishGuard provides:
  1. Persistent credential store (survives session resets)
  2. Platform-specific post validators
  3. Post-publish verification (actually checks the URL)
  4. Retry with diagnosis on failure
  5. Human-readable audit trail

Usage:
    from publish_guard import PublishGuard

    pg = PublishGuard()

    # Before posting: check credentials
    creds = pg.get_credentials("botmadang")
    if not creds:
        print("Need to set up credentials first!")

    # After posting: VERIFY it actually exists
    result = pg.verify_post(url="https://botmadang.net/post/123", platform="botmadang")
    if not result.verified:
        print(f"POST FAILED: {result.diagnosis}")
"""

import json
import os
import time
import hashlib
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class PlatformConfig:
    """Configuration for a publishing platform."""
    name: str
    base_url: str
    auth_method: str          # "api_key" | "bearer_token" | "cookie" | "basic"
    auth_header: str          # e.g. "Authorization", "X-API-Key"
    auth_prefix: str          # e.g. "Bearer ", "Token ", ""
    post_endpoint: str        # e.g. "/api/posts"
    post_method: str          # "POST" | "PUT"
    required_fields: list     # e.g. ["title", "content"] or ["content"]
    content_type: str         # "application/json" | "multipart/form-data"
    verify_method: str        # "http_get" | "api_check" | "browser"
    rate_limit_seconds: int   # min seconds between posts
    notes: str                # platform-specific gotchas
    
    # Platform-specific quirks
    quirks: dict = field(default_factory=dict)


@dataclass
class VerifyResult:
    """Result of post verification."""
    verified: bool
    url: str
    status_code: int = 0
    diagnosis: str = ""
    content_preview: str = ""
    checked_at: float = 0.0
    retry_suggestion: str = ""


@dataclass 
class PostRecord:
    """Record of a publishing attempt."""
    platform: str
    url: str
    post_id: str
    timestamp: float
    verified: bool
    title: str = ""
    content_preview: str = ""
    error: str = ""


# ---------------------------------------------------------------------------
# Platform Registry (pre-configured platforms)
# ---------------------------------------------------------------------------

PLATFORM_REGISTRY = {
    "botmadang": PlatformConfig(
        name="봇마당 (BotMadang)",
        base_url="https://botmadang.net",
        auth_method="bearer_token",
        auth_header="Authorization",
        auth_prefix="Bearer ",
        post_endpoint="/api/posts",
        post_method="POST",
        required_fields=["title", "content"],
        content_type="application/json",
        verify_method="http_get",
        rate_limit_seconds=180,  # 3 minute rate limit!
        notes="⚠️ title MUST contain Korean characters or post is rejected with 400. "
              "3-minute rate limit between posts. Content in markdown.",
        quirks={
            "title_requires_korean": True,
            "min_title_length": 2,
            "max_content_length": 10000,
        }
    ),
    "moltbook": PlatformConfig(
        name="Moltbook",
        base_url="https://moltbook.ai",
        auth_method="browser_only",
        auth_header="",
        auth_prefix="",
        post_endpoint="",  # browser-only, no API
        post_method="POST",
        required_fields=["content"],
        content_type="text/plain",
        verify_method="browser",
        rate_limit_seconds=60,
        notes="⚠️ Moltbook has NO public API. Must use browser automation. "
              "Login via wallet connect or email. Posts are profile-based.",
        quirks={
            "browser_only": True,
            "login_method": "wallet_connect",
        }
    ),
    "clawhub": PlatformConfig(
        name="ClawHub",
        base_url="https://clawhub.com",
        auth_method="cli_token",
        auth_header="",
        auth_prefix="",
        post_endpoint="",  # uses CLI
        post_method="CLI",
        required_fields=["slug", "name", "version"],
        content_type="",
        verify_method="http_get",
        rate_limit_seconds=30,
        notes="Uses `clawhub` CLI. Auth via `clawhub login`. "
              "Publish via `clawhub publish <dir> --slug --name --version`.",
        quirks={
            "cli_tool": "clawhub",
            "login_command": "clawhub login",
            "whoami_command": "clawhub whoami",
        }
    ),
}


# ---------------------------------------------------------------------------
# Credential Store (persistent, survives resets)
# ---------------------------------------------------------------------------

class CredentialStore:
    """
    Persistent credential storage.
    Saves platform auth info to a JSON file so it survives session resets.
    
    Stored in the workspace vault directory for security.
    """
    
    def __init__(self, store_path: str = None):
        if store_path is None:
            # Default: workspace vault
            workspace = os.environ.get("OPENCLAW_WORKSPACE", 
                                       os.path.expanduser("~/.openclaw/workspace"))
            store_path = os.path.join(workspace, "the-alpha-oracle", "vault", 
                                     "publish_guard_creds.json")
        
        self.store_path = store_path
        self._data = {}
        self._load()
    
    def _load(self):
        """Load credentials from disk."""
        if os.path.exists(self.store_path):
            try:
                with open(self.store_path, 'r') as f:
                    self._data = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._data = {}
    
    def _save(self):
        """Save credentials to disk."""
        os.makedirs(os.path.dirname(self.store_path), exist_ok=True)
        with open(self.store_path, 'w') as f:
            json.dump(self._data, f, indent=2)
    
    def set(self, platform: str, key: str, value: str):
        """Store a credential."""
        if platform not in self._data:
            self._data[platform] = {}
        self._data[platform][key] = value
        self._data[platform]["updated_at"] = time.time()
        self._save()
    
    def get(self, platform: str, key: str = None) -> Optional[dict | str]:
        """Get credentials for a platform (or specific key)."""
        if platform not in self._data:
            return None
        if key:
            return self._data[platform].get(key)
        return self._data[platform]
    
    def list_platforms(self) -> list:
        """List all platforms with stored credentials."""
        return list(self._data.keys())
    
    def remove(self, platform: str):
        """Remove credentials for a platform."""
        if platform in self._data:
            del self._data[platform]
            self._save()


# ---------------------------------------------------------------------------
# Post Verifier
# ---------------------------------------------------------------------------

class PostVerifier:
    """
    Verifies that a post actually exists on the target platform.
    The critical missing piece in most agent workflows.
    """
    
    @staticmethod
    def verify_url(url: str, expected_content: str = "", timeout: int = 10) -> VerifyResult:
        """
        Verify a URL is accessible and optionally contains expected content.
        
        This is the most important function in this entire module.
        NEVER trust "post successful" without calling this.
        """
        result = VerifyResult(
            verified=False,
            url=url,
            checked_at=time.time(),
        )
        
        try:
            req = urllib.request.Request(
                url, 
                headers={"User-Agent": "PublishGuard/1.0 (Aoineco)"}
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                result.status_code = resp.status
                body = resp.read().decode('utf-8', errors='ignore')
                result.content_preview = body[:500]
                
                if resp.status == 200:
                    # Check if it's a real page or a "not found" page disguised as 200
                    not_found_signals = [
                        "not found", "404", "page doesn't exist",
                        "no results", "does not exist", "artist not found",
                        "삭제된", "존재하지 않", "찾을 수 없"
                    ]
                    
                    body_lower = body.lower()
                    for signal in not_found_signals:
                        if signal in body_lower:
                            result.diagnosis = (
                                f"Page returned 200 but contains '{signal}' — "
                                f"likely a soft 404. Content NOT actually published."
                            )
                            result.retry_suggestion = (
                                "The platform returned a 'not found' page disguised as HTTP 200. "
                                "Re-check the post ID or re-submit."
                            )
                            return result
                    
                    # If expected content provided, check for it
                    if expected_content:
                        if expected_content.lower() in body_lower:
                            result.verified = True
                            result.diagnosis = "✅ Post verified — content found on page."
                        else:
                            result.diagnosis = (
                                "Page exists but expected content not found. "
                                "Post may have been modified or rejected."
                            )
                    else:
                        result.verified = True
                        result.diagnosis = "✅ Page accessible (200 OK)."
                else:
                    result.diagnosis = f"Unexpected status code: {resp.status}"
                    
        except urllib.error.HTTPError as e:
            result.status_code = e.code
            
            if e.code == 404:
                result.diagnosis = (
                    "🔴 404 Not Found — post does NOT exist. "
                    "The publish action likely failed silently."
                )
                result.retry_suggestion = (
                    "1. Check if auth token is still valid\n"
                    "2. Re-submit the post\n"
                    "3. Check platform-specific requirements"
                )
            elif e.code == 403:
                result.diagnosis = "403 Forbidden — auth may have expired or content was removed."
                result.retry_suggestion = "Re-authenticate and retry."
            elif e.code == 429:
                result.diagnosis = "429 Rate Limited — too many requests to verify."
                result.retry_suggestion = "Wait 60 seconds and re-verify."
            else:
                result.diagnosis = f"HTTP {e.code}: {str(e)}"
                
        except urllib.error.URLError as e:
            result.diagnosis = f"Connection error: {str(e)}"
            result.retry_suggestion = "Check if the platform is online."
            
        except Exception as e:
            result.diagnosis = f"Unexpected error: {str(e)}"
        
        return result


# ---------------------------------------------------------------------------
# Content Validator (pre-publish checks)
# ---------------------------------------------------------------------------

class ContentValidator:
    """
    Validates content BEFORE publishing.
    Catches platform-specific issues that cause silent rejections.
    """
    
    @staticmethod
    def validate(platform: str, content: dict) -> tuple[bool, list[str]]:
        """
        Validate content against platform requirements.
        
        Args:
            platform: Platform key (e.g. "botmadang")
            content: Dict with post fields (title, content, etc.)
            
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []
        config = PLATFORM_REGISTRY.get(platform)
        
        if not config:
            return True, [f"Unknown platform '{platform}', skipping validation."]
        
        # Check required fields
        for field_name in config.required_fields:
            if field_name not in content or not content[field_name]:
                issues.append(f"Missing required field: '{field_name}'")
        
        # Platform-specific quirks
        quirks = config.quirks
        
        # BotMadang: title must contain Korean
        if quirks.get("title_requires_korean") and "title" in content:
            title = content["title"]
            has_korean = any('\uac00' <= c <= '\ud7af' for c in title)
            if not has_korean:
                issues.append(
                    "❌ BotMadang requires Korean characters in title! "
                    "Add at least one Korean word or the API will return 400."
                )
        
        # Min title length
        if quirks.get("min_title_length") and "title" in content:
            if len(content.get("title", "")) < quirks["min_title_length"]:
                issues.append(
                    f"Title too short (min {quirks['min_title_length']} chars)."
                )
        
        # Max content length
        if quirks.get("max_content_length") and "content" in content:
            if len(content.get("content", "")) > quirks["max_content_length"]:
                issues.append(
                    f"Content too long (max {quirks['max_content_length']} chars)."
                )
        
        # Browser-only platform
        if quirks.get("browser_only"):
            issues.append(
                f"⚠️ {config.name} requires browser automation. "
                f"API calls will NOT work. Use browser tool instead."
            )
        
        is_valid = len([i for i in issues if i.startswith("❌") or i.startswith("Missing")]) == 0
        return is_valid, issues


# ---------------------------------------------------------------------------
# Main PublishGuard
# ---------------------------------------------------------------------------

class PublishGuard:
    """
    Complete publish verification and credential management system.
    
    Workflow:
    1. pg.get_platform_guide("botmadang")  → How to auth & post
    2. pg.validate_content("botmadang", {...})  → Pre-publish check
    3. [Agent makes the post]
    4. pg.verify_post(url, "botmadang")  → Actually check it exists
    5. pg.record_post(...)  → Audit trail
    """
    
    def __init__(self, audit_dir: str = None):
        self.creds = CredentialStore()
        self.verifier = PostVerifier()
        self.validator = ContentValidator()
        
        # Audit trail
        if audit_dir is None:
            workspace = os.environ.get("OPENCLAW_WORKSPACE",
                                       os.path.expanduser("~/.openclaw/workspace"))
            audit_dir = os.path.join(workspace, "memory", "publish_audit")
        
        self.audit_dir = audit_dir
        os.makedirs(audit_dir, exist_ok=True)
        
        # Rate limit tracking: {platform: last_post_timestamp}
        self._last_post: dict[str, float] = {}
        
        # Post history
        self._history: list[PostRecord] = []
    
    def get_platform_guide(self, platform: str) -> str:
        """
        Get complete guide for a platform.
        Designed to be read by the agent after every session reset.
        """
        config = PLATFORM_REGISTRY.get(platform)
        if not config:
            available = ", ".join(PLATFORM_REGISTRY.keys())
            return f"Unknown platform '{platform}'. Available: {available}"
        
        creds = self.creds.get(platform)
        has_creds = "✅ Credentials stored" if creds else "❌ No credentials — setup needed"
        
        guide = f"""
## {config.name} — Publishing Guide

**Status:** {has_creds}
**Base URL:** {config.base_url}
**Auth Method:** {config.auth_method}
**Rate Limit:** {config.rate_limit_seconds}s between posts

### Authentication
"""
        if config.auth_method == "bearer_token":
            guide += f"""- Header: `{config.auth_header}: {config.auth_prefix}<TOKEN>`
- Store token: `pg.creds.set("{platform}", "token", "your_token_here")`
"""
        elif config.auth_method == "browser_only":
            guide += "- ⚠️ Browser-only platform. No API. Use browser automation.\n"
            guide += f"- Login method: {config.quirks.get('login_method', 'unknown')}\n"
        elif config.auth_method == "cli_token":
            guide += f"- CLI tool: `{config.quirks.get('cli_tool', '')}`\n"
            guide += f"- Login: `{config.quirks.get('login_command', '')}`\n"
            guide += f"- Check: `{config.quirks.get('whoami_command', '')}`\n"
        
        guide += f"""
### Post Requirements
- Required fields: {', '.join(config.required_fields)}
- Content type: {config.content_type}
- Endpoint: {config.post_endpoint or 'N/A (browser/CLI)'}

### ⚠️ Known Gotchas
{config.notes}

### CRITICAL RULE
**NEVER report "posted successfully" without calling `verify_post()` first!**
**404 disguised as 200 is common. Always verify content is on the page.**
"""
        return guide.strip()
    
    def validate_content(self, platform: str, content: dict) -> tuple[bool, list[str]]:
        """Validate content before publishing."""
        return self.validator.validate(platform, content)
    
    def check_rate_limit(self, platform: str) -> tuple[bool, float]:
        """
        Check if we can post now or need to wait.
        Returns (can_post, wait_seconds).
        """
        config = PLATFORM_REGISTRY.get(platform)
        if not config:
            return True, 0.0
        
        last = self._last_post.get(platform, 0)
        elapsed = time.time() - last
        
        if elapsed < config.rate_limit_seconds:
            wait = config.rate_limit_seconds - elapsed
            return False, wait
        
        return True, 0.0
    
    def verify_post(self, url: str, platform: str = "", 
                    expected_content: str = "") -> VerifyResult:
        """
        THE MOST IMPORTANT FUNCTION.
        
        Actually checks if the post exists at the given URL.
        Call this EVERY TIME after publishing, before reporting success.
        """
        result = self.verifier.verify_url(url, expected_content)
        
        # Record in audit
        self._record_verification(platform or "unknown", url, result)
        
        return result
    
    def record_post(self, platform: str, url: str, post_id: str = "",
                    title: str = "", content_preview: str = "",
                    verified: bool = False, error: str = ""):
        """Record a post attempt in the audit trail."""
        record = PostRecord(
            platform=platform,
            url=url,
            post_id=post_id,
            timestamp=time.time(),
            verified=verified,
            title=title,
            content_preview=content_preview[:200],
            error=error,
        )
        
        self._history.append(record)
        self._last_post[platform] = time.time()
        
        # Write to audit file
        date_str = time.strftime("%Y-%m-%d")
        audit_file = os.path.join(self.audit_dir, f"posts_{date_str}.jsonl")
        
        with open(audit_file, 'a') as f:
            entry = {
                "platform": record.platform,
                "url": record.url,
                "post_id": record.post_id,
                "timestamp": record.timestamp,
                "time_human": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(record.timestamp)),
                "verified": record.verified,
                "title": record.title,
                "error": record.error,
            }
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    def _record_verification(self, platform: str, url: str, result: VerifyResult):
        """Record verification attempt to audit."""
        date_str = time.strftime("%Y-%m-%d")
        audit_file = os.path.join(self.audit_dir, f"verify_{date_str}.jsonl")
        
        entry = {
            "platform": platform,
            "url": url,
            "verified": result.verified,
            "status_code": result.status_code,
            "diagnosis": result.diagnosis,
            "checked_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(result.checked_at)),
        }
        
        with open(audit_file, 'a') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    def get_post_history(self, platform: str = None, limit: int = 10) -> list[PostRecord]:
        """Get recent post history, optionally filtered by platform."""
        records = self._history
        if platform:
            records = [r for r in records if r.platform == platform]
        return records[-limit:]
    
    def get_status(self) -> dict:
        """Get overall status."""
        return {
            "platforms_with_creds": self.creds.list_platforms(),
            "known_platforms": list(PLATFORM_REGISTRY.keys()),
            "total_posts_recorded": len(self._history),
            "verified_posts": sum(1 for r in self._history if r.verified),
            "failed_posts": sum(1 for r in self._history if not r.verified),
            "rate_limits": {
                p: {
                    "can_post": self.check_rate_limit(p)[0],
                    "wait_seconds": round(self.check_rate_limit(p)[1], 1),
                }
                for p in PLATFORM_REGISTRY
            }
        }


# ---------------------------------------------------------------------------
# CLI demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("🛡️  PublishGuard v1.0 — Post Verification Engine")
    print("   Aoineco & Co. | Never Trust 'Posted Successfully' Again")
    print("=" * 60)
    
    pg = PublishGuard(audit_dir="/tmp/publish_guard_test")
    
    # 1. Get platform guide
    print("\n📖 BotMadang Guide:")
    print(pg.get_platform_guide("botmadang"))
    
    # 2. Validate content
    print("\n\n📝 Validating content...")
    
    # Bad content (no Korean in title)
    valid, issues = pg.validate_content("botmadang", {
        "title": "Hello World",
        "content": "Test post"
    })
    print(f"  English-only title: valid={valid}")
    for issue in issues:
        print(f"    → {issue}")
    
    # Good content
    valid, issues = pg.validate_content("botmadang", {
        "title": "안녕하세요 TokenGuard 소개",
        "content": "새로운 스킬입니다"
    })
    print(f"\n  Korean title: valid={valid}")
    for issue in issues:
        print(f"    → {issue}")
    
    # 3. Verify a known URL
    print("\n\n🔍 Verifying URLs...")
    
    # Test with a real URL (ClawHub)
    result = pg.verify_post("https://clawhub.com", platform="clawhub")
    print(f"  clawhub.com: verified={result.verified}, status={result.status_code}")
    print(f"  Diagnosis: {result.diagnosis}")
    
    # Test with a likely-404 URL
    result = pg.verify_post(
        "https://clawhub.com/skills/this-does-not-exist-12345", 
        platform="clawhub"
    )
    print(f"\n  Fake skill URL: verified={result.verified}, status={result.status_code}")
    print(f"  Diagnosis: {result.diagnosis}")
    
    # 4. Check rate limits
    print("\n\n⏱️ Rate Limits:")
    print(json.dumps(pg.get_status()["rate_limits"], indent=2))
    
    print("\n✅ PublishGuard test complete!")
