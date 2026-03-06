#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   chis-chisf.sh chis <slug> [workdir] [version]
#   chis-chisf.sh chisf <slug> [workdir] [version]
#   chis-chisf.sh inspect <slug> [workdir]

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <chis|chisf|inspect> <slug> [workdir] [version]" >&2
  exit 1
fi

mode="$1"
slug="$2"
workdir="${3:-/Users/zququ/.openclaw/workspace}"
version="${4:-}"

case "$mode" in
  chis)
    cmd=(clawhub install "$slug" --workdir "$workdir" --dir skills)
    ;;
  chisf)
    cmd=(clawhub install "$slug" --force --workdir "$workdir" --dir skills)
    ;;
  inspect)
    cmd=(clawhub inspect "$slug" --workdir "$workdir")
    ;;
  *)
    echo "Unknown mode: $mode" >&2
    exit 2
    ;;
esac

if [[ "$mode" != "inspect" && -n "$version" ]]; then
  cmd+=(--version "$version")
fi

"${cmd[@]}"
