#!/usr/bin/env python3
"""
mem.py — Cognitive Memory CLI for OpenClaw agents

Usage:
    mem.py store <content> [--type TYPE] [--source SOURCE] [--importance N]
    mem.py recall <query> [--strategy hybrid|vector|keyword] [--limit N]
    mem.py forget <id|--query QUERY>
    mem.py hard-delete <id>
    mem.py stats
    mem.py associate <source_id> <target_id> [--type TYPE] [--weight N]
    mem.py links <memory_id>
    mem.py recall-assoc <query> [--hops N] [--limit N]
    mem.py graph-stats
    mem.py build-hierarchy [--levels N]
    mem.py recall-adaptive <query> [--detail auto|broad|specific|0-3] [--limit N]
    mem.py hierarchy-stats
    mem.py primed-recall <query> [--context 'text1' 'text2'] [--limit N]
    mem.py share <memory_id> --with <agent> [--sensitivity N]
    mem.py shared [--from AGENT] [--to AGENT]
    mem.py revoke <share_id> | --memory <id>
    mem.py consolidate [--days N] [--decay-only]
    mem.py init
    mem.py migrate  (migrate existing jarvis.db documents)

Examples:
    mem.py store "Oscar prefers wired home automation" --type semantic --importance 0.8
    mem.py recall "home automation preferences"
    mem.py recall "PRIVACY.md" --strategy keyword
    mem.py forget --query "that old project"
    mem.py stats
"""
import sys
import os
import json
import time
import logging

# Add parent to path for lib imports
sys.path.insert(0, os.path.dirname(__file__))

from lib.memory_core import (
    get_conn, init_db, store, recall, forget, hard_delete, stats,
    apply_decay, consolidate,
    associate, get_associations, recall_associated, association_stats,
    build_temporal_associations,
    build_hierarchy, recall_adaptive, hierarchy_stats,
    spreading_activation, primed_recall,
    share_memory, approve_share, revoke_share, get_shared, sharing_stats,
    WORKSPACE, DB_PATH
)

logging.basicConfig(
    level=logging.DEBUG if "--verbose" in sys.argv else logging.WARNING,
    format="%(levelname)s %(message)s"
)

def cmd_init():
    conn = get_conn()
    init_db(conn)
    s = stats(conn)
    print(f"✓ Database initialized at {s['db_path']}")
    print(f"  Active memories: {s['total_active']}")
    conn.close()

def cmd_store(args):
    if not args:
        print("Usage: mem.py store <content> [--type TYPE] [--source SOURCE] [--importance N]")
        sys.exit(1)

    # Parse flags
    content_parts = []
    mem_type = "episodic"
    source = "agent"
    importance = 0.5

    i = 0
    while i < len(args):
        if args[i] == "--type" and i + 1 < len(args):
            mem_type = args[i + 1]; i += 2
        elif args[i] == "--source" and i + 1 < len(args):
            source = args[i + 1]; i += 2
        elif args[i] == "--importance" and i + 1 < len(args):
            importance = float(args[i + 1]); i += 2
        else:
            content_parts.append(args[i]); i += 1

    content = " ".join(content_parts)
    if not content:
        print("Error: no content provided")
        sys.exit(1)

    conn = get_conn()
    init_db(conn)
    t0 = time.time()
    mid = store(conn, content, memory_type=mem_type, source=source, importance=importance)
    elapsed = (time.time() - t0) * 1000
    print(f"✓ Stored memory #{mid} ({mem_type}, importance={importance}) [{elapsed:.0f}ms]")
    conn.close()

