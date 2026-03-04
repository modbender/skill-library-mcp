"""
Fanfic Writer v2.0 - Utility Functions
Core utilities: run_id, book_uid, slug conversion, filename sanitization
"""
import os
import re
import json
import secrets
import string
import hashlib
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple


# ============================================================================
# Timezone & Timestamp
# ============================================================================

def get_timestamp_iso(tz_name: str = "Asia/Shanghai") -> str:
    """Get current timestamp in ISO8601 format with timezone"""
    # Use fixed offset for Windows compatibility
    return datetime.now().isoformat() + "+08:00"


def get_timestamp_compact(tz_name: str = "Asia/Shanghai") -> str:
    """Get compact timestamp: YYYYMMDD_HHMMSS"""
    # Use local time for Windows compatibility
    return datetime.now().strftime("%Y%m%d_%H%M%S")


# ============================================================================
# ID Generation
# ============================================================================

def generate_run_id(tz_name: str = "Asia/Shanghai") -> str:
    """
    Generate unique run_id: YYYYMMDD_HHMMSS_{RAND6}
    Example: 20260215_224500_A9F3KQ
    """
    timestamp = get_timestamp_compact(tz_name)
    rand6 = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    return f"{timestamp}_{rand6}"


def generate_book_uid(title: str = "") -> str:
    """
    Generate book_uid: 6-10 character short UUID/hash
    If title provided, hash it for deterministic generation
    """
    if title:
        # Deterministic hash from title
        hash_bytes = hashlib.sha256(title.encode('utf-8')).digest()
        # Take first 8 bytes, convert to hex, take first 8 chars
        return hashlib.sha256(title.encode('utf-8')).hexdigest()[:8]
    else:
        # Random generation
        return ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(8))


def generate_event_id(run_id: str, phase: str, chapter: Optional[int] = None) -> str:
    """
    Generate event_id for audit trail
    Format: {run_id}_{phase}_{chapter}_{rand4}
    """
    rand4 = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(4))
    if chapter is not None:
        return f"{run_id}_{phase}_ch{chapter:03d}_{rand4}"
    return f"{run_id}_{phase}_{rand4}"


# ============================================================================
# Slug & Filename Sanitization
# ============================================================================

def to_slug(text: str) -> str:
    """
    Convert text to ASCII slug (snake_case)
    Used for directory names, keys, and system identifiers
    """
    # Normalize unicode (NFKC: compatibility decomposition)
    text = unicodedata.normalize('NFKC', text)
    
    # Convert to lowercase
    text = text.lower()
    
    # Replace spaces and common separators with underscore
    text = re.sub(r'[\s\-]+', '_', text)
    
    # Remove non-alphanumeric characters (except underscore)
    text = re.sub(r'[^a-z0-9_]', '', text)
    
    # Collapse multiple underscores
    text = re.sub(r'_+', '_', text)
    
    # Strip leading/trailing underscores
    text = text.strip('_')
    
    # Limit length
    if len(text) > 64:
        text = text[:64]
    
    return text or 'untitled'


def sanitize_filename(text: str, max_length: int = 80) -> str:
    """
    Sanitize text for use in filenames (allows Chinese)
    Removes forbidden characters for Windows/Linux/macOS
    
    Forbidden characters: backslash, forward slash, colon, asterisk, question mark, double quote, less than, greater than, pipe
    """
    if not text:
        return "untitled"
    
    # Unicode normalization (NFC for consistency)
    text = unicodedata.normalize('NFC', text)
    
    # Remove forbidden characters
    forbidden = r'[\x00-\x1f\\/:*?"<>|]'
    text = re.sub(forbidden, '_', text)
    
    # Collapse multiple underscores
    text = re.sub(r'_+', '_', text)
    
    # Strip leading/trailing spaces and dots
    text = text.strip(' .')
    
    # Limit length
    if len(text) > max_length:
        # Keep first 80 + last 30
        text = text[:80] + '_' + text[-30:]
    
    return text or "untitled"


def sanitize_chapter_filename(chapter_num: int, title: str, is_forced: bool = False) -> str:
    """
    Generate chapter filename
    Format: 第###章_{title}.txt or ⚠️_第###章_{title}_FORCED.txt
    """
    safe_title = sanitize_filename(title, max_length=60)
    
    if is_forced:
        return f"⚠️_第{chapter_num:03d}章_{safe_title}_FORCED.txt"
    return f"第{chapter_num:03d}章_{safe_title}.txt"


# ============================================================================
# Path Management
# ============================================================================

def get_workspace_root(base_dir: Path, title_slug: str, book_uid: str) -> Path:
    """
    Generate workspace root path
    Format: {base_dir}/{title_slug}__{book_uid}/
    """
    return base_dir / f"{title_slug}__{book_uid}"


