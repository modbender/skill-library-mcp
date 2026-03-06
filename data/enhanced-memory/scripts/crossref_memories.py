#!/usr/bin/env python3
"""Build cross-reference network between memory chunks.

Finds semantically related chunks across different files using embedding similarity.
Uses file-representative approach to reduce O(n²) comparisons.

Usage:
    python3 crossref_memories.py build          # Build cross-reference index
    python3 crossref_memories.py show <file>    # Show references for a file
    python3 crossref_memories.py graph          # Print graph statistics

Environment variables:
    MEMORY_DIR - Override memory directory path
"""

import json, math, os, sys
from collections import defaultdict
from pathlib import Path

MEMORY_DIR = Path(os.environ.get('MEMORY_DIR', Path(__file__).resolve().parent.parent.parent.parent / 'memory'))
VECTORS_FILE = MEMORY_DIR / 'vectors.json'
CROSSREF_FILE = MEMORY_DIR / 'crossrefs.json'

SIMILARITY_THRESHOLD = 0.75
MAX_REPS_PER_FILE = 5
MAX_REFS_PER_CHUNK = 5


def load_vectors():
    with open(VECTORS_FILE) as f:
        return [c for c in json.load(f) if 'embedding' in c]


def cosine_sim(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb) if na and nb else 0.0


def build_crossrefs():
    """Build cross-reference index between chunks in different files."""
    chunks = load_vectors()
    print(f'Loaded {len(chunks)} chunks')

    by_file = defaultdict(list)
    for i, c in enumerate(chunks):
        by_file[c['file']].append(i)

    files = list(by_file.keys())
    print(f'Files: {len(files)}')

    # Pick representative chunks per file (longest text)
    reps = {}
    for f, indices in by_file.items():
        sorted_idx = sorted(indices, key=lambda i: -len(chunks[i].get('text', '')))
        reps[f] = sorted_idx[:MAX_REPS_PER_FILE]

    crossrefs = {}
    file_links = defaultdict(lambda: defaultdict(float))
    comparisons = 0

    for fi, file_a in enumerate(files):
        for idx_a in reps[file_a]:
            ca = chunks[idx_a]
            key_a = f'{ca["file"]}:{ca.get("line", 0)}'
            refs = []
            for file_b in files:
                if file_b == file_a:
                    continue
                for idx_b in reps[file_b]:
                    cb = chunks[idx_b]
                    sim = cosine_sim(ca['embedding'], cb['embedding'])
                    comparisons += 1
                    if sim >= SIMILARITY_THRESHOLD:
                        refs.append((f'{cb["file"]}:{cb.get("line", 0)}', sim, cb.get('header', ''), cb['file']))
                        file_links[file_a][file_b] = max(file_links[file_a][file_b], sim)
            refs.sort(key=lambda x: -x[1])
            if refs:
                crossrefs[key_a] = [{'target': r[0], 'sim': round(r[1], 3),
                                      'header': r[2], 'file': r[3]} for r in refs[:MAX_REFS_PER_CHUNK]]
        if (fi + 1) % 20 == 0:
            print(f'  Processed {fi + 1}/{len(files)} files...')

    file_graph = {}
    for fa, links in file_links.items():
        top = sorted(links.items(), key=lambda x: -x[1])[:10]
        file_graph[fa] = [{'file': fb, 'strength': round(s, 3)} for fb, s in top if s >= SIMILARITY_THRESHOLD]

    result = {
        'total_chunks': len(chunks),
        'total_crossrefs': sum(len(v) for v in crossrefs.values()),
        'chunks_with_refs': len(crossrefs),
        'chunk_refs': crossrefs,
        'file_graph': file_graph,
    }

    with open(CROSSREF_FILE, 'w') as f:
        json.dump(result, f, indent=2)

    print(f'\nCross-reference index built:')
    print(f'  Chunks with refs: {len(crossrefs)} / {len(chunks)}')
    print(f'  Total cross-refs: {result["total_crossrefs"]}')
    print(f'  Files in graph: {len(file_graph)}')
    print(f'  Comparisons: {comparisons:,}')


def show_file_refs(target):
    with open(CROSSREF_FILE) as f:
        data = json.load(f)

    print(f'\n=== Cross-references for: {target} ===\n')
    fg = data.get('file_graph', {})
    if target in fg:
        print('File-level connections:')
        for l in fg[target]:
            print(f'  → {l["file"]} (strength: {l["strength"]})')

    print(f'\nChunk-level references:')
    for key, refs in data.get('chunk_refs', {}).items():
        if key.startswith(target + ':'):
            print(f'\n  {key}:')
            for r in refs:
                print(f'    → {r["target"]} [{r["header"]}] (sim: {r["sim"]})')

    print(f'\nIncoming references:')
    count = 0
    for key, refs in data.get('chunk_refs', {}).items():
        for r in refs:
            if r['file'] == target:
                print(f'  ← {key} [{r["header"]}] (sim: {r["sim"]})')
                count += 1
                if count >= 20:
                    break
        if count >= 20:
            break


def show_graph_stats():
    with open(CROSSREF_FILE) as f:
        data = json.load(f)
    print(f'Total chunks: {data["total_chunks"]}')
    print(f'Chunks with refs: {data["chunks_with_refs"]}')
    print(f'Total cross-refs: {data["total_crossrefs"]}')
    fg = data.get('file_graph', {})
    print(f'\nFile graph ({len(fg)} files):')
    for f_name, links in sorted(fg.items(), key=lambda x: -len(x[1]))[:15]:
        avg = sum(l['strength'] for l in links) / len(links) if links else 0
        print(f'  {f_name[:40]:<42} {len(links):>3} connections (avg: {avg:.3f})')


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == 'build':
        build_crossrefs()
    elif cmd == 'show' and len(sys.argv) >= 3:
        show_file_refs(sys.argv[2])
    elif cmd == 'graph':
        show_graph_stats()
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
