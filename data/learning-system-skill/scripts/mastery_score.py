#!/usr/bin/env python3
"""
Mastery Score Calculator for Learning System Skill

Calculates mastery scores by weighting:
- Recency: how recently you engaged with a topic (exponential decay)
- Repetition: how many times you've engaged across different sessions
- Depth: deep-dive notes count more than passing mentions

Score formula:
  raw_score = sum(weight_i * decay(days_since_i))
  where weight_i = 3.0 for deep-dive, 2.0 for PR/recap, 1.0 for mention

Decay function: exp(-days / half_life), half_life = 30 days

Output: ranked topics with scores, suggested level changes, and decay warnings.
"""
import re
import sys
import json
import math
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

# --- Config ---
WORKSPACE = Path.home() / ".openclaw/workspace"
KNOWLEDGE_MAP = WORKSPACE / "notes/areas/ai-knowledge-map.md"
DEEP_DIVES = WORKSPACE / "notes/areas/deep-dives"
MEMORY_DIR = WORKSPACE / "memory"
HALF_LIFE_DAYS = 30  # score halves every 30 days
WEIGHTS = {"deep-dive": 3.0, "pr": 2.0, "recap": 2.0, "mention": 1.0}

# Thresholds for level suggestions
SCORE_THRESHOLDS = {
    "green": 8.0,   # 🟢 精通: high score = frequent + recent + deep
    "yellow": 3.0,  # 🟡 熟悉: moderate engagement
    # below yellow = 🔴 入门
}

DECAY_WARNING_DAYS = 60  # warn if no engagement in 60 days


def decay(days_ago: float) -> float:
    """Exponential decay: returns 1.0 for today, 0.5 at half_life days."""
    return math.exp(-days_ago * math.log(2) / HALF_LIFE_DAYS)


def parse_knowledge_map():
    """Parse current knowledge map, return {topic: level}."""
    if not KNOWLEDGE_MAP.exists():
        return {}
    topics = {}
    # Skip lines: headers, separators, dates (YYYY-MM-DD)
    skip_re = re.compile(r"^(\d{4}-\d{2}-\d{2}|主题|---)")
    for line in KNOWLEDGE_MAP.read_text().split("\n"):
        if "|" in line and any(e in line for e in ["🔴", "🟡", "🟢"]):
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 4:
                topic = parts[1].strip()
                level = "🟢" if "🟢" in parts[2] else "🟡" if "🟡" in parts[2] else "🔴"
                if topic and not skip_re.match(topic):
                    topics[topic] = level
    return topics


def scan_deep_dives():
    """Scan deep-dive notes, return {topic_keyword: [dates]}."""
    engagements = defaultdict(list)
    if not DEEP_DIVES.exists():
        return engagements
    for note in DEEP_DIVES.glob("*.md"):
        mtime = datetime.fromtimestamp(note.stat().st_mtime)
        # Use filename as topic keyword (e.g., mcp-tool-call-design -> mcp, tool, call, design)
        keywords = note.stem.lower().replace("-", " ").replace("_", " ").split()
        content = note.read_text().lower()
        for kw in keywords:
            if len(kw) > 2:  # skip tiny words
                engagements[kw].append({"date": mtime, "type": "deep-dive"})
        # Also extract topic from first heading
        heading = re.search(r"^#\s+(.+)", note.read_text(), re.MULTILINE)
        if heading:
            for word in heading.group(1).lower().split():
                word = re.sub(r"[^\w]", "", word)
                if len(word) > 2:
                    engagements[word].append({"date": mtime, "type": "deep-dive"})
    return engagements


def scan_memory_logs(days=90):
    """Scan memory logs for topic mentions, PRs, recaps."""
    engagements = defaultdict(list)
    now = datetime.now()
    for i in range(days):
        date = now - timedelta(days=i)
        log_file = MEMORY_DIR / f"{date.strftime('%Y-%m-%d')}.md"
        if not log_file.exists():
            continue
        content = log_file.read_text()
        lines = content.split("\n")
        for line in lines:
            line_lower = line.lower()
            # Detect recaps
            if "复盘" in line or "recap" in line_lower:
                keywords = extract_keywords(line)
                for kw in keywords:
                    engagements[kw].append({"date": date, "type": "recap"})
            # Detect PRs
            elif "pr #" in line_lower or "pr#" in line_lower:
                keywords = extract_keywords(line)
                for kw in keywords:
                    engagements[kw].append({"date": date, "type": "pr"})
            # General mentions of known topics
            else:
                keywords = extract_keywords(line)
                for kw in keywords:
                    engagements[kw].append({"date": date, "type": "mention"})
    return engagements


