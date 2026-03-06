#!/usr/bin/env python3
"""
Librarian Skill - Python Wrapper
Enforces ZERO TOLERANCE protocol for book research.

Usage:
    python3 librarian.py "query" --topics topic1,topic2 [--book BookName] [--top-k N]
"""

import sys
import json
import subprocess
from pathlib import Path

LIBRARIAN_PATH = Path.home() / "Documents" / "librarian"
RESEARCH_SCRIPT = LIBRARIAN_PATH / "engine" / "scripts" / "research.py"


def main():
    if len(sys.argv) < 2:
        print("❌ ERROR: Query required")
        print("Usage: librarian.py \"query\" --topics topic1,topic2 [--book BookName]")
        sys.exit(1)

    # Build command (pass all args to research.py)
    cmd = ["python3", str(RESEARCH_SCRIPT)] + sys.argv[1:]

    # Run research.py
    try:
        result = subprocess.run(
            cmd,
            cwd=str(LIBRARIAN_PATH),
            capture_output=True,
            text=True,
            timeout=60
        )
    except subprocess.TimeoutExpired:
        print("❌ ERROR: Research timed out (>60s)")
        sys.exit(1)
    except Exception as e:
        print(f"❌ ERROR: Failed to run research.py: {e}")
        sys.exit(1)

    # Check for errors
    if result.returncode != 0:
        print(f"❌ ERROR: research.py failed (exit {result.returncode})")
        if result.stderr:
            print(result.stderr)
        sys.exit(1)

    # Parse JSON output
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print("❌ ERROR: Invalid JSON output from research.py")
        print(f"Raw output: {result.stdout[:500]}")
        sys.exit(1)

    # Check if empty results
    results = data.get("results", [])
    if not results:
        query = sys.argv[1]
        topics = "unknown"
        book = None
        
        # Parse topics/book from args
        for i, arg in enumerate(sys.argv):
            if arg == "--topics" and i + 1 < len(sys.argv):
                topics = sys.argv[i + 1]
            elif arg == "--book" and i + 1 < len(sys.argv):
                book = sys.argv[i + 1]
        
        scope = f"topics: {topics}" + (f", book: {book}" if book else "")
        print(f"❌ Não achei resultados sobre \"{query}\" ({scope})")
        print("\n💡 Sugestões:")
        print("- Verifique se o topic está indexado (run index_library.py)")
        print("- Tente outros topics ou query mais ampla")
        if book:
            print(f"- Confirme se livro '{book}' existe no topic")
        sys.exit(1)

    # Format results as citations
    query = sys.argv[1]
    topics = "unknown"
    book = None
    
    for i, arg in enumerate(sys.argv):
        if arg == "--topics" and i + 1 < len(sys.argv):
            topics = sys.argv[i + 1]
        elif arg == "--book" and i + 1 < len(sys.argv):
            book = sys.argv[i + 1]
    
    scope = f"topics: {topics}" + (f", book: {book}" if book else "")
    
    print(f"📚 **RESEARCH:** {query}")
    print(f"\nAchei **{len(results)} resultado(s)** ({scope})\n")
    print("---\n")

    for idx, result in enumerate(results, 1):
        title = result.get("title", "Untitled")
        source = result.get("source_file", "Unknown source")
        text = result.get("text", "")
        score = result.get("score", 0.0)

        # Extract book name from path
        book_name = Path(source).stem.replace("-", " ").title()

        print(f"{idx}️⃣ **{title}**")
        print(f"**Fonte:** *{book_name}* (score: {score:.2f})")
        print(f"\n> {text}\n")
        print("---\n")

    # List unique sources
    sources = list(set(Path(r.get("source_file", "")).stem for r in results))
    if sources:
        print("**Fontes citadas:**")
        for source in sources:
            book_name = source.replace("-", " ").title()
            print(f"- *{book_name}*")


if __name__ == "__main__":
    main()
