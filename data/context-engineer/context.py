#!/usr/bin/env python3
"""Context Window Optimizer — analyze, audit, and optimize agent context utilization.

Stdlib-only (no external deps). Renders rich terminal reports with Unicode
box drawing, block-element bar charts, and ANSI colours.

Token estimates are approximate (word-count heuristic, ~1 token per 4 chars).

Part of the Anvil AI toolkit — https://anvil-ai.io
"""

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# ANSI colour helpers
# ---------------------------------------------------------------------------

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
WHITE = "\033[97m"
MAGENTA = "\033[95m"

# Detect colour support
NO_COLOR = os.environ.get("NO_COLOR") is not None or not sys.stdout.isatty()


def c(text, *codes):
    """Wrap *text* with ANSI escape codes (respects NO_COLOR)."""
    if NO_COLOR:
        return str(text)
    return "".join(codes) + str(text) + RESET


def strip_ansi(s: str) -> str:
    """Remove ANSI escape sequences for length calculations."""
    return re.sub(r"\033\[[0-9;]*m", "", s)


# ---------------------------------------------------------------------------
# Token estimation
# ---------------------------------------------------------------------------

def estimate_tokens(text: str) -> int:
    """Approximate token count using character-based heuristic (~4 chars/token).

    This is a rough estimate. For precise counts, use a model-specific tokenizer.
    """
    return max(1, len(text) // 4)


def format_tokens(n: int) -> str:
    """Human-friendly token count: 1.3M, 847K, 198."""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


# ---------------------------------------------------------------------------
# Box-drawing helpers (matching cacheforge-stats style)
# ---------------------------------------------------------------------------

BOX_TL = "\u250c"
BOX_TR = "\u2510"
BOX_BL = "\u2514"
BOX_BR = "\u2518"
BOX_H = "\u2500"
BOX_V = "\u2502"
BOX_ML = "\u251c"
BOX_MR = "\u2524"

BLOCK_FULL = "\u2588"
BLOCK_LIGHT = "\u2591"


def term_width(default: int = 60) -> int:
    try:
        cols = shutil.get_terminal_size((default, 24)).columns
    except Exception:
        cols = default
    return max(cols, 40)


def box_top(w: int) -> str:
    return BOX_TL + BOX_H * w + BOX_TR


def box_bot(w: int) -> str:
    return BOX_BL + BOX_H * w + BOX_BR


def box_sep(w: int) -> str:
    return BOX_ML + BOX_H * w + BOX_MR


def box_row(text: str, w: int) -> str:
    visible = len(strip_ansi(text))
    pad = max(w - visible - 1, 0)
    return f"{BOX_V} {text}{' ' * pad}{BOX_V}"


def box_empty(w: int) -> str:
    return box_row("", w)


def print_box(title: str, rows: list, w: int = 60):
    print(box_top(w))
    print(box_row(c(f" {title}", BOLD, CYAN), w))
    print(box_sep(w))
    for row in rows:
        print(box_row(row, w))
    print(box_bot(w))


def bar(value: float, max_val: float, width: int = 30) -> str:
    if max_val <= 0:
        filled = 0
    else:
        filled = int(round((value / max_val) * width))
        filled = max(0, min(filled, width))
    empty = width - filled
    return c(BLOCK_FULL * filled, GREEN) + c(BLOCK_LIGHT * empty, DIM)


def pct_bar(pct: float, width: int = 30) -> str:
    return bar(pct, 100, width)


def grade(score: float) -> str:
    """Return a coloured letter grade for an efficiency score (0-100)."""
    if score >= 90:
        return c("A+", BOLD, GREEN)
    elif score >= 80:
        return c("A", GREEN)
    elif score >= 70:
        return c("B", GREEN)
    elif score >= 60:
        return c("C", YELLOW)
    elif score >= 40:
        return c("D", YELLOW)
    else:
        return c("F", RED)


# ---------------------------------------------------------------------------
# File scanning utilities
# ---------------------------------------------------------------------------

WORKSPACE_FILES = [
    "SKILL.md", "SOUL.md", "MEMORY.md", "AGENTS.md", "TOOLS.md",
    "CLAUDE.md", "SYSTEM.md", "PERSONA.md", "CONTEXT.md", "README.md",
    "INSTRUCTIONS.md",
]


def find_workspace_files(workspace: str) -> dict:
    """Scan workspace for known context files. Returns {name: (path, content, tokens)}."""
    results = {}
    ws = Path(workspace)

    if not ws.exists():
        return results

    # Check top-level workspace files
    for name in WORKSPACE_FILES:
        fp = ws / name
        if fp.is_file():
            content = fp.read_text(errors="replace")
            results[name] = (str(fp), content, estimate_tokens(content))

    # Check for skill directories
    skills_dir = ws / "skills"
    if skills_dir.is_dir():
        for skill_dir in sorted(skills_dir.iterdir()):
            if skill_dir.is_dir():
                skill_md = skill_dir / "SKILL.md"
                if skill_md.is_file():
                    content = skill_md.read_text(errors="replace")
                    key = f"skills/{skill_dir.name}/SKILL.md"
                    results[key] = (str(skill_md), content, estimate_tokens(content))

    # Check for .md files in common config directories
    for subdir in [".openclaw", ".claude", ".cursor"]:
        cfg_dir = ws / subdir
        if cfg_dir.is_dir():
            for md_file in sorted(cfg_dir.glob("*.md")):
                if md_file.is_file():
                    content = md_file.read_text(errors="replace")
                    key = f"{subdir}/{md_file.name}"
                    results[key] = (str(md_file), content, estimate_tokens(content))

    return results


def detect_redundancy(text: str) -> list:
    """Detect redundant patterns in text. Returns list of (issue, detail) tuples."""
    issues = []
    lines = text.split("\n")

    # Duplicate lines
    seen = {}
    for i, line in enumerate(lines):
        stripped = line.strip()
        if len(stripped) > 20:
            if stripped in seen:
                issues.append(("Duplicate line", f"Line {i + 1} duplicates line {seen[stripped] + 1}"))
            else:
                seen[stripped] = i

    # Repeated phrases (3+ word sequences appearing 3+ times)
    words = text.lower().split()
    trigrams = {}
    for i in range(len(words) - 2):
        tri = " ".join(words[i:i + 3])
        if len(tri) > 15:
            trigrams[tri] = trigrams.get(tri, 0) + 1
    for tri, count in sorted(trigrams.items(), key=lambda x: -x[1]):
        if count >= 3:
            issues.append(("Repeated phrase", f'"{tri}" appears {count} times'))
            if len(issues) >= 10:
                break

    # Excessive whitespace
    blank_count = sum(1 for line in lines if not line.strip())
    if blank_count > len(lines) * 0.3 and blank_count > 5:
        issues.append(("Excessive whitespace", f"{blank_count} blank lines ({blank_count * 100 // len(lines)}% of file)"))

    # Very long lines that could be compressed
    long_lines = sum(1 for line in lines if len(line) > 200)
    if long_lines > 3:
        issues.append(("Long lines", f"{long_lines} lines exceed 200 chars — consider splitting"))

    return issues


def compute_efficiency_score(files: dict, context_budget: int) -> float:
    """Compute an overall efficiency score (0-100) for the workspace."""
    if not files:
        return 100.0

    total_tokens = sum(tokens for _, _, tokens in files.values())
    if total_tokens == 0:
        return 100.0

    # Factor 1: Total size relative to budget (40% weight)
    budget_ratio = total_tokens / context_budget
    if budget_ratio < 0.1:
        size_score = 100
    elif budget_ratio < 0.3:
        size_score = 80
    elif budget_ratio < 0.5:
        size_score = 60
    elif budget_ratio < 0.7:
        size_score = 40
    else:
        size_score = max(0, 100 - int(budget_ratio * 100))

    # Factor 2: Redundancy across all files (30% weight)
    total_issues = 0
    for name, (path, content, tokens) in files.items():
        total_issues += len(detect_redundancy(content))
    redundancy_score = max(0, 100 - total_issues * 5)

    # Factor 3: File count overhead (30% weight)
    file_count = len(files)
    if file_count <= 5:
        count_score = 100
    elif file_count <= 10:
        count_score = 80
    elif file_count <= 20:
        count_score = 60
    else:
        count_score = max(20, 100 - file_count * 2)

    return size_score * 0.4 + redundancy_score * 0.3 + count_score * 0.3


# ---------------------------------------------------------------------------
# Tool definition parsing
# ---------------------------------------------------------------------------

def parse_tool_definitions(config_path: str) -> list:
    """Parse tool definitions from an OpenClaw config file.

    Returns list of dicts: [{name, description, tokens, params}]
    """
    tools = []
    try:
        with open(config_path, "r", errors="replace") as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError, OSError) as exc:
        print(c(f"  Warning: Could not parse {config_path}: {exc}", YELLOW))
        return tools

    # Look for tool definitions in common config shapes
    tool_defs = []
    if isinstance(data, dict):
        tool_defs = data.get("tools", data.get("functions", data.get("mcpServers", [])))
        if isinstance(tool_defs, dict):
            # mcpServers style: {name: {tools: [...]}}
            expanded = []
            for server_name, server_conf in tool_defs.items():
                if isinstance(server_conf, dict):
                    server_tools = server_conf.get("tools", [])
                    if isinstance(server_tools, list):
                        for t in server_tools:
                            if isinstance(t, dict):
                                t.setdefault("server", server_name)
                                expanded.append(t)
                    else:
                        expanded.append({"name": server_name, "raw": server_conf})
            tool_defs = expanded

    if isinstance(tool_defs, list):
        for tdef in tool_defs:
            if isinstance(tdef, dict):
                name = tdef.get("name", tdef.get("function", {}).get("name", "unknown"))
                desc = tdef.get("description", tdef.get("function", {}).get("description", ""))
                raw = json.dumps(tdef)
                tokens = estimate_tokens(raw)
                params = []
                schema = tdef.get("parameters", tdef.get("input_schema",
                         tdef.get("function", {}).get("parameters", {})))
                if isinstance(schema, dict):
                    props = schema.get("properties", {})
                    params = list(props.keys())
                tools.append({
                    "name": name,
                    "description": desc,
                    "tokens": tokens,
                    "params": params,
                    "server": tdef.get("server", ""),
                })

    return tools


