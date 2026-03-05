#!/usr/bin/env python3
"""
Manage reading state for a sequential_read session.

Handles the structured reading state (short-term + long-term memory),
reflection saving, annotation saving, and mechanical consolidation.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


def get_workspace():
    ws = os.environ.get("OPENCLAW_WORKSPACE")
    if ws:
        return Path(ws)
    return Path.home() / ".openclaw" / "workspace"


def get_session_dir(session_id):
    return get_workspace() / "memory" / "sequential_read" / session_id


def require_session(session_id):
    sd = get_session_dir(session_id)
    if not sd.exists():
        print(f"Error: session not found: {session_id}", file=sys.stderr)
        sys.exit(1)
    return sd


def read_state(session_dir):
    sp = session_dir / "reading_state.json"
    if not sp.exists():
        print("Error: reading state not initialised. Run 'init' first.", file=sys.stderr)
        sys.exit(1)
    return json.loads(sp.read_text(encoding="utf-8"))


def write_state(session_dir, state):
    sp = session_dir / "reading_state.json"
    sp.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def read_session_meta(session_dir):
    sp = session_dir / "session.json"
    return json.loads(sp.read_text(encoding="utf-8"))


def write_session_meta(session_dir, meta):
    sp = session_dir / "session.json"
    sp.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")


SHORT_TERM_LIMIT = 2


# ── Consolidation logic ─────────────────────────────────────────────

def extract_section(text, header):
    """Extract content under a markdown ### header from a reflection."""
    pattern = rf"###\s*{re.escape(header)}\s*\n(.*?)(?=\n###\s|\Z)"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return ""


def extract_items(text):
    """Pull bullet-point items from a block of text."""
    items = []
    for line in text.split("\n"):
        line = line.strip()
        if line.startswith(("- ", "* ", "• ")):
            items.append(line[2:].strip())
        elif line and not line.startswith("#"):
            items.append(line)
    return items


def deduplicate_list(existing, new_items):
    """Add new items that aren't already in the list (case-insensitive)."""
    lower_existing = {x.lower() for x in existing}
    for item in new_items:
        if item.lower() not in lower_existing:
            existing.append(item)
            lower_existing.add(item.lower())
    return existing


