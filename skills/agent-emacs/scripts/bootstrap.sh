#!/bin/bash
# Bootstrap Emacs for Agents
if ! command -v emacs &> /dev/null; then
    echo "Error: Emacs not found. Please install Emacs 29.1+ first."
    exit 1
fi

EMACS_DIR="$HOME/.emacs.d"
mkdir -p "$EMACS_DIR"

if [ ! -f "$EMACS_DIR/init.el" ]; then
    cp assets/agent-init.el "$EMACS_DIR/init.el"
fi

# Ensure Daemon is running
if ! pgrep -f "emacs --daemon" > /dev/null; then
    emacs --daemon
fi

echo "Agent Emacs Daemon is ready."
