#!/usr/bin/env python3
"""
RAG Document Ingestor - Load workspace files, skills, docs into vector store
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from rag_system import RAGSystem


def read_file_safe(file_path: Path) -> str:
    """Read file with error handling"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"   ⚠️  Error reading: {e}")
        return None


def is_text_file(file_path: Path, max_size_mb: float = 1.0) -> bool:
    """Check if file is text and not too large"""
    # Skip binary files
    if file_path.suffix.lower() in ['.pyc', '.so', '.o', '.a', '.png', '.jpg', '.jpeg', '.gif', '.zip', '.tar', '.gz']:
        return False

    # Check size
    try:
        size_mb = file_path.stat().st_size / (1024 * 1024)
        if size_mb > max_size_mb:
            return False
    except:
        return False

    return True


def chunk_text(text: str, max_chars: int = 4000, overlap: int = 200) -> List[str]:
    """Split text into chunks"""
    chunks = []

    if len(text) <= max_chars:
        return [text]

    # Simple splitting by newline for now (could be improved to split at sentences)
    paragraphs = text.split('\n\n')
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) + 2 <= max_chars:
            current_chunk += para + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para + "\n\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def ingest_workspace(
    workspace_dir: str = None,
    collection_name: str = "openclaw_knowledge",
    file_patterns: List[str] = None
):
    """
    Ingest workspace files into RAG system

    Args:
        workspace_dir: Path to workspace directory
        collection_name: Name of the ChromaDB collection
        file_patterns: List of file patterns to include (default: all)
    """
    if workspace_dir is None:
        workspace_dir = os.path.expanduser("~/.openclaw/workspace")

    workspace_path = Path(workspace_dir)

    if not workspace_path.exists():
        print(f"❌ Workspace not found: {workspace_dir}")
        return

    print(f"🔍 Scanning workspace: {workspace_path}")

    # Default file patterns
    if file_patterns is None:
        file_patterns = [
            "*.md", "*.py", "*.js", "*.ts", "*.json", "*.yaml", "*.yml",
            "*.txt", "*.sh", "*.html", "*.css"
        ]

    # Find all matching files
    all_files = []

    for pattern in file_patterns:
        for file_path in workspace_path.rglob(pattern):
            if is_text_file(file_path):
                all_files.append(file_path)

    if not all_files:
        print(f"⚠️  No files found")
        return

    print(f"✅ Found {len(all_files)} files\n")

    # Initialize RAG
    rag = RAGSystem(collection_name=collection_name)

    total_chunks = 0

    for file_path in all_files[:100]:  # Limit to 100 files for testing
        relative_path = file_path.relative_to(workspace_path)
        print(f"\n📄 {relative_path}")

        # Read file
        content = read_file_safe(file_path)

        if content is None:
            continue

        # Chunk if too large
        if len(content) > 4000:
            text_chunks = chunk_text(content)
            print(f"   Chunks: {len(text_chunks)}")
        else:
            text_chunks = [content]
            print(f"   Size: {len(content)} chars")

        # Add each chunk
        for i, chunk in enumerate(text_chunks):
            metadata = {
                "type": "workspace",
                "source": str(relative_path),
                "file_path": str(file_path),
                "file_size": len(content),
                "chunk_index": i,
                "total_chunks": len(text_chunks),
                "file_extension": file_path.suffix.lower(),
                "ingested_at": datetime.now().isoformat()
            }

            doc_id = rag.add_document(chunk, metadata)
            total_chunks += 1

        print(f"   ✅ Indexed {len(text_chunks)} chunk(s)")

    print(f"\n📊 Summary:")
    print(f"   Files processed: {len([f for f in all_files[:100]])}")
    print(f"   Total chunks indexed: {total_chunks}")

    stats = rag.get_stats()
    print(f"   Total documents in collection: {stats['total_documents']}")


def ingest_skills(
    skills_base_dir: str = None,
    collection_name: str = "openclaw_knowledge"
):
    """
    Ingest all SKILL.md files from skills directory

    Args:
        skills_base_dir: Base directory for skills
        collection_name: Name of the ChromaDB collection
    """
    # Default to OpenClaw skills dir
    if skills_base_dir is None:
        # Check both system and workspace skills
        system_skills = Path("/usr/lib/node_modules/openclaw/skills")
        workspace_skills = Path(os.path.expanduser("~/.openclaw/workspace/skills"))

        skills_dirs = [d for d in [system_skills, workspace_skills] if d.exists()]

        if not skills_dirs:
            print(f"❌ No skills directories found")
            return
    else:
        skills_dirs = [Path(skills_base_dir)]

    print(f"🔍 Scanning for skills...")

    # Find all SKILL.md files
    skill_files = []

    for skills_dir in skills_dirs:
        # Direct SKILL.md files
        for skill_file in skills_dir.rglob("SKILL.md"):
            skill_files.append(skill_file)

    if not skill_files:
        print(f"⚠️  No SKILL.md files found")
        return

    print(f"✅ Found {len(skill_files)} skills\n")

    # Initialize RAG
    rag = RAGSystem(collection_name=collection_name)

    total_chunks = 0

    for skill_file in skill_files:
        # Determine skill name from path
        if skill_file.name == "SKILL.md":
            skill_name = skill_file.parent.name
        else:
            skill_name = skill_file.stem

        print(f"\n📜 {skill_name}")

        content = read_file_safe(skill_file)

        if content is None:
            continue

        # Chunk skill documentation
        chunks = chunk_text(content, max_chars=3000, overlap=100)

        for i, chunk in enumerate(chunks):
            metadata = {
                "type": "skill",
                "source": f"skill:{skill_name}",
                "skill_name": skill_name,
                "file_path": str(skill_file),
                "chunk_index": i,
                "total_chunks": len(chunks),
                "ingested_at": datetime.now().isoformat()
            }

            doc_id = rag.add_document(chunk, metadata)
            total_chunks += 1

        print(f"   ✅ Indexed {len(chunks)} chunk(s)")

    print(f"\n📊 Summary:")
    print(f"   Skills processed: {len(skill_files)}")
    print(f"   Total chunks indexed: {total_chunks}")

    stats = rag.get_stats()
    print(f"   Total documents in collection: {stats['total_documents']}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Ingest files into OpenClaw RAG")
    parser.add_argument("type", choices=["workspace", "skills"], help="What to ingest")
    parser.add_argument("--path", help="Path to workspace or skills directory")
    parser.add_argument("--collection", default="openclaw_knowledge", help="Collection name")

    args = parser.parse_args()

    if args.type == "workspace":
        ingest_workspace(workspace_dir=args.path, collection_name=args.collection)
    elif args.type == "skills":
        ingest_skills(skills_base_dir=args.path, collection_name=args.collection)