#!/usr/bin/env python3
"""
bo-faq-bot: Build and query a FAQ knowledge base from markdown files.
Uses TF-IDF-like fuzzy matching for question search. No external dependencies.
"""

import argparse
import json
import math
import os
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(os.environ.get("FAQ_BOT_DIR", Path.home() / ".faq-bot"))
KB_FILE = DATA_DIR / "knowledge-base.json"

# ─── Storage ─────────────────────────────────────────────────

def ensure_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def load_kb() -> dict:
    if KB_FILE.exists():
        return json.loads(KB_FILE.read_text())
    return {"entries": [], "next_id": 1, "created": None}

def save_kb(kb: dict):
    ensure_dir()
    KB_FILE.write_text(json.dumps(kb, indent=2, ensure_ascii=False))

# ─── Text Processing ────────────────────────────────────────

STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "can", "shall", "to", "of", "in", "for",
    "on", "with", "at", "by", "from", "as", "into", "through", "during",
    "before", "after", "above", "below", "between", "out", "off", "over",
    "under", "again", "further", "then", "once", "here", "there", "when",
    "where", "why", "how", "all", "both", "each", "few", "more", "most",
    "other", "some", "such", "no", "nor", "not", "only", "own", "same",
    "so", "than", "too", "very", "just", "because", "but", "and", "or",
    "if", "while", "about", "up", "it", "its", "i", "me", "my", "we",
    "our", "you", "your", "he", "she", "they", "them", "what", "which",
    "who", "whom", "this", "that", "these", "those", "am",
}


