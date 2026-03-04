"""Import usage data from Clawdbot/OpenClaw session JSONL files."""

import json
import hashlib
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

from .db import init_db, get_db_path
from .pricing import calculate_cost


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


def _normalize_model(model: str) -> str:
    """Normalize model names to match pricing table.
    
    Clawdbot logs full model IDs like 'claude-opus-4-5', 'claude-sonnet-4-20250514', etc.
    Map these to our pricing model names.
    """
    model = model.lower()
    
    # Anthropic model mapping — catch all dated variants
    mappings = {
        "claude-opus-4-5": "claude-opus-4",
        "claude-opus-4-6": "claude-opus-4",
        "claude-opus-4-5-20250414": "claude-opus-4",
        "claude-opus-4-5-20251101": "claude-opus-4",
        "claude-opus-4-6-20250618": "claude-opus-4",
        "claude-sonnet-4-20250514": "claude-sonnet-4",
        "claude-sonnet-4-5-20250514": "claude-sonnet-4",
        "claude-sonnet-4-5": "claude-sonnet-4",
        "claude-3-5-sonnet-latest": "claude-3.5-sonnet",
        "claude-3-5-sonnet-20241022": "claude-3.5-sonnet",
        "claude-3-5-haiku-latest": "claude-3.5-haiku",
        "claude-3-5-haiku-20241022": "claude-3.5-haiku",
        "claude-haiku-3-5-latest": "claude-3.5-haiku",
        "claude-haiku-4-5-20251015": "claude-3.5-haiku",
        "claude-3-opus-20240229": "claude-3-opus",
    }
    
    # Fuzzy fallback: if not in exact map, try prefix matching
    if model not in mappings:
        for prefix, normalized in [
            ("claude-opus-4", "claude-opus-4"),
            ("claude-sonnet-4", "claude-sonnet-4"),
            ("claude-3.5-sonnet", "claude-3.5-sonnet"),
            ("claude-3-5-sonnet", "claude-3.5-sonnet"),
            ("claude-3.5-haiku", "claude-3.5-haiku"),
            ("claude-3-5-haiku", "claude-3.5-haiku"),
            ("claude-haiku", "claude-3.5-haiku"),
        ]:
            if model.startswith(prefix):
                return normalized
    
    return mappings.get(model, model)


def _extract_provider(raw_provider: str, raw_model: str) -> str:
    """Extract provider name from the raw data."""
    if raw_provider:
        return raw_provider.lower()
    # Infer from model name
    if "claude" in raw_model.lower():
        return "anthropic"
    if "gpt" in raw_model.lower() or "o1" in raw_model.lower():
        return "openai"
    if "gemini" in raw_model.lower():
        return "google"
    return "unknown"


