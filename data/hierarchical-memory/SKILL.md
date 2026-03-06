---
name: hierarchical-memory
description: Manage and navigate a multi-layered, branch-based memory system. This skill helps organize complex agent context into Root, Domain, and Project layers to prevent context bloat. It includes a helper script `add_branch.py` which creates local markdown files and directories to structure your memory.
---

# Hierarchical Memory (Neural Branching)

This skill provides a structured method for managing long-term memory in a multi-layered, branched format to prevent context bloat and ensure high-fidelity recall.

## 🛡️ Security & Transparency
This skill includes a Python script `scripts/add_branch.py`. This script is used solely to:
1. Create directories in your `memory/` folder.
2. Create boilerplate markdown files for new memory branches.
3. Append links to these new files in your existing memory maps.
**It does not perform any network activity, access sensitive system files, or execute external code.**

## Memory Architecture

The memory system is organized into three primary layers:

1.  **Layer 1: Root Memory (`MEMORY.md`)**
    - The central nervous system.
    - Contains high-level context about the partnership, core missions, and global goals.
    - Acts as a map to all other memory layers.

2.  **Layer 2: Domain Memories (`memory/domains/*.md`)**
    - Specialized knowledge silos.
    - Examples: `coding.md`, `trading.md`, `social.md`, `research.md`.
    - Contains domain-specific philosophies, tech stacks, and project indices.

3.  **Layer 3: Project Memories (`memory/projects/*.md`)**
    - Deep-dive details for specific initiatives.
    - Examples: `hesapgaraj.md`, `clawguard.md`, `baa.md`.
    - Contains project status, to-dos, technical specs, and history.

## How to Use This Skill

### 1. Recalling Information
- Always start by searching `MEMORY.md`.
- Follow the "Map" links to the relevant Domain or Project file.
- Use `read` to load only the specific branch needed for the current task.

### 2. Adding New Information
- **New Fact about the Partnership:** Update `MEMORY.md`.
- **New Domain:** Create a new file in `memory/domains/` and link it from `MEMORY.md`.
- **New Project:** Create a new file in `memory/projects/` and link it from its primary Domain file.

### 3. Cross-Referencing
- If a project belongs to multiple domains (e.g., a trading bot that requires coding), link the Project file from both Domain files.

## Automation Tools

Use the provided scripts to maintain the hierarchy:
- `scripts/add_branch.py`: Automatically create a new domain or project file with the correct template and linking.

## Best Practices
- **Atomic Writes:** Keep project files focused only on that project.
- **Backlinks:** Every branch should have a "Back to Root" or "Back to Domain" link.
- **Pruning:** During heartbeats, review branches and remove obsolete information.
- **Why This Matters:** Every branch and major entry must include a "Significance" line (Why is this important?) to prevent "Zombie Memory" (useless data accumulation).
- **Recent Delta:** Maintain a `recent_delta.md` in each domain/project folder containing changes from the last 3-7 days for rapid context synchronization.
