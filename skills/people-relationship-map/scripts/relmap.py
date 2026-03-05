#!/usr/bin/env python3
"""
People Relationship Map — CLI for OpenClaw.

Storage:
  - <workspace>/people/_graph.json   → nodes + edges (machine-readable)
  - <workspace>/people/<slug>.md     → one Markdown card per person (Obsidian-friendly)

Commands:
  add, link, note, touch, show, connections, query, search, list, stale, mermaid
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, date
from difflib import SequenceMatcher
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

WORKSPACE = os.environ.get(
    "OPENCLAW_WORKSPACE",
    os.path.expanduser("~/.openclaw/workspace"),
)
PEOPLE_DIR = Path(WORKSPACE) / "people"
GRAPH_FILE = PEOPLE_DIR / "_graph.json"


def ensure_dirs():
    PEOPLE_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Graph helpers
# ---------------------------------------------------------------------------

def load_graph() -> dict:
    if GRAPH_FILE.exists():
        with open(GRAPH_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"nodes": {}, "edges": []}


def save_graph(graph: dict):
    ensure_dirs()
    with open(GRAPH_FILE, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2, ensure_ascii=False)


def slugify(name: str) -> str:
    """alex-chen from 'Alex Chen'."""
    s = name.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def fuzzy_resolve(graph: dict, name: str) -> str | None:
    """Return the slug of the best-matching node, or None."""
    slug = slugify(name)
    if slug in graph["nodes"]:
        return slug
    # Try substring / fuzzy
    best_slug, best_score = None, 0.0
    for s, node in graph["nodes"].items():
        score = SequenceMatcher(None, slug, s).ratio()
        display_score = SequenceMatcher(
            None, name.lower(), node["displayName"].lower()
        ).ratio()
        m = max(score, display_score)
        if m > best_score:
            best_score = m
            best_slug = s
    if best_score >= 0.6:
        return best_slug
    return None


def today_str() -> str:
    return date.today().isoformat()


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------

def render_md(slug: str, node: dict, edges: list[dict]) -> str:
    """Produce an Obsidian-friendly Markdown card."""
    lines = [f"# {node['displayName']}", ""]

    if node.get("tags"):
        tag_str = " ".join(f"#{t}" for t in node["tags"])
        lines.append(f"- **Tags:** {tag_str}")
    if node.get("org"):
        lines.append(f"- **Org:** {node['org']}")
    if node.get("role"):
        lines.append(f"- **Role:** {node['role']}")
    if node.get("met"):
        lines.append(f"- **Met:** {node['met']}")
    if node.get("lastContact"):
        lines.append(f"- **Last contact:** {node['lastContact']}")
    if node.get("tier"):
        lines.append(f"- **Tier:** {node['tier']}")

    # Notes
    notes = node.get("notes", [])
    if notes:
        lines += ["", "## Notes"]
        for n in notes:
            lines.append(f"- {n['date']} — {n['text']}")

    # Connections
    my_edges = [e for e in edges if e["from"] == slug or e["to"] == slug]
    if my_edges:
        lines += ["", "## Connections"]
        graph = load_graph()
        for e in my_edges:
            other_slug = e["to"] if e["from"] == slug else e["from"]
            other = graph["nodes"].get(other_slug, {})
            other_name = other.get("displayName", other_slug)
            label = f" — {e['label']}" if e.get("label") else ""
            lines.append(f"- [[{other_name}]]{label}")

    lines.append("")
    return "\n".join(lines)


def write_person_md(slug: str, node: dict, edges: list[dict]):
    """Write (or overwrite) the Markdown card for a person."""
    ensure_dirs()
    md_path = PEOPLE_DIR / f"_{slug}.md"
    md_path.write_text(render_md(slug, node, edges), encoding="utf-8")


def refresh_all_md(graph: dict):
    """Re-render every person's Markdown card."""
    for slug, node in graph["nodes"].items():
        write_person_md(slug, node, graph["edges"])


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_add(args):
    graph = load_graph()
    slug = slugify(args.name)

    if slug in graph["nodes"]:
        print(f"⚠️  '{args.name}' already exists. Use 'note' to add info.")
        return

    node = {
        "displayName": args.name.strip(),
        "tags": [t.strip() for t in args.tags.split(",")] if args.tags else [],
        "org": args.org or "",
        "role": args.role or "",
        "met": args.met or today_str(),
        "lastContact": today_str(),
        "tier": args.tier or "acquaintance",
        "notes": [],
        "file": f"_{slug}.md",
    }

    if args.note:
        node["notes"].append({"date": today_str(), "text": args.note})

    graph["nodes"][slug] = node
    save_graph(graph)
    write_person_md(slug, node, graph["edges"])
    print(f"✅ Added {args.name}")


