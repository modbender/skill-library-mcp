# Agent Emacs: A Living Home for AI

Most AI agents live in a void. They wake up, run a few commands in a terminal, and then forget everything they've seen. This setup is fine for simple scripts, but it fails for complex engineering work.

Agent Emacs changes the model. It gives the AI a persistent "nervous system" using an Emacs daemon. Instead of just editing files, the agent lives in a high-performance, stateful environment where files, remote servers, and project logic exist as continuous buffers.

## Why this exists

*   **Continuous Context:** Your agent doesn't have to re-read files every time you ask a question. The buffers stay open, and the context remains exactly where it was.
*   **Structural Power:** By using Lisp to edit code, the agent can make surgical changes without the risk of breaking files with messy regex replacements.
*   **Transparent Remotes:** With TRAMP, your agent can manage an entire fleet of servers as if they were local files. No more manual SSH juggling.
*   **Unified Interface:** Git, file management, and shell execution all happen through one consistent, high-speed pipe.

## How it works

The agent communicates with a persistent Emacs process via `emacsclient`. This allows for zero-latency interactions and a shared state that survives between conversation turns.

## Installation

1.  Clone the repository.
2.  Run `scripts/bootstrap.sh`.
3.  Load the `agent-emacs` skill into your OpenClaw environment.

This is more than an editor; it's a foundation for building stateful, autonomous AI colleagues.
