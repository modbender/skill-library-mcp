---
name: react-agent
version: "2.0.0-tricore"
description: A ReAct Agent implementation refactored based on the TriCore architecture. Natively integrates memory_search, WORKING.md, and kb knowledge base, abandoning the old independently maintained three-layer memory classes, fully merging into the system-level underlying memory infrastructure.
allowed-tools:
  - default_api:exec
  - memory_search
  - memory_get
---

# ReAct Agent Skill (TriCore Edition)

This is a ReAct Agent architecture implementation deeply customized for the OpenClaw environment. In version `v2.0.0`, we have completely removed the independently maintained `ShortTermMemory`, `WorkingMemory`, and `LongTermMemory` Python classes of the old version, and fully integrated into the system-level **TriCore** architecture.

## Core Features

### 1. ReAct Loop (Reasoning-Action Loop)
- Thought → Action → Observation → Record → Loop
- Completely relies on built-in system tools

### 2. TriCore Memory Mapping
The old In-Memory Dict implementation has been replaced by persistent file/vector retrieval infrastructure:

*   **Short-Term Memory**: Directly uses the **last 10-20 turns of conversation context** maintained by OpenClaw.
*   **Working Memory**: Mapped to `memory/state/WORKING.md`. Uses `tools/memctl.py work_upsert` to manage intermediate reasoning states and task progress.
*   **Long-Term Memory**: Mapped to `memory/kb/*.md` and daily logs `memory/daily/*.md`. Writing uses `tools/memctl.py kb_append` or `capture`, **reading mandatorily uses the semantic retrieval tool `memory_search`**.

### 3. Tool Registry Pattern
- Natively uses OpenClaw `TOOLS.md` or the extension/plugin system.
- After tool execution, key observations are accumulated into WORKING.md.

## Architecture Usage (Code-First Paradigm)

When writing the Python version of the ReAct Agent, instead of using memory arrays to manage context, it calls the `memctl.py` and `memory_search` tools via `subprocess`:

```python
import subprocess
import json

class TriCoreReActAgent:
    def __init__(self, task_id):
        self.task_id = task_id

    # --- Memory Interface (Docking with TriCore) ---
    def update_working_memory(self, title, goal, log):
        """Update working memory (WORKING.md)"""
        cmd = [
            "python3", "tools/memctl.py", "work_upsert", 
            "--task_id", self.task_id,
            "--title", title, 
            "--goal", goal
        ]
        subprocess.run(cmd, check=True)
        
        # Record temporary step
        subprocess.run(["python3", "tools/memctl.py", "capture", f"[{self.task_id}] {log}"])

    def recall_long_term_memory(self, query):
        """Retrieve long-term memory (Relies on external memory_search tool or system API)"""
        # In actual use, this is supported by OpenClaw's memory_search tool
        # The agent obtains this part through the system prompt
        pass

    def commit_long_term_knowledge(self, kb_type, content):
        """Accumulate experience into long-term memory (memory/kb)"""
        cmd = ["python3", "tools/memctl.py", "kb_append", kb_type, content]
        subprocess.run(cmd, check=True)

    # --- ReAct Loop ---
    def run(self, user_query):
        # 1. Create task tracking
        self.update_working_memory(
            title=f"ReAct Task: {user_query[:20]}", 
            goal=user_query, 
            log="Started ReAct loop"
        )
        
        # 2. Loop execution (Pseudocode)
        # while not done:
        #    thought = llm(query + current_working_memory)
        #    action = ...
        #    observation = ...
        #    self.update_working_memory(..., log=f"Observed: {observation}")
        
        # 3. Complete task, extract into Playbook
        self.commit_long_term_knowledge("playbooks", f"Task {user_query} resolved by...")
        subprocess.run(["python3", "tools/memctl.py", "work_done", self.task_id])
        return "Done"
```

## Design Principles and Evolution

### 1. Eliminate State Silos
The old ReAct Agent kept state in its own process memory, which was lost upon restart. With TriCore, even if the Agent restarts, it can instantly recover its mental state by reading `WORKING.md`.

### 2. Search-First
It is strictly forbidden for the Agent to `cat` or `read` massive history files. If historical experience is needed, it must call `memory_search` to fetch the most relevant snippet before the ReAct loop starts.

### 3. From Standalone Script to Native Skill
Under this architecture, ReAct is no longer an independent bot that needs to be started via `python run.py`, but your (OpenClaw Agent) own reasoning paradigm—you can directly execute this loop in your "brain" and persistently write the state to the hard drive.

---
**Sara's ReAct Agent (v2.0.0)** - A runtime mental model perfectly integrated with TriCore. 🚀✨