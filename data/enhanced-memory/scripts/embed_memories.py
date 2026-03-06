#!/usr/bin/env python3
"""Embed memory files into vectors for semantic search.

Chunks markdown files by headers and embeds each chunk via Ollama.
Outputs memory/vectors.json.

Usage:
    python3 embed_memories.py [memory_dir]

Environment variables:
    MEMORY_DIR    - Override memory directory path
    OLLAMA_URL    - Override Ollama API URL (default: http://localhost:11434/api/embed)
    EMBED_MODEL   - Override embedding model (default: nomic-embed-text)
"""

import json, os, re, sys, urllib.request

MEMORY_DIR = os.environ.get('MEMORY_DIR', os.path.join(os.path.dirname(__file__), '..', '..', '..', 'memory'))
VECTORS_FILE = os.path.join(MEMORY_DIR, 'vectors.json')
OLLAMA_URL = os.environ.get('OLLAMA_URL', 'http://localhost:11434/api/embed')
MODEL = os.environ.get('EMBED_MODEL', 'nomic-embed-text')

# Core workspace files to also index (relative to workspace root)
CORE_FILES = ['MEMORY.md', 'AGENTS.md', 'USER.md', 'SOUL.md', 'research.md']


def get_md_files(memory_dir):
    """Collect all .md files from memory directory and core workspace files."""
    files = []
    for root, _, fnames in os.walk(memory_dir):
        for f in fnames:
            if f.endswith('.md'):
                files.append(os.path.join(root, f))

    workspace = os.path.abspath(os.path.join(memory_dir, '..'))
    for name in CORE_FILES:
        path = os.path.join(workspace, name)
        if os.path.exists(path):
            files.append(os.path.abspath(path))
    return files


def split_into_chunks(filepath, workspace_root):
    """Split a markdown file into chunks by headers."""
    with open(filepath) as f:
        content = f.read()

    chunks = []
    header = os.path.basename(filepath)
    lines = []
    start = 1

    for i, line in enumerate(content.split('\n'), 1):
        if re.match(r'^#{1,4}\s', line):
            if lines:
                text = '\n'.join(lines).strip()
                if text and len(text) > 20:
                    chunks.append({
                        'file': os.path.relpath(filepath, workspace_root),
                        'header': header,
                        'line': start,
                        'text': text,
                    })
            header = line.lstrip('#').strip()
            lines = [line]
            start = i
        else:
            lines.append(line)

    if lines:
        text = '\n'.join(lines).strip()
        if text and len(text) > 20:
            chunks.append({
                'file': os.path.relpath(filepath, workspace_root),
                'header': header,
                'line': start,
                'text': text,
            })
    return chunks


def embed_batch(texts):
    """Get embeddings for a batch of texts from Ollama."""
    data = json.dumps({'model': MODEL, 'input': texts}).encode()
    req = urllib.request.Request(OLLAMA_URL, data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())['embeddings']


def main():
    memory_dir = sys.argv[1] if len(sys.argv) > 1 else MEMORY_DIR
    memory_dir = os.path.abspath(memory_dir)
    workspace_root = os.path.abspath(os.path.join(memory_dir, '..'))

    files = get_md_files(memory_dir)
    all_chunks = []
    for f in files:
        all_chunks.extend(split_into_chunks(f, workspace_root))

    if not all_chunks:
        print('No chunks found.')
        return

    print(f'Embedding {len(all_chunks)} chunks from {len(files)} files...')

    for i in range(0, len(all_chunks), 20):
        batch = all_chunks[i:i + 20]
        texts = [c['text'][:2000] for c in batch]
        vectors = embed_batch(texts)
        for chunk, vec in zip(batch, vectors):
            chunk['embedding'] = vec
        done = min(i + 20, len(all_chunks))
        print(f'  {done}/{len(all_chunks)} chunks embedded')

    vectors_path = os.path.join(memory_dir, 'vectors.json')
    with open(vectors_path, 'w') as f:
        json.dump(all_chunks, f, indent=None)

    print(f'Saved {len(all_chunks)} vectors to {vectors_path}')


if __name__ == '__main__':
    main()
