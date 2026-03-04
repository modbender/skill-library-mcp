#!/bin/bash
#
# vectorize.sh - Vectorize research findings into Qdrant
#
# Usage: vectorize.sh <markdown_file> <topic> <sources>
#

set -euo pipefail

# Configuration
QDRANT_URL="${QDRANT_URL:-http://10.0.0.120:6333}"
COLLECTION="web_research"
INGEST_TOOL="/Users/gregborden/.openclaw/workspace/tools/research-ingest.py"

# Arguments
RESEARCH_FILE="${1:-}"
TOPIC="${2:-}"
SOURCES="${3:-}"

if [[ -z "$RESEARCH_FILE" || ! -f "$RESEARCH_FILE" ]]; then
    echo "Error: Research file not found: $RESEARCH_FILE" >&2
    exit 1
fi

if [[ -z "$TOPIC" ]]; then
    echo "Error: Topic required" >&2
    exit 1
fi

# Check for OpenAI API key
OPENAI_API_KEY="${OPENAI_API_KEY:-}"
if [[ -z "$OPENAI_API_KEY" ]]; then
    # Try to load from auth profiles
    AUTH_FILE="$HOME/.openclaw/agents/main/agent/auth-profiles.json"
    if [[ -f "$AUTH_FILE" ]]; then
        OPENAI_API_KEY=$(jq -r '.["openai:default"].apiKey // empty' "$AUTH_FILE" 2>/dev/null || echo "")
    fi
fi

if [[ -z "$OPENAI_API_KEY" ]]; then
    echo "Warning: OPENAI_API_KEY not found. Vectorization requires API key." >&2
    exit 1
fi

export OPENAI_API_KEY

# Check if research-ingest.py exists, create if needed
if [[ ! -f "$INGEST_TOOL" ]]; then
    mkdir -p "$(dirname "$INGEST_TOOL")"
    
    cat > "$INGEST_TOOL" << 'INGEST_EOF'
#!/usr/bin/env python3
"""
research-ingest.py - Ingest research documents into Qdrant vector store
"""

import sys
import os
import re
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any

try:
    import requests
    from openai import OpenAI
except ImportError as e:
    print(f"Error: Required package not installed: {e}")
    sys.exit(1)

QDRANT_URL = os.getenv("QDRANT_URL", "http://10.0.0.120:6333")
COLLECTION = "web_research"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

