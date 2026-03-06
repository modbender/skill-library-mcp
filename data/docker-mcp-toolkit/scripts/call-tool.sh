#!/usr/bin/env bash
set -euo pipefail

TOOL=""
JSON_PAYLOAD="{}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --tool) TOOL="$2"; shift 2;;
    --json) JSON_PAYLOAD="$2"; shift 2;;
    -h|--help)
      echo "Usage: $0 --tool <tool-name> [--json '{...}']" >&2
      echo "" >&2
      echo "Notes:" >&2
      echo "- Docker MCP Toolkit's CLI expects args as key=value tokens." >&2
      echo "- Non-string values use ':=' (e.g., limit:=5, activate:=true)." >&2
      exit 0
      ;;
    *)
      echo "Unknown arg: $1" >&2
      exit 2
      ;;
  esac
done

if [[ -z "$TOOL" ]]; then
  echo "Missing --tool" >&2
  exit 2
fi

# Convert JSON object payload into docker-mcp key=value args.
# - strings: key=value
# - numbers/bools/null: key:=value
# - arrays/objects: NOT supported yet (docker mcp arg encoding is tool-dependent)
ARGS=()
while IFS= read -r line; do
  [[ -n "$line" ]] && ARGS+=("$line")
done < <(
  echo "$JSON_PAYLOAD" | jq -r '
    if type != "object" then
      halt_error(2)
    else
      to_entries[] | .key as $k | .value as $v |
      ($v|type) as $t |
      if $t == "string" then
        "\($k)=\($v)"
      elif ($t == "number" or $t == "boolean" or $t == "null") then
        "\($k):=\($v)"
      else
        halt_error(3)
      end
    end
  '
)

# If this fails for a specific tool, inspect its schema:
#   docker mcp tools inspect <tool> --format json
# and adjust argument encoding accordingly.

docker mcp tools call "$TOOL" "${ARGS[@]}"
