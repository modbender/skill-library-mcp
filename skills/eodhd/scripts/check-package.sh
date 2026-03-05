#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
MANIFEST="${ROOT_DIR}/agents/openai.yaml"

fail() {
  printf 'FAIL: %s\n' "$*" >&2
  exit 1
}

assert_file() {
  local path="$1"
  [[ -f "${ROOT_DIR}/${path}" ]] || fail "missing packaged file: ${path}"
}

assert_manifest_contains() {
  local needle="$1"
  if ! grep -Fq -- "${needle}" "${MANIFEST}"; then
    fail "manifest missing expected value: ${needle}"
  fi
}

assert_doc_contains() {
  local path="$1"
  local needle="$2"
  if ! grep -Fq -- "${needle}" "${ROOT_DIR}/${path}"; then
    fail "${path} missing expected value: ${needle}"
  fi
}

main() {
  [[ -f "${MANIFEST}" ]] || fail "missing manifest: agents/openai.yaml"

  assert_manifest_contains 'entrypoint: "scripts/eodhd"'
  assert_manifest_contains 'primary: "EODHD_API_KEY"'
  assert_manifest_contains 'name: "EODHD_API_KEY"'

  assert_file "SKILL.md"
  assert_file "README.md"
  assert_file "agents/openai.yaml"
  assert_file "references/implementation-plan.md"
  assert_file "references/openclaw-secrets.md"
  assert_file "scripts/eodhd"
  assert_file "scripts/test-smoke.sh"
  assert_file "scripts/check-package.sh"

  assert_doc_contains "SKILL.md" 'Expect `EODHD_API_KEY` to be injected by OpenClaw.'
  assert_doc_contains "README.md" 'Prefer `EODHD_API_KEY` injected by OpenClaw secrets management.'
  assert_doc_contains "README.md" '[scripts/eodhd](./scripts/eodhd)'

  if find "${ROOT_DIR}" -maxdepth 2 \( -name '.env' -o -name '*.local' \) | grep -q .; then
    fail "unexpected local secret file found in package tree"
  fi

  printf 'PASS: package manifest and file contract are coherent\n'
}

main "$@"
