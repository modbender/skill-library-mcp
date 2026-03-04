#!/bin/bash
# AgxntSix Brain Setup — Full Intelligence Layer
# Run after container rebuild to install all Python dependencies

set -e

VENV_PATH="$HOME/.openclaw/workspace/.venv"

echo "=== Creating Python venv ==="
python3 -m venv "$VENV_PATH"
source "$VENV_PATH/bin/activate"

echo "=== Upgrading pip ==="
pip install --upgrade pip

echo "=== Installing Mem0 (unified memory engine + graph extras) ==="
pip install "mem0ai[graph]"

echo "=== Installing Qdrant client ==="
pip install qdrant-client

echo "=== Installing document processing ==="
pip install pdfplumber beautifulsoup4

echo "=== Installing data & research tools ==="
pip install pandas requests

echo "=== Verifying installations ==="
python3 -c "from mem0 import Memory; print('Mem0 OK')"
python3 -c "from qdrant_client import QdrantClient; print('Qdrant client OK')"
python3 -c "from neo4j import GraphDatabase; print('Neo4j client OK')"
python3 -c "import pdfplumber; print('pdfplumber OK')"
python3 -c "import sqlite3; print('sqlite3 OK')"
python3 -c "import pandas; print(f'pandas {pandas.__version__}')"

echo ""
echo "=== Brain setup complete ==="
echo "Activate with: source ~/.openclaw/workspace/.venv/bin/activate"