def get_run_dir(workspace_root: Path, run_id: str) -> Path:
    """
    Get run directory
    Format: {workspace_root}/runs/{run_id}/
    """
    return workspace_root / "runs" / run_id


# ============================================================================
# Directory Structure Generator
# ============================================================================

DIRECTORY_STRUCTURE = """
novels/
└── {book_title_slug}__{book_uid}/
    └── runs/
        └── {run_id}/
            ├── 0-config/
            │   ├── 0-book-config.json
            │   ├── intent_checklist.json
            │   ├── style_guide.md
            │   └── price-table.json
            ├── 1-outline/
            │   ├── 1-main-outline.md
            │   └── 5-chapter-outlines.json
            ├── 2-planning/
            │   └── 2-chapter-plan.json
            ├── 3-world/
            │   └── 3-world-building.md
            ├── 4-state/
            │   ├── 4-writing-state.json
            │   ├── prompt_registry.json
            │   ├── characters.json
            │   ├── plot_threads.json
            │   ├── timeline.json
            │   ├── inventory.json
            │   ├── locations_factions.json
            │   ├── pov_rules.json
            │   ├── session_memory.json
            │   ├── user_interactions.jsonl
            │   ├── backpatch.jsonl
            │   └── sanitizer_output.jsonl
            ├── drafts/
            │   ├── alignment/
            │   ├── outlines/
            │   ├── chapters/
            │   └── qc/
            ├── chapters/
            ├── anchors/
            │   ├── Ch001_anchor.md
            │   └── qc_rubric.md
            ├── logs/
            │   ├── token-report.jsonl
            │   ├── token-report.json
            │   ├── cost-report.jsonl
            │   ├── errors.jsonl
            │   ├── rescue.jsonl
            │   ├── run-summary.md
            │   └── prompts/
            ├── archive/
            │   ├── snapshots/
            │   ├── reverted/
            │   └── backpatch_resolved.jsonl
            └── final/
                ├── {book_title_display}_完整版.txt
                ├── quality-report.md
                ├── auto_abort_report.md
                ├── auto_rescue_report.md
                └── 7-whole-book-check.md
"""


def create_directory_structure(run_dir: Path, book_title_display: str) -> Dict[str, Path]:
    """
    Create the complete directory structure for a run
    Returns dict mapping logical names to paths
    """
    paths = {}
    
    # Config layer
    paths['config_dir'] = run_dir / "0-config"
    paths['book_config'] = paths['config_dir'] / "0-book-config.json"
    paths['intent_checklist'] = paths['config_dir'] / "intent_checklist.json"
    paths['style_guide'] = paths['config_dir'] / "style_guide.md"
    paths['price_table'] = paths['config_dir'] / "price-table.json"
    
    # Outline layer
    paths['outline_dir'] = run_dir / "1-outline"
    paths['main_outline'] = paths['outline_dir'] / "1-main-outline.md"
    paths['chapter_outlines'] = paths['outline_dir'] / "5-chapter-outlines.json"
    
    # Planning layer
    paths['planning_dir'] = run_dir / "2-planning"
    paths['chapter_plan'] = paths['planning_dir'] / "2-chapter-plan.json"
    
    # World layer
    paths['world_dir'] = run_dir / "3-world"
    paths['world_building'] = paths['world_dir'] / "3-world-building.md"
    
    # State layer
    paths['state_dir'] = run_dir / "4-state"
    paths['writing_state'] = paths['state_dir'] / "4-writing-state.json"
    paths['prompt_registry'] = paths['state_dir'] / "prompt_registry.json"
    paths['characters'] = paths['state_dir'] / "characters.json"
    paths['plot_threads'] = paths['state_dir'] / "plot_threads.json"
    paths['timeline'] = paths['state_dir'] / "timeline.json"
    paths['inventory'] = paths['state_dir'] / "inventory.json"
    paths['locations_factions'] = paths['state_dir'] / "locations_factions.json"
    paths['pov_rules'] = paths['state_dir'] / "pov_rules.json"
    paths['session_memory'] = paths['state_dir'] / "session_memory.json"
    paths['user_interactions'] = paths['state_dir'] / "user_interactions.jsonl"
    paths['backpatch'] = paths['state_dir'] / "backpatch.jsonl"
    paths['sanitizer_output'] = paths['state_dir'] / "sanitizer_output.jsonl"
    
    # Drafts layer
    paths['drafts_dir'] = run_dir / "drafts"
    paths['drafts_alignment'] = paths['drafts_dir'] / "alignment"
    paths['drafts_outlines'] = paths['drafts_dir'] / "outlines"
    paths['drafts_chapters'] = paths['drafts_dir'] / "chapters"
    paths['drafts_qc'] = paths['drafts_dir'] / "qc"
    
    # Chapters layer
    paths['chapters_dir'] = run_dir / "chapters"
    
    # Anchors layer
    paths['anchors_dir'] = run_dir / "anchors"
    
    # Logs layer
    paths['logs_dir'] = run_dir / "logs"
    paths['token_report_jsonl'] = paths['logs_dir'] / "token-report.jsonl"
    paths['token_report_json'] = paths['logs_dir'] / "token-report.json"
    paths['cost_report_jsonl'] = paths['logs_dir'] / "cost-report.jsonl"
    paths['errors'] = paths['logs_dir'] / "errors.jsonl"
    paths['rescue'] = paths['logs_dir'] / "rescue.jsonl"
    paths['run_summary'] = paths['logs_dir'] / "run-summary.md"
    paths['logs_prompts'] = paths['logs_dir'] / "prompts"
    
    # Archive layer
    paths['archive_dir'] = run_dir / "archive"
    paths['archive_snapshots'] = paths['archive_dir'] / "snapshots"
    paths['archive_reverted'] = paths['archive_dir'] / "reverted"
    paths['backpatch_resolved'] = paths['archive_dir'] / "backpatch_resolved.jsonl"
    
    # Final layer
    paths['final_dir'] = run_dir / "final"
    safe_title = sanitize_filename(book_title_display, max_length=50)
    paths['final_book'] = paths['final_dir'] / f"{safe_title}_完整版.txt"
    paths['quality_report'] = paths['final_dir'] / "quality-report.md"
    paths['auto_abort_report'] = paths['final_dir'] / "auto_abort_report.md"
    paths['auto_rescue_report'] = paths['final_dir'] / "auto_rescue_report.md"
    paths['whole_book_check'] = paths['final_dir'] / "7-whole-book-check.md"
    
    # Create all directories
    for key, path in paths.items():
        if 'dir' in key or key in ['drafts_alignment', 'drafts_outlines', 'drafts_chapters', 
                                    'drafts_qc', 'anchors_dir', 'logs_prompts', 
                                    'archive_snapshots', 'archive_reverted']:
            path.mkdir(parents=True, exist_ok=True)
    
    return paths


