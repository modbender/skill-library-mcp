#!/usr/bin/env bash
set -euo pipefail

# List notes in a folder (default: Notes)
FOLDER="${1:-Notes}"

memo notes -f "$FOLDER"