def import_sessions(
    sessions_dir: Path,
    app_name: str = "clawdbot",
    dry_run: bool = False,
    incremental: Optional[bool] = None,
    _checkpoint: Optional[dict] = None,
) -> dict:
    """Import usage from Clawdbot/OpenClaw JSONL session files.
    
    Scans all .jsonl files in the given directory, extracts usage records,
    deduplicates against previously imported data, and logs new records.
    
    When incremental=True (or None with existing checkpoint), uses the
    checkpoint system to only read new/changed data since the last import.
    
    Pass _checkpoint to share state across multiple calls (avoids overwriting).
    
    Returns a summary dict with counts and costs.
    """
    from .checkpoint import (
        load_checkpoint, save_checkpoint, classify_file,
        update_file_checkpoint, prune_deleted_files,
    )
    
    if not sessions_dir.exists():
        return {"error": f"Directory not found: {sessions_dir}", "imported": 0}
    
    # Resolve symlinks to avoid scanning the same directory twice
    sessions_dir = sessions_dir.resolve()
    
    jsonl_files = list(sessions_dir.glob("*.jsonl"))
    if not jsonl_files:
        return {"error": f"No .jsonl files found in {sessions_dir}", "imported": 0}
    
    # Use shared checkpoint if provided, otherwise load from disk
    checkpoint = _checkpoint if _checkpoint is not None else load_checkpoint()
    use_incremental = incremental if incremental is not None else bool(checkpoint.get("files"))
    
    conn = init_db()
    _ensure_dedup_table(conn)
    
    stats = {
        "files_scanned": 0,
        "files_skipped": 0,
        "files_incremental": 0,
        "files_full": 0,
        "records_found": 0,
        "records_imported": 0,
        "records_skipped_dup": 0,
        "records_skipped_no_usage": 0,
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "total_cache_read_tokens": 0,
        "total_cache_write_tokens": 0,
        "total_cost": 0.0,
        "total_api_equivalent_cost": 0.0,
        "by_model": {},
        "errors": [],
        "incremental": use_incremental,
    }
    
    # Prune checkpoint entries for deleted files — only prune files
    # that were in THIS directory (don't touch entries from other directories)
    existing_file_paths = {str(f.resolve()) for f in jsonl_files}
    dir_prefix = str(sessions_dir.resolve())
    pruned_keys = [
        k for k in checkpoint.get("files", {})
        if k.startswith(dir_prefix) and k not in existing_file_paths
    ]
    for k in pruned_keys:
        del checkpoint["files"][k]
    if pruned_keys:
        stats.setdefault("files_pruned", len(pruned_keys))
    
    for jsonl_file in sorted(jsonl_files):
        stats["files_scanned"] += 1
        
        # Classify file for incremental import
        if use_incremental:
            action, byte_offset = classify_file(jsonl_file, checkpoint)
        else:
            action, byte_offset = "full", 0
        
        if action == "skip":
            stats["files_skipped"] += 1
            continue
        elif action == "incremental":
            stats["files_incremental"] += 1
        else:
            stats["files_full"] += 1
        
        try:
            with open(jsonl_file, "r") as f:
                # Seek to byte offset for incremental reads
                if action == "incremental" and byte_offset > 0:
                    f.seek(byte_offset)
                
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    
                    # Extract usage - can be at top level or nested under message
                    usage = None
                    message = data.get("message", {})
                    
                    if isinstance(message, dict):
                        usage = message.get("usage")
                    
                    if not usage and "usage" in data:
                        usage = data["usage"]
                    
                    if not usage:
                        continue
                    
                    stats["records_found"] += 1
                    
                    # Extract token counts
                    input_tokens = usage.get("input", usage.get("input_tokens", 0))
                    output_tokens = usage.get("output", usage.get("output_tokens", 0))
                    cache_read = usage.get("cacheRead", usage.get("cache_read_input_tokens", 0))
                    cache_write = usage.get("cacheWrite", usage.get("cache_write_input_tokens", 0))
                    
                    # Extract model info
                    raw_model = message.get("model", data.get("model", "unknown"))
                    raw_provider = message.get("provider", data.get("provider", ""))
                    
                    provider = _extract_provider(raw_provider, raw_model)
                    model = _normalize_model(raw_model)
                    
                    # Extract timestamp
                    ts_str = data.get("timestamp", message.get("timestamp"))
                    if ts_str:
                        try:
                            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                        except (ValueError, AttributeError):
                            ts = datetime.now()
                    else:
                        ts = datetime.now()
                    
                    # Check for embedded cost (Clawdbot calculates this)
                    embedded_cost = None
                    cost_data = usage.get("cost")
                    if isinstance(cost_data, dict):
                        embedded_cost = cost_data.get("total", 0)
                    elif isinstance(cost_data, (int, float)):
                        embedded_cost = cost_data
                    
                    # Calculate API-equivalent cost from our pricing table
                    api_cost = calculate_cost(provider, model, input_tokens, output_tokens)
                    
                    # Also account for cache read tokens (much cheaper)
                    # Cache read is typically 10% of input price
                    if cache_read > 0:
                        from .pricing import get_pricing
                        pricing = get_pricing(provider, model)
                        if pricing:
                            cache_cost = (cache_read / 1_000_000) * pricing.input_per_1m * 0.1
                            api_cost += cache_cost
                    
                    # Use embedded cost if available, otherwise our calculation
                    final_cost = embedded_cost if embedded_cost is not None else api_cost
                    
                    # Dedup check
                    rec_hash = _record_hash(provider, model, ts.isoformat(), input_tokens, output_tokens)
                    existing = conn.execute(
                        "SELECT 1 FROM import_log WHERE hash = ?", (rec_hash,)
                    ).fetchone()
                    
                    if existing:
                        stats["records_skipped_dup"] += 1
                        continue
                    
                    # Track stats
                    stats["total_input_tokens"] += input_tokens
                    stats["total_output_tokens"] += output_tokens
                    stats["total_cache_read_tokens"] += cache_read
                    stats["total_cache_write_tokens"] += cache_write
                    stats["total_cost"] += final_cost
                    stats["total_api_equivalent_cost"] += api_cost
                    
                    model_key = f"{provider}/{model}"
                    if model_key not in stats["by_model"]:
                        stats["by_model"][model_key] = {
                            "input": 0, "output": 0, "cache_read": 0,
                            "cost": 0.0, "calls": 0
                        }
                    stats["by_model"][model_key]["input"] += input_tokens
                    stats["by_model"][model_key]["output"] += output_tokens
                    stats["by_model"][model_key]["cache_read"] += cache_read
                    stats["by_model"][model_key]["cost"] += final_cost
                    stats["by_model"][model_key]["calls"] += 1
                    
                    if not dry_run:
                        # Log the usage record
                        conn.execute(
                            """INSERT INTO usage 
                               (timestamp, provider, model, input_tokens, output_tokens, cache_read_tokens, cache_write_tokens, cost, source, app)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                            (ts.isoformat(), provider, model, input_tokens, output_tokens,
                             cache_read, cache_write, final_cost, "import", app_name)
                        )
                        # Mark as imported
                        conn.execute(
                            "INSERT INTO import_log (hash, imported_at, source_file) VALUES (?, ?, ?)",
                            (rec_hash, datetime.now().isoformat(), str(jsonl_file.name))
                        )
                    
                    stats["records_imported"] += 1
                
                # Track final byte position for checkpoint (inside with block)
                final_byte_offset = f.tell()
                    
        except Exception as e:
            stats["errors"].append(f"{jsonl_file.name}: {e}")
            continue
        
        # Update checkpoint for this file
        if not dry_run:
            update_file_checkpoint(checkpoint, jsonl_file, final_byte_offset)
    
    if not dry_run:
        conn.commit()
        # Only save checkpoint if we own it (not shared from caller)
        if _checkpoint is None:
            save_checkpoint(checkpoint)
    conn.close()
    
    return stats


def find_session_dirs() -> list[dict]:
    """Auto-discover Clawdbot/OpenClaw session directories.
    
    Resolves symlinks to avoid scanning the same directory twice
    (e.g., ~/.openclaw → ~/.clawdbot).
    """
    home = Path.home()
    found = []
    seen_resolved = set()  # Track resolved paths to dedup symlinks
    
    # Standard Clawdbot locations
    for base in [home / ".clawdbot", home / ".openclaw"]:
        if not base.exists() and not base.is_symlink():
            continue
        
        # Resolve symlinks to canonical path
        resolved_base = base.resolve()
        
        agents_dir = resolved_base / "agents"
        if agents_dir.exists():
            for agent_dir in agents_dir.iterdir():
                sessions_dir = agent_dir / "sessions"
                if sessions_dir.exists():
                    resolved_sessions = sessions_dir.resolve()
                    if str(resolved_sessions) in seen_resolved:
                        continue  # Skip duplicate (symlink target already scanned)
                    seen_resolved.add(str(resolved_sessions))
                    
                    jsonl_count = len(list(sessions_dir.glob("*.jsonl")))
                    if jsonl_count > 0:
                        found.append({
                            "path": resolved_sessions,
                            "agent": agent_dir.name,
                            "base": resolved_base.name,
                            "files": jsonl_count,
                        })
    
    # Claude Code locations
    claude_dir = home / ".claude" / "projects"
    if claude_dir.exists():
        for project_dir in claude_dir.rglob("*.jsonl"):
            parent = project_dir.parent.resolve()
            if str(parent) in seen_resolved:
                continue
            seen_resolved.add(str(parent))
            
            jsonl_count = len(list(parent.glob("*.jsonl")))
            found.append({
                "path": parent,
                "agent": f"claude-code/{parent.name}",
                "base": ".claude",
                "files": jsonl_count,
            })
    
    return found
