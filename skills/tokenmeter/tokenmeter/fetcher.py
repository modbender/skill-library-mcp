"""Fetch usage data from provider APIs using environment variables."""

import os
import hashlib
import sqlite3
from datetime import datetime
from typing import Optional

from .db import init_db
from .pricing import calculate_cost

# Known API key environment variables
ENV_VARS = {
    "anthropic": ["ANTHROPIC_API_KEY"],
    "openai": ["OPENAI_API_KEY", "OPENAI_KEY"],
    "google": ["GOOGLE_API_KEY", "GEMINI_API_KEY"],
    "azure": ["AZURE_OPENAI_API_KEY"],
}


def _ensure_dedup_table(conn: sqlite3.Connection):
    """Create dedup tracking table if it doesn't exist."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS import_log (
            hash TEXT PRIMARY KEY,
            imported_at TEXT NOT NULL,
            source_file TEXT
        )
    """)
    conn.commit()


def _record_hash(provider: str, model: str, timestamp: str, input_tokens: int, output_tokens: int) -> str:
    """Create a unique hash for a usage record to avoid duplicate imports."""
    key = f"{provider}:{model}:{timestamp}:{input_tokens}:{output_tokens}"
    return hashlib.sha256(key.encode()).hexdigest()[:16]


def scan_env_vars() -> dict[str, Optional[str]]:
    """Scan environment for known API key variables.
    
    Returns a dict mapping provider -> env var name (if found) or None.
    """
    found = {}
    for provider, vars in ENV_VARS.items():
        found[provider] = None
        for var in vars:
            if os.environ.get(var):
                found[provider] = var
                break
    return found


def fetch_anthropic(api_key: str) -> dict:
    """Fetch usage from Anthropic.
    
    Note: Anthropic does not currently expose a public usage/billing API.
    This function validates the API key and returns an informative message.
    """
    import requests
    
    # Validate the API key by making a simple API call
    try:
        resp = requests.get(
            "https://api.anthropic.com/v1/models",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            },
            timeout=10,
        )
        valid = resp.status_code == 200
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to validate API key: {e}",
            "records_imported": 0,
            "total_cost": 0.0,
        }
    
    if not valid:
        return {
            "success": False,
            "error": f"API key validation failed (status {resp.status_code})",
            "records_imported": 0,
            "total_cost": 0.0,
        }
    
    return {
        "success": True,
        "no_api": True,
        "message": "Anthropic doesn't expose a usage API. Use 'tokenmeter import --auto' for local session data.",
        "records_imported": 0,
        "total_cost": 0.0,
    }