def consolidate_reflection(state, reflection_text, chunk_number):
    """
    Fold a reflection's key info into long-term memory.

    This is mechanical — no LLM calls. It:
    1. Appends a one-line summary to long_term.summary
    2. Merges characters, themes, questions (deduplicating)
    3. Moves predictions from the reflection into running_predictions
    4. Prunes resolved questions and confirmed/denied predictions
    """
    lt = state["long_term"]

    # 1. Build summary line from Comprehension section
    comprehension = extract_section(reflection_text, "Comprehension")
    if comprehension:
        # Take first sentence or first 150 chars as the one-liner
        first_sentence = comprehension.split(".")[0].strip()
        if len(first_sentence) > 150:
            first_sentence = first_sentence[:147] + "..."
        summary_line = f"[Chunk {chunk_number}] {first_sentence}."
        if lt["summary"]:
            lt["summary"] += " " + summary_line
        else:
            lt["summary"] = summary_line

    # 2. Extract characters mentioned (look for capitalised names in comprehension)
    # Simple heuristic: capitalised words that appear multiple times or after character-related words
    comp_text = comprehension or ""
    # Also check for explicit character mentions in the reflection
    for name in re.findall(r"\b([A-Z][a-z]{3,}(?:\s+[A-Z][a-z]+)?)\b", comp_text):
        # Filter out common sentence starters, section names, and non-name words
        if name.lower() not in (
            "the", "this", "that", "these", "those", "what", "when",
            "where", "which", "while", "after", "before", "during",
            "chunk", "chapter", "section", "part", "here", "there",
            "overall", "however", "although", "perhaps", "finally",
            "meanwhile", "furthermore", "additionally", "interestingly",
            "also", "then", "they", "their", "with", "from", "into",
            "about", "just", "been", "have", "will", "would", "could",
            "should", "some", "more", "most", "very", "each", "every",
            "still", "both", "between", "through", "being", "other",
            "another", "such", "much", "many", "only", "over", "under",
            "again", "once", "upon", "like", "well", "back", "even",
            "first", "last", "next", "long", "good", "great", "little",
            "said", "says", "told", "asked", "went", "came", "made",
            "left", "took", "gave", "found", "knew", "thought", "felt",
            "seemed", "began", "started", "continued", "turned", "looked",
            "none", "nothing", "something", "everything", "anything",
        ):
            deduplicate_list(lt["key_characters"], [name])

    # 3. Extract themes
    themes_text = extract_section(reflection_text, "Craft")
    reactions_text = extract_section(reflection_text, "Reactions")
    for text_block in (themes_text, reactions_text, comp_text):
        # Look for thematic keywords after "theme" mentions or in bold
        for match in re.findall(r"\*\*([^*]+)\*\*", text_block):
            if len(match.split()) <= 4:  # Short bold phrases are likely thematic
                deduplicate_list(lt["key_themes"], [match])

    # 4. Questions → merge new, prune resolved
    questions_text = extract_section(reflection_text, "Questions")
    new_questions = extract_items(questions_text)
    
    revisions_text = extract_section(reflection_text, "Revisions")
    revisions_lower = revisions_text.lower() if revisions_text else ""

    # Prune questions that seem answered (mentioned in revisions as resolved)
    pruned_questions = []
    for q in lt["unresolved_questions"]:
        # If the question's key words appear in revisions, it may be resolved
        q_words = set(re.findall(r"\w{4,}", q.lower()))
        overlap = sum(1 for w in q_words if w in revisions_lower)
        if overlap < len(q_words) * 0.4:  # Less than 40% overlap → still unresolved
            pruned_questions.append(q)
    lt["unresolved_questions"] = pruned_questions

    deduplicate_list(lt["unresolved_questions"], new_questions)

    # 5. Predictions
    # Extract predictions from Questions section (lines about expectations)
    prediction_keywords = ("predict", "expect", "think will", "suspect", "bet", "guess", "wonder if")
    for q in new_questions:
        if any(kw in q.lower() for kw in prediction_keywords):
            deduplicate_list(lt["running_predictions"], [f"[Chunk {chunk_number}] {q}"])

    # Prune predictions confirmed/denied in revisions
    if revisions_text:
        pruned_predictions = []
        for p in lt["running_predictions"]:
            p_words = set(re.findall(r"\w{4,}", p.lower()))
            overlap = sum(1 for w in p_words if w in revisions_lower)
            if overlap < len(p_words) * 0.3:
                pruned_predictions.append(p)
            # else: prediction was likely addressed, drop it
        lt["running_predictions"] = pruned_predictions

    state["long_term"] = lt
    return state


# ── Subcommands ──────────────────────────────────────────────────────

def cmd_init(args):
    sd = require_session(args.session_id)
    state = {
        "current_chunk": 0,
        "short_term": [],
        "long_term": {
            "summary": "",
            "key_characters": [],
            "key_themes": [],
            "unresolved_questions": [],
            "running_predictions": [],
        },
    }
    write_state(sd, state)
    print(f"Initialised reading state for {args.session_id}")


def cmd_get(args):
    sd = require_session(args.session_id)
    state = read_state(sd)
    print(json.dumps(state, indent=2))


