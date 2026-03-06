#!/usr/bin/env bash
set -euo pipefail

: "${NOTION_TOKEN:?Missing NOTION_TOKEN}"
: "${NOTION_TASKS_PAGE_ID:?Missing NOTION_TASKS_PAGE_ID}"

api="https://api.notion.com/v1"
version="2022-06-28"
cmd="${1:-}"
shift || true

request() {
  local method="$1"; shift
  local url="$1"; shift
  local data="${1:-}"
  if [[ -n "$data" ]]; then
    curl -sS -X "$method" "$url" \
      -H "Authorization: Bearer $NOTION_TOKEN" \
      -H "Notion-Version: $version" \
      -H "Content-Type: application/json" \
      --data "$data"
  else
    curl -sS -X "$method" "$url" \
      -H "Authorization: Bearer $NOTION_TOKEN" \
      -H "Notion-Version: $version" \
      -H "Content-Type: application/json"
  fi
}

get_todos_json() {
  local raw
  raw="$(request GET "$api/blocks/$NOTION_TASKS_PAGE_ID/children?page_size=100")"
  node -e '
const j = JSON.parse(process.argv[1]);
if (j.object === "error") { console.log(JSON.stringify(j)); process.exit(0); }
const getText = (arr=[]) => (arr||[]).map(x => x?.plain_text || x?.text?.content || "").join("").trim();
const todos = (j.results||[])
  .filter(b => b.type === "to_do")
  .map((b, i) => ({
    index: i + 1,
    id: b.id,
    checked: !!b.to_do?.checked,
    text: getText(b.to_do?.rich_text)
  }));
console.log(JSON.stringify({todos, total: todos.length}));
' "$raw"
}

case "$cmd" in
  list)
    get_todos_json
    ;;

  add)
    text="${1:-}"
    if [[ -z "$text" ]]; then
      echo 'Usage: notion_tasks_blocks.sh add "<text>"' >&2
      exit 1
    fi
    payload="$(node -e '
const text = process.argv[1];
const p = {
  children: [{
    object: "block",
    type: "to_do",
    to_do: {
      checked: false,
      rich_text: [{ type: "text", text: { content: text } }]
    }
  }]
};
process.stdout.write(JSON.stringify(p));
' "$text")"
    request PATCH "$api/blocks/$NOTION_TASKS_PAGE_ID/children" "$payload"
    ;;

  done|undo)
    idx="${1:-}"
    if [[ -z "$idx" ]]; then
      echo "Usage: notion_tasks_blocks.sh $cmd <index>" >&2
      exit 1
    fi
    todos="$(get_todos_json)"
    block_id="$(node -e '
const j = JSON.parse(process.argv[1]);
const idx = Number(process.argv[2]);
const t = (j.todos||[]).find(x => x.index === idx);
if (!t) process.exit(2);
process.stdout.write(t.id);
' "$todos" "$idx" 2>/dev/null || true)"
    if [[ -z "$block_id" ]]; then
      echo "Task index not found: $idx" >&2
      exit 1
    fi
    checked="false"
    [[ "$cmd" == "done" ]] && checked="true"
    payload="{\"to_do\":{\"checked\":$checked}}"
    request PATCH "$api/blocks/$block_id" "$payload"
    ;;

  *)
    cat >&2 <<'TXT'
Usage:
  notion_tasks_blocks.sh list
  notion_tasks_blocks.sh add "<text>"
  notion_tasks_blocks.sh done <index>
  notion_tasks_blocks.sh undo <index>
TXT
    exit 1
    ;;
esac
