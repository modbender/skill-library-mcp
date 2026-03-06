#!/usr/bin/env bash
set -euo pipefail
PROJECT_NAME=$(basename "$(pwd)" | tr -cs '[:alnum:]' '-')
echo "${PROJECT_NAME}-code-session"