def cmd_recall(args):
    if not args:
        print("Usage: mem.py recall <query> [--strategy hybrid|vector|keyword] [--limit N]")
        sys.exit(1)

    query_parts = []
    strategy = "hybrid"
    limit = 10

    i = 0
    while i < len(args):
        if args[i] == "--strategy" and i + 1 < len(args):
            strategy = args[i + 1]; i += 2
        elif args[i] == "--limit" and i + 1 < len(args):
            limit = int(args[i + 1]); i += 2
        else:
            query_parts.append(args[i]); i += 1

    query = " ".join(query_parts)
    conn = get_conn()
    init_db(conn)

    t0 = time.time()
    results = recall(conn, query, strategy=strategy, limit=limit)
    elapsed = (time.time() - t0) * 1000

    if not results:
        print(f"No memories found for '{query}' ({strategy}) [{elapsed:.0f}ms]")
    else:
        print(f"Found {len(results)} memories ({strategy}) [{elapsed:.0f}ms]:\n")
        for r in results:
            score = r.get('score', 0)
            mtype = r.get('memory_type', '?')
            strength = r.get('strength', 0)
            content = r.get('content', '')
            # Truncate long content
            if len(content) > 120:
                content = content[:117] + "..."
            print(f"  #{r['id']:>4}  [{mtype:10s}]  str={strength:.2f}  score={score:.3f}")
            print(f"        {content}")
            print()

    conn.close()

def cmd_forget(args):
    conn = get_conn()
    init_db(conn)

    if args and args[0] == "--query":
        query = " ".join(args[1:])
        count = forget(conn, query=query)
        print(f"✓ Soft-deleted {count} memories matching '{query}'")
    elif args and args[0].isdigit():
        mid = int(args[0])
        forget(conn, memory_id=mid)
        print(f"✓ Soft-deleted memory #{mid}")
    else:
        print("Usage: mem.py forget <id> | mem.py forget --query <text>")
        sys.exit(1)
    conn.close()

def cmd_hard_delete(args):
    if not args or not args[0].isdigit():
        print("Usage: mem.py hard-delete <id>")
        sys.exit(1)
    conn = get_conn()
    init_db(conn)
    ok = hard_delete(conn, int(args[0]))
    print(f"✓ Hard-deleted memory #{args[0]}" if ok else f"Memory #{args[0]} not found")
    conn.close()

def cmd_stats():
    conn = get_conn()
    init_db(conn)
    s = stats(conn)
    print(f"╔══════════════════════════════════════╗")
    print(f"║       COGNITIVE MEMORY STATS         ║")
    print(f"╠══════════════════════════════════════╣")
    print(f"║  Active memories:  {s['total_active']:>6}            ║")
    print(f"║  Deleted (soft):   {s['total_deleted']:>6}            ║")
    print(f"║  With embeddings:  {s['with_embeddings']:>6}            ║")
    print(f"║  DB size:          {s['db_size_kb']:>6} KB         ║")
    print(f"║──────────────────────────────────────║")
    for mtype, count in sorted(s.get('by_type', {}).items()):
        print(f"║  {mtype:<18} {count:>6}            ║")
    print(f"╚══════════════════════════════════════╝")
    print(f"  Path: {s['db_path']}")
    conn.close()

def cmd_associate(args):
    """Manually create an association between two memories."""
    if len(args) < 2:
        print("Usage: mem.py associate <source_id> <target_id> [--type TYPE] [--weight N]")
        sys.exit(1)
    source_id = int(args[0])
    target_id = int(args[1])
    edge_type = "explicit"
    weight = 0.7
    i = 2
    while i < len(args):
        if args[i] == "--type" and i + 1 < len(args):
            edge_type = args[i + 1]; i += 2
        elif args[i] == "--weight" and i + 1 < len(args):
            weight = float(args[i + 1]); i += 2
        else:
            i += 1

    conn = get_conn()
    init_db(conn)
    aid = associate(conn, source_id, target_id, edge_type, weight)
    if aid:
        print(f"✓ Associated #{source_id} → #{target_id} ({edge_type}, weight={weight})")
    else:
        print(f"✗ Failed to create association")
    conn.close()

