---
name: tricore
version: "1.0.0"
description: TriCore Architecture - A deterministic (Code-First) three-layer memory and cognitive framework designed for low-resource servers/Agents. It includes the underlying memctl engine, system policy constraints (Linter), and a fully refactored suite of cognitive tools for planning (Planning), reasoning (ReAct), and self-evolution (Self-Evolution).
author: Berton Han
repository: https://github.com/bertonhan/tricore
allowed-tools:
  - default_api:exec
  - memory_search
  - memory_get
---

# 🤖 Agent Usage Guide (Read First)

**If you are the current AI Agent and have just been asked to load, use, or analyze this skill:**
1. This is your fundamental operating system law. Your memory and state have been completely constrained under the TriCore architecture. You are **STRICTLY FORBIDDEN** from arbitrarily creating independent text files like `task_plan.md` or `findings.md` in the root directory!
2. Your memory write operations must and can only be proxied by the command-line `python3 tools/memctl.py (capture/work_upsert/kb_append)`. When reading history, you **MUST** use the native semantic retrieval tool `memory_search` to fetch fragments.
3. Please use this manual as your base operating instructions. If instructed to configure Cron or write system automation scripts, you must call `memctl.py lint` to test the scheme's legality after writing the commands.

---

# TriCore Architecture

> **The underlying infrastructure of "storage and computation decoupling" built for true autonomous Agents.**

Traditional Agent skills often carry their own "memory baggage" (such as generating `task_plan.md`, `reflection.md`, or scattered learning notes in the project root), leading to context silos and storage chaos.

**TriCore** abandons the paradigm of arbitrarily reading and writing text based on LLMs, and instead adopts a **Code-First** deterministic state machine:
1. **Unified Engine**: All memory additions, deletions, modifications, and queries must be routed through `tools/memctl.py`.
2. **Three-Layer Storage**:
   - **Brief (Layer 1)**: `MEMORY.md` (System-level micro-profile, storing only pointers and laws)
   - **Living (Layer 2)**: `memory/state/WORKING.md` (Currently running task streams/lifecycle tracking)
   - **Stable/Volatile (Layer 3)**: `memory/kb/*.md` (Accumulated knowledge base) & `memory/daily/*.md` (Temporary logs)
3. **Retrieval First**: It is forbidden to directly pour huge files using the `read` tool; you must use semantic retrieval `memory_search` to fetch code snippets, greatly saving Tokens and protecting low-resource environments.
4. **Hard Constraints (Linting)**: Features a native `memctl.py lint` mechanism; any Cron or Skill changes that break the architecture will be intercepted and reported as errors by the Linter.
5. **System Compatibility (Compaction Hook)**: Automatically overrides OpenClaw's underlying `pre-compaction memory flush` prompt during installation, preventing HTTP 429 request burst death loops caused by unauthorized file writing attempts during Token compaction.

---

## 📦 Architectural Components

This skill package contains complete system components:

1. **`tools/memctl.py`**: The core engine, containing subcommands like `ensure`, `capture`, `work_upsert`, `kb_append`, `lint`.
2. **`install.sh`**: One-click installation script that automatically initializes directories and injects TriCore compliance policies into `POLICY.md`.
3. **`cognitive-skills/`**: Three core cognitive skills refactored based on TriCore (as templates for your Agent to load):
   - `planning-with-files.md`: A PEP planning system that discards detached task lists.
   - `react-agent.md`: A ReAct loop based on persisting mental states to `WORKING.md`.
   - `self-evolution.md`: An evolution system that completely detaches memory management and focuses on "Code-level CI/CD".

---

## 🧩 Core Dependencies & Runtime Requirements

As an underlying cognitive foundation, TriCore itself and its embedded three major cognitive skills have the following dependencies on the host environment:

### 1. Hard Dependencies
- **OpenClaw (v2026+)**: Must support native `memory_search` and `memory_get` tools (this is the retrieval basis for completely deprecating reading large files).
- **Python 3.6+**: Python 3 must be installed in the host environment (used to execute the `tools/memctl.py` state engine).
- **System Tools**: `bash`, `sed`, `grep` (used for regular expression parsing by the Linter and Hooks).

### 2. Cognitive Skill Soft Dependencies
If you enable `cognitive-skills/self-evolution.md` (Self Code Evolution Skill), your Agent must have tentacles to explore outward, otherwise, it can only undergo "hallucinated self-evolution" in an internal infinite loop.

- **🌟 `agent-browser` (Highly Recommended)**: 
  - **Function**: Enables the Agent to truly read GitHub source code, official API documentation, and the latest papers.
  - **Installation**: You need to separately install OpenClaw's `agent-browser` skill, which provides WYSIWYG crawling and clicking capabilities based on a headless browser.
- **Search Tools (`web_search` / `web_fetch`)**:
  - **Function**: Acts as a lightweight fallback for the browser, used to quickly extract Markdown snippets from public web pages.
- **Runtime Modification Permissions (`default_api:exec` & `default_api:write`)**:
  - **Function**: The essence of the evolution skill is "modifying code"; if your Agent is running in a ReadOnly sandbox, evolution cannot occur.

---

## 🚀 Installation & Initialization (The 3-Step Setup)

In any completely new OpenClaw environment, executing the following command will deploy the TriCore architecture:

```bash
# Grant installation script permissions and execute
bash ./install.sh
```

**`install.sh` executes in the following order:**

### Step 1: Core Engine Deployment
1. Creates standard directories like `memory/state/`, `memory/kb/`, `memory/daily/`.
2. Deploys the `tools/memctl.py` engine to the current environment.

### Step 2: Force Legacy MEMORY Migration (Agent Action Required)
In a low-resource architecture, a massive `MEMORY.md` full of conversation history and diaries is extremely fatal.
The script will automatically detect the current `MEMORY.md`:
- If found to be too bloated (> 1500 bytes), it will be renamed and **moved to `memory/archive/legacy-MEMORY-<date>.md`**.
- Then, a compliant **minimalist `MEMORY.md` template** will be rebuilt in the root directory.
- **Agent Note: At this time, you need to actively use `read` to read the legacy backup file, and call `memctl.py` to redistribute this legacy** (facts into `kb/facts`, rules into `kb/playbooks`, logs into `daily`); it is **STRICTLY FORBIDDEN** to paste long texts intact back into the new MEMORY.md!

### Step 3: System Global Linter Blockade Deployment
The script will inject a `[CRITICAL: TriCore Compliance]` top-priority defense line into the system's `POLICY.md`. Thereafter, all planning for disk-writing, state updating, and automated tasks executed by the Agent must all pass the `memctl.py lint` regex check, otherwise, they will be rejected in red text in the terminal.

---

## 📚 Core Command Cheat Sheet

In the Agent tool flow or internal sub-scripts, please strictly use the following API to access states:

**1. Record temporary logs / session ledger (Volatile)**
```bash
python3 tools/memctl.py capture "Tested API connectivity, successful."
```

**2. Create / Update task tracking (Living State)**
```bash
python3 tools/memctl.py work_upsert --task_id "T-API-01" --title "Fix API" --goal "Connect interface" --done_when "Returns 200"
```

**3. Accumulate knowledge & experience (Stable KB)**
```bash
python3 tools/memctl.py kb_append facts "This API only accepts JSON format."
python3 tools/memctl.py kb_append playbooks "When encountering an error in this module, check if Redis is started first."
```

**4. Check script / Cron command compliance (Linter)**
```bash
python3 tools/memctl.py lint "Command to execute or .md file path to check"
# Pass normally: Exit Code 0 (LINT PASS)
# Illegal write: Exit Code 1 (LINT ERROR)
```

---
*Built with ❤️ for OpenClaw / Berton Han*