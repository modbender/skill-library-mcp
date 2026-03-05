#!/usr/bin/env bash
set -euo pipefail

REPO_URL="git+https://github.com/yazelin/clawpet.git"

if command -v clawpet >/dev/null 2>&1; then
  exec clawpet "$@"
fi

if command -v uvx >/dev/null 2>&1; then
  exec uvx --from "$REPO_URL" clawpet "$@"
fi

if command -v uv >/dev/null 2>&1; then
  exec uv tool run --from "$REPO_URL" clawpet "$@"
fi

echo "Error: clawpet executable not found, and uv/uvx is unavailable." >&2
echo "Please install uv first: https://docs.astral.sh/uv/getting-started/installation/" >&2
exit 1

