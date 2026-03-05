#!/bin/bash
# RAG Agent Launcher - Spawns an agent with automatic knowledge base access
#
# This spawns a sub-agent that has RAG automatically integrated
# The agent will query your knowledge base before responding to questions

# Dynamic path resolution for portability
RAG_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SESSION_SPAWN_COMMAND='python3 -c "
import sys
import os
sys.path.insert(0, os.path.expanduser(\"~/.openclaw/workspace/rag\"))

# Add RAG context to system prompt
ORIGINAL_TASK=\"$@\"

# Search for relevant context
from rag_system import RAGSystem
rag = RAGSystem()

# Find similar past conversations
results = rag.search(ORIGINAL_TASK, n_results=3)

if results:
    context = \"\\n=== RELEVANT CONTEXT FROM KNOWLEDGE BASE ===\\n\"
    for i, r in enumerate(results, 1):
        meta = r.get(\"metadata\", {})
        text = r.get(\"text\", \"\")[:500]
        doc_type = meta.get(\"type\", \"unknown\")
        source = meta.get(\"source\", \"unknown\")
        context += f\"\\n[{doc_type.upper()} - {source}]\\n{text}\\n\"
else:
    context = \"\"

# Respond with context-aware task
print(f\"\"\"{context}

=== CURRENT TASK ===
{ORIGINAL_TASK}

Use the context above if relevant to help answer the question.\"

\"\")"

# Spawn the agent with RAG context
# Use 'openclaw' from PATH if available, fallback to local installation
if command -v openclaw >/dev/null 2>&1; then
    openclaw sessions spawn "$SESSION_SPAWN_COMMAND"
elif [ -f "$HOME/.local/bin/openclaw" ]; then
    "$HOME/.local/bin/openclaw" sessions spawn "$SESSION_SPAWN_COMMAND"
else
    echo "Error: openclaw command not found in PATH or ~/.local/bin/" >&2
    exit 1
fi