#!/usr/bin/env bash
DIR="$(cd "$(dirname "$0")" && pwd)"
exec node "$DIR/add_rule.mjs" "$@"
