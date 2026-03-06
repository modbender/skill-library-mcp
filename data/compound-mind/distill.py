#!/usr/bin/env python3
"""
CompoundMind v0.1 - Experience Distiller
Reads conversation logs / memory files and extracts structured knowledge.
Primary extraction: rule-based (no API required, instant, free).
Optional LLM enhancement: set COMPOUND_MIND_LLM_KEY to a real Anthropic key.

Output: compressed experience files in data/experiences/
"""

import os
import sys
import json
import hashlib
import re
import argparse
from datetime import datetime, date
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
EXP_DIR = DATA_DIR / "experiences"
MEMORY_DIR = Path("/root/.openclaw/workspace/memory")
STATE_FILE = DATA_DIR / "distill_state.json"

# Known people for relationship extraction
KNOWN_PERSONS = [
    "chartist", "xanalystx", "@xanalystx", "shellraiser", "kingmolt"
]

# Domain keyword mapping
DOMAIN_KEYWORDS = {
    "trading": ["trade", "trading", "polymarket", "bet", "kelly", "position", "usdc", "btc", "eth", "crypto",
                "market", "wallet", "price", "pnl", "p&l", "profit", "loss", "redemption", "snipe", "order",
                "balance", "fund", "token", "polygon", "clobclient", "gamma"],
    "coding": ["code", "git", "python", "script", "bug", "deploy", "build", "function", "api", "error",
               "debug", "cron", "service", "install", "pip", "import", "exception", "module", "subprocess",
               "systemd", "flutter", "dart", "android", "appbundle", "npm", "node"],
    "social": ["tweet", "post", "twitter", "x.com", "moltx", "moltbook", "farcaster", "instagram",
               "youtube", "content", "followers", "viral", "nostr", "upload", "engagement"],
    "communication": ["chartist", "message", "telegram", "reply", "conversation", "told", "asked", "said",
                      "per chartist", "instruction", "request"],
    "system": ["server", "vps", "cron", "systemd", "nginx", "proxy", "env", "config", "service", "daemon",
               "log", "memory", "skill", "workspace", "openclaw"],
}

# Patterns that signal a lesson
LESSON_PATTERNS = [
    r"(?i)(key\s+learn|lesson|learned|takeaway|important\s+note|critical\s+rule|remember|insight|discovery)",
    r"(?i)(must\s+always|never\s+again|never\s+use|always\s+add|never\s+share|never\s+assume)",
    r"(?i)(root\s+cause|the\s+fix|the\s+issue|the\s+problem\s+was)",
    r"(?i)(this\s+works\s+because|works\s+better|solution|resolved\s+by)",
]

# Patterns that signal a negative outcome / mistake
NEGATIVE_PATTERNS = [
    r"(?i)(fail|broke|bug|error|wrong|crash|lost|\-\$|burned|depleted|dead|killed|never\s+again)",
    r"(?i)(mistake|problem|issue|blocked|stuck|ruin|loss|negative)",
]

# Patterns that signal a positive outcome
POSITIVE_PATTERNS = [
    r"(?i)(success|worked|fixed|profit|gain|\+\$|won|correct|solved|breakthrough|live)",
    r"(?i)(first\s+profitable|validated|improved|better|launched|deployed|complete)",
]

# Patterns for decisions (action + outcome)
DECISION_PATTERNS = [
    r"(?i)(changed|switched|replaced|moved|rebuilt|rewrote|disabled|enabled|added|removed|upgraded)",
    r"(?i)(decided\s+to|chose\s+to|opted\s+to|went\s+with|picked|selected)",
]

# Patterns for skill updates
SKILL_PATTERNS = [
    r"(?i)(built|created|implemented|developed|wrote|designed|deployed|integrated|fixed|improved)",
    r"(?i)(first\s+time|new\s+skill|figured\s+out|mastered|learned\s+how\s+to)",
]

# Patterns for facts (specific, concrete facts worth storing)
FACT_PATTERNS = [
    r"(?i)(address:|wallet:|api key:|token:|endpoint:|port:|url:|path:|config:|must use|always use|version:)",
    r"(?i)(0x[0-9a-fA-F]{10,})",  # Ethereum addresses
    r"(?i)(\bsignature_type\s*=|chain_id|max_price|kelly\s+fraction|half.?life)",
]


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"processed": {}, "last_run": None}


