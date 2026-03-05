# Advanced Agent Workflows in Emacs

This guide covers high-level patterns for agents to operate with maximum efficiency within the Emacs environment.

## 1. Recursive Data Processing (RLM Mode)
When dealing with massive files or logs that exceed your context window:
1. Use `find-file-noselect` to load the target into a buffer.
2. Use `narrow-to-region` to isolate specific "chunks" for analysis.
3. Spawn sub-agents to process these chunks.
4. Synthesize the results back into a final summary buffer.

## 2. Guaranteed Accuracy (The Lisp REPL)
Never perform manual arithmetic or complex data string manipulation.
- Use `(eval '(+ 1 2 3))` or the `*ielm*` buffer for precise calculations.
- Use Emacs's built-in string and list processing functions (`s.el`, `dash.el`) for data transformation.

## 3. Persistent Agent Memory (Org-mode vs. Markdown)
Treat your workspace state as a structured database using Org-mode, but maintain clear boundaries with the host memory system:
- **Technical State (Org-mode)**: Use `WORKSPACE.org` for internal task tracking, clocking into sub-tasks, recording PID numbers, and managing temporary buffer locations.
- **Human-Relevant Memory (Markdown)**: Significant outcomes, decisions, and cross-session facts MUST be mirrored to the host's `.md` memory files (e.g., `MEMORY.md`, `YYYY-MM-DD.md`).
- **Guideline**: Org is for the *process* of working; Markdown is for the *record* of what was done.

## 4. Resource Concurrency & Lockfiles
Since the Emacs Daemon is a shared environment:
- **Lockfiles**: Emacs generates `.jkt.filename.ext#` style lockfiles by default. The `agent-init.el` disables these to prevent agents from blocking each other on shared project files.
- **Atomic Operations**: Always use `with-current-buffer` and `save-buffer` to ensure your edits are flushed to disk immediately so other agents (or the human) see the updated state.
- **Daemon Namespacing**: If multiple separate agent fleets are required, use `--socket-name` to isolate their environments.

## 5. Cross-Image Interoperability
If your system involves other running Lisp processes (e.g., a Common Lisp web server):
- Use `SLIME` or `Sly` inside Emacs to connect to the remote Swank server.
- This allows you to inspect and modify the state of other "Living Images" through the same unified interface.
