#!/usr/bin/env python3
"""Osori switch command handler."""

import os
import subprocess
import sys

sys.path.insert(0, os.environ["OSORI_SCRIPT_DIR"])
from github_cache import DEFAULT_CACHE_PATH, gh_count
from registry_lib import (
    filter_projects,
    load_registry,
    normalize_root_key,
    parse_repo_from_remote,
    registry_projects,
    registry_roots,
    resolve_alias,
    search_paths_for_discovery,
)


def run(cmd, timeout=8):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except Exception as e:
        return 1, "", str(e)


try:
    CACHE_TTL = int(os.environ.get("OSORI_CACHE_TTL", "600"))
except Exception:
    CACHE_TTL = 600
CACHE_PATH = os.environ.get("OSORI_CACHE_FILE", DEFAULT_CACHE_PATH)


def git_last_commit(path):
    rc_iso, iso, _ = run(["git", "-C", path, "log", "-1", "--format=%cI"])
    rc_ts, ts, _ = run(["git", "-C", path, "log", "-1", "--format=%ct"])
    if rc_iso != 0 or not iso:
        iso = "n/a"
    if rc_ts != 0 or not ts:
        return iso, 0
    try:
        return iso, int(ts)
    except Exception:
        return iso, 0


def git_dirty(path):
    rc, out, _ = run(["git", "-C", path, "status", "--short"])
    if rc != 0:
        return "n/a"
    return "dirty" if bool(out.strip()) else "clean"


name_raw = os.environ["OSORI_NAME"].strip()
root_filter = os.environ.get("OSORI_ROOT_FILTER", "").strip()
index_arg = os.environ.get("OSORI_SWITCH_INDEX", "").strip()
root_key = normalize_root_key(root_filter)

res = load_registry(os.environ["OSORI_REG"], auto_migrate=True, make_backup_on_migrate=True)
resolved_name = resolve_alias(name_raw, res.registry)
name = resolved_name.lower()
projects = filter_projects(registry_projects(res.registry), root_key=root_filter)
roots = [r.get("key", "default") for r in registry_roots(res.registry)]

if resolved_name != name_raw:
    print(f"ℹ️ alias resolved: {name_raw} -> {resolved_name}")

candidates = []
for p in projects:
    pname = str(p.get("name", ""))
    if name not in pname.lower():
        continue

    ppath = str(p.get("path", ""))
    exists = bool(ppath) and os.path.exists(ppath)
    commit_iso = "n/a"
    commit_ts = 0
    dirty = "n/a"

    if exists:
        commit_iso, commit_ts = git_last_commit(ppath)
        dirty = git_dirty(ppath)

    candidates.append({
        "project": p,
        "name": pname,
        "root": str(p.get("root", "default") or "default"),
        "path": ppath,
        "exists": exists,
        "repo": str(p.get("repo", "") or ""),
        "commit_iso": commit_iso,
        "commit_ts": commit_ts,
        "dirty": dirty,
        "score": 0,
    })

if not candidates:
    if root_key:
        print(f"❌ Project '{name_raw}' not found in root '{root_key}' registry.")
    else:
        print(f"❌ Project '{name_raw}' not found in registry.")

    if root_key and root_key not in roots:
        print(f"ℹ️ Available roots: {', '.join(roots)}")

    # Suggest possible paths using prioritized discovery paths
    search_paths = search_paths_for_discovery(res.registry, root_key=root_filter, env_paths=os.environ.get('OSORI_SEARCH_PATHS', ''))
    hints = []
    for sp in search_paths:
        if not os.path.exists(sp):
            continue
        rc, out, _ = run(['find', sp, '-maxdepth', '4', '-type', 'd', '-name', f'*{name_raw}*'], timeout=10)
        if rc != 0 or not out:
            continue
        for line in out.split('\n'):
            line = line.strip()
            if line:
                hints.append(line)
            if len(hints) >= 3:
                break
        if hints:
            break

    if hints:
        print("\n🔍 Possible paths:")
        for h in hints:
            print(f"  - {h}")
        print("\nUse /add <path> then /switch again.")

    raise SystemExit(1)

