---
name: knowledge-vault
description: Long-term RAG memory storage for your agent, powered by TiDB Vector.
metadata:
  openclaw:
    emoji: 📚
    requires:
      bins: ["python3", "curl"]
      env: ["TIDB_HOST", "TIDB_PORT", "TIDB_USER", "TIDB_PASSWORD", "GEMINI_API_KEY"]
---

# Knowledge Vault (Powered by TiDB Zero)

## Overview
**Knowledge Vault** is a Long-Term Memory module for AI Agents, powered by **TiDB Vector Search (RAG)**.

Traditional agent memory (context window) is ephemeral and limited. Knowledge Vault allows agents to:
1.  **Store:** Ingest documents, notes, and facts as vector embeddings.
2.  **Retrieve:** Semantically search for relevant information based on user queries ("RAG").
3.  **Remember:** Access unlimited historical context without overflowing the LLM prompt.

## Why use this?
*   **Infinite Recall:** Store millions of documents without confusing the agent.
*   **Contextual Relevance:** Find *exact* paragraphs related to a question, not just keywords.
*   **Privacy:** Keep your knowledge base private in your own TiDB Cloud instance.

## Prerequisites
*   **TiDB Cloud (Serverless):** With Vector Search enabled.
*   **Embedding Model:** Requires `GEMINI_API_KEY` (or compatible).

### 🔐 Security & Provisioning
This skill operates in two modes:
1.  **Bring Your Own Database (Recommended):** Set `TIDB_HOST`, `TIDB_USER`, `TIDB_PASSWORD` environment variables. The skill will use your existing database.
2.  **Auto-Provisioning (Fallback):** If no credentials are found, the skill calls the **TiDB Zero API** to create a temporary, ephemeral database for you. It caches the connection string locally (`~/.openclaw_knowledge_vault_dsn`) to persist memory across runs.

## Installation

### 1. Add to `TOOLS.md`
```markdown
- **knowledge-vault**: Store and retrieve knowledge using vector search.
  - **Location:** `{baseDir}/skills/knowledge_vault/SKILL.md`
  - **Command:** `python {baseDir}/skills/knowledge_vault/run.py --action search --query "<QUESTION>"`
```

### 2. Add to `AGENTS.md` (Protocol)
Copy [PROTOCOL.md](PROTOCOL.md).

## Usage
*   **Add Knowledge:**
    ```bash
    python {baseDir}/run.py --action add --content "The user prefers spicy food but is allergic to peanuts."
    ```
*   **Search (RAG):**
    ```bash
    python {baseDir}/run.py --action search --query "What are the user's dietary restrictions?"
    ```