def save_state(state: dict):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def file_hash(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def get_memory_files(memory_dir: Path, since: str = None) -> list[Path]:
    """Return all .md files in memory_dir, optionally filtered by date."""
    files = sorted(memory_dir.glob("*.md"))
    if since:
        cutoff = datetime.fromisoformat(since).date()
        filtered = []
        for f in files:
            match = re.match(r"(\d{4}-\d{2}-\d{2})", f.stem)
            if match:
                file_date = date.fromisoformat(match.group(1))
                if file_date >= cutoff:
                    filtered.append(f)
            else:
                filtered.append(f)
        return filtered
    return files


def detect_domain(text: str) -> str:
    """Detect primary domain from text."""
    text_lower = text.lower()
    scores = {}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[domain] = score
    if not scores:
        return "general"
    return max(scores, key=scores.get)


def is_negative(text: str) -> bool:
    return any(re.search(p, text) for p in NEGATIVE_PATTERNS)


def is_positive(text: str) -> bool:
    return any(re.search(p, text) for p in POSITIVE_PATTERNS)


def outcome_of(text: str) -> str:
    if is_positive(text) and not is_negative(text):
        return "positive"
    elif is_negative(text) and not is_positive(text):
        return "negative"
    elif is_positive(text) and is_negative(text):
        return "mixed"
    return "neutral"


def importance_of(text: str, outcome: str) -> int:
    """Estimate importance 1-5."""
    score = 3
    text_lower = text.lower()
    # High-signal keywords
    if any(kw in text_lower for kw in ["critical", "never", "always", "must", "key learning", "important"]):
        score += 1
    if outcome in ("positive", "negative"):
        score += 1
    if len(text) > 200:
        score += 1  # Detailed entries are usually more important
    if "chartist" in text_lower:
        score += 1  # Direct user instructions are critical
    return min(score, 5)


def extract_tags(text: str) -> list[str]:
    """Extract relevant tags from text."""
    tags = []
    text_lower = text.lower()
    all_keywords = {}
    for domain, kws in DOMAIN_KEYWORDS.items():
        for kw in kws:
            if kw in text_lower:
                all_keywords[kw] = domain
    # Top 5 keywords
    for kw in list(all_keywords.keys())[:5]:
        tags.append(kw)
    return list(set(tags))


def parse_markdown_sections(content: str) -> list[dict]:
    """Parse markdown into sections with headers and body text."""
    sections = []
    current_header = None
    current_lines = []

    for line in content.splitlines():
        header_match = re.match(r"^(#{1,3})\s+(.+)", line)
        if header_match:
            if current_lines and current_header is not None:
                sections.append({
                    "header": current_header,
                    "body": "\n".join(current_lines).strip()
                })
            current_header = header_match.group(2).strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines and current_header is not None:
        sections.append({
            "header": current_header or "intro",
            "body": "\n".join(current_lines).strip()
        })

    return sections


def extract_bullet_items(text: str) -> list[str]:
    """Extract bullet points from text."""
    items = []
    for line in text.splitlines():
        line = line.strip()
        # Markdown bullets, numbered, or **bold:** patterns
        if re.match(r"^[-*+]\s+(.+)", line):
            items.append(re.sub(r"^[-*+]\s+", "", line))
        elif re.match(r"^\d+\.\s+(.+)", line):
            items.append(re.sub(r"^\d+\.\s+", "", line))
        elif re.match(r"^\*\*(.+?)\*\*:?\s*(.+)", line):
            m = re.match(r"^\*\*(.+?)\*\*:?\s*(.*)", line)
            if m:
                items.append(f"{m.group(1)}: {m.group(2)}")
    return [i for i in items if len(i) > 15]  # Skip too-short items


def extract_lessons(sections: list[dict], source_date: str) -> list[dict]:
    """Extract lessons from sections."""
    lessons = []
    seen = set()

    for section in sections:
        header = section["header"]
        body = section["body"]
        full = f"{header}\n{body}"

        # Section-level lesson check
        section_is_lesson = any(re.search(p, header) for p in LESSON_PATTERNS)
        section_is_lesson = section_is_lesson or "learn" in header.lower() or "lesson" in header.lower() or "key" in header.lower()

        if section_is_lesson:
            # Extract all bullets from this section as lessons
            bullets = extract_bullet_items(body)
            for bullet in bullets:
                if bullet in seen:
                    continue
                seen.add(bullet)
                outcome = outcome_of(bullet)
                domain = detect_domain(bullet + " " + header)
                importance = importance_of(bullet, outcome)
                lessons.append({
                    "text": bullet[:500],
                    "domain": domain,
                    "outcome": outcome,
                    "importance": importance,
                    "tags": extract_tags(bullet)
                })
        else:
            # Scan body for lesson-pattern lines
            for line in body.splitlines():
                line = line.strip()
                if len(line) < 30:
                    continue
                if any(re.search(p, line) for p in LESSON_PATTERNS):
                    if line in seen:
                        continue
                    seen.add(line)
                    outcome = outcome_of(line)
                    domain = detect_domain(line + " " + header)
                    importance = importance_of(line, outcome)
                    lessons.append({
                        "text": line[:500],
                        "domain": domain,
                        "outcome": outcome,
                        "importance": importance,
                        "tags": extract_tags(line)
                    })

    return lessons[:30]  # Cap per file


def extract_decisions(sections: list[dict]) -> list[dict]:
    """Extract decision triplets from sections."""
    decisions = []
    seen_contexts = set()

    for section in sections:
        header = section["header"]
        body = section["body"]
        bullets = extract_bullet_items(body)

        # Look for pairs: action bullet near outcome bullet
        for i, bullet in enumerate(bullets):
            if not any(re.search(p, bullet) for p in DECISION_PATTERNS):
                continue

            # Context = header or preceding text
            context = header
            action = bullet[:300]
            outcome_text = ""

            # Look for outcome in next 2 bullets
            for j in range(i + 1, min(i + 3, len(bullets))):
                if is_positive(bullets[j]) or is_negative(bullets[j]):
                    outcome_text = bullets[j][:300]
                    break

            if not outcome_text:
                # Check if the bullet itself mentions outcome
                outcome_text = bullet[:300]

            key = action[:60]
            if key in seen_contexts:
                continue
            seen_contexts.add(key)

            quality = "good" if is_positive(outcome_text) else ("bad" if is_negative(outcome_text) else "neutral")
            decisions.append({
                "context": context[:200],
                "action": action,
                "outcome": outcome_text,
                "domain": detect_domain(action + " " + context),
                "quality": quality
            })

    return decisions[:20]


def extract_skills(sections: list[dict]) -> list[dict]:
    """Extract skill improvements from sections."""
    skills = []
    seen = set()

    for section in sections:
        header = section["header"]
        body = section["body"]

        # Sections about building/creating are skill-rich
        if any(kw in header.lower() for kw in ["built", "created", "deployed", "fixed", "launch", "achievement", "success"]):
            bullets = extract_bullet_items(body)
            for bullet in bullets[:5]:
                if any(re.search(p, bullet) for p in SKILL_PATTERNS):
                    # Extract the skill name
                    m = re.match(r"(?i)(built|created|implemented|fixed|improved|deployed|wrote|designed)\s+(.{5,60}?)[\s,\.:]", bullet)
                    skill_name = m.group(2) if m else header[:50]
                    key = skill_name[:40]
                    if key in seen:
                        continue
                    seen.add(key)
                    skills.append({
                        "skill": skill_name,
                        "domain": detect_domain(bullet + " " + header),
                        "change": bullet[:300],
                        "evidence": header[:100]
                    })

        # Also catch single build lines anywhere
        for line in body.splitlines():
            line = line.strip()
            if len(line) < 30 or len(line) > 400:
                continue
            if any(re.search(p, line) for p in SKILL_PATTERNS) and is_positive(line):
                m = re.match(r"(?i)(built|created|implemented|fixed|improved|deployed|wrote|designed)\s+(.{5,60}?)[\s,\.:]", line)
                skill_name = m.group(2) if m else line[:50]
                key = skill_name[:40]
                if key in seen:
                    continue
                seen.add(key)
                skills.append({
                    "skill": skill_name,
                    "domain": detect_domain(line),
                    "change": line[:300],
                    "evidence": f"From section: {header}"
                })

    return skills[:15]


def extract_relationships(sections: list[dict]) -> list[dict]:
    """Extract relationship/person insights."""
    relationships = []
    seen = set()

    for section in sections:
        body = section["body"]
        header = section["header"]
        full_text = f"{header} {body}"

        for person in KNOWN_PERSONS:
            if person.lower() not in full_text.lower():
                continue

            # Find sentences mentioning this person
            sentences = re.split(r"[.!?\n]", full_text)
            for sentence in sentences:
                if person.lower() not in sentence.lower():
                    continue
                sentence = sentence.strip()
                if len(sentence) < 20 or len(sentence) > 400:
                    continue

                # Only include sentences that reveal preference/insight
                if any(kw in sentence.lower() for kw in ["prefer", "said", "told", "wants", "asked", "rule", "instruction", "never", "always", "per ", "note:"]):
                    key = sentence[:50]
                    if key in seen:
                        continue
                    seen.add(key)
                    clean_person = person.lstrip("@").capitalize()
                    relationships.append({
                        "person": clean_person,
                        "insight": sentence[:300],
                        "interaction_type": "feedback" if any(kw in sentence.lower() for kw in ["said", "told", "per", "asked"]) else "collaboration"
                    })

    return relationships[:10]


def extract_facts(sections: list[dict]) -> list[dict]:
    """Extract specific, concrete facts."""
    facts = []
    seen = set()

    for section in sections:
        body = section["body"]
        header = section["header"]

        for line in body.splitlines():
            line = line.strip()
            if len(line) < 15 or len(line) > 400:
                continue

            if any(re.search(p, line) for p in FACT_PATTERNS):
                key = line[:50]
                if key in seen:
                    continue
                seen.add(key)
                # Strip markdown formatting
                clean = re.sub(r"\*{1,2}(.+?)\*{1,2}", r"\1", line)
                clean = re.sub(r"`(.+?)`", r"\1", clean)
                facts.append({
                    "fact": clean[:400],
                    "domain": detect_domain(line + " " + header),
                    "tags": extract_tags(line)
                })

    return facts[:20]


def extract_experiences_rule_based(content: str, source_file: str) -> dict:
    """Pure rule-based extraction. No API required."""
    sections = parse_markdown_sections(content)

    lessons = extract_lessons(sections, source_file)
    decisions = extract_decisions(sections)
    skill_updates = extract_skills(sections)
    relationships = extract_relationships(sections)
    facts = extract_facts(sections)

    return {
        "lessons": lessons,
        "decisions": decisions,
        "skill_updates": skill_updates,
        "relationships": relationships,
        "facts": facts
    }


def distill_file(path: Path, state: dict, force: bool = False) -> dict | None:
    """Distill a single memory file. Returns experience dict or None if skipped."""
    h = file_hash(path)
    relative = str(path.relative_to(path.parent)) if MEMORY_DIR not in path.parents else str(path.relative_to(MEMORY_DIR))

    if not force and state["processed"].get(relative) == h:
        print(f"  skip (unchanged): {relative}")
        return None

    print(f"  distilling: {relative}")
    content = path.read_text(errors="replace")

    if len(content.strip()) < 50:
        print(f"  skip (too short): {relative}")
        return None

    extracted = extract_experiences_rule_based(content, relative)

    # Parse date from filename
    match = re.match(r"(\d{4}-\d{2}-\d{2})", path.stem)
    source_date = match.group(1) if match else date.today().isoformat()

    exp_id = hashlib.md5(relative.encode()).hexdigest()[:12]

    experience = {
        "id": exp_id,
        "source": relative,
        "source_date": source_date,
        "distilled_at": datetime.now().isoformat(),
        "hash": h,
        **extracted
    }

    EXP_DIR.mkdir(parents=True, exist_ok=True)
    exp_path = EXP_DIR / f"{exp_id}.json"
    exp_path.write_text(json.dumps(experience, indent=2))

    state["processed"][relative] = h
    total = sum(len(experience.get(k, [])) for k in ["lessons", "decisions", "skill_updates", "relationships", "facts"])
    print(f"  -> {exp_path.name}: {total} items ({len(extracted['lessons'])}L/{len(extracted['decisions'])}D/{len(extracted['skill_updates'])}S/{len(extracted['relationships'])}R/{len(extracted['facts'])}F)")
    return experience


def distill_all(memory_dir: Path, since: str = None, force: bool = False, limit: int = None):
    """Distill all (or new) memory files."""
    state = load_state()
    files = get_memory_files(memory_dir, since)

    if limit:
        files = files[-limit:]

    print(f"CompoundMind Distiller")
    print(f"Processing {len(files)} files from: {memory_dir}")
    print(f"Output: {EXP_DIR}")
    print()

    distilled = 0
    skipped = 0
    total_items = 0

    for f in files:
        result = distill_file(f, state, force=force)
        if result is not None:
            distilled += 1
            total_items += sum(len(result.get(k, [])) for k in ["lessons", "decisions", "skill_updates", "relationships", "facts"])
        else:
            skipped += 1

    state["last_run"] = datetime.now().isoformat()
    save_state(state)

    print(f"\nDone. Distilled: {distilled} files, Skipped: {skipped} (unchanged)")
    print(f"Total items extracted: {total_items}")
    print(f"Total experience files: {len(list(EXP_DIR.glob('*.json')))}")


def main():
    parser = argparse.ArgumentParser(description="CompoundMind Experience Distiller")
    parser.add_argument("--since", help="Only process files from this date (YYYY-MM-DD)")
    parser.add_argument("--force", action="store_true", help="Re-distill even unchanged files")
    parser.add_argument("--limit", type=int, help="Only process last N files")
    parser.add_argument("--file", help="Distill a single specific file")
    parser.add_argument("--memory-dir", default=str(MEMORY_DIR), help="Memory directory")
    args = parser.parse_args()

    mem_dir = Path(args.memory_dir)
    if not mem_dir.exists():
        print(f"Memory dir not found: {mem_dir}", file=sys.stderr)
        sys.exit(1)

    if args.file:
        path = Path(args.file)
        if not path.exists():
            path = mem_dir / args.file
        state = load_state()
        distill_file(path, state, force=True)
        state["last_run"] = datetime.now().isoformat()
        save_state(state)
    else:
        distill_all(mem_dir, since=args.since, force=args.force, limit=args.limit)


if __name__ == "__main__":
    main()
