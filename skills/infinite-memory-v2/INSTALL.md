# 🦞 OpenClaw Memory Bridge: Setup Guide

This folder contains a standalone integration that brings the Phase 16 **100% Accuracy Memory Engine** into OpenClaw.

## 📦 How to Install

### Method A: Direct Install from URL (Recommended)
Paste this link into your OpenClaw chat:
`https://github.com/mhndayesh/infinite-context-rag/tree/main/openclaw_memory_bridge`

*OpenClaw will automatically download the skill folder into your workspace.*

### Method B: Manual Install
1. **Move this Folder:**
   Copy the `openclaw_memory_bridge` folder into your OpenClaw skills directory:
   `~/.openclaw/workspace/skills/openclaw_memory_bridge`

2. **Install Dependencies:**
   Open a terminal in this folder and run:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the Sidecar API:**
   Run the bridge service:
   ```bash
   python memory_service.py
   ```
   *Note: Keep this terminal open while you use OpenClaw.*

4. **Verify LM Studio:**
   Ensure LM Studio is running on `http://localhost:1234` with at least **16 parallel slots** enabled.

---

## 🛠 Usage in OpenClaw

The agent will automatically recognize these new capabilities:

- **Searching:** "Search the database for the mainframe password." -> Calls `recall_facts`.
- **Storing:** "Memorize this project document: [text content]" -> Calls `memorize_data`.

## 🧠 Why is this better than normal RAG?
- **Hybrid Retrieval:** Uses Vector + BM25 to find data that standard RAG misses.
- **Parallel Extraction:** Uses 16 workers to read your docs in seconds.
- **Direct-Return:** Bypasses LLM hallucinations by returning exact text hits.