def get_embedding(text: str, client: OpenAI) -> List[float]:
    """Generate embedding using OpenAI API."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text[:8000]  # Limit input size
    )
    return response.data[0].embedding

def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = min(start + size, text_len)
        # Try to break at sentence or word boundary
        if end < text_len:
            # Look for sentence ending
            sentence_break = text.rfind('. ', start, end)
            if sentence_break > start + size // 2:
                end = sentence_break + 1
            else:
                # Look for word boundary
                word_break = text.rfind(' ', start, end)
                if word_break > start:
                    end = word_break
        
        chunks.append(text[start:end].strip())
        start = end - overlap
    
    return chunks

def extract_urls(text: str) -> List[str]:
    """Extract URLs from markdown text."""
    url_pattern = r'\[([^\]]+)\]\((https?://[^\)]+)\)'
    matches = re.findall(url_pattern, text)
    return [url for _, url in matches]

def extract_metadata(content: str) -> Dict[str, Any]:
    """Extract metadata from research document."""
    metadata = {
        "date": datetime.now().isoformat(),
        "confidence": "Unknown",
        "depth": "standard",
        "source_count": 0
    }
    
    # Extract date
    date_match = re.search(r'\*\*Date:\*\*\s*(\d{4}-\d{2}-\d{2})', content)
    if date_match:
        metadata["date"] = date_match.group(1)
    
    # Extract confidence
    conf_match = re.search(r'\*\*Confidence:\*\*\s*(High|Medium|Low)', content, re.IGNORECASE)
    if conf_match:
        metadata["confidence"] = conf_match.group(1)
    
    # Extract depth
    depth_match = re.search(r'\*\*Depth:\*\*\s*(quick|standard|deep)', content, re.IGNORECASE)
    if depth_match:
        metadata["depth"] = depth_match.group(1).lower()
    
    # Extract source count
    count_match = re.search(r'\*\*Sources:\*\*\s*(\d+)', content)
    if count_match:
        metadata["source_count"] = int(count_match.group(1))
    
    return metadata

def ensure_collection():
    """Ensure web_research collection exists."""
    try:
        # Check if collection exists
        resp = requests.get(f"{QDRANT_URL}/collections/{COLLECTION}")
        if resp.status_code == 200:
            return
        
        # Create collection
        resp = requests.put(
            f"{QDRANT_URL}/collections/{COLLECTION}",
            json={
                "vectors": {
                    "size": 1536,
                    "distance": "Cosine"
                }
            }
        )
        resp.raise_for_status()
        print(f"Created collection: {COLLECTION}")
    except Exception as e:
        print(f"Warning: Could not ensure collection: {e}")

def ingest_document(file_path: str, topic: str, sources_text: str = ""):
    """Ingest a research document into Qdrant."""
    
    client = OpenAI()
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    metadata = extract_metadata(content)
    metadata["topic"] = topic
    metadata["file_path"] = file_path
    
    # Extract source URLs
    source_urls = extract_urls(content)
    if sources_text:
        source_urls.extend(extract_urls(sources_text))
    metadata["source_urls"] = list(set(source_urls))
    
    # Generate document ID
    doc_id = hashlib.sha256(f"{topic}:{metadata['date']}".encode()).hexdigest()[:16]
    
    # Chunk the content
    # Skip frontmatter and metadata sections
    clean_content = re.sub(r'^# Research:.*?(?=\n##)', '', content, flags=re.DOTALL)
    clean_content = re.sub(r'\*\*[^*]+:\*\*[^\n]*\n', '', clean_content)
    
    chunks = chunk_text(clean_content)
    
    print(f"Processing {len(chunks)} chunks for topic: {topic}")
    
    points = []
    for i, chunk in enumerate(chunks):
        if len(chunk.strip()) < 50:
            continue
            
        chunk_id = f"{doc_id}-{i:04d}"
        embedding = get_embedding(chunk, client)
        
        point = {
            "id": chunk_id,
            "vector": embedding,
            "payload": {
                "topic": topic,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "text": chunk[:2000],
                **metadata
            }
        }
        points.append(point)
    
    # Upsert to Qdrant in batches
    batch_size = 50
    for i in range(0, len(points), batch_size):
        batch = points[i:i+batch_size]
        try:
            resp = requests.put(
                f"{QDRANT_URL}/collections/{COLLECTION}/points?wait=true",
                json={"points": batch}
            )
            resp.raise_for_status()
        except Exception as e:
            print(f"Error upserting batch {i}: {e}")
            raise
    
    print(f"Successfully ingested {len(points)} vectors for: {topic}")
    return len(points)

def main():
    if len(sys.argv) < 3:
        print("Usage: research-ingest.py <file_path> <topic> [sources]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    topic = sys.argv[2]
    sources = sys.argv[3] if len(sys.argv) > 3 else ""
    
    ensure_collection()
    count = ingest_document(file_path, topic, sources)
    print(f"Ingested {count} chunks to {COLLECTION}")

if __name__ == "__main__":
    main()
INGEST_EOF

    chmod +x "$INGEST_TOOL"
fi

# Extract category from topic
categorize_topic() {
    local topic="$1"
    topic_lower=$(echo "$topic" | tr '[:upper:]' '[:lower:]')
    
    if [[ "$topic_lower" =~ (software|app|platform|tool|crm|erp|saas) ]]; then
        echo "software"
    elif [[ "$topic_lower" =~ (market|industry|business|economy|finance) ]]; then
        echo "business"
    elif [[ "$topic_lower" =~ (ai|artificial intelligence|machine learning|ml|automation|robotics) ]]; then
        echo "ai"
    elif [[ "$topic_lower" =~ (tech|technology|computer|digital|internet) ]]; then
        echo "technology"
    elif [[ "$topic_lower" =~ (health|medical|healthcare|medicine|clinical) ]]; then
        echo "healthcare"
    elif [[ "$topic_lower" =~ (science|research|study|academic) ]]; then
        echo "science"
    else
        echo "general"
    fi
}

CATEGORY=$(categorize_topic "$TOPIC")

# Run the ingest tool
if python3 "$INGEST_TOOL" "$RESEARCH_FILE" "$TOPIC" "$SOURCES"; then
    echo "Research vectorized successfully in category: $CATEGORY"
    exit 0
else
    echo "Error: Vectorization failed" >&2
    exit 1
fi
