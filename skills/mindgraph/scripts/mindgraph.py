#!/usr/bin/env python3
"""
MindGraph — Obsidian-style [[wikilink]] knowledge graph for OpenClaw workspaces.
Indexes, queries, and traverses bidirectional links across all markdown files.
"""

import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from datetime import datetime, timezone

WORKSPACE = os.environ.get("MINDGRAPH_WORKSPACE", os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
GRAPH_FILE = os.path.join(WORKSPACE, "mindgraph.json")
WIKILINK_RE = re.compile(r'\[\[([^\]|]+?)(?:\|[^\]]+?)?\]\]')

def normalize(name):
    """Normalize a link target for matching."""
    return name.strip().lower().replace(" ", "-").replace("_", "-")

def scan_files():
    """Find all .md files in workspace."""
    files = []
    for root, dirs, fnames in os.walk(WORKSPACE):
        # Skip hidden dirs, node_modules, .git
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
        for f in fnames:
            if f.endswith('.md'):
                files.append(os.path.join(root, f))
    return files

def extract_links(filepath):
    """Extract all [[wikilinks]] from a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except (UnicodeDecodeError, FileNotFoundError):
        return [], "", []
    
    links = WIKILINK_RE.findall(content)
    
    # Extract aliases from frontmatter
    aliases = []
    if content.startswith('---'):
        end = content.find('---', 3)
        if end != -1:
            frontmatter = content[3:end]
            alias_match = re.search(r'aliases:\s*\[([^\]]*)\]', frontmatter)
            if alias_match:
                aliases = [a.strip().strip('"').strip("'") for a in alias_match.group(1).split(',') if a.strip()]
    
    return links, content, aliases

def extract_context(content, link_name, max_chars=150):
    """Extract surrounding context for a link mention."""
    pattern = re.compile(r'\[\[' + re.escape(link_name) + r'(?:\|[^\]]+?)?\]\]', re.IGNORECASE)
    contexts = []
    for match in pattern.finditer(content):
        start = max(0, match.start() - 60)
        end = min(len(content), match.end() + 60)
        ctx = content[start:end].replace('\n', ' ').strip()
        if start > 0:
            ctx = '...' + ctx
        if end < len(content):
            ctx = ctx + '...'
        contexts.append(ctx)
    return contexts

def node_id_from_path(filepath):
    """Create a node ID from a file path."""
    rel = os.path.relpath(filepath, WORKSPACE)
    name = rel.replace('/', '-').replace('\\', '-')
    if name.endswith('.md'):
        name = name[:-3]
    return normalize(name)

def build_index():
    """Build the full graph index."""
    files = scan_files()
    nodes = {}
    # Map from normalized name/alias to node_id
    name_to_node = {}
    
    # First pass: create nodes for all files
    for fp in files:
        node_id = node_id_from_path(fp)
        links, content, aliases = extract_links(fp)
        rel_path = os.path.relpath(fp, WORKSPACE)
        
        # Determine type
        if 'projects/' in rel_path:
            node_type = 'project'
        elif 'memory/' in rel_path:
            node_type = 'memory'
        elif rel_path in ('SOUL.md', 'IDENTITY.md', 'USER.md', 'AGENTS.md'):
            node_type = 'core'
        else:
            node_type = 'file'
        
        nodes[node_id] = {
            'type': node_type,
            'file': rel_path,
            'aliases': aliases,
            'outLinks': [normalize(l) for l in links],
            'inLinks': []  # populated in second pass
        }
        
        # Register name mappings
        name_to_node[node_id] = node_id
        basename = normalize(Path(fp).stem)
        name_to_node[basename] = node_id
        for alias in aliases:
            name_to_node[normalize(alias)] = node_id
    
    # Second pass: build inLinks (collect new concept nodes separately to avoid mutation during iteration)
    new_concepts = {}
    for node_id, node in list(nodes.items()):
        for target in node['outLinks']:
            target_node_id = name_to_node.get(target)
            if target_node_id and target_node_id in nodes:
                if node_id not in nodes[target_node_id]['inLinks']:
                    nodes[target_node_id]['inLinks'].append(node_id)
            else:
                if target in new_concepts:
                    if node_id not in new_concepts[target]['inLinks']:
                        new_concepts[target]['inLinks'].append(node_id)
                else:
                    new_concepts[target] = {
                        'type': 'concept',
                        'file': None,
                        'aliases': [],
                        'outLinks': [],
                        'inLinks': [node_id]
                    }
                    name_to_node[target] = target
    nodes.update(new_concepts)
    
    graph = {
        'nodes': nodes,
        'nameMap': name_to_node,
        'lastIndexed': datetime.now(timezone.utc).isoformat(),
        'fileCount': len(files),
        'nodeCount': len(nodes),
        'linkCount': sum(len(n['outLinks']) for n in nodes.values())
    }
    
    with open(GRAPH_FILE, 'w') as f:
        json.dump(graph, f, indent=2)
    
    file_nodes = sum(1 for n in nodes.values() if n['file'])
    concept_nodes = sum(1 for n in nodes.values() if not n['file'])
    print(f"✅ Indexed {len(files)} files → {file_nodes} file nodes + {concept_nodes} concept nodes")
    print(f"   {graph['linkCount']} links total")
    return graph

def load_graph():
    """Load the graph from disk."""
    if not os.path.exists(GRAPH_FILE):
        print("⚠️  No index found. Run: mindgraph.py index")
        sys.exit(1)
    with open(GRAPH_FILE) as f:
        return json.load(f)

def resolve_name(graph, name):
    """Resolve a name to a node_id."""
    n = normalize(name)
    name_map = graph.get('nameMap', {})
    if n in name_map:
        return name_map[n]
    # Fuzzy: check if any key contains the search term
    matches = [k for k in graph['nodes'] if n in k]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        print(f"Multiple matches for '{name}': {', '.join(matches)}")
        return matches[0]
    return n

def cmd_backlinks(graph, name):
    """Show what links TO this topic."""
    node_id = resolve_name(graph, name)
    node = graph['nodes'].get(node_id)
    
    if not node:
        print(f"❌ '{name}' not found in graph")
        return
    
    in_links = node.get('inLinks', [])
    if not in_links:
        print(f"No backlinks to '{name}'")
        return
    
    print(f"🔗 Backlinks to [[{name}]] ({len(in_links)}):\n")
    for src_id in sorted(in_links):
        src_node = graph['nodes'].get(src_id, {})
        src_file = src_node.get('file', '(concept)')
        print(f"  ← {src_file or src_id}")

def cmd_links(graph, name):
    """Show what this file/topic links TO."""
    node_id = resolve_name(graph, name)
    node = graph['nodes'].get(node_id)
    
    if not node:
        print(f"❌ '{name}' not found in graph")
        return
    
    out_links = node.get('outLinks', [])
    if not out_links:
        print(f"No outgoing links from '{name}'")
        return
    
    print(f"🔗 Links from [[{name}]] ({len(out_links)}):\n")
    for target_id in sorted(set(out_links)):
        target_node = graph['nodes'].get(target_id, {})
        target_file = target_node.get('file', '(concept)')
        print(f"  → {target_file or target_id}")

def cmd_query(graph, name):
    """Show all connections + context for a topic."""
    node_id = resolve_name(graph, name)
    node = graph['nodes'].get(node_id)
    
    if not node:
        print(f"❌ '{name}' not found in graph")
        return
    
    print(f"📊 [[{name}]]")
    print(f"   Type: {node.get('type', 'unknown')}")
    if node.get('file'):
        print(f"   File: {node['file']}")
    if node.get('aliases'):
        print(f"   Aliases: {', '.join(node['aliases'])}")
    
    in_links = node.get('inLinks', [])
    out_links = node.get('outLinks', [])
    
    if in_links:
        print(f"\n   ← Referenced by ({len(in_links)}):")
        for src_id in sorted(in_links):
            src_node = graph['nodes'].get(src_id, {})
            print(f"     {src_node.get('file') or src_id}")
            # Show context
            if src_node.get('file'):
                fp = os.path.join(WORKSPACE, src_node['file'])
                if os.path.exists(fp):
                    with open(fp, 'r', encoding='utf-8') as f:
                        content = f.read()
                    contexts = extract_context(content, name)
                    for ctx in contexts[:2]:
                        print(f"       \"{ctx}\"")
    
    if out_links:
        unique_out = sorted(set(out_links))
        print(f"\n   → Links to ({len(unique_out)}):")
        for target_id in unique_out:
            target_node = graph['nodes'].get(target_id, {})
            print(f"     {target_node.get('file') or target_id}")

def cmd_connections(graph, name):
    """Show bidirectional connections for a topic."""
    node_id = resolve_name(graph, name)
    node = graph['nodes'].get(node_id)
    
    if not node:
        print(f"❌ '{name}' not found in graph")
        return
    
    in_links = set(node.get('inLinks', []))
    out_links = set(node.get('outLinks', []))
    bidirectional = in_links & out_links
    only_in = in_links - out_links
    only_out = out_links - in_links
    
    print(f"🕸️  Connections for [[{name}]]:\n")
    
    if bidirectional:
        print(f"  ↔ Bidirectional ({len(bidirectional)}):")
        for nid in sorted(bidirectional):
            n = graph['nodes'].get(nid, {})
            print(f"    {n.get('file') or nid}")
    
    if only_in:
        print(f"  ← Inbound only ({len(only_in)}):")
        for nid in sorted(only_in):
            n = graph['nodes'].get(nid, {})
            print(f"    {n.get('file') or nid}")
    
    if only_out:
        print(f"  → Outbound only ({len(only_out)}):")
        for nid in sorted(only_out):
            n = graph['nodes'].get(nid, {})
            print(f"    {n.get('file') or nid}")

def cmd_orphans(graph):
    """Find concept nodes (linked but no file)."""
    orphans = [(nid, n) for nid, n in graph['nodes'].items() if not n.get('file')]
    if not orphans:
        print("✅ No orphan nodes — all links resolve to files")
        return
    
    print(f"👻 Orphan nodes ({len(orphans)}) — linked but no file:\n")
    for nid, node in sorted(orphans, key=lambda x: len(x[1].get('inLinks', [])), reverse=True):
        in_count = len(node.get('inLinks', []))
        print(f"  [[{nid}]] — referenced {in_count}x")

def cmd_deadlinks(graph):
    """Find links pointing to nothing (no file, no other references)."""
    dead = [(nid, n) for nid, n in graph['nodes'].items() 
            if not n.get('file') and len(n.get('inLinks', [])) == 1 and not n.get('outLinks')]
    if not dead:
        print("✅ No dead links")
        return
    
    print(f"💀 Dead links ({len(dead)}) — single reference, no file:\n")
    for nid, node in sorted(dead):
        src = node['inLinks'][0]
        src_node = graph['nodes'].get(src, {})
        print(f"  [[{nid}]] ← {src_node.get('file') or src}")

def cmd_lonely(graph):
    """Find files with no links in or out."""
    lonely = [(nid, n) for nid, n in graph['nodes'].items() 
              if n.get('file') and not n.get('inLinks') and not n.get('outLinks')]
    if not lonely:
        print("✅ All files are connected")
        return
    
    print(f"🏝️  Lonely files ({len(lonely)}) — no links in or out:\n")
    for nid, node in sorted(lonely):
        print(f"  {node['file']}")

def cmd_stats(graph):
    """Show graph statistics."""
    nodes = graph['nodes']
    file_nodes = sum(1 for n in nodes.values() if n.get('file'))
    concept_nodes = sum(1 for n in nodes.values() if not n.get('file'))
    total_links = sum(len(n.get('outLinks', [])) for n in nodes.values())
    
    by_type = defaultdict(int)
    for n in nodes.values():
        by_type[n.get('type', 'unknown')] += 1
    
    most_linked = sorted(nodes.items(), key=lambda x: len(x[1].get('inLinks', [])), reverse=True)[:10]
    most_linking = sorted(nodes.items(), key=lambda x: len(x[1].get('outLinks', [])), reverse=True)[:10]
    
    print(f"📊 MindGraph Stats")
    print(f"   Last indexed: {graph.get('lastIndexed', 'never')}")
    print(f"   Files scanned: {graph.get('fileCount', '?')}")
    print(f"   Total nodes: {len(nodes)} ({file_nodes} files + {concept_nodes} concepts)")
    print(f"   Total links: {total_links}")
    print()
    print(f"   By type:")
    for t, c in sorted(by_type.items()):
        print(f"     {t}: {c}")
    print()
    print(f"   🔥 Most referenced (top 10):")
    for nid, node in most_linked:
        in_count = len(node.get('inLinks', []))
        if in_count == 0:
            break
        label = node.get('file') or nid
        print(f"     [{in_count:3d}←] {label}")
    print()
    print(f"   🔗 Most outgoing links (top 10):")
    for nid, node in most_linking:
        out_count = len(node.get('outLinks', []))
        if out_count == 0:
            break
        label = node.get('file') or nid
        print(f"     [→{out_count:3d}] {label}")

def cmd_tree(graph, name, depth=2, _visited=None, _prefix="", _level=0):
    """Show ASCII tree of connections."""
    if _visited is None:
        _visited = set()
        print(f"🌳 Tree for [[{name}]] (depth {depth}):\n")
    
    node_id = resolve_name(graph, name)
    if node_id in _visited or _level > depth:
        return
    _visited.add(node_id)
    
    node = graph['nodes'].get(node_id)
    if not node:
        return
    
    label = node.get('file') or node_id
    type_icon = {'project': '📁', 'memory': '📝', 'core': '⭐', 'concept': '💡', 'file': '📄'}.get(node.get('type', ''), '📄')
    
    if _level == 0:
        print(f"  {type_icon} {label}")
    else:
        print(f"  {_prefix}{'└── ' if _level > 0 else ''}{type_icon} {label}")
    
    # Show connections
    all_connected = set(node.get('outLinks', [])) | set(node.get('inLinks', []))
    all_connected -= _visited
    
    for i, conn_id in enumerate(sorted(all_connected)):
        is_last = i == len(all_connected) - 1
        new_prefix = _prefix + ("    " if is_last or _level == 0 else "│   ")
        cmd_tree(graph, conn_id, depth, _visited, new_prefix, _level + 1)

MINDSKILLS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'mindskills')

def cmd_skills():
    """List all learned mindskills."""
    if not os.path.exists(MINDSKILLS_DIR):
        print("No mindskills learned yet. Use: mindgraph.py learn <name>")
        return
    
    skills = []
    for d in sorted(os.listdir(MINDSKILLS_DIR)):
        process_file = os.path.join(MINDSKILLS_DIR, d, 'PROCESS.md')
        if os.path.isdir(os.path.join(MINDSKILLS_DIR, d)) and os.path.exists(process_file):
            # Read first line after # heading for description
            with open(process_file, 'r') as f:
                lines = f.readlines()
            desc = ""
            for line in lines:
                line = line.strip()
                if line.startswith('#'):
                    continue
                if line:
                    desc = line[:80]
                    break
            
            # Count results
            results_dir = os.path.join(MINDSKILLS_DIR, d, 'results')
            result_count = 0
            if os.path.exists(results_dir):
                result_count = len([f for f in os.listdir(results_dir) if f.endswith('.md')])
            
            skills.append((d, desc, result_count))
    
    if not skills:
        print("No mindskills learned yet. Use: mindgraph.py learn <name>")
        return
    
    print(f"🧠 Learned MindSkills ({len(skills)}):\n")
    for name, desc, count in skills:
        print(f"  📋 {name} ({count} results)")
        if desc:
            print(f"     {desc}")

def cmd_skill(name):
    """Show a mindskill's process."""
    skill_dir = os.path.join(MINDSKILLS_DIR, name)
    process_file = os.path.join(skill_dir, 'PROCESS.md')
    
    if not os.path.exists(process_file):
        print(f"❌ MindSkill '{name}' not found")
        print(f"   Available: {', '.join(os.listdir(MINDSKILLS_DIR)) if os.path.exists(MINDSKILLS_DIR) else 'none'}")
        return
    
    with open(process_file, 'r') as f:
        print(f.read())

def cmd_results(name):
    """List results for a mindskill."""
    results_dir = os.path.join(MINDSKILLS_DIR, name, 'results')
    
    if not os.path.exists(results_dir):
        print(f"No results for '{name}' yet")
        return
    
    files = sorted([f for f in os.listdir(results_dir) if f.endswith('.md')])
    if not files:
        print(f"No results for '{name}' yet")
        return
    
    print(f"📊 Results for [[{name}]] ({len(files)}):\n")
    for fname in files:
        filepath = os.path.join(results_dir, fname)
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Extract verdict from frontmatter
        verdict = ""
        subject = fname.replace('.md', '')
        if content.startswith('---'):
            end = content.find('---', 3)
            if end != -1:
                fm = content[3:end]
                for line in fm.split('\n'):
                    if line.startswith('verdict:'):
                        verdict = line.split(':', 1)[1].strip()
                    if line.startswith('subject:'):
                        subject = line.split(':', 1)[1].strip()
        
        verdict_str = f" → {verdict}" if verdict else ""
        print(f"  {subject}{verdict_str}")
        print(f"    {filepath}")

def cmd_learn(name):
    """Create a new mindskill directory structure."""
    skill_dir = os.path.join(MINDSKILLS_DIR, name)
    
    if os.path.exists(skill_dir):
        print(f"⚠️  MindSkill '{name}' already exists at {skill_dir}")
        return
    
    os.makedirs(os.path.join(skill_dir, 'results'), exist_ok=True)
    
    process_file = os.path.join(skill_dir, 'PROCESS.md')
    with open(process_file, 'w') as f:
        f.write(f"""# [[{name.replace('-', ' ').title()}]]

<!-- PURPOSE: What this process does and when to use it -->

## Trigger Phrases

- "Run a {name.replace('-', ' ')} on X"
- <!-- Add more trigger phrases -->

## Process

1. **Step 1** — <!-- Description -->
2. **Step 2** — <!-- Description -->
3. **Step 3** — <!-- Description -->
4. **Verdict** — <!-- How to summarize the outcome -->

## Output Format

Each result file should contain:
- Subject and date
- Findings per step
- Verdict/score
- `[[wikilinks]]` to related topics

## Scoring

<!-- Define how to score/rate results, if applicable -->
<!-- e.g., ✅ PASS / ⚠️ WARNING / ❌ FAIL -->
""")
    
    print(f"✅ MindSkill '{name}' created at {skill_dir}")
    print(f"   Edit: {process_file}")
    print(f"   Results will be saved to: {os.path.join(skill_dir, 'results/')}")

def main():
    if len(sys.argv) < 2:
        print("Usage: mindgraph.py <command> [args]")
        print()
        print("Graph Commands:")
        print("  index                  Build/rebuild the graph index")
        print("  backlinks <name>       What links TO this topic?")
        print("  links <name>           What does this topic link TO?")
        print("  query <name>           Full info + context for a topic")
        print("  connections <name>     Bidirectional connections")
        print("  orphans                Concept nodes with no file")
        print("  deadlinks              Single-reference dead links")
        print("  lonely                 Files with no connections")
        print("  stats                  Graph statistics")
        print("  tree <name> [depth]    ASCII tree visualization")
        print()
        print("MindSkill Commands:")
        print("  skills                 List all learned mindskills")
        print("  skill <name>           Show a mindskill's process")
        print("  results <name>         List results for a mindskill")
        print("  learn <name>           Create a new mindskill")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'index':
        build_index()
    elif cmd == 'backlinks' and len(sys.argv) >= 3:
        cmd_backlinks(load_graph(), sys.argv[2])
    elif cmd == 'links' and len(sys.argv) >= 3:
        cmd_links(load_graph(), sys.argv[2])
    elif cmd == 'query' and len(sys.argv) >= 3:
        cmd_query(load_graph(), sys.argv[2])
    elif cmd == 'connections' and len(sys.argv) >= 3:
        cmd_connections(load_graph(), sys.argv[2])
    elif cmd == 'orphans':
        cmd_orphans(load_graph())
    elif cmd == 'deadlinks':
        cmd_deadlinks(load_graph())
    elif cmd == 'lonely':
        cmd_lonely(load_graph())
    elif cmd == 'stats':
        cmd_stats(load_graph())
    elif cmd == 'tree' and len(sys.argv) >= 3:
        depth = int(sys.argv[3]) if len(sys.argv) >= 4 else 2
        cmd_tree(load_graph(), sys.argv[2], depth)
    elif cmd == 'skills':
        cmd_skills()
    elif cmd == 'skill' and len(sys.argv) >= 3:
        cmd_skill(sys.argv[2])
    elif cmd == 'results' and len(sys.argv) >= 3:
        cmd_results(sys.argv[2])
    elif cmd == 'learn' and len(sys.argv) >= 3:
        cmd_learn(sys.argv[2])
    else:
        print(f"Unknown command or missing args: {cmd}")
        sys.exit(1)

if __name__ == '__main__':
    main()