def cmd_get_context(args):
    """Build the context window for the next reflection."""
    sd = require_session(args.session_id)
    state = read_state(sd)
    meta = read_session_meta(sd)

    next_chunk = state["current_chunk"] + 1
    total = meta.get("total_chunks", 0)

    parts = []

    # Long-term memory
    lt = state["long_term"]
    parts.append("## Long-Term Reading Memory\n")
    if lt["summary"]:
        parts.append(f"**Summary so far:** {lt['summary']}\n")
    if lt["key_characters"]:
        parts.append(f"**Key characters:** {', '.join(lt['key_characters'])}\n")
    if lt["key_themes"]:
        parts.append(f"**Key themes:** {', '.join(lt['key_themes'])}\n")
    if lt["unresolved_questions"]:
        parts.append("**Unresolved questions:**")
        for q in lt["unresolved_questions"]:
            parts.append(f"- {q}")
        parts.append("")
    if lt["running_predictions"]:
        parts.append("**Running predictions:**")
        for p in lt["running_predictions"]:
            parts.append(f"- {p}")
        parts.append("")

    # Short-term: recent full reflections
    if state["short_term"]:
        parts.append("\n## Recent Reflections\n")
        for entry in state["short_term"]:
            cn = entry["chunk_number"]
            parts.append(f"### Reflection on Chunk {cn}\n")
            ref_path = sd / "reflections" / f"{cn:03d}.md"
            if ref_path.exists():
                parts.append(ref_path.read_text(encoding="utf-8").strip())
            else:
                parts.append("*(reflection file missing)*")
            # Check for annotations
            ann_path = sd / "annotations" / f"{cn:03d}.md"
            if ann_path.exists():
                parts.append(f"\n**Annotations added later:**\n{ann_path.read_text(encoding='utf-8').strip()}")
            parts.append("")

    # Current chunk metadata
    chunk_meta_path = sd / "chunks" / f"{next_chunk:03d}.meta.json"
    if chunk_meta_path.exists():
        cm = json.loads(chunk_meta_path.read_text(encoding="utf-8"))
        parts.append(f"\n## Chunk {next_chunk} of {total} — Metadata\n")
        parts.append(f"**Tone:** {cm.get('tone', '—')}")
        parts.append(f"**Intensity:** {cm.get('intensity', '—')}")
        if cm.get("themes"):
            parts.append(f"**Themes:** {', '.join(cm['themes'])}")
        if cm.get("adjacent_relationship"):
            parts.append(f"**Context:** {cm['adjacent_relationship']}")
        parts.append("")

    print("\n".join(parts))


def cmd_save_reflection(args):
    sd = require_session(args.session_id)
    n = int(args.chunk_number)

    ref_file = Path(args.file)
    if not ref_file.exists():
        print(f"Error: reflection file not found: {ref_file}", file=sys.stderr)
        sys.exit(1)

    text = ref_file.read_text(encoding="utf-8")

    # Save reflection file
    dest = sd / "reflections" / f"{n:03d}.md"
    dest.write_text(text, encoding="utf-8")

    # Update state
    state = read_state(sd)

    # Add to short-term
    state["short_term"].append({"chunk_number": n, "saved_at": "now"})

    # Evict oldest if over limit — consolidate first
    evicted_text = None
    if len(state["short_term"]) > SHORT_TERM_LIMIT:
        evicted = state["short_term"].pop(0)
        evicted_cn = evicted["chunk_number"]
        evicted_path = sd / "reflections" / f"{evicted_cn:03d}.md"
        if evicted_path.exists():
            evicted_text = (evicted_cn, evicted_path.read_text(encoding="utf-8"))

    # Update current chunk
    state["current_chunk"] = n

    # Consolidate evicted reflection
    if evicted_text:
        state = consolidate_reflection(state, evicted_text[1], evicted_text[0])

    write_state(sd, state)

    # Also update session.json
    meta = read_session_meta(sd)
    meta["current_chunk"] = n
    write_session_meta(sd, meta)

    print(f"Saved reflection for chunk {n:03d}")


