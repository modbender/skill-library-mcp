#!/usr/bin/env bash

# Shared helpers for openclaw-github-sync shell scripts.

openclaw_github_sync_default_skill_dir() {
  local script_dir
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  printf '%s\n' "$(cd "$script_dir/.." && pwd)/"
}

openclaw_github_sync_load_env() {
  local -a managed_vars=("$@")
  local env_path
  local need_source=0
  local var i
  local -a had_values values names

  env_path="$(openclaw_github_sync_default_skill_dir)references/.env"

  [[ -f "$env_path" ]] || return 0

  for var in "${managed_vars[@]}"; do
    if [[ -z "${!var:-}" ]]; then
      need_source=1
      break
    fi
  done
  [[ "$need_source" -eq 1 ]] || return 0

  for var in "${managed_vars[@]}"; do
    names+=("$var")
    if [[ "${!var+x}" == "x" ]]; then
      had_values+=("1")
      values+=("${!var}")
    else
      had_values+=("0")
      values+=("")
    fi
  done

  # shellcheck disable=SC1090
  source "$env_path" || true

  for i in "${!names[@]}"; do
    if [[ "${had_values[$i]}" == "1" ]]; then
      printf -v "${names[$i]}" '%s' "${values[$i]}"
    fi
  done
}