def fetch_openai(api_key: str, dry_run: bool = False) -> dict:
    """Fetch usage from OpenAI organization API.
    
    Uses the organization usage endpoint to get completion usage data.
    Note: This requires organization-level API access.
    """
    import requests
    from datetime import date, timedelta
    
    # Try to fetch usage from the past 7 days
    end_date = date.today()
    start_date = end_date - timedelta(days=7)
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    # Try the newer usage API endpoint
    try:
        # First try to get organization info to validate the key
        org_resp = requests.get(
            "https://api.openai.com/v1/models",
            headers=headers,
            timeout=10,
        )
        
        if org_resp.status_code == 401:
            return {
                "success": False,
                "error": "Invalid API key",
                "records_imported": 0,
                "total_cost": 0.0,
            }
        
        if org_resp.status_code != 200:
            return {
                "success": False,
                "error": f"API validation failed (status {org_resp.status_code})",
                "records_imported": 0,
                "total_cost": 0.0,
            }
        
        # Try to fetch usage data
        # Note: The usage API endpoint requires specific organization permissions
        usage_url = "https://api.openai.com/v1/organization/usage/completions"
        params = {
            "start_time": int(datetime.combine(start_date, datetime.min.time()).timestamp()),
            "bucket_width": "1d",
        }
        
        usage_resp = requests.get(
            usage_url,
            headers=headers,
            params=params,
            timeout=30,
        )
        
        if usage_resp.status_code == 403:
            return {
                "success": False,
                "error": "Usage API requires organization admin permissions. Your API key is valid but lacks the required access level.",
                "records_imported": 0,
                "total_cost": 0.0,
            }
        
        if usage_resp.status_code == 404:
            return {
                "success": False,
                "error": "Usage API not available for your account type.",
                "records_imported": 0,
                "total_cost": 0.0,
            }
        
        if usage_resp.status_code != 200:
            return {
                "success": False,
                "error": f"Usage API returned status {usage_resp.status_code}: {usage_resp.text[:200]}",
                "records_imported": 0,
                "total_cost": 0.0,
            }
        
        # Parse the usage data
        usage_data = usage_resp.json()
        
        if dry_run:
            # Just return what we would import
            return {
                "success": True,
                "dry_run": True,
                "records_found": len(usage_data.get("data", [])),
                "records_imported": 0,
                "total_cost": 0.0,
            }
        
        # Import records
        conn = init_db()
        _ensure_dedup_table(conn)
        
        records_imported = 0
        records_skipped = 0
        total_cost = 0.0
        
        for bucket in usage_data.get("data", []):
            for result in bucket.get("results", []):
                model = result.get("model", "unknown")
                input_tokens = result.get("input_tokens", 0)
                output_tokens = result.get("output_tokens", 0)
                timestamp = datetime.fromtimestamp(bucket.get("start_time", 0))
                
                # Check for duplicates
                record_hash = _record_hash(
                    "openai", model, timestamp.isoformat(),
                    input_tokens, output_tokens
                )
                
                existing = conn.execute(
                    "SELECT 1 FROM import_log WHERE hash = ?",
                    (record_hash,)
                ).fetchone()
                
                if existing:
                    records_skipped += 1
                    continue
                
                # Calculate cost
                cost = calculate_cost("openai", model, input_tokens, output_tokens)
                
                # Insert record
                conn.execute(
                    """
                    INSERT INTO usage (timestamp, provider, model, input_tokens, output_tokens, cost, source, app)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (timestamp.isoformat(), "openai", model, input_tokens, output_tokens, cost, "fetch", None)
                )
                
                # Log the import
                conn.execute(
                    """
                    INSERT INTO import_log (hash, imported_at, source_file)
                    VALUES (?, ?, ?)
                    """,
                    (record_hash, datetime.now().isoformat(), "openai-api-fetch")
                )
                
                records_imported += 1
                total_cost += cost
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "records_imported": records_imported,
            "records_skipped": records_skipped,
            "total_cost": total_cost,
        }
        
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Request timed out",
            "records_imported": 0,
            "total_cost": 0.0,
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Request failed: {e}",
            "records_imported": 0,
            "total_cost": 0.0,
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {e}",
            "records_imported": 0,
            "total_cost": 0.0,
        }


def fetch_google(api_key: str) -> dict:
    """Fetch usage from Google/Gemini.
    
    Note: Google AI Studio does not currently expose a public usage/billing API.
    """
    import requests
    
    # Validate the API key by listing models
    try:
        resp = requests.get(
            f"https://generativelanguage.googleapis.com/v1/models?key={api_key}",
            timeout=10,
        )
        valid = resp.status_code == 200
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to validate API key: {e}",
            "records_imported": 0,
            "total_cost": 0.0,
        }
    
    if not valid:
        return {
            "success": False,
            "error": f"API key validation failed (status {resp.status_code})",
            "records_imported": 0,
            "total_cost": 0.0,
        }
    
    return {
        "success": True,
        "no_api": True,
        "message": "Google AI Studio doesn't expose a usage API.",
        "records_imported": 0,
        "total_cost": 0.0,
    }


def fetch_azure(api_key: str) -> dict:
    """Fetch usage from Azure OpenAI.
    
    Note: Azure OpenAI usage is tracked through Azure Cost Management,
    which requires different authentication (Azure AD/RBAC).
    """
    return {
        "success": True,
        "no_api": True,
        "message": "Azure OpenAI usage is tracked through Azure Cost Management portal.",
        "records_imported": 0,
        "total_cost": 0.0,
    }


def fetch_provider(provider: str, api_key: str, dry_run: bool = False) -> dict:
    """Fetch usage for a specific provider.
    
    Args:
        provider: Provider name (anthropic, openai, google, azure)
        api_key: API key for the provider
        dry_run: If True, don't actually import records
        
    Returns:
        dict with success status, records imported, and any error messages
    """
    fetchers = {
        "anthropic": fetch_anthropic,
        "openai": fetch_openai,
        "google": fetch_google,
        "azure": fetch_azure,
    }
    
    fetcher = fetchers.get(provider.lower())
    if not fetcher:
        return {
            "success": False,
            "error": f"Unknown provider: {provider}",
            "records_imported": 0,
            "total_cost": 0.0,
        }
    
    # OpenAI supports dry_run parameter
    if provider.lower() == "openai":
        return fetcher(api_key, dry_run=dry_run)
    return fetcher(api_key)


def fetch_all(dry_run: bool = False) -> dict:
    """Scan environment and fetch from all available providers.
    
    Returns:
        dict with results for each provider
    """
    env_vars = scan_env_vars()
    results = {}
    
    for provider, env_var in env_vars.items():
        if env_var:
            api_key = os.environ.get(env_var)
            results[provider] = {
                "env_var": env_var,
                **fetch_provider(provider, api_key, dry_run=dry_run)
            }
        else:
            results[provider] = {
                "env_var": None,
                "success": False,
                "not_found": True,
                "records_imported": 0,
                "total_cost": 0.0,
            }
    
    return results
