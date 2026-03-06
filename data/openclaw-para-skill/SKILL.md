---
name: para
description: Organize files and projects using the PARA method (Projects, Areas, Resources, Archives).
author: Evo
version: 1.0.0
---

# PARA Organization Skill

Use the PARA method to keep the workspace clean and organized.

## Structure
- `/root/clawd/1-Projects/`: Active efforts with a deadline/goal.
- `/root/clawd/2-Areas/`: Ongoing responsibilities (e.g., Finances, Health, Personal Development).
- `/root/clawd/3-Resources/`: Interests and reference material.
- `/root/clawd/4-Archives/`: Completed projects or inactive areas/resources.

## Mandate: Automatic Organization
You MUST follow the PARA structure for ALL file operations. Never leave new files in the root directory (`/root/clawd/`) unless they are core identity files (AGENTS.md, MEMORY.md, etc.).

1.  **New Project Files?** Create a subfolder in `1-Projects/`.
2.  **Long-term reference or data?** Put it in `3-Resources/`.
3.  **Finished work?** Move it to `4-Archives/`.
4.  **System/Config updates?** Keep them in `2-Areas/`.

## Workflow
1. **Identify**: Determine which category a file or directory belongs to.
2. **Move**: Use `mv` to place it in the correct PARA folder.
3. **Maintain**: Periodically review Projects and move finished ones to Archives.

## Categorization Guide
- **Projects**: Bot development, Specific homework assignments, Reports being written.
- **Areas**: Financial logs (`MIANJY`), Email configurations, Skill development.
- **Resources**: Research papers, Diagrams for learning, Snippets.
- **Archives**: Old reports, Finished semester files.
