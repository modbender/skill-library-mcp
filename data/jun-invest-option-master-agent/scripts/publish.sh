#!/usr/bin/env bash
set -euo pipefail

# Publish the current ARTIFACT (this skill folder) to ClawHub.
# Designed to run unattended (best-effort). It will only publish when:
# - There are new runtime git commits since last publish, OR
# - A force flag file exists in the runtime workspace.
#
# Runtime is the source of truth:
#   ~/.openclaw/workspace-jun-invest-option-master-agent
# Artifact lives here:
#   ~/.openclaw/workspace/skills/jun-invest-option-master-agent

RUNTIME_DIR="${RUNTIME_DIR:-/Users/lijunsheng/.openclaw/workspace-jun-invest-option-master-agent}"
SKILL_DIR="${SKILL_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
STATE_FILE="${STATE_FILE:-${RUNTIME_DIR}/.publish-state.json}"
FORCE_FLAG="${FORCE_FLAG:-${RUNTIME_DIR}/.publish-now}"

SLUG="${SLUG:-jun-invest-option-master-agent}"
NAME="${NAME:-jun-invest-option-master-agent}"

CLAWHUB_BIN="${CLAWHUB_BIN:-}"
if [[ -z "${CLAWHUB_BIN}" ]]; then
  CLAWHUB_BIN=$(command -v clawhub 2>/dev/null || true)
fi
[[ -n "${CLAWHUB_BIN}" ]] || { echo "SKIP: clawhub not found"; exit 0; }
command -v git >/dev/null 2>&1 || { echo "SKIP: git not found"; exit 0; }
command -v node >/dev/null 2>&1 || { echo "SKIP: node not found"; exit 0; }

if [[ ! -d "${RUNTIME_DIR}/.git" ]]; then
  echo "SKIP: runtime git not initialized: ${RUNTIME_DIR}"; exit 0
fi

runtime_head=$(cd "${RUNTIME_DIR}" && git rev-parse HEAD)

last_head=""
last_date=""
if [[ -f "${STATE_FILE}" ]]; then
  last_head=$(node -e 'const fs=require("fs"); const j=JSON.parse(fs.readFileSync(process.argv[1],"utf8")); console.log(j.lastPublishedHead||"")' "${STATE_FILE}" 2>/dev/null || true)
  last_date=$(node -e 'const fs=require("fs"); const j=JSON.parse(fs.readFileSync(process.argv[1],"utf8")); console.log(j.lastPublishedDate||"")' "${STATE_FILE}" 2>/dev/null || true)
fi

today=$(date +%Y-%m-%d)
force="false"
if [[ -f "${FORCE_FLAG}" ]]; then
  force="true"
fi

# Publish policy:
# - Daily publish if new commits since last publish.
# - Allow immediate publish when FORCE_FLAG exists.
if [[ "${force}" != "true" ]]; then
  if [[ "${runtime_head}" == "${last_head}" ]]; then
    echo "SKIP: no new commits since last publish"
    exit 0
  fi
fi

# Ensure artifact is up to date (sync is commit-triggered, but do it defensively)
if [[ -x "${SKILL_DIR}/scripts/sync-runtime-to-artifact.sh" ]]; then
  "${SKILL_DIR}/scripts/sync-runtime-to-artifact.sh" || true
fi

# Create a semver-ish version automatically.
# Example: 0.2.202603041112 (YYYYMMDDHHMM)
version="0.2.$(date +%Y%m%d%H%M)"

# Build changelog from git commits since last publish.
changelog="auto publish"
if [[ -n "${last_head}" ]]; then
  changelog=$(cd "${RUNTIME_DIR}" && git log --oneline "${last_head}..${runtime_head}" | head -n 50 | sed 's/"/\\"/g')
  [[ -n "${changelog}" ]] || changelog="auto publish"
else
  changelog=$(cd "${RUNTIME_DIR}" && git log --oneline -n 20 | sed 's/"/\\"/g')
fi

cd "${SKILL_DIR}"

echo "Publishing ${SLUG}@${version} ..."
# Best-effort: publishing may fail if not logged in; do not crash the whole system.
# clawhub publish can occasionally timeout; retry a few times.
try=1
max=3
ok="false"
while [[ ${try} -le ${max} ]]; do
  echo "Publish attempt ${try}/${max}..."
  if "${CLAWHUB_BIN}" publish . --slug "${SLUG}" --name "${NAME}" --version "${version}" --changelog "${changelog}"; then
    ok="true"; break
  fi
  sleep $((try * 5))
  try=$((try + 1))
done

if [[ "${ok}" == "true" ]]; then
  mkdir -p "$(dirname "${STATE_FILE}")"
  node -e 'const fs=require("fs"); const p=process.argv[1]; const head=process.argv[2]; const date=process.argv[3]; fs.writeFileSync(p, JSON.stringify({lastPublishedHead: head, lastPublishedDate: date}, null, 2));' "${STATE_FILE}" "${runtime_head}" "${today}"
  if [[ -f "${FORCE_FLAG}" ]]; then rm -f "${FORCE_FLAG}"; fi
  echo "OK: published and state updated"
else
  echo "WARN: publish failed (timeout/network/auth?)"
  exit 0
fi
