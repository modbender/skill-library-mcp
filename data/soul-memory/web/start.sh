#!/bin/bash
# Soul Memory Web UI - Start Script

cd "$(dirname "$0")"

echo "🧠 Starting Soul Memory Web UI..."
echo "📦 Installing dependencies..."
pip3 install -q fastapi uvicorn jinja2 2>/dev/null || python3 -m pip install -q fastapi uvicorn jinja2

echo "🚀 Starting server on http://localhost:8000"
python3 -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