def cmd_links(args):
    """Show associations for a memory."""
    if not args or not args[0].isdigit():
        print("Usage: mem.py links <memory_id>")
        sys.exit(1)
    mid = int(args[0])
    conn = get_conn()
    init_db(conn)
    assocs = get_associations(conn, mid)
    if not assocs:
        print(f"No associations for memory #{mid}")
    else:
        print(f"Associations for memory #{mid} ({len(assocs)} edges):\n")
        for a in assocs:
            direction = "→" if a['source_id'] == mid else "←"
            other_id = a['target_id'] if a['source_id'] == mid else a['source_id']
            content = a.get('target_content') or a.get('source_content', '?')
            if len(content) > 80:
                content = content[:77] + "..."
            print(f"  {direction} #{other_id:>4}  [{a['edge_type']:10s}]  w={a['weight']:.3f}")
            print(f"           {content}\n")
    conn.close()

def cmd_graph_stats():
    """Show association graph statistics."""
    conn = get_conn()
    init_db(conn)
    s = association_stats(conn)
    mem_s = stats(conn)
    print(f"╔══════════════════════════════════════╗")
    print(f"║       ASSOCIATION GRAPH STATS         ║")
    print(f"╠══════════════════════════════════════╣")
    print(f"║  Total edges:     {s['total_edges']:>6}             ║")
    print(f"║  Connected nodes: {s['connected_memories']:>6} / {mem_s['total_active']:<6}     ║")
    print(f"║  Avg weight:      {s['avg_weight']:>6.3f}             ║")
    print(f"║──────────────────────────────────────║")
    for etype, count in sorted(s.get('by_type', {}).items()):
        print(f"║  {etype:<18} {count:>6}             ║")
    print(f"╚══════════════════════════════════════╝")
    conn.close()

def cmd_recall_assoc(args):
    """Recall with multi-hop association traversal."""
    if not args:
        print("Usage: mem.py recall-assoc <query> [--hops N] [--limit N]")
        sys.exit(1)
    query_parts = []
    hops = 1
    limit = 10
    i = 0
    while i < len(args):
        if args[i] == "--hops" and i + 1 < len(args):
            hops = int(args[i + 1]); i += 2
        elif args[i] == "--limit" and i + 1 < len(args):
            limit = int(args[i + 1]); i += 2
        else:
            query_parts.append(args[i]); i += 1

    query = " ".join(query_parts)
    conn = get_conn()
    init_db(conn)
    t0 = time.time()
    results = recall_associated(conn, query, hops=hops, limit=limit)
    elapsed = (time.time() - t0) * 1000

    if not results:
        print(f"No memories found for '{query}' [{elapsed:.0f}ms]")
    else:
        print(f"Found {len(results)} memories (multi-hop, {hops} hops) [{elapsed:.0f}ms]:\n")
        for r in results:
            hop = r.get('hop', 0)
            via = r.get('via_edge', 'direct')
            content = r.get('content', '')[:120]
            hop_label = f"hop={hop}" if hop > 0 else "direct"
            via_label = f" via={via}" if hop > 0 else ""
            print(f"  #{r['id']:>4}  [{r.get('memory_type','?'):10s}]  score={r.get('score',0):.3f}  {hop_label}{via_label}")
            print(f"        {content}")
            print()
    conn.close()

def cmd_build_hierarchy(args):
    """Build RAPTOR-style multi-level hierarchy."""
    max_level = 3
    for i, a in enumerate(args):
        if a == "--levels" and i + 1 < len(args):
            max_level = int(args[i + 1])

    conn = get_conn()
    init_db(conn)
    print(f"Building hierarchy (max {max_level} levels)...")
    result = build_hierarchy(conn, max_level=max_level)
    print(f"╔══════════════════════════════════════╗")
    print(f"║       HIERARCHY BUILD RESULTS        ║")
    print(f"╠══════════════════════════════════════╣")
    print(f"║  Total nodes:     {result['total_nodes']:>6}             ║")
    for level, count in sorted(result.get('by_level', {}).items()):
        label = ["raw", "topic", "theme", "domain"][level] if level < 4 else f"L{level}"
        print(f"║  L{level} ({label:6s}):   {count:>6}             ║")
    print(f"║──────────────────────────────────────║")
    print(f"║  Elapsed:     {result['elapsed_ms']:>6} ms            ║")
    print(f"╚══════════════════════════════════════╝")
    conn.close()

