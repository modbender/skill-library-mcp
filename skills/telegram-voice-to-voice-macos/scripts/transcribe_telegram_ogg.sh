#!/usr/bin/env bash
set -euo pipefail

OGG_PATH="${1:-}"

if [[ -z "${OGG_PATH}" ]]; then
  OGG_PATH="$(ls -t "${HOME}/.openclaw/media/inbound"/*.ogg 2>/dev/null | head -n 1 || true)"
fi

if [[ -z "${OGG_PATH}" || ! -f "${OGG_PATH}" ]]; then
  echo "ERROR: no .ogg file found (pass a path or ensure ~/.openclaw/media/inbound/*.ogg exists)" >&2
  exit 2
fi

if ! command -v yap >/dev/null 2>&1; then
  echo "ERROR: yap not found in PATH" >&2
  exit 3
fi

# Locale: if YAP_LOCALE is not set, fall back to macOS system locale.
# Example AppleLocale values: it_IT, en_US@currency=EUR
if [[ -z "${YAP_LOCALE:-}" ]]; then
  SYS_LOCALE="$(defaults read -g AppleLocale 2>/dev/null || true)"
  SYS_LOCALE="${SYS_LOCALE%%@*}"
  SYS_LOCALE="${SYS_LOCALE//_/-}"
  if [[ -n "${SYS_LOCALE}" ]]; then
    YAP_LOCALE="${SYS_LOCALE}"
  else
    YAP_LOCALE="en-US"
  fi
fi

yap transcribe --locale "${YAP_LOCALE}" "${OGG_PATH}"
