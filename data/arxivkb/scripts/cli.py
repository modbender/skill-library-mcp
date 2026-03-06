#!/usr/bin/env python3
"""
cli.py — ArXivKB command-line interface.

Usage:
    akb topics browse [filter]
    akb topics list
    akb topics add cs.AI cs.CV cs.LG
    akb topics delete cs.AI
    akb ingest [--days 7] [--dry-run]
    akb paper <arxiv_id>
    akb stats
    akb expire [--days 30]
"""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DEFAULT_DATA_DIR = os.path.expanduser("~/Downloads/ArXivKB")


def _data_dir(args) -> str:
    if hasattr(args, "data_dir") and args.data_dir:
        return os.path.expanduser(args.data_dir)
    return os.environ.get("ARXIVKB_DATA_DIR", DEFAULT_DATA_DIR)


def _db_path(args) -> str:
    d = _data_dir(args)
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "arxivkb.db")


def _pdf_dir(args) -> str:
    d = os.path.join(_data_dir(args), "pdfs")
    os.makedirs(d, exist_ok=True)
    return d


# ---------------------------------------------------------------------------
# topics
# ---------------------------------------------------------------------------

from arxiv_taxonomy import ALL_CATEGORIES, CATEGORY_GROUP


def is_valid_category(code: str) -> bool:
    return code in ALL_CATEGORIES


def search_categories(query: str) -> list[tuple[str, str, str]]:
    query = query.lower()
    matches = []
    for code, desc in ALL_CATEGORIES.items():
        if query in code.lower() or query in desc.lower():
            matches.append((code, desc, CATEGORY_GROUP.get(code, "")))
    return sorted(matches)


def cmd_topics(args):
    db_path = _db_path(args)

    from db import init_db, get_categories, add_categories, remove_categories, seed_taxonomy
    init_db(db_path)
    seed_taxonomy(db_path)

    categories = get_categories(db_path, enabled_only=True)

    if args.topics_cmd == "add":
        to_add = [c.strip() for c in args.categories]
        valid, invalid = [], []
        for cat in to_add:
            if not is_valid_category(cat):
                invalid.append(cat)
            else:
                valid.append(cat)
        descs = {cat: ALL_CATEGORIES.get(cat, "") for cat in valid}
        added, existed = add_categories(valid, descs, db_path) if valid else ([], [])
        for c in added:
            print(f"  ✅ Enabled: {c} ({ALL_CATEGORIES.get(c, '')})")
        for c in existed:
            print(f"  ℹ️  Already enabled: {c}")
        for c in invalid:
            print(f"  ❌ Invalid category: {c}")
            matches = search_categories(c)
            if matches:
                print(f"     Did you mean: {', '.join(m[0] for m in matches[:5])}")

    elif args.topics_cmd == "list":
        if not categories:
            print("  No categories enabled.")
            print("  Browse:  akb topics browse")
            print("  Add:     akb topics add cs.AI cs.CV cs.LG")
        else:
            print(f"  {len(categories)} category(ies) enabled:\n")
            for cat in categories:
                desc = cat["description"] or ALL_CATEGORIES.get(cat["code"], "")
                group = cat["group_name"] or CATEGORY_GROUP.get(cat["code"], "")
                print(f"    {cat['code']:<22} {desc}  [{group}]")

    elif args.topics_cmd == "delete":
        to_del = [c.strip() for c in args.categories]
        removed, not_found = remove_categories(to_del, db_path)
        for c in removed:
            print(f"  ✅ Disabled: {c}")
        for c in not_found:
            print(f"  ❌ Not enabled: {c}")

    elif args.topics_cmd == "browse":
        query = (args.filter or "").strip().lower()
        all_cats = get_categories(db_path, enabled_only=False)
        enabled_set = set(c["code"] for c in all_cats if c["enabled"])

        if query:
            matches = [c for c in all_cats if query in c["code"].lower() or query in c["description"].lower() or query in c["group_name"].lower()]
            if not matches:
                print(f"  No categories match '{query}'")
                return
            print(f"  Categories matching '{query}':\n")
            cur_group = ""
            for c in matches:
                if c["group_name"] != cur_group:
                    print(f"\n  {c['group_name']}")
                    cur_group = c["group_name"]
                marker = " ✅" if c["code"] in enabled_set else ""
                print(f"    {c['code']:<22} {c['description']}{marker}")
        else:
            cur_group = ""
            for c in all_cats:
                if c["group_name"] != cur_group:
                    print(f"\n  {c['group_name']}")
                    cur_group = c["group_name"]
                marker = " ✅" if c["code"] in enabled_set else ""
                print(f"    {c['code']:<22} {c['description']}{marker}")

        n = len(enabled_set)
        print(f"\n  {n} enabled / {len(all_cats)} total")
        print("  Enable:  akb categories add <code>")
        print("  Disable: akb categories delete <code>")