def cmd_recall_adaptive(args):
    """Adaptive recall across hierarchy levels."""
    if not args:
        print("Usage: mem.py recall-adaptive <query> [--detail auto|broad|specific|0-3] [--limit N]")
        sys.exit(1)
    query_parts = []
    detail = "auto"
    limit = 10
    i = 0
    while i < len(args):
        if args[i] == "--detail" and i + 1 < len(args):
            detail = args[i + 1]; i += 2
        elif args[i] == "--limit" and i + 1 < len(args):
            limit = int(args[i + 1]); i += 2
        else:
            query_parts.append(args[i]); i += 1

    query = " ".join(query_parts)
    conn = get_conn()
    init_db(conn)
    t0 = time.time()
    results = recall_adaptive(conn, query, detail_level=detail, limit=limit)
    elapsed = (time.time() - t0) * 1000

    if not results:
        print(f"No memories found [{elapsed:.0f}ms]")
    else:
        level = results[0].get('hierarchy_level', '?')
        print(f"Found {len(results)} memories (adaptive, level={level}) [{elapsed:.0f}ms]:\n")
        for r in results:
            content = r.get('content', '')[:120]
            print(f"  #{r['id']:>4}  [{r.get('memory_type','?'):10s}]  score={r.get('score',0):.3f}")
            print(f"        {content}\n")
    conn.close()

def cmd_hierarchy_stats():
    """Show hierarchy statistics."""
    conn = get_conn()
    init_db(conn)
    s = hierarchy_stats(conn)
    print(f"╔══════════════════════════════════════╗")
    print(f"║       HIERARCHY STATS                ║")
    print(f"╠══════════════════════════════════════╣")
    print(f"║  Total nodes:     {s['total_nodes']:>6}             ║")
    print(f"║  Root summaries:  {s['root_summaries']:>6}             ║")
    print(f"║──────────────────────────────────────║")
    for level, count in sorted(s.get('by_level', {}).items()):
        label = ["raw", "topic", "theme", "domain"][level] if level < 4 else f"L{level}"
        print(f"║  L{level} ({label:6s}):   {count:>6}             ║")
    print(f"╚══════════════════════════════════════╝")
    conn.close()

def cmd_primed_recall(args):
    """Context-primed recall with spreading activation."""
    if not args:
        print("Usage: mem.py primed-recall <query> [--context 'text1' 'text2'] [--limit N]")
        sys.exit(1)
    query_parts = []
    context = []
    limit = 10
    i = 0
    while i < len(args):
        if args[i] == "--context" and i + 1 < len(args):
            i += 1
            while i < len(args) and not args[i].startswith("--"):
                context.append(args[i]); i += 1
        elif args[i] == "--limit" and i + 1 < len(args):
            limit = int(args[i + 1]); i += 2
        else:
            query_parts.append(args[i]); i += 1

    query = " ".join(query_parts)
    conn = get_conn()
    init_db(conn)
    t0 = time.time()
    results = primed_recall(conn, query, context=context or None, limit=limit)
    elapsed = (time.time() - t0) * 1000

    if not results:
        print(f"No memories found [{elapsed:.0f}ms]")
    else:
        ctx_label = f" + {len(context)} context" if context else ""
        print(f"Found {len(results)} memories (primed{ctx_label}) [{elapsed:.0f}ms]:\n")
        for r in results:
            content = r.get('content', '')[:120]
            act = r.get('activation', 0)
            fscore = r.get('final_score', 0)
            via = f" [{r['via']}]" if r.get('via') else ""
            print(f"  #{r['id']:>4}  [{r.get('memory_type','?'):10s}]  final={fscore:.3f}  act={act:.3f}{via}")
            print(f"        {content}\n")
    conn.close()

