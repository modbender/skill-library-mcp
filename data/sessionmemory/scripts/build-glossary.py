#!/usr/bin/env python3
"""
Session Glossary Builder
Scans session transcripts and builds a structured glossary index.
Designed to run periodically (cron) to keep the glossary up-to-date.

Output: memory/SESSION-GLOSSAR.md — a structured index of all sessions,
tagged by people, projects, decisions, tools, and key events.

Usage:
  python3 scripts/build-glossary.py                    # Full rebuild
  python3 scripts/build-glossary.py --incremental      # Only new sessions
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict

WORKSPACE = Path(os.environ.get("WORKSPACE", Path.home() / ".openclaw" / "workspace"))
SESSIONS_DIR = WORKSPACE / "memory" / "sessions"
GLOSSARY_PATH = WORKSPACE / "memory" / "SESSION-GLOSSAR.md"
STATE_PATH = WORKSPACE / "memory" / ".glossary-state.json"

# Known entities to track (bootstrap - will grow over time)
KNOWN_PEOPLE = {
    "annika": "Annika Reiß (@annika.jobwellbeing) — Job & Karriere Coach",
    "ilonka": "Ilonka Kokila Petal (@ilonka_kokila) — Holistic Psychologist",
    "wolf": "Wolf — Sítio do Castelo, Carrapateira",
    "igor": "Igor Pogany — CEO AI Advantage",
    "steffi": "Steffi — Dirks Partnerin, Byron Katie Coach",
    "stephanie": "Stephanie — PM bei AIA",
    "ariadne": "Ariadne — Visuals bei AIA",
    "daniel": "Daniel — Research bei AIA",
    "soraya": "Soraya — Dirks Tochter (~5 Jahre)",
    "tony": "Tony Robbins — AIA Partner",
    "hofreiter": "Hofreiter — Erlebnisfelder, CloneForce-Pitch",
    "thomas": "Thomas Hofreiter — Betreiber Hofreiter Erlebnisfelder",
}

KNOWN_PROJECTS = {
    "content.studio": "Content Studio — Cold Outreach Pipeline",
    "content-studio": "Content Studio — Cold Outreach Pipeline",
    "ilonka.website": "Ilonka Website — Case Study Showcase",
    "ilonka-website": "Ilonka Website — Case Study Showcase",
    "cloneforce": "CloneForce — AI Employee Business",
    "fairchain": "FairChain — Fair-Price Corridor App",
    "skillbook": "SkillBooks — Books for AI Agents",
    "workshop.factory": "Workshop Factory — AIA Curriculum Pipeline",
    "workshop-factory": "Workshop Factory — AIA Curriculum Pipeline",
    "mastery": "AIA Mastery — 12-Month Curriculum",
    "openclaw.starter": "OpenClaw Starter Kit — FaaS Setup",
    "faya.as.a.service": "FaaS — Faya as a Service",
    "faas": "FaaS — Faya as a Service",
}

DECISION_MARKERS = [
    "entscheidung", "decision", "decided", "entschieden",
    "ab jetzt", "from now on", "neue regel", "new rule",
    "standard", "default", "immer", "always", "nie mehr", "never again",
    "lesson", "lektion", "fehler", "mistake", "fix:",
]

def load_state():
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text())
    return {"processed": [], "last_run": None}

def save_state(state):
    STATE_PATH.write_text(json.dumps(state, indent=2))

def extract_date_from_filename(filename):
    """Extract date from session-YYYY-MM-DD-HHMM-*.md"""
    m = re.match(r"session-(\d{4}-\d{2}-\d{2})-(\d{4})", filename)
    if m:
        return m.group(1), m.group(2)
    return None, None

def scan_session(filepath):
    """Scan a session transcript for entities, topics, and key moments."""
    text = filepath.read_text(errors="replace")
    text_lower = text.lower()
    filename = filepath.name
    date, time = extract_date_from_filename(filename)
    
    result = {
        "file": filename,
        "date": date,
        "time": time,
        "size_kb": round(filepath.stat().st_size / 1024, 1),
        "people": [],
        "projects": [],
        "decisions": [],
        "topics": [],
        "summary_hints": [],
    }
    
    # Find people mentions
    for key, desc in KNOWN_PEOPLE.items():
        # Case-insensitive search, but require word boundary-ish matching
        if re.search(rf'\b{re.escape(key)}\b', text_lower):
            result["people"].append(key)
    
    # Find project mentions
    for key, desc in KNOWN_PROJECTS.items():
        pattern = key.replace(".", r"[\.\-_ ]?")
        if re.search(pattern, text_lower):
            result["projects"].append(key)
    
    # Find potential decisions (lines containing decision markers in context)
    lines = text.split("\n")
    for i, line in enumerate(lines):
        line_lower = line.lower()
        for marker in DECISION_MARKERS:
            if marker in line_lower and len(line.strip()) > 30 and len(line.strip()) < 300:
                snippet = line.strip()
                # Skip code, JSON, URLs, table rows, headers with just keywords
                if any(skip in snippet for skip in ['{', '}', 'http', '|', '```', 'MUST read', 'pending']):
                    continue
                if snippet.startswith(("**toolResult", "**Faya:**", "> -")):
                    continue
                if snippet.startswith("**") or snippet.startswith("- "):
                    snippet = snippet.lstrip("*- ").strip()
                if len(snippet) < 20:
                    continue
                if len(snippet) > 150:
                    snippet = snippet[:147] + "..."
                result["decisions"].append(snippet)
                break
    
    # Deduplicate decisions (keep unique-ish ones)
    seen = set()
    unique_decisions = []
    for d in result["decisions"]:
        key = d[:50].lower()
        if key not in seen:
            seen.add(key)
            unique_decisions.append(d)
    result["decisions"] = unique_decisions[:10]  # Cap at 10 per session
    
    # Detect major topics — require stronger signal (multiple mentions or specific context)
    topic_patterns = {
        "Instagram Analyse": r"(instagram.*(analy|scrape|profil)|@\w+.*follower|engagement.rate)",
        "Email Drafts": r"(_v[2-6]\.txt|email.*draft|outreach.*mail|agentmail.*send)",
        "Website Build": r"(vercel.*deploy|next\.?js.*build|ilonka.*vercel|lovable.*app)",
        "Cron Jobs": r"(cron.*(job|erstell|delet|disabl|enabl)|schedule.*every)",
        "Security": r"(security.*harden|prompt.*inject|credentials.*redact|gitignore)",
        "Curriculum": r"(month\s*[1-9]|amplifier|mastery.*curriculum|workshop.*build|PROPOSAL)",
        "Chatbot": r"(chatbot.*widget|chat.*panel|gpt.?4.?1.?nano|chatbot.*fix)",
        "CloneForce": r"(cloneforce|ai.employee|mac.?mini.*setup|mitarbeiter.*config)",
        "Research": r"(research.*engine|program.*discovery|competitor.*analy|reverse.*engineer)",
        "Memory/Sessions": r"(session.*transcript|vektoris|memory.*search|glossar|compact.*memory)",
        "Booking/Cal": r"(cal\.com|booking.*section|stripe.*integr|termin.*buch)",
        "Lead Capture": r"(lead.*captur|kontakt.*form.*submit|agentmail.*notification)",
    }
    for topic, pattern in topic_patterns.items():
        if re.search(pattern, text_lower):
            result["topics"].append(topic)
    
    return result

def build_glossary(sessions_data):
    """Build the glossary markdown from scanned session data."""
    
    # Organize by different dimensions
    people_sessions = defaultdict(list)
    project_sessions = defaultdict(list)
    topic_sessions = defaultdict(list)
    date_sessions = defaultdict(list)
    all_decisions = []
    
    for s in sessions_data:
        date = s["date"] or "unknown"
        date_sessions[date].append(s)
        
        for p in s["people"]:
            people_sessions[p].append(s)
        for p in s["projects"]:
            project_sessions[p].append(s)
        for t in s["topics"]:
            topic_sessions[t].append(s)
        for d in s["decisions"]:
            all_decisions.append({"date": date, "text": d, "file": s["file"]})
    
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    
    lines = [
        f"# SESSION-GLOSSAR",
        f"",
        f"Automatisch generiert: {now}",
        f"Sessions indexiert: {len(sessions_data)}",
        f"",
        f"Dieses Glossar ist ein strukturierter Index über alle Session-Transcripts.",
        f"Nutze es als Einstiegspunkt: finde hier WER, WAS, WANN — dann lies die Session für Details.",
        f"",
    ]
    
    # === PEOPLE ===
    lines.append("## 👤 Personen\n")
    for key in sorted(people_sessions.keys(), key=lambda k: len(people_sessions[k]), reverse=True):
        desc = KNOWN_PEOPLE.get(key, key)
        sessions = people_sessions[key]
        dates = sorted(set(s["date"] for s in sessions if s["date"]))
        date_range = f"{dates[0]} bis {dates[-1]}" if len(dates) > 1 else (dates[0] if dates else "?")
        files = [s["file"] for s in sessions[:5]]
        lines.append(f"### {desc}")
        lines.append(f"- **Erwähnt in:** {len(sessions)} Sessions ({date_range})")
        lines.append(f"- **Sessions:** {', '.join(files[:5])}" + (" ..." if len(sessions) > 5 else ""))
        if key == "annika":
            lines.append(f"- **Detail-Log:** memory/annika-log.md")
        lines.append("")
    
    # === PROJECTS ===
    lines.append("## 📁 Projekte\n")
    seen_projects = set()
    for key in sorted(project_sessions.keys(), key=lambda k: len(project_sessions[k]), reverse=True):
        desc = KNOWN_PROJECTS.get(key, key)
        # Dedupe aliases
        if desc in seen_projects:
            continue
        seen_projects.add(desc)
        sessions = project_sessions[key]
        dates = sorted(set(s["date"] for s in sessions if s["date"]))
        date_range = f"{dates[0]} bis {dates[-1]}" if len(dates) > 1 else (dates[0] if dates else "?")
        lines.append(f"### {desc}")
        lines.append(f"- **Erwähnt in:** {len(sessions)} Sessions ({date_range})")
        # Only show topics that appear in >20% of this project's sessions
        topic_counts = defaultdict(int)
        for s in sessions:
            for t in s["topics"]:
                topic_counts[t] += 1
        threshold = max(1, len(sessions) * 0.2)
        relevant_topics = [t for t, c in sorted(topic_counts.items(), key=lambda x: -x[1]) if c >= threshold]
        if relevant_topics:
            lines.append(f"- **Themen:** {', '.join(relevant_topics[:6])}")
        lines.append("")
    
    # === TOPICS ===
    lines.append("## 🏷️ Themen\n")
    for topic in sorted(topic_sessions.keys(), key=lambda k: len(topic_sessions[k]), reverse=True):
        sessions = topic_sessions[topic]
        dates = sorted(set(s["date"] for s in sessions if s["date"]))
        lines.append(f"- **{topic}:** {len(sessions)} Sessions ({dates[0] if dates else '?'} – {dates[-1] if dates else '?'})")
    lines.append("")
    
    # === TIMELINE ===
    lines.append("## 📅 Timeline\n")
    for date in sorted(date_sessions.keys()):
        sessions = date_sessions[date]
        total_kb = sum(s["size_kb"] for s in sessions)
        all_topics = set()
        all_people = set()
        for s in sessions:
            all_topics.update(s["topics"])
            all_people.update(s["people"])
        topics_str = ", ".join(sorted(all_topics)[:6])
        people_str = ", ".join(sorted(all_people)[:5])
        lines.append(f"### {date}")
        lines.append(f"- **Sessions:** {len(sessions)} ({total_kb:.0f} KB)")
        if all_people:
            lines.append(f"- **Personen:** {people_str}")
        if all_topics:
            lines.append(f"- **Themen:** {topics_str}")
        lines.append("")
    
    # === DECISIONS (last 30) ===
    lines.append("## ⚡ Entscheidungen & Lektionen (neueste zuerst)\n")
    all_decisions.sort(key=lambda d: d["date"], reverse=True)
    for d in all_decisions[:30]:
        lines.append(f"- [{d['date']}] {d['text']}")
    lines.append("")
    
    return "\n".join(lines)

def main():
    incremental = "--incremental" in sys.argv
    
    if not SESSIONS_DIR.exists():
        print(f"No sessions directory at {SESSIONS_DIR}")
        sys.exit(1)
    
    state = load_state() if incremental else {"processed": [], "last_run": None}
    processed_set = set(state["processed"])
    
    # Find all session files
    session_files = sorted(SESSIONS_DIR.glob("session-*.md"))
    print(f"Found {len(session_files)} session files")
    
    if incremental:
        session_files = [f for f in session_files if f.name not in processed_set]
        print(f"  → {len(session_files)} new (incremental mode)")
    
    if not session_files and incremental:
        print("Nothing new to process.")
        return
    
    # Scan all sessions (for full rebuild, scan everything; for incremental, merge)
    all_data = []
    
    # If incremental, load existing scan results
    scan_cache_path = WORKSPACE / "memory" / ".glossary-scans.json"
    if incremental and scan_cache_path.exists():
        all_data = json.loads(scan_cache_path.read_text())
        print(f"  Loaded {len(all_data)} cached scans")
    
    # Scan new files
    for i, fp in enumerate(session_files):
        if (i + 1) % 50 == 0:
            print(f"  Scanning {i+1}/{len(session_files)}...")
        try:
            data = scan_session(fp)
            all_data.append(data)
            processed_set.add(fp.name)
        except Exception as e:
            print(f"  Error scanning {fp.name}: {e}")
    
    print(f"Total sessions indexed: {len(all_data)}")
    
    # Build glossary
    glossary = build_glossary(all_data)
    GLOSSARY_PATH.write_text(glossary)
    print(f"Glossary written to {GLOSSARY_PATH} ({len(glossary)} bytes)")
    
    # Save state + scan cache
    state["processed"] = list(processed_set)
    state["last_run"] = datetime.utcnow().isoformat()
    save_state(state)
    
    scan_cache_path.write_text(json.dumps(all_data, ensure_ascii=False))
    print(f"Scan cache saved ({len(all_data)} entries)")

if __name__ == "__main__":
    main()
