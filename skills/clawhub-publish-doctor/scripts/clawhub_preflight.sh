#!/usr/bin/env bash
set -euo pipefail

ok() { printf '✔ %s\n' "$*"; }
warn() { printf '⚠ %s\n' "$*"; }

if command -v clawhub >/dev/null 2>&1; then
  ok "clawhub found: $(clawhub --cli-version 2>/dev/null || echo 'unknown version')"
else
  warn "clawhub not found. Install: npm i -g clawhub"
fi

if command -v clawdhub >/dev/null 2>&1; then
  warn "legacy clawdhub binary also present (possible confusion). Prefer clawhub."
fi

if command -v xdg-open >/dev/null 2>&1; then
  ok "xdg-open available (browser login should work)"
else
  warn "xdg-open missing. Browser login may fail on this host; use token login: clawhub login --token <clh_token>"
fi

if command -v rg >/dev/null 2>&1; then
  ok "ripgrep available"
else
  warn "ripgrep missing (optional). Install for faster diagnostics."
fi

if command -v clawhub >/dev/null 2>&1; then
  if clawhub whoami >/tmp/clawhub_whoami.txt 2>/tmp/clawhub_whoami.err; then
    ok "authenticated: $(cat /tmp/clawhub_whoami.txt | tail -n 1)"
  else
    warn "not authenticated. Run: clawhub login --token <clh_token>"
  fi
fi