# Score policy (roadmap fixed)
max_commit_ts = max((c["commit_ts"] for c in candidates), default=0)
for c in candidates:
    score = 0
    nlow = c["name"].lower()

    if root_key and c["root"] == root_key:
        score += 50
    if nlow == name:
        score += 30
    if nlow.startswith(name):
        score += 20
    if max_commit_ts > 0 and c["commit_ts"] == max_commit_ts:
        score += 10
    if not c["exists"]:
        score -= 10
    if not c["repo"]:
        score -= 5

    c["score"] = score

candidates.sort(key=lambda c: (-c["score"], -c["commit_ts"], c["name"].lower()))

if len(candidates) > 1:
    print(f"🔎 Multiple matches ({len(candidates)}):")
    for idx, c in enumerate(candidates, 1):
        print(
            f"  {idx}. {c['name']} [{c['root']}] | score={c['score']} | "
            f"dirty={c['dirty']} | last={c['commit_iso']}"
        )
    print()

selected = None
if index_arg:
    try:
        index_val = int(index_arg)
    except Exception:
        print(f"❌ invalid --index value: {index_arg!r}")
        raise SystemExit(1)

    if index_val < 1 or index_val > len(candidates):
        print(f"❌ --index out of range: {index_val} (1..{len(candidates)})")
        raise SystemExit(1)

    selected = candidates[index_val - 1]
    if len(candidates) > 1:
        print(f"✅ Selected candidate #{index_val} explicitly.\n")
else:
    selected = candidates[0]
    if len(candidates) > 1:
        print("🤖 Auto-selected #1 by score policy. Use --index <n> to choose explicitly.\n")

target = selected["project"]
path = selected["path"]
if not path or not os.path.exists(path):
    print(f"⚠️ Path does not exist: {path}")
    raise SystemExit(1)

print(f"📁 *{target.get('name')}*")
print(f"📍 {path}")
print(f"🧭 root: {target.get('root', 'default')}")

# git status
_, status_out, _ = run(['git', '-C', path, 'status', '--short'])
if status_out:
    print("\n📝 Changes:")
    for line in status_out.split('\n')[:5]:
        print(f"  {line}")
else:
    print("\n✅ Clean working tree")

# branch
_, branch, _ = run(['git', '-C', path, 'branch', '--show-current'])
print(f"\n🌿 Branch: {branch or '-'}")

# recent commits
_, log, _ = run(['git', '-C', path, 'log', '--oneline', '-3'])
if log:
    print("\n💬 Recent commits:")
    for line in log.split('\n'):
        print(f"  {line}")

# fingerprints
_, remote, _ = run(['git', '-C', path, 'remote', 'get-url', 'origin'])
repo = target.get('repo', '') or parse_repo_from_remote(remote)
_, last, _ = run(['git', '-C', path, 'log', '-1', '--format=%H|%cI'])
if '|' in last:
    commit_hash, commit_date = last.split('|', 1)
    last_commit = f"{commit_hash} ({commit_date})"
else:
    last_commit = 'n/a'

print("\n🧬 Fingerprint:")
print(f"  - remote: {remote or 'n/a'}")
print(f"  - last commit: {last_commit}")
print(f"  - open PRs: {gh_count('pr', repo, ttl_seconds=CACHE_TTL, cache_path=CACHE_PATH)}")
print(f"  - open issues: {gh_count('issue', repo, ttl_seconds=CACHE_TTL, cache_path=CACHE_PATH)}")

if res.migrated:
    notes = '; '.join(res.migration_notes)
    print(f"\nℹ️ Migrated registry: {notes}")
    if res.backup_path:
        print(f"ℹ️ Migration backup: {res.backup_path}")