def find_overlapping_tools(tools: list) -> list:
    """Identify tools with overlapping descriptions or similar names."""
    overlaps = []
    for i in range(len(tools)):
        for j in range(i + 1, len(tools)):
            a, b = tools[i], tools[j]
            # Name similarity
            name_a = a["name"].lower().replace("-", "_").replace(".", "_")
            name_b = b["name"].lower().replace("-", "_").replace(".", "_")

            # Check for shared significant words
            words_a = set(re.split(r"[_\s]+", name_a)) - {"get", "set", "list", "the", "a"}
            words_b = set(re.split(r"[_\s]+", name_b)) - {"get", "set", "list", "the", "a"}
            shared = words_a & words_b

            if len(shared) >= 1 and (len(shared) / max(len(words_a), len(words_b), 1)) > 0.5:
                overlaps.append((a["name"], b["name"], "Similar names"))
                continue

            # Description similarity (simple word overlap)
            if a["description"] and b["description"]:
                desc_words_a = set(a["description"].lower().split()) - {"the", "a", "an", "to", "of", "and", "is", "in"}
                desc_words_b = set(b["description"].lower().split()) - {"the", "a", "an", "to", "of", "and", "is", "in"}
                if desc_words_a and desc_words_b:
                    overlap_pct = len(desc_words_a & desc_words_b) / min(len(desc_words_a), len(desc_words_b))
                    if overlap_pct > 0.6:
                        overlaps.append((a["name"], b["name"], "Similar descriptions"))

    return overlaps


