#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPO_ROOT_CANDIDATE="$(cd "${SKILL_DIR}/../.." 2>/dev/null && pwd || true)"

DEFAULT_BIN="${REPO_ROOT_CANDIDATE}/bin/safespace-rater"
GO_INSTALL_SPEC="${SAFESPACE_RATER_GO_INSTALL:-github.com/vpn2004/SkillVet/cmd/safespace-rater@latest}"
BIN_PATH=""

has_command() {
  command -v "$1" >/dev/null 2>&1
}

resolve_bin() {
  if [[ -n "${SAFESPACE_RATER_BIN:-}" && -x "${SAFESPACE_RATER_BIN}" ]]; then
    BIN_PATH="${SAFESPACE_RATER_BIN}"
    return 0
  fi

  if [[ -x "${DEFAULT_BIN}" ]]; then
    BIN_PATH="${DEFAULT_BIN}"
    return 0
  fi

  if has_command go; then
    local gobin gopath first_gopath
    gobin="$(go env GOBIN 2>/dev/null || true)"
    if [[ -n "${gobin}" && -x "${gobin}/safespace-rater" ]]; then
      BIN_PATH="${gobin}/safespace-rater"
      return 0
    fi

    gopath="$(go env GOPATH 2>/dev/null || true)"
    first_gopath="${gopath%%:*}"
    if [[ -n "${first_gopath}" && -x "${first_gopath}/bin/safespace-rater" ]]; then
      BIN_PATH="${first_gopath}/bin/safespace-rater"
      return 0
    fi
  fi

  if has_command safespace-rater; then
    BIN_PATH="$(command -v safespace-rater)"
    return 0
  fi

  BIN_PATH="${SAFESPACE_RATER_BIN:-${DEFAULT_BIN}}"
  return 1
}

print_dep_status() {
  resolve_bin >/dev/null 2>&1 || true

  echo "[safespace-rater] dependency check"
  echo "- skill_dir: ${SKILL_DIR}"
  echo "- server(default): ${SAFESPACE_SERVER:-https://skillvet.cc.cd}"
  echo "- go-install-spec: ${GO_INSTALL_SPEC}"

  if has_command go; then
    echo "- go: $(go version)"
  else
    echo "- go: not found (required when binary is missing)"
  fi

  if [[ -x "${BIN_PATH}" ]]; then
    echo "- binary: ok (${BIN_PATH})"
    return 0
  fi

  echo "- binary: missing (${BIN_PATH})"
  echo "  hint: set SAFESPACE_RATER_BIN=/absolute/path/to/safespace-rater"
  echo "  hint: or keep go installed and this script will auto-run: go install ${GO_INSTALL_SPEC}"
  echo "  hint: or build from repo root: make build"
  return 1
}

try_auto_build() {
  if resolve_bin; then
    return 0
  fi

  if [[ -n "${REPO_ROOT_CANDIDATE}" && -f "${REPO_ROOT_CANDIDATE}/go.mod" && -d "${REPO_ROOT_CANDIDATE}/cmd/safespace-rater" ]] && has_command go; then
    echo "[safespace-rater] binary not found, trying local auto-build..."
    mkdir -p "${REPO_ROOT_CANDIDATE}/bin"
    if [[ -f "${REPO_ROOT_CANDIDATE}/Makefile" ]] && has_command make; then
      (cd "${REPO_ROOT_CANDIDATE}" && make build)
    else
      (cd "${REPO_ROOT_CANDIDATE}" && go build -o "${REPO_ROOT_CANDIDATE}/bin/safespace-rater" ./cmd/safespace-rater)
    fi
  fi

  if resolve_bin; then
    return 0
  fi

  if has_command go; then
    echo "[safespace-rater] trying auto-bootstrap via go install..."
    go install "${GO_INSTALL_SPEC}"
  fi

  resolve_bin
}

if [[ "${1:-}" == "--check" ]]; then
  print_dep_status
  exit $?
fi

if ! try_auto_build; then
  print_dep_status >/dev/stderr || true
  cat >/dev/stderr <<'EOF'

[safespace-rater] cannot locate executable.
Use one of the following:
1) Auto-bootstrap with Go (recommended):
   go install github.com/vpn2004/SkillVet/cmd/safespace-rater@latest
2) Build in repository root:
   make build
3) Point to an existing binary:
   export SAFESPACE_RATER_BIN=/absolute/path/to/safespace-rater
EOF
  exit 1
fi

exec "${BIN_PATH}" "$@"
