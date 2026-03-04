#!/usr/bin/env python3
"""
antigravity_digest.py — Antigravity walkthrough → Zettel note pipeline

Scans ~/.gemini/antigravity/brain/*/walkthrough.md for new or updated
walkthroughs and converts them into Zettel notes in memory/notes/.

Designed to run alongside session_digest_write.py via LaunchAgent or manually.
"""
from __future__ import annotations
import json, hashlib, os, pathlib, datetime as dt, re, subprocess

ROOT = pathlib.Path(os.environ.get('OPENCLAW_WORKSPACE', os.path.expanduser('~/.openclaw/workspace')))
BRAIN_DIR = pathlib.Path(os.environ.get('ANTIGRAVITY_BRAIN', os.path.expanduser('~/.gemini/antigravity/brain')))
NOTES_DIR = ROOT / 'memory' / 'notes'
STATE_PATH = ROOT / 'projects' / 'zettel-memory-openclaw' / 'state' / 'antigravity_state.json'
LINK_SCRIPT = ROOT / 'projects' / 'zettel-memory-openclaw' / 'scripts' / 'link_notes.py'


def iso_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def load_state() -> dict:
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text(encoding='utf-8'))
        except Exception:
            pass
    return {'processed': {}}


def save_state(st: dict):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(st, ensure_ascii=False, indent=2), encoding='utf-8')


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def slug(text: str) -> str:
    s = re.sub(r'[^a-zA-Z0-9\u3040-\u9fff]+', '-', text.lower())
    return s.strip('-')[:50]


def extract_title(text: str) -> str:
    """Extract title from walkthrough markdown."""
    for line in text.split('\n'):
        line = line.strip()
        if line.startswith('# '):
            title = line[2:].strip()
            # Remove "Walkthrough:" prefix if present
            title = re.sub(r'^Walkthrough:\s*', '', title, flags=re.IGNORECASE)
            return title[:80]
    return 'Antigravity Session'


def extract_tags(text: str) -> list[str]:
    """Extract meaningful tags from walkthrough content."""
    # Look for file extensions, tool names, key concepts
    tag_patterns = {
        r'\bAGENTS\.md\b': 'agents',
        r'\bRUNBOOK\.md\b': 'runbook',
        r'\bSOUL\.md\b': 'soul',
        r'\bMEMORY\.md\b': 'memory',
        r'\bguard-scanner\b': 'guard-scanner',
        r'\bzettel\b': 'zettelkasten',
        r'\bnote\.com\b': 'note-com',
        r'\bMoltbook\b': 'moltbook',
        r'\bLaunchAgent\b': 'launchagent',
        r'\bPDF\b': 'pdf',
        r'\barXiv\b': 'arxiv',
        r'\bZenodo\b': 'zenodo',
        r'\bTailscale\b': 'tailscale',
        r'\bOpenClaw\b': 'openclaw',
        r'\bComfyUI\b': 'comfyui',
        r'\b論文\b': 'paper',
        r'\bエピソード\b': 'episode',
        r'\bセキュリティ\b': 'security',
        r'\bブラウザ\b': 'browser',
    }
    tags = ['antigravity', 'walkthrough']
    for pattern, tag in tag_patterns.items():
        if re.search(pattern, text, re.IGNORECASE):
            tags.append(tag)
    return tags[:8]  # Cap at 8 tags


def extract_summary(text: str) -> str:
    """Extract a concise summary from walkthrough content."""
    lines = text.split('\n')
    summary_parts = []
    in_section = False

    for line in lines:
        stripped = line.strip()
        # Grab content from ## sections (not sub-sub sections)
        if stripped.startswith('## ') and not stripped.startswith('### '):
            in_section = True
            continue
        if stripped.startswith('# '):
            in_section = False
            continue
        if in_section and stripped and not stripped.startswith('|') and not stripped.startswith('```'):
            # Clean markdown formatting
            clean = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', stripped)
            clean = re.sub(r'[*_`]', '', clean)
            if clean and len(clean) > 10:
                summary_parts.append(clean)
            if len(summary_parts) >= 6:
                break

    return '\n'.join(f'- {p}' for p in summary_parts) if summary_parts else text[:300]


def make_note(conv_id: str, walkthrough_text: str, mtime: float) -> pathlib.Path:
    """Create a Zettel note from walkthrough content."""
    NOTES_DIR.mkdir(parents=True, exist_ok=True)

    now = dt.datetime.now(dt.timezone.utc)
    zid = f"zettel-{now.strftime('%Y%m%d-%H%M%S')}-{now.microsecond:06d}"

    title = extract_title(walkthrough_text)
    tags = extract_tags(walkthrough_text)
    summary = extract_summary(walkthrough_text)
    slug_title = slug(title)

    content = f"""---
id: {zid}
title: {title}
tags: [{', '.join(tags)}]
entities: [Antigravity, Guava]
source: antigravity/brain/{conv_id}/walkthrough.md
created_at: {now.isoformat()}
updated_at: {now.isoformat()}
supersedes: null
links: []
confidence: 0.75
---

## Antigravity Session Summary

{summary}

---
*Auto-generated from Antigravity walkthrough `{conv_id}`*
"""
    filename = f"{zid}-antigravity-{slug_title}.md"
    out = NOTES_DIR / filename
    out.write_text(content, encoding='utf-8')
    return out


def main() -> int:
    st = load_state()
    processed = st.get('processed', {})
    new_count = 0

    # Scan all brain directories for walkthrough.md
    if not BRAIN_DIR.exists():
        print(f'Brain directory not found: {BRAIN_DIR}')
        return 1

    for conv_dir in sorted(BRAIN_DIR.iterdir()):
        if not conv_dir.is_dir():
            continue

        walkthrough = conv_dir / 'walkthrough.md'
        if not walkthrough.exists():
            continue

        conv_id = conv_dir.name
        text = walkthrough.read_text(encoding='utf-8').strip()
        if not text or len(text) < 50:
            continue

        chash = content_hash(text)
        mtime = walkthrough.stat().st_mtime

        # Skip if already processed with same hash
        prev = processed.get(conv_id, {})
        if prev.get('hash') == chash:
            continue

        note_path = make_note(conv_id, text, mtime)
        processed[conv_id] = {
            'hash': chash,
            'note': str(note_path),
            'processed_at': iso_now(),
        }
        new_count += 1
        print(f'Created: {note_path.name} (from {conv_id[:8]}...)')

    if new_count > 0:
        # Re-link all notes
        subprocess.run(['python3', str(LINK_SCRIPT)], check=False)
        print(f'Processed {new_count} new walkthrough(s)')
    else:
        print('No new walkthroughs')

    st['processed'] = processed
    st['last_run'] = iso_now()
    save_state(st)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
