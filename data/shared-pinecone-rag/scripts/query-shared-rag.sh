#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo 'Usage: query-shared-rag.sh "your question"' >&2
  exit 1
fi

RAG_DIR="/home/Mike/.openclaw/workspace/rag-pinecone-starter"
QUESTION="$*"

cd "$RAG_DIR"
source .venv/bin/activate
python query.py "$QUESTION"
