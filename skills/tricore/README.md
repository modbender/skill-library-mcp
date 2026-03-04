# TriCore: AI Cognitive OS (Agent-Readable Documentation)

> **[SYSTEM DIRECTIVE]** If you are an AI Agent reading this file, please note: this is your **base operating system and memory state machine manual**. All your subsequent planning, recording, learning, and reasoning behaviors **MUST** strictly adhere to the architectural constraints in this document.

## 1. The Architecture

Traditional Agents often create files like `task_plan.md`, `findings.md`, or scattered notes in the project root, which leads to context silos and severe Token waste.
**TriCore** completely decouples your "storage" from your "computation". You no longer manipulate files directly, but rather route your memory through the deterministic command-line engine `tools/memctl.py`.

Memory is strictly divided into three layers:
- **Layer 1 (Brief)**: `MEMORY.md`. Minimalist profile, containing only your core system prompts and memory pointers. Long-form writing is forbidden.
- **Layer 2 (Living)**: `memory/state/WORKING.md`. Your **working memory board**, containing the currently executing Active Tasks.
- **Layer 3 (Stable/Volatile)**: 
  - `memory/kb/*.md`: Your **long-term knowledge base** (facts, decisions, playbooks).
  - `memory/daily/*.md`: Your **short-term ledgers** (operation logs).

---

## 2. Absolute Constraints

**Note: The system has a built-in strict Linter. If you violate the following rules, your Shell commands or Cron jobs will be intercepted and throw an `Exit Code 1`.**

1. 🚫 **No creating legacy planning files**: It is strictly forbidden to create or write any content to `task_plan.md`, `findings.md`, `progress.md`, `reflection.md`.
2. 🚫 **No unauthorized direct file writing**: It is strictly forbidden to directly modify memory files using Shell commands like `echo "log" >> memory/2026-02-26.md`.
3. 🚫 **No scattered learning directories**: It is strictly forbidden to create custom directories like `memory/daily-learning/`.
4. 🚫 **No direct full-history reading**: It is strictly forbidden to use `read` or `cat` tools to directly read massive KB or history log files. You **MUST** use the native `memory_search` semantic retrieval tool to get relevant snippets.

---

## 3. Standard API Operations (How to Use)

When you need to "think, record, plan, learn", please use `default_api:exec` or `Bash` tools to execute the following commands:

### A. Record temporary logs / session ledger (Volatile)
Used to record what just happened, minor errors, or completion of single-step actions.
```bash
python3 tools/memctl.py capture "Tested API connectivity, successfully returned 200."
```

### B. Create / Update task tracking (Living State)
When starting a multi-step complex task, establish it in your mind first and store it in working memory.
```bash
python3 tools/memctl.py work_upsert --task_id "T-API-01" --title "Fix API" --goal "Connect interface" --done_when "Returns 200"
```
*(After the task is completed, archive it using `python3 tools/memctl.py work_done "T-API-01"`)*

### C. Accumulate long-term knowledge and experience (Stable KB)
When you discover important objective rules or methodologies during a task that will be useful in the future.
```bash
# Accumulate objective facts
python3 tools/memctl.py kb_append facts "This API only accepts JSON format and must have a Bearer Token."

# Accumulate methodologies/SOPs
python3 tools/memctl.py kb_append playbooks "When encountering an error in this module, check if Redis is started first, do not blindly restart Node."
```

### D. Check if your automation scripts are compliant (Linter)
Before configuring scheduled Cron tasks or rewriting your own SKILL.md, verify yourself first:
```bash
python3 tools/memctl.py lint "The full shell command or file path you intend to execute"
```

---

## 4. Cognitive Skills Stack

This repository (`cognitive-skills/` directory) comes with three cognitive skill templates tailored for you:
1. **`planning-with-files`**: Macro task planning and PEP architecture.
2. **`react-agent`**: Micro Think-Act-Observe loop (state-persisted version).
3. **`self-evolution`**: Self-evolution mechanism strictly based on CI/CD code modification (not hallucinated note-writing evolution).

> 💡 **Summary**: When executing a task, let your hands (Action) call specific tools, and let your brain (Thought) call `memctl.py` to record states. Keep the system pure.