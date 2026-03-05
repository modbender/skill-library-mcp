#!/usr/bin/env python3
"""
embed.py — Embed notes and cache results as JSON.

Supports multiple providers: ollama, openai, gemini.
Reads settings from config/config.json.
Cache is stored at <directory>/.embeddings/embeddings.json.
Incrementally updates cache based on file modification time.

Usage:
  uv run scripts/embed.py --input <directory>
  uv run scripts/embed.py --input <directory> --force
  uv run scripts/embed.py --config path/to/config.json --input <directory>
"""

import os
import re
import sys
import json
import fnmatch
import hashlib
import argparse
import datetime
import urllib.request
import urllib.error
from pathlib import Path

# ── Default skip lists (overridden by config) ───────────────────────────────

DEFAULT_SKIP_DIRS = [
    ".obsidian", ".trash", ".smart-env", ".makemd", ".space",
    ".claude", ".embeddings", "Spaces", "templates",
]

DEFAULT_SKIP_FILES = [
    "CLAUDE.md", "Vault.md", "Dashboard.md", "templates.md",
]

# ── Regex patterns ───────────────────────────────────────────────────────────

FM_PATTERN = re.compile(r'^---\n.*?\n---\n?', re.DOTALL)
CODE_BLOCK_RE = re.compile(r'```.*?```', re.DOTALL)
MD_LINK_RE = re.compile(r'\[([^\]]+)\]\([^)]+\)')
WIKILINK_RE = re.compile(r'\[\[([^\]|]+)(?:\|[^\]]*)?]]')
HTML_RE = re.compile(r'<[^>]+>')
URL_RE = re.compile(r'https?://\S+')


from urllib.parse import urlparse

# ── Allowed Endpoints (Exfiltration Guard) ──────────────────────────────────

ALLOWED_DOMAINS = {
    "openai": ["api.openai.com"],
    "gemini": ["generativelanguage.googleapis.com"],
    "ollama": ["localhost", "127.0.0.1"],
}


def validate_url(url: str, provider_name: str) -> None:
    """Ensure the URL matches the expected official endpoint for the provider."""
    parsed = urlparse(url)
    domain = parsed.netloc.split(':')[0]
    
    allowed = ALLOWED_DOMAINS.get(provider_name, [])
    if allowed and domain not in allowed:
        # If it's a known provider but unknown domain, check if it's explicitly allowed in config
        # For now, we raise a security warning and exit unless it's a local/custom case.
        print(f"⚠️  Security Warning: Provider '{provider_name}' is using an unofficial endpoint: {domain}")
        print(f"   Official domains: {', '.join(allowed)}")
        print("   To bypass this, use a custom provider name in config or verify the URL.")
        sys.exit(1)


# ── Text cleaning ────────────────────────────────────────────────────────────

def clean_text(content: str) -> str:
    """Strip frontmatter, code blocks, URLs, and noise for cleaner embeddings."""
    text = FM_PATTERN.sub('', content, count=1)
    text = CODE_BLOCK_RE.sub('', text)
    text = WIKILINK_RE.sub(r'\1', text)
    text = MD_LINK_RE.sub(r'\1', text)
    text = HTML_RE.sub('', text)
    text = URL_RE.sub('', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


# ── Embedding providers ──────────────────────────────────────────────────────

def embed_ollama(text: str, model: str, provider: dict) -> list[float]:
    """Embed text via Ollama local API."""
    url = provider["url"].rstrip("/") + "/api/embeddings"
    validate_url(url, "ollama")
    
    payload = json.dumps({"model": model, "prompt": text}).encode()
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read())
        return data["embedding"]


def get_api_key(env_var_name: str) -> str:
    """Try to get API key from environment, then from .env file."""
    # 1. Try environment
    key = os.environ.get(env_var_name, "")
    if key:
        return key
    
    # 2. Try .env file in the skill root
    script_dir = Path(__file__).parent
    skill_root = script_dir.parent
    env_file = skill_root / ".env"
    
    if env_file.exists():
        try:
            with open(env_file, "r") as f:
                for line in f:
                    if line.strip().startswith(f"{env_var_name}="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
        except Exception:
            pass
            
    return ""


def embed_openai(text: str, model: str, provider: dict) -> list[float]:
    """Embed text via OpenAI-compatible API."""
    env_var = provider.get("api_key_env", "OPENAI_API_KEY")
    api_key = get_api_key(env_var)
    if not api_key:
        print(f"❌ API key not set: {env_var}")
        sys.exit(1)

    url = provider["url"].rstrip("/") + "/embeddings"
    validate_url(url, "openai")
    
    payload = json.dumps({"model": model, "input": text}).encode()
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read())
        return data["data"][0]["embedding"]


def embed_gemini(text: str, model: str, provider: dict) -> list[float]:
    """Embed text via Google Gemini API."""
    env_var = provider.get("api_key_env", "GEMINI_API_KEY")
    api_key = get_api_key(env_var)
    if not api_key:
        print(f"❌ API key not set: {env_var}")
        sys.exit(1)

    base_url = provider["url"].rstrip("/")
    url = f"{base_url}/v1beta/models/{model}:embedContent"
    validate_url(url, "gemini")

    payload = json.dumps({
        "content": {"parts": [{"text": text}]},
    }).encode()
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read())
        return data["embedding"]["values"]


EMBED_FUNCTIONS = {
    "ollama": embed_ollama,
    "openai": embed_openai,
    "gemini": embed_gemini,
}


