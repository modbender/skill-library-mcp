---
name: agent-emacs
description: Unified persistent text-based environment for AI agents. Use when an agent needs to maintain state across sessions, perform structural code editing, or manage remote nodes via TRAMP. Transforms the agent from a stateless script executor into a stateful resident of a living Emacs daemon.
---

# Agent Emacs: The Living Workspace

This skill provides a persistent, high-performance Emacs environment designed specifically for AI agents. It replaces fragmented CLI tools with a unified "Living Image" workflow.

## Core Concepts

1. **The Daemon**: All work happens inside a persistent Emacs daemon (`emacs-agent.service`).
2. **The Socket**: Communication is handled via `emacsclient -s /tmp/emacs0/server`.
3. **Buffers as State**: Files, terminal outputs, and remote connections are treated as persistent buffers. State is maintained between agent turns.

## Operational Workflow

### 1. Structural Editing
Do not use regex for complex code changes. Use ELisp forms to manipulate the AST.
```bash
emacsclient -s /tmp/emacs0/server --eval "(with-current-buffer \"main.lisp\" (goto-char (point-max)) (insert \"\n(new-function)\"))"
```

### 2. Remote Infrastructure (TRAMP)
Manage remote nodes transparently. Opening a remote file automatically establishes a persistent SSH tunnel.
```elisp
(find-file "/ssh:user@remote-node:/etc/config.json")
```

### 3. Project Management (Magit)
Use Magit for all Git operations to ensure high-integrity commits and staging.

## Advanced Workflows
For detailed patterns on recursive data processing (RLM), memory management, and REPL-based accuracy, see:
- [usage.md](references/usage.md) - Low-level Lisp interaction patterns.
- [agent-workflows.md](references/agent-workflows.md) - High-level operational strategies.

## Guaranteed Accuracy
Always use the Emacs Lisp REPL for math, data manipulation, or status calculations. Accuracy is paramount; do not attempt manual calculations.

## Initialization
Run `scripts/bootstrap.sh` to ensure the daemon is active and the `agent-init.el` configuration is loaded.
