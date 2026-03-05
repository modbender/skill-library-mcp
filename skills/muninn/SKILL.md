---
name: muninn
version: 2.3.7
homepage: https://www.muninn.space
description: Universal Context Protocol (CXP) for AI agents. v2.3.7 includes the latest high-performance CXP engine (compiled 2026-02-13) with fix for memory amnesia, macOS binary support, and pfeilschnell indexing. Created by @Blackknight1dev.
metadata: {"clawdbot":{"emoji":"🐦⬛","requires":{"bins":["node"]},"install":[{"id":"npm","kind":"node","package":"muninn-core","version":"2.3.7","bins":["muninn-core"],"label":"Install Muninn Core"}]}}
---

# Muninn - The Universal Memory Layer

Muninn is an advanced per-project memory system designed for AI agents. It uses the **Context Exchange Protocol (CXP)** to provide high-performance, token-efficient context management.

## 🛡️ Security & Privacy (Local-First)

Muninn is designed with a **Privacy-First** philosophy. 
- **Local Storage**: All project indexes and memories are stored **exclusively on the host machine** within the `.muninn/` folder (per project) or `~/.muninn/` (for global settings).
- **No Data Exfiltration**: Muninn **does not transmit** any code, context, or memories to third-party servers or remote APIs. All processing (semantic search, indexing, and context injection) happens locally using the high-performance Rust-based CXP engine.
- **Transparent Control**: Memories are stored as standard Markdown files. You can inspect, edit, or delete them at any time.

## ⚙️ Integration

Muninn operates as an MCP (Model Context Protocol) server. 

### 🚀 The Muninn Protocol (ENFORCED)

As an agent, you MUST follow the "Brain-First" workflow to remain efficient and accurate. The MCP server ensures project safety by validating context before allowing sensitive tool operations.

1.  **Orient Yourself (`brain_check`)**: Call this at the start of every session or when switching projects. It loads the local project index and identifies key files and patterns.
2.  **Search Before You Code (`search_context`)**: Never assume you know the codebase. Use local semantic search to find existing patterns or prior decisions.
3.  **Learn as You Go (`add_memory`)**: Every significant fix, architectural decision, or user preference should be saved locally as a memory.

## 🛠 Tool Reference (MCP)

- **`init_project`**: Initialize a local Muninn Brain in a project directory.
- **`brain_check`**: MANDATORY orientation step. Loads local context and patterns.
- **`add_memory`**: Persist facts and decisions to the local `.muninn/memories` folder.
- **`search_context`**: Query the local project index semantically.
- **`reindex_context`**: Rebuild the local semantic index.
- **`health_check`**: Verify the status of the local Muninn system.

---

## 🦞 Pro-Tip for Agents
Muninn surgically retrieves only what's needed. Instead of reading large files, use `search_context` to find the exact lines that matter. This significantly reduces context window overhead and token costs while keeping your work strictly local and secure.
