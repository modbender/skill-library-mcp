#!/usr/bin/env bash
set -euo pipefail

RAG_DIR="/home/Mike/.openclaw/workspace/rag-pinecone-starter"

cd "$RAG_DIR"
source .venv/bin/activate
python ingest.py