def cmd_save_annotation(args):
    sd = require_session(args.session_id)
    n = int(args.chunk_number)

    ann_file = Path(args.file)
    if not ann_file.exists():
        print(f"Error: annotation file not found: {ann_file}", file=sys.stderr)
        sys.exit(1)

    text = ann_file.read_text(encoding="utf-8")
    dest = sd / "annotations" / f"{n:03d}.md"

    # Append if exists
    if dest.exists():
        existing = dest.read_text(encoding="utf-8")
        text = existing.rstrip() + "\n\n---\n\n" + text
    dest.write_text(text, encoding="utf-8")
    print(f"Saved annotation for chunk {n:03d}")


def cmd_consolidate(args):
    """
    Run consolidation on the current state. This is normally done automatically
    during save-reflection when a reflection is evicted, but can be triggered
    manually to reconsolidate from all reflections not in short-term.
    """
    sd = require_session(args.session_id)
    state = read_state(sd)

    # Find all reflection files
    ref_dir = sd / "reflections"
    all_refs = sorted(ref_dir.glob("*.md"))

    short_term_chunks = {e["chunk_number"] for e in state["short_term"]}

    consolidated_count = 0
    for ref_path in all_refs:
        cn = int(ref_path.stem)
        if cn not in short_term_chunks:
            text = ref_path.read_text(encoding="utf-8")
            # Check if already consolidated (summary already mentions this chunk)
            if f"[Chunk {cn}]" not in state["long_term"]["summary"]:
                state = consolidate_reflection(state, text, cn)
                consolidated_count += 1

    write_state(sd, state)
    print(f"Consolidated {consolidated_count} reflections into long-term memory")


def cmd_get_all_reflections(args):
    """Print all reflections in order with inline annotations."""
    sd = require_session(args.session_id)
    ref_dir = sd / "reflections"
    ann_dir = sd / "annotations"

    refs = sorted(ref_dir.glob("*.md"))
    if not refs:
        print("No reflections recorded yet.")
        return

    for ref_path in refs:
        cn = int(ref_path.stem)
        print(f"\n{'='*60}")
        print(f"## Reflection — Chunk {cn}")
        print(f"{'='*60}\n")
        print(ref_path.read_text(encoding="utf-8").strip())

        ann_path = ann_dir / f"{cn:03d}.md"
        if ann_path.exists():
            print(f"\n> **Annotations (added after later reading):**")
            for line in ann_path.read_text(encoding="utf-8").strip().split("\n"):
                print(f"> {line}")
        print()


# ── CLI ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Manage reading state for a sequential_read session")
    sub = parser.add_subparsers(dest="command")

    p_init = sub.add_parser("init", help="Initialise reading state for a session")
    p_init.add_argument("session_id")

    p_get = sub.add_parser("get", help="Print current reading state as JSON")
    p_get.add_argument("session_id")

    p_ctx = sub.add_parser("get-context", help="Build context window for next reflection")
    p_ctx.add_argument("session_id")

    p_sr = sub.add_parser("save-reflection", help="Save a reflection and update state")
    p_sr.add_argument("session_id")
    p_sr.add_argument("chunk_number", type=int)
    p_sr.add_argument("--file", required=True, help="Path to the reflection markdown file")

    p_sa = sub.add_parser("save-annotation", help="Save/append an annotation to a chunk")
    p_sa.add_argument("session_id")
    p_sa.add_argument("chunk_number", type=int)
    p_sa.add_argument("--file", required=True, help="Path to the annotation file")

    p_con = sub.add_parser("consolidate", help="Reconsolidate all non-short-term reflections")
    p_con.add_argument("session_id")

    p_all = sub.add_parser("get-all-reflections", help="Print all reflections with annotations")
    p_all.add_argument("session_id")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    {
        "init": cmd_init,
        "get": cmd_get,
        "get-context": cmd_get_context,
        "save-reflection": cmd_save_reflection,
        "save-annotation": cmd_save_annotation,
        "consolidate": cmd_consolidate,
        "get-all-reflections": cmd_get_all_reflections,
    }[args.command](args)


if __name__ == "__main__":
    main()