def cmd_link(args):
    graph = load_graph()
    from_slug = fuzzy_resolve(graph, args.from_name)
    to_slug = fuzzy_resolve(graph, args.to_name)

    if not from_slug:
        print(f"❌ Could not find '{args.from_name}'. Add them first.")
        return
    if not to_slug:
        print(f"❌ Could not find '{args.to_name}'. Add them first.")
        return

    # Avoid duplicate edges
    for e in graph["edges"]:
        pair = {e["from"], e["to"]}
        if pair == {from_slug, to_slug}:
            print("ℹ️  Link already exists. Updating label.")
            e["label"] = args.label or e.get("label", "")
            save_graph(graph)
            refresh_all_md(graph)
            return

    graph["edges"].append({
        "from": from_slug,
        "to": to_slug,
        "label": args.label or "",
    })
    save_graph(graph)
    refresh_all_md(graph)

    fn = graph["nodes"][from_slug]["displayName"]
    tn = graph["nodes"][to_slug]["displayName"]
    print(f"🔗 Linked {fn} ↔ {tn}")


def cmd_note(args):
    graph = load_graph()
    slug = fuzzy_resolve(graph, args.person)
    if not slug:
        print(f"❌ Could not find '{args.person}'. Add them first.")
        return

    node = graph["nodes"][slug]
    node["notes"].append({"date": today_str(), "text": args.text})
    node["lastContact"] = today_str()
    save_graph(graph)
    write_person_md(slug, node, graph["edges"])
    print(f"📝 Note added for {node['displayName']}")


def cmd_touch(args):
    graph = load_graph()
    slug = fuzzy_resolve(graph, args.person)
    if not slug:
        print(f"❌ Could not find '{args.person}'.")
        return

    graph["nodes"][slug]["lastContact"] = today_str()
    save_graph(graph)
    write_person_md(slug, graph["nodes"][slug], graph["edges"])
    print(f"👋 Updated last contact for {graph['nodes'][slug]['displayName']}")


def cmd_show(args):
    graph = load_graph()
    slug = fuzzy_resolve(graph, args.person)
    if not slug:
        print(f"❌ Could not find '{args.person}'.")
        return
    print(render_md(slug, graph["nodes"][slug], graph["edges"]))


def cmd_connections(args):
    graph = load_graph()
    slug = fuzzy_resolve(graph, args.person)
    if not slug:
        print(f"❌ Could not find '{args.person}'.")
        return

    name = graph["nodes"][slug]["displayName"]
    found = []
    for e in graph["edges"]:
        if e["from"] == slug:
            other = graph["nodes"].get(e["to"], {})
            found.append((other.get("displayName", e["to"]), e.get("label", "")))
        elif e["to"] == slug:
            other = graph["nodes"].get(e["from"], {})
            found.append((other.get("displayName", e["from"]), e.get("label", "")))

    if not found:
        print(f"{name} has no connections recorded.")
        return

    print(f"Connections for {name}:")
    for other_name, label in found:
        suffix = f" — {label}" if label else ""
        print(f"  • {other_name}{suffix}")


def cmd_query(args):
    graph = load_graph()
    results = []

    for slug, node in graph["nodes"].items():
        if args.org and args.org.lower() not in node.get("org", "").lower():
            continue
        if args.tag and args.tag.lower() not in [t.lower() for t in node.get("tags", [])]:
            continue
        if args.tier and node.get("tier", "") != args.tier:
            continue
        results.append(node)

    if not results:
        print("No matches found.")
        return

    for r in results:
        tier_badge = f" [{r.get('tier', '')}]" if r.get("tier") else ""
        org_badge = f" @ {r['org']}" if r.get("org") else ""
        print(f"  • {r['displayName']}{org_badge}{tier_badge}")


def cmd_search(args):
    graph = load_graph()
    q = args.query.lower()
    results = []

    for slug, node in graph["nodes"].items():
        # Search display name, org, role, tags, and all notes
        haystack = " ".join([
            node.get("displayName", ""),
            node.get("org", ""),
            node.get("role", ""),
            " ".join(node.get("tags", [])),
            " ".join(n["text"] for n in node.get("notes", [])),
        ]).lower()

        if q in haystack:
            results.append(node)

    if not results:
        print(f"No matches for '{args.query}'.")
        return

    print(f"People matching '{args.query}':")
    for r in results:
        print(f"  • {r['displayName']}")


def cmd_list(args):
    graph = load_graph()
    if not graph["nodes"]:
        print("No people stored yet.")
        return

    for slug, node in sorted(graph["nodes"].items()):
        n_notes = len(node.get("notes", []))
        tier = node.get("tier", "?")
        lc = node.get("lastContact", "?")
        print(f"  • {node['displayName']}  [{tier}]  {n_notes} notes  last: {lc}")


