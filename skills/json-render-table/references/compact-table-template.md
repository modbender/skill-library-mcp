# Compact Generic Table Template (No Temp JSON Files)

Use this starter to render a compact six-column table and adapt field values for your dataset.

## 1) Fill values

```bash
export ID="#1094"
export PRIORITY="MEDIUM"
export STATUS="IN REVIEW"
export ASSIGNEE="Maya"
export UPDATED_AT="Tue 10:22"
export TOPIC="Checkout retry logic verification"
export OUT_PATH="${OUT_PATH:-/tmp/table-render.png}"

if ! command -v json-render >/dev/null 2>&1; then
  npm i -g json-render-cli
fi
export JSON_RENDER_CMD="${JSON_RENDER_CMD:-json-render}"

if [ -z "${SPEC_PATH:-}" ]; then
  for candidate in \
    "${CODEX_HOME:-$HOME/.codex}/skills/json-render-table/references/compact-table-spec.template.json" \
    "./npm/skills/json-render-table/references/compact-table-spec.template.json" \
    "./skills/json-render-table/references/compact-table-spec.template.json"
  do
    if [ -f "$candidate" ]; then
      export SPEC_PATH="$candidate"
      break
    fi
  done
fi
if [ -z "${SPEC_PATH:-}" ] || [ ! -f "$SPEC_PATH" ]; then
  echo "Cannot find compact-table-spec.template.json. Set SPEC_PATH explicitly." >&2
  exit 1
fi

# Optional manual overrides:
# export TOPIC_COL_WIDTH=420
# export VIEWPORT_WIDTH=970
# export VIEWPORT_HEIGHT=108
if [ -z "${TOPIC_COL_WIDTH:-}" ] || [ -z "${VIEWPORT_WIDTH:-}" ] || [ -z "${VIEWPORT_HEIGHT:-}" ]; then
  eval "$(python3 - <<'PY'
import math
import os

topic = os.environ.get("TOPIC", "").strip()
topic_len = len(topic)
topic_col_width = max(260, min(520, topic_len * 8 + 40))
fixed_width = 92 + 108 + 94 + 122 + 132
viewport_width = fixed_width + topic_col_width + 2
chars_per_line = max(18, topic_col_width // 8)
topic_lines = max(1, math.ceil(max(1, topic_len) / chars_per_line))
viewport_height = max(96, min(220, 56 + topic_lines * 24))

print(f"export TOPIC_COL_WIDTH={topic_col_width}")
print(f"export VIEWPORT_WIDTH={viewport_width}")
print(f"export VIEWPORT_HEIGHT={viewport_height}")
PY
)"
fi
```

## 2) Build message JSON in memory

```bash
MESSAGE_JSON="$(python3 - <<'PY'
import json, pathlib, os
p = pathlib.Path(os.environ["SPEC_PATH"])
tpl = p.read_text(encoding="utf-8")
m = {
  "__ID__": os.environ["ID"],
  "__PRIORITY__": os.environ["PRIORITY"],
  "__STATUS__": os.environ["STATUS"],
  "__ASSIGNEE__": os.environ["ASSIGNEE"],
  "__UPDATED_AT__": os.environ["UPDATED_AT"],
  "__TOPIC__": os.environ["TOPIC"],
}
for k, v in m.items():
  tpl = tpl.replace(k, json.dumps(v, ensure_ascii=False)[1:-1])
tpl = tpl.replace("__TOPIC_COL_WIDTH__", str(int(os.environ["TOPIC_COL_WIDTH"])))
print(tpl)
PY
)"
```

## 3) Render

```bash
"$JSON_RENDER_CMD" \
  -m "$MESSAGE_JSON" \
  -c <(cat <<JSON
{
  "version": 1,
  "catalog": {
    "allowedComponents": ["Container", "Row", "Column", "Card", "Heading", "Text", "Badge", "Divider", "Spacer", "Button", "Image"],
    "componentDefaults": {}
  },
  "theme": { "mode": "system" },
  "viewport": { "width": ${VIEWPORT_WIDTH}, "height": ${VIEWPORT_HEIGHT}, "deviceScaleFactor": 2 },
  "screenshot": { "type": "png", "omitBackground": false, "fullPage": true },
  "canvas": { "background": "#ffffff", "padding": 0 }
}
JSON
) \
  -o "$OUT_PATH" \
  --size "${VIEWPORT_WIDTH}x${VIEWPORT_HEIGHT}"
```

If this command is executed by a sub-agent, keep `"$OUT_PATH"` and let the main agent decide final cleanup.

For ticket-focused output with opinionated field semantics, use `json-render-ticket-table`.