def tokenize(text: str) -> list[str]:
    """Tokenize and normalize text."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    tokens = text.split()
    return [t for t in tokens if t not in STOP_WORDS and len(t) > 1]


def compute_tfidf(query_tokens: list[str], doc_tokens: list[str], all_docs_tokens: list[list[str]]) -> float:
    """Compute TF-IDF similarity score between query and document."""
    if not query_tokens or not doc_tokens:
        return 0.0

    n_docs = len(all_docs_tokens)
    score = 0.0

    doc_counter = Counter(doc_tokens)
    doc_len = len(doc_tokens)

    for token in set(query_tokens):
        # Term frequency in document
        tf = doc_counter.get(token, 0) / max(doc_len, 1)

        # Inverse document frequency
        doc_freq = sum(1 for d in all_docs_tokens if token in d)
        idf = math.log((n_docs + 1) / (doc_freq + 1)) + 1

        score += tf * idf

    # Normalize by query length
    return score / max(len(set(query_tokens)), 1)


def fuzzy_match(a: str, b: str) -> float:
    """Simple character-level similarity (Jaccard on bigrams)."""
    if not a or not b:
        return 0.0
    a, b = a.lower(), b.lower()
    a_bigrams = {a[i:i+2] for i in range(len(a)-1)}
    b_bigrams = {b[i:i+2] for i in range(len(b)-1)}
    if not a_bigrams or not b_bigrams:
        return 0.0
    return len(a_bigrams & b_bigrams) / len(a_bigrams | b_bigrams)


# ─── Commands ────────────────────────────────────────────────

def cmd_init():
    """Initialize a new knowledge base."""
    if KB_FILE.exists():
        print(f"Knowledge base already exists at {KB_FILE}")
        return
    kb = {
        "entries": [],
        "next_id": 1,
        "created": datetime.now(timezone.utc).isoformat(),
    }
    save_kb(kb)
    print(f"Created new knowledge base at {KB_FILE}")


def cmd_add(question: str, answer: str, tags: str = None):
    """Add a single FAQ entry."""
    kb = load_kb()
    entry = {
        "id": kb["next_id"],
        "question": question.strip(),
        "answer": answer.strip(),
        "tags": [t.strip() for t in tags.split(",")] if tags else [],
        "added": datetime.now(timezone.utc).isoformat(),
    }
    kb["entries"].append(entry)
    kb["next_id"] += 1
    save_kb(kb)
    print(f"Added FAQ #{entry['id']}: {question[:60]}...")


def cmd_import(filepath: str):
    """Import FAQs from a markdown file. H2 = question, body = answer."""
    path = Path(filepath)
    if not path.exists():
        print(f"File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    content = path.read_text(encoding="utf-8")
    kb = load_kb()
    count = 0

    # Split by H2 headings
    sections = re.split(r"^## ", content, flags=re.MULTILINE)

    for section in sections[1:]:  # Skip content before first H2
        lines = section.strip().split("\n", 1)
        question = lines[0].strip()
        answer = lines[1].strip() if len(lines) > 1 else ""

        if not question:
            continue

        entry = {
            "id": kb["next_id"],
            "question": question,
            "answer": answer,
            "tags": [],
            "added": datetime.now(timezone.utc).isoformat(),
        }
        kb["entries"].append(entry)
        kb["next_id"] += 1
        count += 1

    save_kb(kb)
    print(f"Imported {count} FAQ entries from {filepath}")


def cmd_search(query: str, top: int = 3, threshold: float = 0.3):
    """Search for the best matching FAQ answer."""
    kb = load_kb()
    if not kb["entries"]:
        print("Knowledge base is empty. Add some FAQs first.", file=sys.stderr)
        sys.exit(1)

    query_tokens = tokenize(query)
    all_docs_tokens = [tokenize(e["question"] + " " + e["answer"]) for e in kb["entries"]]

    results = []
    for i, entry in enumerate(kb["entries"]):
        doc_tokens = all_docs_tokens[i]

        # Combine TF-IDF score with fuzzy matching on question
        tfidf_score = compute_tfidf(query_tokens, doc_tokens, all_docs_tokens)
        fuzzy_score = fuzzy_match(query, entry["question"])

        # Weighted combination: TF-IDF is primary, fuzzy is secondary
        combined = (tfidf_score * 0.7) + (fuzzy_score * 0.3)

        if combined >= threshold:
            results.append({
                "id": entry["id"],
                "question": entry["question"],
                "answer": entry["answer"],
                "score": round(combined, 4),
                "tags": entry["tags"],
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    results = results[:top]

    if not results:
        print(json.dumps({"matches": [], "query": query, "message": "No matching FAQs found."}, indent=2))
    else:
        print(json.dumps({"matches": results, "query": query, "top_answer": results[0]["answer"]}, indent=2, ensure_ascii=False))


def cmd_list(tag: str = None):
    """List all FAQ entries."""
    kb = load_kb()
    entries = kb["entries"]

    if tag:
        entries = [e for e in entries if tag in e.get("tags", [])]

    if not entries:
        print("No FAQ entries found.")
        return

    for entry in entries:
        tags_str = f" [{', '.join(entry['tags'])}]" if entry.get("tags") else ""
        print(f"#{entry['id']}{tags_str}: {entry['question']}")
        # Show first line of answer
        first_line = entry["answer"].split("\n")[0][:80]
        print(f"  → {first_line}")
        print()


def cmd_remove(entry_id: int):
    """Remove a FAQ entry by ID."""
    kb = load_kb()
    original_len = len(kb["entries"])
    kb["entries"] = [e for e in kb["entries"] if e["id"] != entry_id]

    if len(kb["entries"]) == original_len:
        print(f"Entry #{entry_id} not found.", file=sys.stderr)
        sys.exit(1)

    save_kb(kb)
    print(f"Removed FAQ #{entry_id}")


def cmd_export(fmt: str = "md", output: str = None):
    """Export knowledge base."""
    kb = load_kb()

    if fmt == "json":
        text = json.dumps(kb["entries"], indent=2, ensure_ascii=False)
    else:
        lines = []
        for entry in kb["entries"]:
            lines.append(f"## {entry['question']}")
            lines.append(entry["answer"])
            lines.append("")
        text = "\n".join(lines)

    if output:
        Path(output).write_text(text, encoding="utf-8")
        print(f"Exported {len(kb['entries'])} entries to {output}", file=sys.stderr)
    else:
        print(text)


def cmd_stats():
    """Show knowledge base statistics."""
    kb = load_kb()
    entries = kb["entries"]

    all_tags = {}
    total_answer_len = 0
    for e in entries:
        total_answer_len += len(e["answer"])
        for tag in e.get("tags", []):
            all_tags[tag] = all_tags.get(tag, 0) + 1

    stats = {
        "total_entries": len(entries),
        "avg_answer_length": round(total_answer_len / max(len(entries), 1)),
        "tags": all_tags,
        "storage_path": str(KB_FILE),
        "created": kb.get("created"),
    }
    print(json.dumps(stats, indent=2, ensure_ascii=False))


# ─── CLI ─────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Business Operations FAQ Bot — Knowledge base from markdown files.")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="Create a new knowledge base")

    p_add = sub.add_parser("add", help="Add a FAQ entry")
    p_add.add_argument("-q", "--question", required=True)
    p_add.add_argument("-a", "--answer", required=True)
    p_add.add_argument("-t", "--tags", help="Comma-separated tags")

    p_imp = sub.add_parser("import", help="Import from markdown")
    p_imp.add_argument("file", help="Markdown file path")

    p_search = sub.add_parser("search", help="Search FAQs")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--top", type=int, default=3)
    p_search.add_argument("--threshold", type=float, default=0.3)

    p_list = sub.add_parser("list", help="List all entries")
    p_list.add_argument("--tag", help="Filter by tag")

    p_rm = sub.add_parser("remove", help="Remove entry by ID")
    p_rm.add_argument("id", type=int)

    p_exp = sub.add_parser("export", help="Export knowledge base")
    p_exp.add_argument("--format", default="md", choices=["md", "json"])
    p_exp.add_argument("-o", "--output", help="Output file")

    sub.add_parser("stats", help="Show statistics")

    args = parser.parse_args()

    if args.command == "init":
        cmd_init()
    elif args.command == "add":
        cmd_add(args.question, args.answer, args.tags)
    elif args.command == "import":
        cmd_import(args.file)
    elif args.command == "search":
        cmd_search(args.query, args.top, args.threshold)
    elif args.command == "list":
        cmd_list(args.tag)
    elif args.command == "remove":
        cmd_remove(args.id)
    elif args.command == "export":
        cmd_export(args.format, args.output)
    elif args.command == "stats":
        cmd_stats()


if __name__ == "__main__":
    main()