# ============================================================================
# Validation
# ============================================================================

def validate_path_in_workspace(path: Path, workspace_root: Path) -> bool:
    """
    Validate that path is within workspace_root (security check)
    Returns True if path is safe, False otherwise
    """
    try:
        resolved_path = path.resolve()
        resolved_root = workspace_root.resolve()
        return str(resolved_path).startswith(str(resolved_root))
    except:
        return False


def validate_run_id_consistency(run_id: str, run_dir: Path) -> bool:
    """
    Validate that run_id matches directory name
    """
    dir_name = run_dir.name
    return run_id == dir_name


# ============================================================================
# JSON Helpers
# ============================================================================

def load_json(path: Path, default: Any = None) -> Any:
    """Load JSON file with default fallback"""
    if not path.exists():
        return default if default is not None else {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return default if default is not None else {}


def save_json(path: Path, data: Any, indent: int = 2) -> bool:
    """Save JSON file (non-atomic, use atomic_write for critical data)"""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving JSON to {path}: {e}")
        return False


# ============================================================================
# Module Test
# ============================================================================

if __name__ == "__main__":
    print("=== Utility Functions Test ===\n")
    
    # Test ID generation
    run_id = generate_run_id()
    book_uid = generate_book_uid("测试小说")
    event_id = generate_event_id(run_id, "6.3", 1)
    
    print(f"run_id: {run_id}")
    print(f"book_uid: {book_uid}")
    print(f"event_id: {event_id}")
    
    # Test slug conversion
    print(f"\nto_slug('阴间外卖'): {to_slug('阴间外卖')}")
    print(f"to_slug('星际漂流者'): {to_slug('星际漂流者')}")
    
    # Test filename sanitization
    print(f"\nsanitize_filename('第一章：落日港'): {sanitize_filename('第一章：落日港')}")
    print(f"sanitize_filename('test<>:\"/\\|?.txt'): {sanitize_filename('test<>:\"/\\|?.txt')}")
    
    # Test chapter filename
    print(f"\nsanitize_chapter_filename(1, '深夜最后一单'): {sanitize_chapter_filename(1, '深夜最后一单')}")
    print(f"sanitize_chapter_filename(15, '恶鬼追杀', is_forced=True): {sanitize_chapter_filename(15, '恶鬼追杀', is_forced=True)}")
    
    print("\n=== All tests passed ===")