# ---------------------------------------------------------------------------
# Snapshot I/O (for compare command)
# ---------------------------------------------------------------------------

def save_snapshot(data: dict, path: str):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(c(f"  Snapshot saved: {path}", GREEN))


def load_snapshot(path: str) -> dict:
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError, OSError) as exc:
        print(c(f"  Error loading snapshot: {exc}", RED))
        sys.exit(1)


# ---------------------------------------------------------------------------
# Subcommand: analyze
# ---------------------------------------------------------------------------

def cmd_analyze(args: argparse.Namespace) -> None:
    """Analyze workspace context files for token usage and efficiency."""
    workspace = args.workspace
    context_budget = args.budget
    w = min(term_width(), 80)

    if not os.path.isdir(workspace):
        print(c(f"  Error: Workspace not found: {workspace}", RED))
        sys.exit(1)

    files = find_workspace_files(workspace)

    if not files:
        print(c(f"  No context files found in: {workspace}", YELLOW))
        print(c(f"  Looked for: {', '.join(WORKSPACE_FILES)}", DIM))
        return

    total_tokens = sum(tokens for _, _, tokens in files.values())
    budget_pct = (total_tokens / context_budget * 100) if context_budget > 0 else 0
    efficiency = compute_efficiency_score(files, context_budget)
    bar_w = max(w - 40, 10)

    # --- Header ---
    print()
    print(box_top(w))
    title = c(" Context Window Analysis", BOLD, CYAN)
    print(box_row(title, w))
    print(box_row(c(f" Workspace: {workspace}", DIM), w))
    print(box_sep(w))

    # --- Overview ---
    print(box_row(c(" Overview", BOLD, WHITE), w))
    print(box_row(f"  Files scanned:     {c(str(len(files)), WHITE)}", w))
    print(box_row(f"  Total tokens:      {c(format_tokens(total_tokens), BOLD, WHITE)}  (approx.)", w))
    print(box_row(f"  Context budget:    {c(format_tokens(context_budget), WHITE)}", w))
    print(box_row(f"  Budget used:       {pct_bar(budget_pct, bar_w)}  {budget_pct:.1f}%", w))
    print(box_row(f"  Efficiency score:  {grade(efficiency)}  ({efficiency:.0f}/100)", w))
    print(box_empty(w))

    # --- Per-file breakdown ---
    print(box_sep(w))
    print(box_row(c(" File Breakdown", BOLD, WHITE), w))
    print(box_row(c("  " + BOX_H * (w - 4), DIM), w))

    sorted_files = sorted(files.items(), key=lambda x: -x[1][2])
    max_file_tokens = max(tokens for _, _, tokens in files.values()) if files else 1

    for name, (path, content, tokens) in sorted_files:
        file_pct = (tokens / total_tokens * 100) if total_tokens > 0 else 0
        name_display = name[:30] if len(name) > 30 else name
        file_bar = bar(tokens, max_file_tokens, max(bar_w - 5, 5))
        line = f"  {name_display:<32s}{file_bar}  {format_tokens(tokens):>6s}  ({file_pct:.0f}%)"
        print(box_row(line, w))

    print(box_empty(w))

    # --- Context Budget Visualization ---
    print(box_sep(w))
    print(box_row(c(" Context Budget", BOLD, WHITE), w))

    static_pct = min(budget_pct, 100)
    available_pct = max(100 - static_pct, 0)

    static_blocks = int(static_pct / 100 * (w - 8))
    avail_blocks = (w - 8) - static_blocks

    budget_vis = c(BLOCK_FULL * static_blocks, YELLOW) + c(BLOCK_FULL * avail_blocks, GREEN)
    print(box_row(f"  {budget_vis}", w))
    print(box_row(f"  {c(BLOCK_FULL, YELLOW)} Static content: {static_pct:.1f}%    {c(BLOCK_FULL, GREEN)} Available: {available_pct:.1f}%", w))
    print(box_empty(w))

    # --- Redundancy check ---
    all_issues = []
    for name, (path, content, tokens) in sorted_files:
        issues = detect_redundancy(content)
        if issues:
            all_issues.append((name, issues))

    if all_issues:
        print(box_sep(w))
        print(box_row(c(" Optimization Opportunities", BOLD, WHITE), w))
        for name, issues in all_issues:
            print(box_row(f"  {c(name, CYAN)}", w))
            for issue_type, detail in issues[:5]:
                print(box_row(f"    {c('\u26a0', YELLOW)} {issue_type}: {detail}", w))
        print(box_empty(w))

    # --- Recommendations ---
    print(box_sep(w))
    print(box_row(c(" Recommendations", BOLD, WHITE), w))

    recs = _generate_recommendations(files, total_tokens, context_budget, all_issues)
    for i, (rec, savings) in enumerate(recs[:6], 1):
        savings_str = f" (~{format_tokens(savings)} tokens)" if savings > 0 else ""
        print(box_row(f"  {c(str(i) + '.', DIM)} {rec}{c(savings_str, GREEN)}", w))

    print(box_empty(w))

    # --- Footer ---
    print(box_sep(w))
    print(box_row(c("  \u2139  Token estimates are approximate (~4 chars/token)", DIM), w))
    print(box_row(c("  https://anvil-ai.io", DIM), w))
    print(box_bot(w))
    print()

    # Save snapshot for compare
    if args.snapshot:
        snapshot = {
            "workspace": workspace,
            "total_tokens": total_tokens,
            "budget": context_budget,
            "efficiency": efficiency,
            "files": {name: {"tokens": tokens, "path": path} for name, (path, _, tokens) in files.items()},
            "issues_count": sum(len(issues) for _, issues in all_issues),
        }
        save_snapshot(snapshot, args.snapshot)