# ---------------------------------------------------------------------------
# ingest
# ---------------------------------------------------------------------------

def cmd_ingest(args):
    db_path = _db_path(args)
    pdf_dir = _pdf_dir(args)
    data_dir = _data_dir(args)

    from db import (init_db, insert_paper, update_paper_status, insert_chunk,
                    update_chunk_faiss_id, get_categories, get_chunks_for_paper,
                    get_unembedded_chunks, pdf_path_for)
    from arxiv_crawler import crawl_topics
    from pdf_processor import process_pdf
    from embed import embed_texts, DIM
    from faiss_index import FaissIndex

    init_db(db_path)

    categories = get_categories(db_path)
    if not categories:
        print("❌ No categories enabled. Run: akb topics add cs.AI cs.CV")
        sys.exit(1)
    category_codes = [c["code"] for c in categories]

    days_back = args.days if args.days is not None else 7
    max_results = 50

    print(f"🔍 Crawling {len(category_codes)} category(ies) for papers from the last {days_back} day(s)...")
    if args.dry_run:
        print("  [dry-run]")

    papers = crawl_topics(
        topics=category_codes,
        pdf_dir=pdf_dir,
        max_results=max_results,
        days_back=days_back,
        download_pdfs=not args.dry_run and not args.no_pdf,
        dry_run=args.dry_run,
    )

    if not papers:
        print("  No new papers found.")
    elif args.dry_run:
        print(f"\n[dry-run] Would ingest {len(papers)} papers")
        return
    else:
        ingested = 0
        for p in papers:
            arxiv_id = p["arxiv_id"]
            paper_id = insert_paper(
                db_path=db_path, arxiv_id=arxiv_id, title=p["title"],
                abstract=p.get("abstract"), categories=p.get("categories"),
                published=p.get("published"),
            )

            # Skip if already chunked
            if get_chunks_for_paper(db_path, paper_id):
                continue

            # Process PDF into chunks
            pdf = pdf_path_for(arxiv_id, data_dir)
            chunks_data = []
            if os.path.exists(pdf):
                try:
                    chunks_data = process_pdf(pdf, max_tokens=500, overlap_tokens=50)
                except Exception as e:
                    print(f"  ⚠️ PDF error {arxiv_id}: {e}")

            # Fallback to abstract
            if not chunks_data and p.get("abstract"):
                chunks_data = [{"section": "Abstract", "text": p["abstract"], "chunk_index": 0}]

            if not chunks_data:
                continue

            for c in chunks_data:
                insert_chunk(db_path, paper_id, c.get("section", ""), c.get("chunk_index", 0), c["text"])

            update_paper_status(db_path, arxiv_id, "chunked")
            ingested += 1

        print(f"  📥 {ingested} papers chunked")

    # Embed unembedded chunks
    unembedded = get_unembedded_chunks(db_path)
    if not unembedded:
        print("  ✅ All chunks embedded")
        return

    if args.dry_run:
        print(f"  [dry-run] Would embed {len(unembedded)} chunks")
        return

    print(f"  🔄 Embedding {len(unembedded)} chunks...")
    index = FaissIndex(data_dir, dim=DIM)
    index.load()

    BATCH = 100
    for i in range(0, len(unembedded), BATCH):
        batch = unembedded[i:i + BATCH]
        texts = [c["text"] for c in batch]
        vectors = embed_texts(texts)
        faiss_ids = index.add(vectors)
        for chunk, fid in zip(batch, faiss_ids):
            update_chunk_faiss_id(db_path, chunk["id"], fid)

    index.save()
    print(f"  ✅ Embedded {len(unembedded)} chunks (FAISS: {index.size} total)")


# ---------------------------------------------------------------------------
# paper
# ---------------------------------------------------------------------------