def cmd_share(args):
    """Share a memory with another agent."""
    if len(args) < 2:
        print("Usage: mem.py share <memory_id> --with <agent> [--sensitivity N]")
        sys.exit(1)
    memory_id = int(args[0])
    agent = None
    sensitivity = 0.5
    i = 1
    while i < len(args):
        if args[i] == "--with" and i + 1 < len(args):
            agent = args[i + 1]; i += 2
        elif args[i] == "--sensitivity" and i + 1 < len(args):
            sensitivity = float(args[i + 1]); i += 2
        else:
            i += 1
    if not agent:
        print("Error: --with <agent> required")
        sys.exit(1)

    conn = get_conn()
    init_db(conn)
    sid = share_memory(conn, memory_id, "jarvis", agent, sensitivity)
    if sid:
        print(f"✓ Shared memory #{memory_id} with {agent} (share #{sid})")
    else:
        print(f"✗ Memory #{memory_id} blocked by sensitivity gate or not shareable")
    conn.close()

def cmd_shared(args):
    """List shared memories."""
    agent = None
    direction = "both"
    i = 0
    while i < len(args):
        if args[i] == "--from" and i + 1 < len(args):
            agent = args[i + 1]; direction = "from"; i += 2
        elif args[i] == "--to" and i + 1 < len(args):
            agent = args[i + 1]; direction = "to"; i += 2
        elif args[i] == "--agent" and i + 1 < len(args):
            agent = args[i + 1]; i += 2
        else:
            i += 1

    conn = get_conn()
    init_db(conn)
    shares = get_shared(conn, agent=agent, direction=direction)
    if not shares:
        print("No shared memories found")
    else:
        print(f"Shared memories ({len(shares)}):\n")
        for s in shares:
            content = s.get('content', '')[:80]
            consent = "✅" if s['consent_owner'] and s['consent_target'] else "⏳"
            print(f"  share #{s['id']}  mem #{s['memory_id']}  {s['shared_by']}→{s['shared_with']}  {consent}  sens={s['sensitivity']:.1f}")
            print(f"        {content}\n")
    conn.close()

def cmd_revoke(args):
    """Revoke a shared memory."""
    if not args:
        print("Usage: mem.py revoke <share_id> | mem.py revoke --memory <id>")
        sys.exit(1)
    conn = get_conn()
    init_db(conn)
    if args[0] == "--memory" and len(args) > 1:
        count = revoke_share(conn, memory_id=int(args[1]))
        print(f"✓ Revoked {count} shares for memory #{args[1]}")
    else:
        revoke_share(conn, share_id=int(args[0]))
        print(f"✓ Revoked share #{args[0]}")
    conn.close()

def cmd_consolidate(args):
    """Run consolidation: decay + clustering + summaries."""
    days = 1
    decay_only = False
    i = 0
    while i < len(args):
        if args[i] == "--days" and i + 1 < len(args):
            days = int(args[i + 1]); i += 2
        elif args[i] == "--decay-only":
            decay_only = True; i += 1
        else:
            i += 1

    conn = get_conn()
    init_db(conn)

    if decay_only:
        result = apply_decay(conn)
        print(f"╔══════════════════════════════════════╗")
        print(f"║          DECAY RESULTS               ║")
        print(f"╠══════════════════════════════════════╣")
        print(f"║  Decayed:     {result['decayed']:>6}                ║")
        print(f"║  Soft-deleted:{result['deleted']:>6}                ║")
        print(f"║  Unchanged:   {result['unchanged']:>6}                ║")
        print(f"╚══════════════════════════════════════╝")
    else:
        print(f"Running consolidation (last {days} day{'s' if days > 1 else ''})...")
        result = consolidate(conn, days=days)
        d = result['decay']
        print(f"╔══════════════════════════════════════╗")
        print(f"║       CONSOLIDATION RESULTS          ║")
        print(f"╠══════════════════════════════════════╣")
        print(f"║  Decay:                              ║")
        print(f"║    Decayed:     {d['decayed']:>6}              ║")
        print(f"║    Soft-deleted:{d['deleted']:>6}              ║")
        print(f"║    Unchanged:   {d['unchanged']:>6}              ║")
        print(f"║──────────────────────────────────────║")
        print(f"║  Clustering:                         ║")
        print(f"║    Clusters:    {result['clusters_found']:>6}              ║")
        print(f"║    Summaries:   {result['summaries_created']:>6}              ║")
        print(f"║──────────────────────────────────────║")
        print(f"║  Associations:                       ║")
        print(f"║    Created:     {result.get('associations_created', 0):>6}              ║")
        print(f"║──────────────────────────────────────║")
        print(f"║  Elapsed:     {result['elapsed_ms']:>6} ms            ║")
        print(f"╚══════════════════════════════════════╝")

    conn.close()