def cmd_stale(args):
    graph = load_graph()
    thresholds = {
        "close": args.close_days,
        "regular": args.regular_days,
        "acquaintance": args.acquaintance_days,
    }
    today = date.today()
    stale = []

    for slug, node in graph["nodes"].items():
        tier = node.get("tier", "acquaintance")
        lc = node.get("lastContact")
        if not lc:
            stale.append((node["displayName"], tier, "never"))
            continue
        try:
            last = date.fromisoformat(lc)
        except ValueError:
            stale.append((node["displayName"], tier, "unknown"))
            continue

        days_ago = (today - last).days
        threshold = thresholds.get(tier, 90)
        if days_ago > threshold:
            stale.append((node["displayName"], tier, f"{days_ago}d ago"))

    if not stale:
        if args.format == "message":
            print("All relationships are fresh! 🌱 No follow-ups needed this week.")
        else:
            print("No stale relationships.")
        return

    if args.format == "message":
        lines = ["🔔 *Relationship check-in*\n"]
        for name, tier, ago in sorted(stale, key=lambda x: x[1]):
            emoji = {"close": "❤️", "regular": "👋", "acquaintance": "📇"}.get(tier, "•")
            lines.append(f"{emoji} *{name}* ({tier}) — last contact: {ago}")
        lines.append("\nConsider reaching out to keep these connections warm!")
        print("\n".join(lines))
    else:
        for name, tier, ago in stale:
            print(f"  ⚠️  {name} [{tier}] — last contact: {ago}")


def cmd_mermaid(args):
    graph = load_graph()
    if not graph["nodes"]:
        print("Empty graph.")
        return

    lines = ["graph LR"]
    for slug, node in graph["nodes"].items():
        safe_name = node["displayName"].replace('"', "'")
        lines.append(f'    {slug}["{safe_name}"]')

    for e in graph["edges"]:
        label = e.get("label", "")
        if label:
            safe_label = label.replace('"', "'")
            lines.append(f'    {e["from"]} -- "{safe_label}" --> {e["to"]}')
        else:
            lines.append(f'    {e["from"]} --> {e["to"]}')

    print("\n".join(lines))


# ---------------------------------------------------------------------------
# CLI parser
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        prog="relmap",
        description="People Relationship Map for OpenClaw",
    )
    sub = parser.add_subparsers(dest="command")

    # add
    p = sub.add_parser("add", help="Add a new person")
    p.add_argument("--name", required=True)
    p.add_argument("--tags", default="")
    p.add_argument("--org", default="")
    p.add_argument("--role", default="")
    p.add_argument("--met", default="")
    p.add_argument("--tier", default="acquaintance", choices=["close", "regular", "acquaintance"])
    p.add_argument("--note", default="")

    # link
    p = sub.add_parser("link", help="Link two people")
    p.add_argument("--from", dest="from_name", required=True)
    p.add_argument("--to", dest="to_name", required=True)
    p.add_argument("--label", default="")

    # note
    p = sub.add_parser("note", help="Add a note to a person")
    p.add_argument("--person", required=True)
    p.add_argument("--text", required=True)

    # touch
    p = sub.add_parser("touch", help="Update last contact date")
    p.add_argument("--person", required=True)

    # show
    p = sub.add_parser("show", help="Show a person's full card")
    p.add_argument("--person", required=True)

    # connections
    p = sub.add_parser("connections", help="Show who is connected to a person")
    p.add_argument("--person", required=True)

    # query
    p = sub.add_parser("query", help="Find people by org, tag, or tier")
    p.add_argument("--org", default="")
    p.add_argument("--tag", default="")
    p.add_argument("--tier", default="")

    # search
    p = sub.add_parser("search", help="Full-text search across notes")
    p.add_argument("--query", required=True)

    # list
    sub.add_parser("list", help="List all people")

    # stale
    p = sub.add_parser("stale", help="Find stale relationships")
    p.add_argument("--close-days", type=int, default=14)
    p.add_argument("--regular-days", type=int, default=30)
    p.add_argument("--acquaintance-days", type=int, default=90)
    p.add_argument("--format", choices=["text", "message"], default="text")

    # mermaid
    sub.add_parser("mermaid", help="Export graph as Mermaid diagram")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    {
        "add": cmd_add,
        "link": cmd_link,
        "note": cmd_note,
        "touch": cmd_touch,
        "show": cmd_show,
        "connections": cmd_connections,
        "query": cmd_query,
        "search": cmd_search,
        "list": cmd_list,
        "stale": cmd_stale,
        "mermaid": cmd_mermaid,
    }[args.command](args)


if __name__ == "__main__":
    main()
