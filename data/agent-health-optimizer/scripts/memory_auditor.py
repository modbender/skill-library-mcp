#!/usr/bin/env python3
"""Memory Auditor — check memory files for hygiene issues.

Usage: python3 memory_auditor.py [workspace_path]

Checks:
  - Imperative rules (should be declarative)
  - Missing source tags
  - Stale/outdated entries
  - External content stored as instructions
  - Size and organization
"""

import os, sys, re, json
from pathlib import Path
from datetime import datetime, timedelta

ws = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / ".openclaw" / "workspace"

class MemoryAuditor:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.stats = {}

    def audit_memory_md(self):
        """Audit MEMORY.md for hygiene issues."""
        mem = ws / "MEMORY.md"
        if not mem.exists():
            self.issues.append("❌ MEMORY.md does not exist")
            return

        content = mem.read_text()
        lines = content.split('\n')
        self.stats["memory_md_lines"] = len(lines)
        self.stats["memory_md_bytes"] = len(content)

        # Check 1: Imperative rules (anti-poisoning)
        imperative_lines = []
        for i, line in enumerate(lines):
            stripped = line.strip()
            if re.match(r'^[-*]\s+(always|never|you must|you should|do not|don\'t|make sure)\b', stripped, re.IGNORECASE):
                imperative_lines.append((i+1, stripped[:80]))

        if imperative_lines:
            self.issues.append(f"⚠️ {len(imperative_lines)} imperative rules found (should be declarative facts):")
            for lineno, text in imperative_lines[:5]:
                self.issues.append(f"   Line {lineno}: {text}")
            if len(imperative_lines) > 5:
                self.issues.append(f"   ... and {len(imperative_lines)-5} more")

        # Check 2: Source tags
        fact_lines = [l for l in lines if re.match(r'^[-*]\s+\w', l.strip())]
        tagged = [l for l in fact_lines if re.search(r'\(source:|来源:', l, re.IGNORECASE)]
        self.stats["facts_total"] = len(fact_lines)
        self.stats["facts_tagged"] = len(tagged)
        
        if fact_lines:
            ratio = len(tagged) / len(fact_lines)
            if ratio < 0.1:
                self.warnings.append(f"💡 Only {len(tagged)}/{len(fact_lines)} facts have source tags ({ratio:.0%})")

        # Check 3: Dates — find entries with dates and check staleness
        date_pattern = re.compile(r'(\d{4}-\d{2}-\d{2})')
        stale_entries = []
        cutoff = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        for i, line in enumerate(lines):
            dates = date_pattern.findall(line)
            for d in dates:
                if d < cutoff and any(kw in line.lower() for kw in ["准备", "计划", "待", "todo", "pending", "waiting"]):
                    stale_entries.append((i+1, line.strip()[:80]))

        if stale_entries:
            self.warnings.append(f"💡 {len(stale_entries)} potentially stale entries (>30 days with pending status):")
            for lineno, text in stale_entries[:3]:
                self.warnings.append(f"   Line {lineno}: {text}")

        # Check 4: Size check
        if len(content) > 10000:
            self.warnings.append(f"💡 MEMORY.md is large ({len(content)} bytes) — consider archiving old entries")
        
        # Check 5: External content patterns (URLs stored as instructions)
        external_patterns = [
            (r'https?://\S+.*(?:always|must|should)', "URL with imperative language"),
            (r'(?:webhook|api|curl).*(?:run|execute|call)', "Possible stored command from external source"),
        ]
        for pattern, desc in external_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                self.warnings.append(f"💡 Found pattern '{desc}' — verify not from external source")

    def audit_daily_logs(self):
        """Audit daily log files."""
        mem_dir = ws / "memory"
        if not mem_dir.exists():
            self.issues.append("❌ memory/ directory missing")
            return

        daily_files = sorted(mem_dir.glob("????-??-??.md"))
        self.stats["daily_files_total"] = len(daily_files)

        if not daily_files:
            self.warnings.append("💡 No daily log files found")
            return

        # Check recent activity
        today = datetime.now().strftime("%Y-%m-%d")
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        recent = [f for f in daily_files if f.stem >= week_ago]
        self.stats["daily_files_last_week"] = len(recent)

        if not recent:
            self.warnings.append("💡 No daily logs in the last week — agent may not be logging")

        # Check for very large daily files
        for f in daily_files[-7:]:  # Last 7
            size = f.stat().st_size
            if size > 20000:
                self.warnings.append(f"💡 {f.name} is large ({size} bytes) — consider summarizing to MEMORY.md")

        # Check oldest file — suggest archiving
        if len(daily_files) > 30:
            oldest = daily_files[0].stem
            self.warnings.append(f"💡 {len(daily_files)} daily files (oldest: {oldest}) — consider archiving old ones")

    def audit_agents_md(self):
        """Check AGENTS.md for completeness."""
        agents = ws / "AGENTS.md"
        if not agents.exists():
            self.issues.append("❌ AGENTS.md missing")
            return

        content = agents.read_text()
        
        recommended_sections = {
            "memory": "Memory management",
            "safety": "Safety rules", 
            "wal": "WAL Protocol",
            "heartbeat": "Heartbeat configuration",
        }
        
        for keyword, desc in recommended_sections.items():
            if keyword.lower() not in content.lower():
                self.warnings.append(f"💡 AGENTS.md missing section: {desc}")

    def run(self):
        print("\n🔍 Memory Auditor")
        print("=" * 60)

        self.audit_memory_md()
        self.audit_daily_logs()
        self.audit_agents_md()

        # Results
        print("\n📊 Stats:")
        for k, v in self.stats.items():
            print(f"  {k}: {v}")

        if self.issues:
            print(f"\n🚨 Issues ({len(self.issues)}):")
            for i in self.issues:
                print(f"  {i}")

        if self.warnings:
            print(f"\n💡 Suggestions ({len(self.warnings)}):")
            for w in self.warnings:
                print(f"  {w}")

        if not self.issues and not self.warnings:
            print("\n✅ Memory is clean — no issues found!")

        # Health summary
        issue_count = len(self.issues)
        warning_count = len(self.warnings)
        if issue_count == 0 and warning_count <= 2:
            health = "🟢 Healthy"
        elif issue_count <= 1 and warning_count <= 5:
            health = "🟡 Needs attention"
        else:
            health = "🔴 Needs cleanup"

        print(f"\n🏥 Memory Health: {health}")

        # Save report
        report = {
            "health": health,
            "stats": self.stats,
            "issues": self.issues,
            "warnings": self.warnings,
            "timestamp": datetime.now().isoformat()
        }
        report_path = ws / "memory" / "memory-audit.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
        print(f"📊 Report saved: {report_path}")

if __name__ == "__main__":
    MemoryAuditor().run()
