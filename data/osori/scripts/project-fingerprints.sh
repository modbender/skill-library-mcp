#!/usr/bin/env bash
# Show project fingerprints (repo/commit/PR/issue) from osori registry
# Usage:
#   project-fingerprints.sh [name-query]
#   project-fingerprints.sh --root <root-key> [name-query]

set -euo pipefail

QUERY=""
ROOT_FILTER=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root)
      ROOT_FILTER="${2:-}"
      shift 2
      ;;
    -h|--help)
      echo "Usage: $0 [name-query] [--root <root-key>]"
      exit 0
      ;;
    *)
      if [[ -z "$QUERY" ]]; then
        QUERY="$1"
      fi
      shift
      ;;
  esac
done

REGISTRY_FILE="${OSORI_REGISTRY:-$HOME/.openclaw/osori.json}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

OSORI_SCRIPT_DIR="$SCRIPT_DIR" \
OSORI_REG="$REGISTRY_FILE" \
OSORI_QUERY="$QUERY" \
OSORI_ROOT_FILTER="$ROOT_FILTER" \
python3 << 'PYEOF'
import os
import subprocess
import sys
from typing import List

sys.path.insert(0, os.environ["OSORI_SCRIPT_DIR"])
from github_cache import DEFAULT_CACHE_PATH, gh_count
from registry_lib import filter_projects, load_registry, parse_repo_from_remote, registry_projects, resolve_alias


def run(cmd: List[str], timeout: int = 8):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except Exception as e:
        return 1, "", str(e)


CACHE_PATH = os.environ.get("OSORI_CACHE_FILE", DEFAULT_CACHE_PATH)
try:
    CACHE_TTL = int(os.environ.get("OSORI_CACHE_TTL", "600"))
except Exception:
    CACHE_TTL = 600


query = os.environ.get("OSORI_QUERY", "").strip()
root_filter = os.environ.get("OSORI_ROOT_FILTER", "").strip()
reg_file = os.environ["OSORI_REG"]

loaded = load_registry(reg_file, auto_migrate=True, make_backup_on_migrate=True)
resolved_query = resolve_alias(query, loaded.registry) if query else query
projects = filter_projects(registry_projects(loaded.registry), root_key=root_filter, name_query=resolved_query)

if not projects:
    where = []
    if root_filter:
        where.append(f"root={root_filter}")
    if query:
        where.append(f"query={query}")
    suffix = f" ({', '.join(where)})" if where else ""
    print(f"📂 No matching projects{suffix}.")
    raise SystemExit(0)

if query and resolved_query != query:
    print(f"ℹ️ alias resolved: {query} -> {resolved_query}")
    print()

if loaded.migrated:
    notes = "; ".join(loaded.migration_notes)
    print(f"ℹ️ Registry migrated: {notes}")
    if loaded.backup_path:
        print(f"ℹ️ Migration backup: {loaded.backup_path}")
    print()

headline = f"🧬 Project fingerprints ({len(projects)})"
if root_filter:
    headline += f" [root={root_filter}]"
print(f"{headline}\n")

for p in projects:
    name = p.get("name", "-")
    path = p.get("path", "")
    root = p.get("root", "default")

    print(f"• {name} [{root}]")

    if not path or not os.path.exists(path):
        print(f"  - path: {path or '-'}")
        print("  - remote: n/a")
        print("  - last commit: n/a")
        print("  - open PRs: n/a")
        print("  - open issues: n/a")
        print()
        continue

    rc, remote, _ = run(["git", "-C", path, "remote", "get-url", "origin"])
    if rc != 0:
        remote = ""

    repo = p.get("repo", "") or parse_repo_from_remote(remote)

    rc, last, _ = run(["git", "-C", path, "log", "-1", "--format=%H|%cI"])
    if rc == 0 and "|" in last:
        commit_hash, commit_date = last.split("|", 1)
        commit_str = f"{commit_hash} ({commit_date})"
    else:
        commit_str = "n/a"

    pr_count = gh_count("pr", repo, ttl_seconds=CACHE_TTL, cache_path=CACHE_PATH)
    issue_count = gh_count("issue", repo, ttl_seconds=CACHE_TTL, cache_path=CACHE_PATH)

    print(f"  - path: {path}")
    print(f"  - remote: {remote or 'n/a'}")
    print(f"  - last commit: {commit_str}")
    print(f"  - open PRs: {pr_count}")
    print(f"  - open issues: {issue_count}")
    print()
PYEOF