def _generate_recommendations(files: dict, total_tokens: int, budget: int, issues: list) -> list:
    """Generate specific recommendations. Returns [(text, estimated_savings)]."""
    recs = []

    # Large files
    for name, (path, content, tokens) in sorted(files.items(), key=lambda x: -x[1][2]):
        if tokens > budget * 0.1:
            recs.append((f"Compress {name} — uses {tokens * 100 // budget}% of budget", tokens // 3))

    # Redundancy
    total_redundancy_issues = sum(len(iss) for _, iss in issues)
    if total_redundancy_issues > 5:
        recs.append((f"Fix {total_redundancy_issues} redundancy issues across files", total_tokens // 10))

    # Memory file
    if "MEMORY.md" in files:
        mem_tokens = files["MEMORY.md"][2]
        if mem_tokens > 2000:
            recs.append(("Prune MEMORY.md — remove stale entries", mem_tokens // 2))

    # Too many skills
    skill_files = [k for k in files if k.startswith("skills/")]
    if len(skill_files) > 5:
        skill_tokens = sum(files[k][2] for k in skill_files)
        recs.append((f"Review {len(skill_files)} installed skills — {format_tokens(skill_tokens)} total", skill_tokens // 4))

    # Budget warning
    if total_tokens > budget * 0.5:
        recs.append(("Consider splitting context across sessions", 0))

    if not recs:
        recs.append(("Context looks well-optimized!", 0))

    return recs


# ---------------------------------------------------------------------------
# Subcommand: audit-tools
# ---------------------------------------------------------------------------

def cmd_audit_tools(args: argparse.Namespace) -> None:
    """Audit tool definitions from config for overhead and overlap."""
    config_path = args.config
    w = min(term_width(), 80)
    bar_w = max(w - 45, 10)

    if not os.path.isfile(config_path):
        print(c(f"  Error: Config not found: {config_path}", RED))
        sys.exit(1)

    tools = parse_tool_definitions(config_path)

    if not tools:
        print(c(f"  No tool definitions found in: {config_path}", YELLOW))
        return

    total_tokens = sum(t["tokens"] for t in tools)
    overlaps = find_overlapping_tools(tools)
    max_tool_tokens = max(t["tokens"] for t in tools) if tools else 1

    print()
    print(box_top(w))
    print(box_row(c(" Tool Definition Audit", BOLD, CYAN), w))
    print(box_row(c(f" Config: {config_path}", DIM), w))
    print(box_sep(w))

    # Summary
    print(box_row(c(" Summary", BOLD, WHITE), w))
    print(box_row(f"  Tools defined:       {c(str(len(tools)), BOLD, WHITE)}", w))
    print(box_row(f"  Total token cost:    {c(format_tokens(total_tokens), BOLD, WHITE)}  (approx.)", w))
    print(box_row(f"  Avg per tool:        {c(format_tokens(total_tokens // len(tools)), WHITE)}", w))
    if overlaps:
        print(box_row(f"  Potential overlaps:  {c(str(len(overlaps)), YELLOW)}", w))
    print(box_empty(w))

    # Per-tool breakdown
    print(box_sep(w))
    print(box_row(c(" Per-Tool Token Cost", BOLD, WHITE), w))

    sorted_tools = sorted(tools, key=lambda t: -t["tokens"])
    for t in sorted_tools:
        name = t["name"][:25] if len(t["name"]) > 25 else t["name"]
        tool_bar = bar(t["tokens"], max_tool_tokens, bar_w)
        pct = (t["tokens"] / total_tokens * 100) if total_tokens > 0 else 0
        print(box_row(f"  {name:<27s}{tool_bar}  {format_tokens(t['tokens']):>6s}  ({pct:.0f}%)", w))

    print(box_empty(w))

    # Overlaps
    if overlaps:
        print(box_sep(w))
        print(box_row(c(" Potential Overlaps", BOLD, YELLOW), w))
        for tool_a, tool_b, reason in overlaps:
            print(box_row(f"  {c('\u26a0', YELLOW)} {tool_a}  {c('\u2194', DIM)}  {tool_b}", w))
            print(box_row(f"    {c(reason, DIM)}", w))
        print(box_empty(w))

    # Recommendations
    print(box_sep(w))
    print(box_row(c(" Recommendations", BOLD, WHITE), w))

    rec_num = 1
    if overlaps:
        print(box_row(f"  {c(str(rec_num) + '.', DIM)} Consolidate {len(overlaps)} overlapping tool pair(s)", w))
        rec_num += 1

    heavy_tools = [t for t in tools if t["tokens"] > total_tokens / len(tools) * 2]
    if heavy_tools:
        for t in heavy_tools[:3]:
            print(box_row(f"  {c(str(rec_num) + '.', DIM)} Trim {t['name']} — {format_tokens(t['tokens'])} tokens (consider shorter description)", w))
            rec_num += 1

    verbose_descs = [t for t in tools if len(t["description"]) > 300]
    if verbose_descs:
        print(box_row(f"  {c(str(rec_num) + '.', DIM)} {len(verbose_descs)} tools have descriptions > 300 chars — shorten them", w))
        rec_num += 1

    if rec_num == 1:
        print(box_row(f"  {c('1.', DIM)} Tool definitions look well-optimized!", w))

    print(box_empty(w))
    print(box_sep(w))
    print(box_row(c("  \u2139  Token estimates are approximate (~4 chars/token)", DIM), w))
    print(box_row(c("  https://anvil-ai.io", DIM), w))
    print(box_bot(w))
    print()


# ---------------------------------------------------------------------------
# Subcommand: report
# ---------------------------------------------------------------------------

def cmd_report(args: argparse.Namespace) -> None:
    """Generate a comprehensive context analysis report."""
    workspace = args.workspace
    context_budget = args.budget
    w = min(term_width(), 80)
    bar_w = max(w - 40, 10)

    if not os.path.isdir(workspace):
        print(c(f"  Error: Workspace not found: {workspace}", RED))
        sys.exit(1)

    files = find_workspace_files(workspace)
    total_tokens = sum(tokens for _, _, tokens in files.values()) if files else 0
    budget_pct = (total_tokens / context_budget * 100) if context_budget > 0 else 0
    efficiency = compute_efficiency_score(files, context_budget) if files else 100.0

    # Categorize files
    categories = {
        "System Prompts": [],
        "Memory & State": [],
        "Skill Definitions": [],
        "Configuration": [],
        "Other": [],
    }
    for name, (path, content, tokens) in files.items():
        if name in ("SOUL.md", "SYSTEM.md", "PERSONA.md", "INSTRUCTIONS.md"):
            categories["System Prompts"].append((name, tokens))
        elif name in ("MEMORY.md", "CONTEXT.md"):
            categories["Memory & State"].append((name, tokens))
        elif name.startswith("skills/"):
            categories["Skill Definitions"].append((name, tokens))
        elif name.startswith("."):
            categories["Configuration"].append((name, tokens))
        else:
            categories["Other"].append((name, tokens))

    print()
    print(box_top(w))
    header = c(" Context Engineering Report", BOLD, CYAN)
    print(box_row(header, w))
    print(box_row(c(f" Built by context engineering experts", DIM), w))
    print(box_sep(w))

    # Overall health
    print(box_row(c(" Context Health", BOLD, WHITE), w))
    print(box_empty(w))

    health_items = [
        ("Efficiency", efficiency, grade(efficiency)),
        ("Budget Usage", budget_pct, f"{budget_pct:.1f}%"),
        ("Files", float(len(files)), str(len(files))),
        ("Total Tokens", float(total_tokens), format_tokens(total_tokens)),
    ]
    for label, _, display in health_items:
        print(box_row(f"  {label:<20s}{display}", w))

    print(box_empty(w))
    print(box_row(f"  Budget  {pct_bar(budget_pct, bar_w)}  {budget_pct:.1f}%", w))
    print(box_empty(w))

    # Category breakdown
    print(box_sep(w))
    print(box_row(c(" Token Distribution by Category", BOLD, WHITE), w))
    print(box_row(c("  " + BOX_H * (w - 4), DIM), w))

    max_cat_tokens = max(
        (sum(t for _, t in items) for items in categories.values() if items),
        default=1,
    )

    for cat_name, items in categories.items():
        if not items:
            continue
        cat_tokens = sum(t for _, t in items)
        cat_pct = (cat_tokens / total_tokens * 100) if total_tokens > 0 else 0
        cat_bar = bar(cat_tokens, max_cat_tokens, bar_w)
        print(box_row(f"  {cat_name:<22s}{cat_bar}  {format_tokens(cat_tokens):>6s}  ({cat_pct:.0f}%)", w))
        for name, tokens in sorted(items, key=lambda x: -x[1]):
            print(box_row(f"    {c(name, DIM):<32s}{format_tokens(tokens):>6s}", w))

    print(box_empty(w))

    # System prompt analysis
    prompt_files = [(name, files[name]) for name in files
                    if name in ("SOUL.md", "SYSTEM.md", "PERSONA.md", "INSTRUCTIONS.md", "CLAUDE.md")]
    if prompt_files:
        print(box_sep(w))
        print(box_row(c(" System Prompt Analysis", BOLD, WHITE), w))
        for name, (path, content, tokens) in prompt_files:
            issues = detect_redundancy(content)
            lines = content.split("\n")
            compression = max(0, 100 - len(issues) * 10)
            print(box_row(f"  {c(name, CYAN)}", w))
            print(box_row(f"    Tokens: {format_tokens(tokens)}  |  Lines: {len(lines)}  |  Compression: {grade(compression)}", w))
            if issues:
                for issue_type, detail in issues[:3]:
                    print(box_row(f"    {c('\u26a0', YELLOW)} {detail}", w))
        print(box_empty(w))

    # Memory analysis
    if "MEMORY.md" in files:
        print(box_sep(w))
        print(box_row(c(" Memory File Analysis", BOLD, WHITE), w))
        _, mem_content, mem_tokens = files["MEMORY.md"]
        mem_lines = mem_content.split("\n")
        non_empty = [l for l in mem_lines if l.strip()]
        print(box_row(f"  Size:       {format_tokens(mem_tokens)} tokens ({len(mem_lines)} lines)", w))
        print(box_row(f"  Density:    {len(non_empty) * 100 // max(len(mem_lines), 1)}% non-empty lines", w))
        if mem_tokens > 2000:
            print(box_row(f"  {c('\u26a0', YELLOW)} Memory file is large — consider pruning stale entries", w))
        if mem_tokens > 5000:
            print(box_row(f"  {c('\u26a0', RED)} Memory file exceeds 5K tokens — significant context overhead", w))
        print(box_empty(w))

    # Footer
    print(box_sep(w))
    print(box_row(c("  \u2139  Token estimates are approximate (~4 chars/token)", DIM), w))
    print(box_row(c("  https://anvil-ai.io", DIM), w))
    print(box_bot(w))
    print()


# ---------------------------------------------------------------------------
# Subcommand: compare
# ---------------------------------------------------------------------------

def cmd_compare(args: argparse.Namespace) -> None:
    """Compare two snapshots to show projected token savings."""
    w = min(term_width(), 80)
    bar_w = max(w - 40, 10)

    before = load_snapshot(args.before)
    after = load_snapshot(args.after)

    before_tokens = before.get("total_tokens", 0)
    after_tokens = after.get("total_tokens", 0)
    diff = before_tokens - after_tokens
    diff_pct = (diff / before_tokens * 100) if before_tokens > 0 else 0

    before_eff = before.get("efficiency", 0)
    after_eff = after.get("efficiency", 0)
    eff_diff = after_eff - before_eff

    before_issues = before.get("issues_count", 0)
    after_issues = after.get("issues_count", 0)

    print()
    print(box_top(w))
    print(box_row(c(" Before / After Comparison", BOLD, CYAN), w))
    print(box_sep(w))

    # Summary
    print(box_row(c(" Token Savings", BOLD, WHITE), w))
    print(box_row(f"  Before:     {c(format_tokens(before_tokens), WHITE)}", w))
    print(box_row(f"  After:      {c(format_tokens(after_tokens), GREEN)}", w))

    if diff > 0:
        print(box_row(f"  Saved:      {c(format_tokens(diff), BOLD, GREEN)}  ({diff_pct:.1f}%)", w))
    elif diff < 0:
        print(box_row(f"  Added:      {c(format_tokens(abs(diff)), BOLD, RED)}  (+{abs(diff_pct):.1f}%)", w))
    else:
        print(box_row(f"  Change:     {c('None', DIM)}", w))

    print(box_empty(w))

    # Visual comparison
    print(box_row(c(" Visual", BOLD, WHITE), w))
    max_tokens = max(before_tokens, after_tokens, 1)
    before_bar = bar(before_tokens, max_tokens, bar_w)
    after_bar = bar(after_tokens, max_tokens, bar_w)
    print(box_row(f"  Before  {before_bar}  {format_tokens(before_tokens)}", w))
    print(box_row(f"  After   {after_bar}  {format_tokens(after_tokens)}", w))
    print(box_empty(w))

    # Efficiency
    print(box_row(c(" Efficiency", BOLD, WHITE), w))
    print(box_row(f"  Before:     {grade(before_eff)}  ({before_eff:.0f}/100)", w))
    print(box_row(f"  After:      {grade(after_eff)}  ({after_eff:.0f}/100)", w))
    if eff_diff > 0:
        print(box_row(f"  Improvement: {c(f'+{eff_diff:.0f} points', GREEN)}", w))
    print(box_empty(w))

    # Issues
    print(box_row(c(" Issues Resolved", BOLD, WHITE), w))
    print(box_row(f"  Before:  {before_issues} issues", w))
    print(box_row(f"  After:   {after_issues} issues", w))
    if before_issues > after_issues:
        print(box_row(f"  Fixed:   {c(str(before_issues - after_issues), GREEN)}", w))
    print(box_empty(w))

    # Per-file diff
    before_files = before.get("files", {})
    after_files = after.get("files", {})
    all_file_names = sorted(set(list(before_files.keys()) + list(after_files.keys())))

    changed = []
    for name in all_file_names:
        bt = before_files.get(name, {}).get("tokens", 0)
        at = after_files.get(name, {}).get("tokens", 0)
        if bt != at:
            changed.append((name, bt, at))

    if changed:
        print(box_sep(w))
        print(box_row(c(" File Changes", BOLD, WHITE), w))
        for name, bt, at in sorted(changed, key=lambda x: x[1] - x[2], reverse=True):
            d = bt - at
            if d > 0:
                indicator = c(f"-{format_tokens(d)}", GREEN)
            elif d < 0:
                indicator = c(f"+{format_tokens(abs(d))}", RED)
            else:
                indicator = c("=", DIM)
            name_display = name[:35] if len(name) > 35 else name
            print(box_row(f"  {name_display:<37s}{format_tokens(bt):>6s} \u2192 {format_tokens(at):>6s}  {indicator}", w))
        print(box_empty(w))

    # Footer
    print(box_sep(w))
    print(box_row(c("  \u2139  Token estimates are approximate (~4 chars/token)", DIM), w))
    print(box_row(c("  https://anvil-ai.io", DIM), w))
    print(box_bot(w))
    print()


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

DEFAULT_WORKSPACE = os.path.expanduser("~/.openclaw/workspace")
DEFAULT_CONFIG = os.path.expanduser("~/.openclaw/openclaw.json")
MODEL_CONTEXT_WINDOWS = {
    "claude-3-opus": 200_000,
    "claude-3.5-sonnet": 200_000,
    "claude-3-haiku": 200_000,
    "gpt-4-turbo": 128_000,
    "gpt-4o": 128_000,
    "gpt-4": 8_192,
    "gpt-3.5-turbo": 16_385,
}
DEFAULT_BUDGET = 200_000


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="context-engineer",
        description="Context Window Optimizer \u2014 analyze, audit, and optimize your agent\u2019s context utilization.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python3 context.py analyze --workspace ~/.openclaw/workspace\n"
            "  python3 context.py audit-tools --config ~/.openclaw/openclaw.json\n"
            "  python3 context.py report --workspace ~/.openclaw/workspace\n"
            "  python3 context.py compare --before snap1.json --after snap2.json\n"
            "\n"
            "Token estimates are approximate (~4 chars/token).\n"
            "Built by Anvil AI \u2014 https://anvil-ai.io\n"
        ),
    )

    sub = parser.add_subparsers(dest="command")

    # analyze
    p_analyze = sub.add_parser("analyze", help="Analyze workspace context files")
    p_analyze.add_argument("--workspace", default=DEFAULT_WORKSPACE,
                           help=f"Workspace directory (default: {DEFAULT_WORKSPACE})")
    p_analyze.add_argument("--budget", type=int, default=DEFAULT_BUDGET,
                           help=f"Context window token budget (default: {DEFAULT_BUDGET})")
    p_analyze.add_argument("--snapshot", metavar="FILE",
                           help="Save analysis snapshot to FILE (for later comparison)")

    # audit-tools
    p_audit = sub.add_parser("audit-tools", help="Audit tool definitions for overhead")
    p_audit.add_argument("--config", default=DEFAULT_CONFIG,
                         help=f"OpenClaw config file (default: {DEFAULT_CONFIG})")

    # report
    p_report = sub.add_parser("report", help="Generate comprehensive context report")
    p_report.add_argument("--workspace", default=DEFAULT_WORKSPACE,
                          help=f"Workspace directory (default: {DEFAULT_WORKSPACE})")
    p_report.add_argument("--budget", type=int, default=DEFAULT_BUDGET,
                          help=f"Context window token budget (default: {DEFAULT_BUDGET})")
    p_report.add_argument("--format", choices=["terminal"], default="terminal",
                          help="Output format (default: terminal)")

    # compare
    p_compare = sub.add_parser("compare", help="Compare before/after snapshots")
    p_compare.add_argument("--before", required=True, help="Path to before snapshot JSON")
    p_compare.add_argument("--after", required=True, help="Path to after snapshot JSON")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    dispatch = {
        "analyze": cmd_analyze,
        "audit-tools": cmd_audit_tools,
        "report": cmd_report,
        "compare": cmd_compare,
    }

    handler = dispatch.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
