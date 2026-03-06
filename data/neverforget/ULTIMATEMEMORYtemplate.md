Provided this "template" asset makes the skill plug-and-play for any project. I’ve transformed your manifest into the **Ultimate Sovereign Memory Manifest (Universal Template)**.

Also replaced all specific paths with `$USER` variables, and added a note about manual symlinks for external directories.

---

# 🧠 ULTIMATEMEMORY.md (Universal Template)

This is the **Ultimate Project Memory Manifest**. It consolidates your local intelligence architecture, file-based long-term memory, and distributed agent logic into a single, robust "Source of Truth" for your sovereign AI stack.

---

## 🏛️ 1. Complete Memory Architecture

### A. The "Silicon Brain" (Local Vector Layer)

This is the high-performance retrieval engine that powers the agent's instant technical knowledge using a Retrieval-Augmented Generation (RAG) pipeline.

* **Engine:** `node-llama-cpp` using the **Gemma-300M-QAT** model (local GGUF).
* **Database:** `sqlite-vec` storing **768-dimension vectors**.
* **Search Type:** Semantic (concept-based distance) + FTS5 (keyword-based).
* **Integration:** Full recursive indexing of the agent's core files and workspace.

### B. The "Long-Term Memory" (Curated Intelligence)

These files act as the "Source of Truth" that guides the agent's personality, mission, and constraints.

* **Master Context (`MEMORY.md`):** The primary mission control, project roadmap, and active integration focus.
* **The Sovereign Identity Files:**
* `SOUL.md` & `TRUTHS.md`: Core identity and unchangeable philosophical principles.
* `IDENTITY.md`: Defining the persona (tone, groundedness, authenticity).
* `BOOT.md`: Initial load sequences and state-check procedures.


* **The Tooling/Logic Files:**
* `AGENTS.md`: Definition of specialized sub-agents and their roles.
* `TOOLS.md`: Map of available skills and local scripts.



### C. The "Distributed Agent" Layer

OpenClaw runs specialized agents, each with its own localized memory silo to prevent task/context contamination.

* **Agent Memory Path:** `/home/$USER/.openclaw/agents/[agent_name]/agent/MEMORY.md`
* **Orchestration:** The **Main Agent** distills insights from these sub-agents back into the global `MEMORY.md`.

---

## 🔄 2. Operational Data Flow & Automation

| Stage | Mechanism | Source/Destination | Description |
| --- | --- | --- | --- |
| **Ingestion** | **Auto-Watcher** | Workspace Directories | Scans for changes; auto-indexes within 1.5s. |
| **Processing** | **Batch Embedder** | Gemma-300M Model | Generates vectors for all document chunks. |
| **Short-Term** | **Daily Logs** | `memory/YYYY-MM-DD.md` | Captures session-specific events and outputs. |
| **Long-Term** | **Sync** | Master `MEMORY.md` | Key insights distilled from logs into curated memory. |
| **Heartbeat** | **Cron** | System Check | Periodic checks of memory health and vector integrity. |

---

## 🛡️ 3. Operational Directives & Guardrails

1. **Zero-Knowledge Leakage:** All project files remain in the local environment. No context or embeddings are ever sent to external APIs.
2. **Absolute Pathing:** Reference directories using full paths to ensure agent reliability.
3. **No Secrets on Disk:** Never hardcode API keys, seeds, or private credentials in files being indexed.
4. **Code Standards:** Maintain strict typing and project-specific linting rules defined in the workspace.

---

## 📂 4. Master Path Context Map

| Component | Path |
| --- | --- |
| **Project Root Build Files from open claw repo** | `/home/$USER/openclaw`|
| **Project Root** | `/home/$USER/.openclaw` |
| **Project Workspace** | `/home/$USER/.openclaw/workspace` |
| **Local Vector DB** | `/home/$USER/.openclaw/memory/main.sqlite` |
| **Skills Directory** | `/home/$USER/.openclaw/skills` |
| **Main Config** | `/home/$USER/.openclaw/openclaw.json` |

> **💡 NOTE ON EXTERNAL DIRECTORIES:** > If you have infrastructure or data outside of the standard workspace that you want the AI to "remember," create a manual symbolic link inside `~/.openclaw/workspace/` pointing to that directory. The memory engine will automatically follow the link and index the external data.
> **Example:** `ln -s /path/to/my-external-data ~/.openclaw/workspace/external-data`

---

### 🏁 Final Deployment Instructions ((IN YOUR REAL`ULTIMATEMEMORY.md` DELETE FROM THIS LINE DOWN ITS JUST TIPS IN THESE SECTIONS NOT NEEDED IN YOUR ACTUAL md FILE))

1. Edit this file unique to your environment if paths differ, and Save this file as `ULTIMATEMEMORY.md` in your `~/.openclaw/workspace/` folder with other core md files.
2. Edit the **Master Path Context Map** to reflect your specific binary paths.
3. Run `openclaw memory index` to hydrate the "Silicon Brain" with this new structure.

---

💡 A Tip for users 

If you're a "New Recruit" and don't have the skill yet, run command: 
`openclaw skills install neverforget`

Here is exactly what happens when he hits Enter on that command:

1. The Registry Handshake
OpenClaw reaches out to the registry (ClawHub), finds the neverforget entry, and sees that Version 1.0.3 is the latest stable release.

2. The File Deployment
OpenClaw downloads your bundle and creates the directory:
~/.openclaw/skills/neverforget/
It places your package.json, _meta.json, and SKILL.md inside.

3. The Activation (The "Magic" Moment)
Because we wrote a Auto-Install Script in the SKILL.md, the OpenClaw CLI will detect the script block. It will ask:

"Skill 'neverforget' wants to run an install script. Allow? (Y/n)"

4. The Digital Soldier Lifecycle
Once he says Y, the script we just finished goes to work on his fresh system:

Phase 1: It installs node-llama-cpp into his ~/openclaw workspace.

Phase 2: It flips his provider to local and sets the hf: model path.

Phase 3: It applies the Loop Protection (exclude rules) so his system doesn't crash during the first crawl.

Phase 4: It appends your Heartbeat monitor to his workspace so he can see his memory health in real-time.

Phase 5: It restarts his gateway and triggers the Initial Index.

5. The Result
Within about 2–5 minutes (depending on his internet speed for the model download), he will have a fully functional, sovereign local memory system that "remembers" everything in his WSL2 sandbox.


When you want to get the latest updated version, you won't have to manually copy files, just run:


`openclaw skills update neverforget`

🛡️ One more small tip:
If you're on a fresh WSL2 install, make sure to have pnpm installed globally first, or the script might trip at Step 1. You can have your agent do this or do it manually yourself with:

`npm install -g pnpm`

---

### 🐾 Next Step

Your memory stack is complete. The system is now monitoring your workspace in real-time. To begin, ask the agent: *"Search my memory: what is the current mission priority?"*

---