def cmd_migrate():
    """Migrate existing jarvis.db documents into memory.db."""
    old_db = WORKSPACE / "db" / "jarvis.db"
    if not old_db.exists():
        print(f"No jarvis.db found at {old_db}")
        return

    import sqlite3 as s3
    old_conn = s3.connect(str(old_db))
    old_conn.row_factory = s3.Row

    docs = old_conn.execute("SELECT * FROM documents WHERE content IS NOT NULL").fetchall()
    print(f"Found {len(docs)} documents in jarvis.db")

    conn = get_conn()
    init_db(conn)

    migrated = 0
    for doc in docs:
        content = doc['content']
        if not content or len(content.strip()) < 10:
            continue
        title = doc['title'] or ''
        dtype = doc['type'] or 'document'
        # Combine title + content for richer embedding
        full = f"{title}\n{content}" if title else content
        # Truncate very long docs to first 2000 chars for embedding
        embed_text = full[:2000]
        try:
            mid = store(conn, embed_text, memory_type="semantic",
                       source=f"import:jarvis.db:{dtype}",
                       importance=0.6,
                       metadata={"original_path": doc['path'], "original_id": doc['id']})
            migrated += 1
            if migrated % 20 == 0:
                print(f"  ... migrated {migrated}/{len(docs)}")
        except Exception as e:
            print(f"  ⚠ Failed to migrate doc #{doc['id']}: {e}")

    print(f"✓ Migrated {migrated} documents into memory.db")
    old_conn.close()
    conn.close()

def main():
    args = [a for a in sys.argv[1:] if a != "--verbose"]
    if not args:
        print(__doc__)
        sys.exit(0)

    cmd = args[0]
    rest = args[1:]

    if cmd == "init":
        cmd_init()
    elif cmd == "store":
        cmd_store(rest)
    elif cmd == "recall":
        cmd_recall(rest)
    elif cmd == "forget":
        cmd_forget(rest)
    elif cmd == "hard-delete":
        cmd_hard_delete(rest)
    elif cmd == "stats":
        cmd_stats()
    elif cmd == "associate":
        cmd_associate(rest)
    elif cmd == "links":
        cmd_links(rest)
    elif cmd == "recall-assoc":
        cmd_recall_assoc(rest)
    elif cmd == "graph-stats":
        cmd_graph_stats()
    elif cmd == "build-hierarchy":
        cmd_build_hierarchy(rest)
    elif cmd == "recall-adaptive":
        cmd_recall_adaptive(rest)
    elif cmd == "hierarchy-stats":
        cmd_hierarchy_stats()
    elif cmd == "primed-recall":
        cmd_primed_recall(rest)
    elif cmd == "share":
        cmd_share(rest)
    elif cmd == "shared":
        cmd_shared(rest)
    elif cmd == "revoke":
        cmd_revoke(rest)
    elif cmd == "consolidate":
        cmd_consolidate(rest)
    elif cmd == "migrate":
        cmd_migrate()
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()
