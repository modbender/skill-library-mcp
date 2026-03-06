#!/usr/bin/env python3
"""
RAG Session Ingestor - Load all session transcripts into vector store
Fixed to handle OpenClaw session event format
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

import sys
sys.path.insert(0, str(Path(__file__).parent))

from rag_system import RAGSystem


def parse_jsonl(file_path: Path) -> List[Dict]:
    """
    Parse OpenClaw session JSONL format

    Session files contain:
    - Line 1: Session metadata (type: "session")
    - Lines 2+: Events including messages, toolCalls, etc.
    """
    messages = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    event = json.loads(line)

                    # Skip session metadata line
                    if line_num == 1 and event.get('type') == 'session':
                        continue

                    # Extract message events only
                    if event.get('type') == 'message':
                        msg_obj = event.get('message', {})

                        messages.append({
                            'role': msg_obj.get('role'),
                            'content': msg_obj.get('content'),
                            'timestamp': event.get('timestamp'),
                            'id': event.get('id'),
                            'sessionKey': event.get('sessionKey')  # Not usually here, but check
                        })

                except json.JSONDecodeError as e:
                    continue
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")

    return messages


def extract_session_key(file_name: str) -> str:
    """Extract session key from filename"""
    return file_name.replace('.jsonl', '')


def extract_session_metadata(session_data: List[Dict], session_key: str) -> Dict:
    """Extract metadata from session messages"""
    if not session_data:
        return {}

    first_msg = session_data[0]
    last_msg = session_data[-1]

    return {
        "start_time": first_msg.get("timestamp"),
        "end_time": last_msg.get("timestamp"),
        "total_messages": len(session_data),
        "has_system": any(msg.get("role") == "system" for msg in session_data),
        "has_user": any(msg.get("role") == "user" for msg in session_data),
        "has_assistant": any(msg.get("role") == "assistant" for msg in session_data),
    }


def format_content(content) -> str:
    """
    Format message content from OpenClaw format to text

    Content can be:
    - String
    - List of dicts with 'type' field (text, thinking, toolCall, toolResult)
    """
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        texts = []

        for item in content:
            if not isinstance(item, dict):
                continue

            item_type = item.get('type', '')

            if item_type == 'text':
                texts.append(item.get('text', ''))
            elif item_type == 'thinking':
                # Skip reasoning, usually not useful for RAG
                # texts.append(f"[Reasoning: {item.get('thinking', '')[:200]}]")
                pass
            elif item_type == 'toolCall':
                tool_name = item.get('name', 'unknown')
                args = str(item.get('arguments', ''))[:100]
                texts.append(f"[Tool: {tool_name}({args})]")
            elif item_type == 'toolResult':
                result = str(item.get('text', item.get('result', ''))).strip()
                # Truncate large tool results
                if len(result) > 500:
                    result = result[:500] + "..."
                texts.append(f"[Tool Result: {result}]")

        return "\n".join(texts)

    return str(content)[:500]


def chunk_messages(
    messages: List[Dict],
    context_window: int = 20,
    overlap: int = 5
) -> List[Dict]:
    """
    Chunk messages for better retrieval

    Args:
        messages: List of message objects
        context_window: Messages per chunk
        overlap: Message overlap between chunks

    Returns:
        List of {"text": str, "metadata": dict} chunks
    """
    chunks = []

    for i in range(0, len(messages), context_window - overlap):
        chunk_messages = messages[i:i + context_window]

        # Build text from messages
        text_parts = []

        for msg in chunk_messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")

            # Format content
            text = format_content(content)

            if text.strip():
                text_parts.append(f"{role.upper()}: {text}")

        text = "\n\n".join(text_parts)

        # Don't add empty chunks
        if not text.strip():
            continue

        # Metadata
        metadata = {
            "type": "session",
            "source": str(chunk_messages[0].get("sessionKey") or chunk_messages[0].get("id") or session_key),
            "chunk_index": int(i // (context_window - overlap)),
            "chunk_start_time": str(chunk_messages[0].get("timestamp") or ""),
            "chunk_end_time": str(chunk_messages[-1].get("timestamp") or ""),
            "message_count": int(len(chunk_messages)),
            "ingested_at": datetime.now().isoformat(),
            "date": str(chunk_messages[0].get("timestamp") or datetime.now().isoformat())
        }

        chunks.append({
            "text": text,
            "metadata": metadata
        })

    return chunks


def ingest_sessions(
    sessions_dir: str = None,
    collection_name: str = "openclaw_knowledge",
    chunk_size: int = 20,
    chunk_overlap: int = 5
):
    """
    Ingest all session transcripts into RAG system

    Args:
        sessions_dir: Directory containing session jsonl files
        collection_name: Name of the ChromaDB collection
        chunk_size: Messages per chunk
        chunk_overlap: Message overlap between chunks
    """
    if sessions_dir is None:
        sessions_dir = os.path.expanduser("~/.openclaw/agents/main/sessions")

    sessions_path = Path(sessions_dir)

    if not sessions_path.exists():
        print(f"❌ Sessions directory not found: {sessions_path}")
        return

    print(f"🔍 Finding session files in: {sessions_path}")

    jsonl_files = list(sessions_path.glob("*.jsonl"))

    if not jsonl_files:
        print(f"⚠️  No jsonl files found in {sessions_path}")
        return

    print(f"✅ Found {len(jsonl_files)} session files\n")

    rag = RAGSystem(collection_name=collection_name)

    total_chunks = 0
    total_messages = 0
    skipped_empty = 0

    for jsonl_file in sorted(jsonl_files):
        session_key = extract_session_key(jsonl_file.name)

        print(f"\n📄 Processing: {jsonl_file.name}")

        messages = parse_jsonl(jsonl_file)

        if not messages:
            print(f"   ⚠️  No messages, skipping")
            skipped_empty += 1
            continue

        total_messages += len(messages)

        # Extract session metadata
        session_metadata = extract_session_metadata(messages, session_key)
        print(f"   Messages: {len(messages)}")

        # Chunk messages
        chunks = chunk_messages(messages, chunk_size, chunk_overlap)

        if not chunks:
            print(f"   ⚠️  No valid chunks, skipping")
            skipped_empty += 1
            continue

        print(f"   Chunks: {len(chunks)}")

        # Add to RAG
        try:
            ids = rag.add_documents_batch(chunks, batch_size=50)
            total_chunks += len(chunks)
            print(f"   ✅ Indexed {len(chunks)} chunks")
        except Exception as e:
            print(f"   ❌ Error: {e}")

    # Summary
    print(f"\n📊 Summary:")
    print(f"   Sessions processed: {len(jsonl_files)}")
    print(f"   Skipped (empty): {skipped_empty}")
    print(f"   Total messages: {total_messages}")
    print(f"   Total chunks indexed: {total_chunks}")

    stats = rag.get_stats()
    print(f"   Total documents in collection: {stats['total_documents']}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Ingest OpenClaw session transcripts into RAG")
    parser.add_argument("--sessions-dir", help="Path to sessions directory (default: ~/.openclaw/agents/main/sessions)")
    parser.add_argument("--chunk-size", type=int, default=20, help="Messages per chunk (default: 20)")
    parser.add_argument("--chunk-overlap", type=int, default=5, help="Message overlap (default: 5)")

    args = parser.parse_args()

    ingest_sessions(
        sessions_dir=args.sessions_dir,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap
    )