def cmd_paper(args):
    db_path = _db_path(args)
    data_dir = _data_dir(args)

    from db import init_db, get_paper, pdf_path_for
    init_db(db_path)

    paper = get_paper(db_path, args.arxiv_id)
    if not paper:
        print(f"❌ Paper not found: {args.arxiv_id}")
        sys.exit(1)

    pdf = pdf_path_for(paper["arxiv_id"], data_dir)
    has_pdf = os.path.exists(pdf)

    print(f"\n  📄 {paper['title']}")
    print(f"  ID:         {paper['arxiv_id']}")
    print(f"  Categories: {paper.get('categories', [])}")
    print(f"  Published:  {paper.get('published', '?')}")
    print(f"  Status:     {paper.get('status', '?')}")
    print(f"  PDF:        {'✅ ' + pdf if has_pdf else 'Not downloaded'}")
    print(f"  arXiv:      https://arxiv.org/abs/{paper['arxiv_id']}")

    if paper.get("abstract"):
        print(f"\n  Abstract:\n  {paper['abstract'][:500]}...")


# ---------------------------------------------------------------------------
# stats
# ---------------------------------------------------------------------------

def cmd_stats(args):
    db_path = _db_path(args)

    from db import init_db, get_stats
    init_db(db_path)

    stats = get_stats(db_path)

    print("\n  📊 ArXivKB Statistics")
    print("  ─────────────────────")
    print(f"  Papers:       {stats['papers']}")
    print(f"  Chunks:       {stats['chunks']}")
    print(f"  Categories:   {stats['categories']} enabled")


# ---------------------------------------------------------------------------
# expire
# ---------------------------------------------------------------------------

def cmd_expire(args):
    db_path = _db_path(args)
    data_dir = _data_dir(args)

    from db import init_db, get_papers_older_than, delete_paper, pdf_path_for
    init_db(db_path)

    days = args.days if args.days is not None else 90
    if days == 0:
        print("  Expiry disabled (expiry_days=0).")
        return

    old_papers = get_papers_older_than(db_path, days)
    if not old_papers:
        print(f"  No papers older than {days} days.")
        return

    print(f"  Found {len(old_papers)} paper(s) older than {days} days:")
    for p in old_papers:
        print(f"    - {p['arxiv_id']}: {p['title'][:50]} ({p.get('created_at', '?')[:10]})")

    if not args.yes and not _confirm(f"  Delete {len(old_papers)} papers?"):
        print("  Cancelled.")
        return

    deleted_pdfs = 0
    for p in old_papers:
        pdf = pdf_path_for(p["arxiv_id"], data_dir)
        if os.path.exists(pdf):
            os.remove(pdf)
            deleted_pdfs += 1
        delete_paper(db_path, p["id"])

    print(f"  ✅ Deleted {len(old_papers)} papers, {deleted_pdfs} PDFs")


def _confirm(msg: str) -> bool:
    try:
        return input(f"{msg} [y/N] ").strip().lower() == "y"
    except (EOFError, KeyboardInterrupt):
        return False


# ---------------------------------------------------------------------------
# CLI parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="akb", description="ArXivKB — arXiv paper manager")
    parser.add_argument("--data-dir", dest="data_dir", help="Data directory (default: ~/Downloads/ArXivKB)")

    sub = parser.add_subparsers(dest="command", help="Command")

    # topics
    tp = sub.add_parser("topics", help="Manage arXiv categories")
    tp_sub = tp.add_subparsers(dest="topics_cmd")
    tp_sub.add_parser("list", help="List enabled categories")
    browse_p = tp_sub.add_parser("browse", help="Browse all arXiv categories")
    browse_p.add_argument("filter", nargs="?", help="Filter by keyword")
    add_p = tp_sub.add_parser("add", help="Enable categories")
    add_p.add_argument("categories", nargs="+")
    del_p = tp_sub.add_parser("delete", help="Disable categories")
    del_p.add_argument("categories", nargs="+")

    # ingest
    ing = sub.add_parser("ingest", help="Crawl arXiv and download papers")
    ing.add_argument("--days", type=int, help="Days back to crawl")
    ing.add_argument("--dry-run", action="store_true")
    ing.add_argument("--no-pdf", action="store_true", help="Skip PDF downloads")

    # paper
    pp = sub.add_parser("paper", help="Show paper details")
    pp.add_argument("arxiv_id", help="arXiv ID")

    # stats
    sub.add_parser("stats", help="Show database statistics")

    # expire
    exp = sub.add_parser("expire", help="Delete old papers")
    exp.add_argument("--days", type=int, help="Delete papers older than N days")
    exp.add_argument("--yes", "-y", action="store_true", help="Skip confirmation")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    cmd_map = {
        "topics": cmd_topics,
        "ingest": cmd_ingest,
        "paper": cmd_paper,
        "stats": cmd_stats,
        "expire": cmd_expire,
    }

    fn = cmd_map.get(args.command)
    if fn:
        fn(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
