#!/bin/bash
# Resolve or create an agent board and print MY_BOARD_ID safely.

set -euo pipefail

PIKABOARD_API="${PIKABOARD_API:-http://localhost:3001/api}"
AGENT_NAME="${AGENT_NAME:-}"
BOARD_NAME="${BOARD_NAME:-${AGENT_NAME}}"
PIKABOARD_TOKEN="${PIKABOARD_TOKEN:-}"
BOARD_ENV_FILE="${BOARD_ENV_FILE:-}"

if [ -z "${AGENT_NAME}" ]; then
  echo "AGENT_NAME is required (example: AGENT_NAME=bulbi)"
  exit 1
fi

if [ -z "${BOARD_NAME}" ]; then
  echo "BOARD_NAME could not be resolved. Set BOARD_NAME or AGENT_NAME."
  exit 1
fi

AUTH_HEADERS=()
if [ -n "${PIKABOARD_TOKEN}" ]; then
  AUTH_HEADERS=(-H "Authorization: Bearer ${PIKABOARD_TOKEN}")
fi

echo "Checking boards on ${PIKABOARD_API}..."
BOARDS_JSON="$(curl -fsS "${AUTH_HEADERS[@]}" "${PIKABOARD_API}/boards")"

BOARD_ID="$(
  printf '%s' "${BOARDS_JSON}" | node -e '
    let input = "";
    process.stdin.on("data", (c) => input += c);
    process.stdin.on("end", () => {
      const name = (process.argv[1] || "").toLowerCase();
      const parsed = JSON.parse(input);
      const boards = Array.isArray(parsed.boards) ? parsed.boards : [];
      const exact = boards.find((b) => String(b.name || "").toLowerCase() === name);
      if (exact && exact.id != null) {
        process.stdout.write(String(exact.id));
        return;
      }
      const partial = boards.find((b) => String(b.name || "").toLowerCase().includes(name));
      if (partial && partial.id != null) process.stdout.write(String(partial.id));
    });
  ' "${BOARD_NAME}"
)"

if [ -z "${BOARD_ID}" ]; then
  echo "Board '${BOARD_NAME}' not found. Creating it..."
  CREATE_PAYLOAD="$(node -e '
    const name = process.argv[1];
    process.stdout.write(JSON.stringify({ name }));
  ' "${BOARD_NAME}")"

  CREATED_JSON="$(
    curl -fsS -X POST "${AUTH_HEADERS[@]}" \
      -H "Content-Type: application/json" \
      -d "${CREATE_PAYLOAD}" \
      "${PIKABOARD_API}/boards"
  )"

  BOARD_ID="$(
    printf '%s' "${CREATED_JSON}" | node -e '
      let input = "";
      process.stdin.on("data", (c) => input += c);
      process.stdin.on("end", () => {
        const parsed = JSON.parse(input);
        if (parsed && parsed.id != null) process.stdout.write(String(parsed.id));
      });
    '
  )"
fi

if [ -z "${BOARD_ID}" ]; then
  echo "Failed to resolve or create board id."
  exit 1
fi

# Defend against command injection in downstream shell usage.
if ! [[ "${BOARD_ID}" =~ ^[0-9]+$ ]]; then
  echo "Unsafe BOARD_ID '${BOARD_ID}' (expected numeric id)."
  exit 1
fi

echo "Resolved board '${BOARD_NAME}' -> id ${BOARD_ID}"
echo "Verifying task access for board ${BOARD_ID}..."
curl -fsS "${AUTH_HEADERS[@]}" \
  "${PIKABOARD_API}/tasks?board_id=${BOARD_ID}&status=up_next" >/dev/null

echo "MY_BOARD_ID=${BOARD_ID}"
echo "Run: export MY_BOARD_ID=${BOARD_ID}"

if [ -n "${BOARD_ENV_FILE}" ]; then
  mkdir -p "$(dirname "${BOARD_ENV_FILE}")"
  {
    echo "MY_BOARD_ID=${BOARD_ID}"
    echo "BOARD_NAME=${BOARD_NAME}"
  } > "${BOARD_ENV_FILE}"
  echo "Wrote ${BOARD_ENV_FILE}"
fi

echo "Done."
