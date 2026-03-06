# Hierarchical Memory (Neural Branching) 🧠🏗️

A modular, multi-layered memory system designed for long-term AI agents to prevent context bloat and ensure high-fidelity recall.

## 🌟 Key Features
- **Neural Branching:** Organize memory into Root, Domain, and Project layers.
- **Recent Delta:** Quick-load mechanism for the last 3-7 days of context.
- **Zombie Prevention:** Mandatory significance markers for every memory branch.
- **Low Latency:** Only load the specific context needed for the current task.

## 🛠️ Structure
```
workspace/
├── MEMORY.md (Root Map)
└── memory/
    ├── domains/ (Coding, Trading, Social, etc.)
    └── projects/ (Project-specific deep dives)
```

## 🚀 How to Use
1. **Initialize:** The skill sets up your base directories.
2. **Add Branch:** Use `scripts/add_branch.py` to create new domains or projects.
3. **Recall:** Start at `MEMORY.md`, follow the link, and `read` the specific branch.

## 📦 Installation
If published on ClawHub:
```bash
clawhub install hierarchical-memory
```
Or manually add the `SKILL.md` to your skills directory.

---
*Built with ❤️ by maymun & Balkan.*