def embed_text(text: str, model: str, provider: dict) -> list[float]:
    """Route to the correct embedding provider."""
    provider_name = provider["name"]
    fn = EMBED_FUNCTIONS.get(provider_name)
    if fn is None:
        print(f"❌ Unknown provider: {provider_name}")
        print(f"   Supported: {', '.join(EMBED_FUNCTIONS.keys())}")
        sys.exit(1)
    try:
        return fn(text, model, provider)
    except urllib.error.URLError as e:
        print(f"\n❌ Embedding API error ({provider_name}): {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Embedding error ({provider_name}): {e}")
        sys.exit(1)


# ── File discovery ───────────────────────────────────────────────────────────

def _matches_any(name: str, patterns: list[str]) -> bool:
    """Check if name matches any of the glob patterns."""
    return any(fnmatch.fnmatch(name, p) for p in patterns)


def collect_notes(
    input_dir: Path,
    skip_dirs: list[str] | None = None,
    skip_files: list[str] | None = None,
) -> list[Path]:
    """Walk the input directory and collect all .md files."""
    sd = skip_dirs if skip_dirs is not None else DEFAULT_SKIP_DIRS
    sf = skip_files if skip_files is not None else DEFAULT_SKIP_FILES
    notes = []
    for root, dirs, files in os.walk(input_dir):
        dirs[:] = sorted(d for d in dirs if not _matches_any(d, sd))
        for f in sorted(files):
            if f.endswith(".md") and not _matches_any(f, sf):
                notes.append(Path(root) / f)
    return notes


# ── JSON cache management ────────────────────────────────────────────────────

def load_cache(cache_path: Path) -> dict:
    """Load JSON cache. Returns the 'data' dict keyed by relative path."""
    if cache_path.exists():
        with open(cache_path, "r") as f:
            raw = json.load(f)
        return raw.get("data", {})
    return {}


def save_cache(
    data: dict,
    cache_path: Path,
    model: str = "",
    provider: str = "",
) -> None:
    """Write cache as JSON with metadata envelope."""
    # Detect embedding size from first entry
    embedding_size = 0
    for entry in data.values():
        emb = entry.get("embedding", [])
        if emb:
            embedding_size = len(emb)
            break

    envelope = {
        "metadata": {
            "generated_at": datetime.datetime.now().isoformat(),
            "model": model,
            "provider": provider,
            "embedding_size": embedding_size,
            "total_notes": len(data),
        },
        "data": data,
    }
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "w") as f:
        json.dump(envelope, f, indent=2)


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Embed notes via embedding API")
    parser.add_argument("--config", default="config/config.json",
                        help="Path to config.json (default: config/config.json)")
    parser.add_argument("--input", required=True,
                        help="Path to the notes directory")
    parser.add_argument("--force", action="store_true",
                        help="Re-embed all notes even if cached")
    args = parser.parse_args()

    # Load config
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"❌ Config not found: {config_path}")
        print("   Run: uv run scripts/config.py")
        sys.exit(1)

    with open(config_path, "r") as f:
        config = json.load(f)

    model = config["model"]
    provider = config["provider"]
    max_input_length = config.get("max_input_length", 8192)
    cache_dir = config.get("cache_dir", ".embeddings")
    skip_dirs = config.get("skip_dirs", DEFAULT_SKIP_DIRS)
    skip_files = config.get("skip_files", DEFAULT_SKIP_FILES)

    input_dir = Path(args.input).resolve()
    cache_path = input_dir / cache_dir / "embeddings.json"

    notes = collect_notes(input_dir, skip_dirs=skip_dirs, skip_files=skip_files)
    print(f"📂 Input directory: {input_dir}")
    print(f"🤖 Provider: {provider['name']} | Model: {model}")
    print(f"📄 Found {len(notes)} notes")

    cache = {} if args.force else load_cache(cache_path)
    print(f"💾 Cache: {len(cache)} entries loaded")

    new_count = 0
    skip_count = 0
    error_count = 0
    removed_count = 0

    # Track which relative paths are still valid (for pruning stale entries)
    active_keys = set()

    for i, path in enumerate(notes):
        rel = str(path.relative_to(input_dir))
        active_keys.add(rel)

        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            print(f"  ⚠️  Read error {rel}: {e}")
            error_count += 1
            continue

        text = clean_text(content)
        if not text.strip():
            skip_count += 1
            continue

        # Check if cached entry is still fresh based on mtime
        mtime = path.stat().st_mtime
        cached = cache.get(rel)
        if cached and not args.force:
            cached_mtime = cached.get("mtime", 0)
            if cached_mtime >= mtime:
                skip_count += 1
                continue

        # Truncate to max_input_length
        truncated = text[:max_input_length]

        # Progress indicator
        print(f"  [{i + 1}/{len(notes)}] Embedding: {Path(rel).name[:60]}", end="\r")

        try:
            embedding = embed_text(truncated, model, provider)
        except SystemExit:
            raise
        except Exception as e:
            print(f"\n  ⚠️  Embed error {rel}: {e}")
            error_count += 1
            continue

        cache[rel] = {
            "path": str(path),
            "stem": path.stem,
            "rel": rel,
            "mtime": mtime,
            "embedding": embedding,
            "text_preview": text[:200],
        }
        new_count += 1

        # Save periodically so we don't lose progress
        if new_count % 20 == 0:
            save_cache(cache, cache_path, model=model, provider=provider["name"])

    # Prune stale entries (files that no longer exist)
    stale_keys = [k for k in cache if k not in active_keys]
    for k in stale_keys:
        del cache[k]
        removed_count += 1

    save_cache(cache, cache_path, model=model, provider=provider["name"])

    print(f"\n\n✅ Done.")
    print(f"   New/updated: {new_count}")
    print(f"   From cache:  {skip_count}")
    print(f"   Removed:     {removed_count}")
    print(f"   Errors:      {error_count}")
    print(f"   Total cached: {len(cache)}")
    print(f"   Cache file: {cache_path}")


if __name__ == "__main__":
    main()