def extract_keywords(text):
    """Extract meaningful keywords from a line of text."""
    # Common AI/ML terms to look for
    ai_terms = [
        "transformer", "attention", "tokeniz", "embedding", "bert", "gpt",
        "llama", "mistral", "qwen", "gemma", "deepseek",
        "sft", "rlhf", "dpo", "ppo", "grpo",
        "pretrain", "finetun", "lora", "qlora", "peft",
        "fsdp", "deepspeed", "megatron", "distributed train",
        "quantiz", "awq", "gptq", "gguf", "bitsandbytes", "fp8", "int4",
        "kv cache", "flash attention", "pagedattention", "speculative decod",
        "vllm", "sglang", "tensorrt", "llama.cpp",
        "mcp", "tool call", "multi-agent", "agent 编排", "agent 安全",
        "agent 可观测", "记忆管理", "memory manag",
        "rag", "vector search", "retrieval",
        "diffusion", "stable diffusion", "imagen",
        "whisper", "tts", "speech",
        "interpretab", "mechanistic", "sae", "probe",
        "moe", "mixture of expert",
        "distillat", "pruning", "model merg",
        "context window", "rope", "alibi", "yarn",
        "guardrail", "jailbreak", "prompt injection",
        "compaction", "context budget",
        "structured output", "json schema",
        "代码生成", "code gen",
        "多模态", "multimodal",
        "视频生成", "video gen",
    ]
    text_lower = text.lower()
    found = []
    for term in ai_terms:
        if term in text_lower:
            found.append(term)
    return found


def match_topic_to_engagements(topic, all_engagements):
    """Match a knowledge map topic to engagement records."""
    topic_lower = topic.lower()
    topic_words = re.sub(r"[^\w\s]", "", topic_lower).split()
    matched = []
    for keyword, records in all_engagements.items():
        # Direct substring match
        if keyword in topic_lower or any(keyword in w for w in topic_words):
            matched.extend(records)
        # Reverse: topic word in keyword
        for tw in topic_words:
            if len(tw) > 2 and tw in keyword:
                matched.extend(records)
                break
    # Deduplicate by date+type
    seen = set()
    unique = []
    for r in matched:
        key = (r["date"].strftime("%Y-%m-%d"), r["type"])
        if key not in seen:
            seen.add(key)
            unique.append(r)
    return unique


def calculate_score(engagements):
    """Calculate mastery score from engagement records."""
    now = datetime.now()
    score = 0.0
    for record in engagements:
        days_ago = (now - record["date"]).days
        weight = WEIGHTS.get(record["type"], 1.0)
        score += weight * decay(days_ago)
    return round(score, 2)


def suggest_level(score):
    """Suggest mastery level based on score."""
    if score >= SCORE_THRESHOLDS["green"]:
        return "🟢"
    elif score >= SCORE_THRESHOLDS["yellow"]:
        return "🟡"
    else:
        return "🔴"


def last_engagement_days(engagements):
    """Days since last engagement."""
    if not engagements:
        return None
    now = datetime.now()
    most_recent = max(r["date"] for r in engagements)
    return (now - most_recent).days


def generate_report():
    """Generate mastery score report."""
    topics = parse_knowledge_map()
    if not topics:
        print("❌ Knowledge map not found or empty.")
        return

    # Collect all engagements
    deep_dive_eng = scan_deep_dives()
    memory_eng = scan_memory_logs(days=90)

    # Merge
    all_eng = defaultdict(list)
    for k, v in deep_dive_eng.items():
        all_eng[k].extend(v)
    for k, v in memory_eng.items():
        all_eng[k].extend(v)

    # Calculate per-topic
    results = []
    for topic, current_level in topics.items():
        matched = match_topic_to_engagements(topic, all_eng)
        score = calculate_score(matched)
        suggested = suggest_level(score)
        last_days = last_engagement_days(matched)
        engagement_count = len(matched)

        change = ""
        if suggested != current_level:
            level_order = {"🔴": 0, "🟡": 1, "🟢": 2}
            if level_order.get(suggested, 0) > level_order.get(current_level, 0):
                change = "⬆️ 建议升级"
            elif level_order.get(suggested, 0) < level_order.get(current_level, 0):
                change = "⬇️ 考虑降级"

        decay_warning = ""
        if last_days is not None and last_days > DECAY_WARNING_DAYS:
            decay_warning = f"⚠️ {last_days}天未接触"
        elif last_days is None:
            decay_warning = "⚠️ 无记录"

        results.append({
            "topic": topic,
            "current": current_level,
            "score": score,
            "suggested": suggested,
            "engagements": engagement_count,
            "last_days": last_days,
            "change": change,
            "warning": decay_warning,
        })

    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)

    # Output
    print("# Mastery Score Report")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Half-life: {HALF_LIFE_DAYS} days | Scan range: 90 days\n")

    print(f"| {'主题':<25} | 当前 | Score | 建议 | 接触次数 | 最近 | 变更 |")
    print(f"|{'-'*27}|------|-------|------|----------|------|------|")
    for r in results:
        last_str = f"{r['last_days']}d" if r['last_days'] is not None else "N/A"
        flags = f"{r['change']} {r['warning']}".strip()
        print(f"| {r['topic']:<25} | {r['current']}  | {r['score']:>5} | {r['suggested']}  | {r['engagements']:>8} | {last_str:>4} | {flags} |")

    # Summary
    changes = [r for r in results if r["change"]]
    warnings = [r for r in results if r["warning"]]
    print(f"\n## Summary")
    print(f"- Topics tracked: {len(results)}")
    print(f"- Level change suggestions: {len(changes)}")
    print(f"- Decay warnings: {len(warnings)}")

    if changes:
        print(f"\n## Suggested Changes")
        for r in changes:
            print(f"- {r['topic']}: {r['current']} → {r['suggested']} (score: {r['score']}, {r['change']})")

    # JSON output option
    if "--json" in sys.argv:
        print("\n## JSON")
        print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    generate_report()
