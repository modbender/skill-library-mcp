#!/usr/bin/env bash
set -u

WORKSPACE="/home/Mike/.openclaw/workspace"
PULSE_DIR="$WORKSPACE/agents/pulse"
RAG_DIR="$WORKSPACE/rag-pinecone-starter"

pulse_status="FAIL"
pulse_detail="check not run"
rag_status="FAIL"
rag_detail="check not run"

# Pulse DB check
if [ -d "$PULSE_DIR" ]; then
  if output=$(cd "$PULSE_DIR" && python3 openclaw_sync.py --check 2>&1); then
    if echo "$output" | grep -qi "connection ok\|database connection ok"; then
      pulse_status="PASS"
      pulse_detail="Database connection OK"
    else
      pulse_status="WARN"
      pulse_detail="$output"
    fi
  else
    pulse_status="FAIL"
    pulse_detail="$output"
  fi
else
  pulse_status="FAIL"
  pulse_detail="Missing directory: $PULSE_DIR"
fi

# RAG/Pinecone check
if [ -d "$RAG_DIR" ]; then
  env_file="$RAG_DIR/.env"
  if [ ! -f "$env_file" ]; then
    rag_status="WARN"
    rag_detail="Missing .env file"
  else
    openai_key=$(grep -E '^OPENAI_API_KEY=' "$env_file" | head -n1 | cut -d= -f2-)
    pinecone_key=$(grep -E '^PINECONE_API_KEY=' "$env_file" | head -n1 | cut -d= -f2-)

    if [ -z "$openai_key" ] || [ -z "$pinecone_key" ]; then
      rag_status="WARN"
      rag_detail="Missing OPENAI_API_KEY or PINECONE_API_KEY in .env"
    else
      if [ -f "$RAG_DIR/.venv/bin/activate" ]; then
        if output=$(cd "$RAG_DIR" && source .venv/bin/activate && python query.py "connectivity test" 2>&1); then
          rag_status="PASS"
          rag_detail="Query executed successfully"
        else
          rag_status="FAIL"
          rag_detail="$output"
        fi
      else
        rag_status="WARN"
        rag_detail=".venv not found; keys present but live query not executed"
      fi
    fi
  fi
else
  rag_status="FAIL"
  rag_detail="Missing directory: $RAG_DIR"
fi

echo "Pulse DB: $pulse_status"
echo "Pulse Detail: $pulse_detail"
echo "RAG Pinecone: $rag_status"
echo "RAG Detail: $rag_detail"
