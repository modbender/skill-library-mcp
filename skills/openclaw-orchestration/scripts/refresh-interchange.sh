#!/bin/bash
set -euo pipefail
# Refresh interchange .md files
cd "$(dirname "$0")/.." && node src/cli.js refresh
