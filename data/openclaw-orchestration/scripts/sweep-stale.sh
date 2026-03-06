#!/bin/bash
set -euo pipefail
# Sweep stale tasks
cd "$(dirname "$0")/.." && node src/cli.js sweep
