#!/usr/bin/env bash
DIR="$(cd "$(dirname "$0")" && pwd)"
exec node "$DIR/list_entities.mjs" "$@"
