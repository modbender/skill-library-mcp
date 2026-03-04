"""
Persistent Memory Indexer
Parses MEMORY.md, reference/*.md, and memory/*.md into ChromaDB vectors + NetworkX knowledge graph.
"""
import os
import re
import glob
import chromadb
from sentence_transformers import SentenceTransformer
from graph import MemoryGraph

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
VECTOR_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chroma_db")
COLLECTION_NAME = "memory_chunks"

# Directories to index (relative to workspace root)
INDEX_DIRS = ["reference", "memory"]
INDEX_FILES = ["MEMORY.md"]


def parse_markdown(file_path, base_dir):
    """Parse a markdown file into chunks based on headers (## or #)."""
    if not os.path.exists(file_path):
        return []

    source = os.path.relpath(file_path, base_dir)

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    chunks = []
    sections = re.split(r'(^##?\s+.*$)', content, flags=re.MULTILINE)

    current_header = "Intro"
    current_content = sections[0].strip()
    if current_content:
        chunks.append({
            'content': current_content,
            'metadata': {'source': source, 'section': current_header}
        })

    for i in range(1, len(sections), 2):
        header = sections[i].strip().replace('#', '').strip()
        content = sections[i + 1].strip() if i + 1 < len(sections) else ""
        if content:
            chunks.append({
                'content': content,
                'metadata': {'source': source, 'section': header}
            })

    return chunks


def gather_all_files(workspace_dir):
    """Collect all indexable markdown files from workspace."""
    files = []
    for f in INDEX_FILES:
        path = os.path.join(workspace_dir, f)
        if os.path.exists(path):
            files.append(path)
    for d in INDEX_DIRS:
        dirpath = os.path.join(workspace_dir, d)
        for f in sorted(glob.glob(os.path.join(dirpath, "*.md"))):
            files.append(f)
    return files


def index_memory():
    # Resolve workspace directory (parent of vector_memory/)
    workspace_dir = BASE_DIR

    print("🧠 Loading Sentence Transformer...")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    print("📂 Connecting to ChromaDB...")
    client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    print("📄 Parsing all knowledge files...")
    all_files = gather_all_files(workspace_dir)
    chunks = []
    for f in all_files:
        file_chunks = parse_markdown(f, workspace_dir)
        print(f"   📄 {os.path.relpath(f, workspace_dir)}: {len(file_chunks)} chunks")
        chunks.extend(file_chunks)

    if not chunks:
        print("⚠️ No content found")
        return

    # Update knowledge graph
    print("🕸️  Updating Knowledge Graph...")
    graph = MemoryGraph()
    graph.build_from_chunks(chunks)

    ids = [f"mem_{i}" for i in range(len(chunks))]
    documents = [c['content'] for c in chunks]
    metadatas = [c['metadata'] for c in chunks]

    print(f"🔢 Generating embeddings for {len(chunks)} chunks...")
    embeddings = model.encode(documents).tolist()

    print("💾 Storing in Vector DB (upsert)...")
    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )

    # Clean up orphaned entries
    existing = collection.count()
    if existing > len(chunks):
        orphan_ids = [f"mem_{i}" for i in range(len(chunks), existing)]
        if orphan_ids:
            collection.delete(ids=orphan_ids)
            print(f"🧹 Cleaned {len(orphan_ids)} orphaned entries.")

    print("✅ Indexing Complete!")


if __name__ == "__main__":
    index_memory()
