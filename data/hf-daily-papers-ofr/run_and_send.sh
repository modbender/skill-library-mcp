#!/bin/bash
set -euo pipefail

# Generate today's HF papers markdown, then send a compact list via OpenClaw messaging.
#
# Required env:
#   TELEGRAM_TARGET   e.g. 6184653533 (user id) or @channelname
# Optional env:
#   OPENCLAW_BIN      default: openclaw
#   HF_DAILY_PAPERS_PROXY  e.g. http://127.0.0.1:7897

WORKDIR="$(cd "$(dirname "$0")" && pwd)"
OUTDIR="${WORKDIR}/recommendations"
DATE_STR="$(date +%Y-%m-%d)"
MD_FILE="${OUTDIR}/${DATE_STR}.md"

OPENCLAW_BIN="${OPENCLAW_BIN:-openclaw}"
TELEGRAM_TARGET="${TELEGRAM_TARGET:-}"

if [ -z "$TELEGRAM_TARGET" ]; then
  echo "Missing TELEGRAM_TARGET env" >&2
  exit 2
fi

cd "$WORKDIR"

# Generate markdown
/usr/bin/python3 "$WORKDIR/generator.py" >/dev/null

if [ ! -f "$MD_FILE" ]; then
  echo "Missing markdown output: $MD_FILE" >&2
  exit 1
fi

MSG=$(/usr/bin/python3 - <<'PY'
import re
from pathlib import Path
from datetime import datetime

md_path = Path(__file__).resolve().parent / "recommendations" / (datetime.now().strftime("%Y-%m-%d") + ".md")
text = md_path.read_text(encoding="utf-8")

sections = {"gen": [], "eff": []}
cur = None

for line in text.splitlines():
    if line.startswith("## 🎨"):
        cur = "gen"
    elif line.startswith("## ⚡"):
        cur = "eff"
    m = re.match(r"^### \[(\d+\.\d+)\]\(https://huggingface\.co/papers/\1\) - (.*)$", line)
    if m and cur:
        pid, title = m.group(1), m.group(2).strip()
        sections[cur].append((pid, title))

seen = set()

def fmt(items, max_n=10):
    out = []
    for pid, title in items:
        if pid in seen:
            continue
        seen.add(pid)
        title = re.sub(r"\s+", " ", title)
        if len(title) > 90:
            title = title[:87] + "..."
        out.append(f"- {pid} {title}\n  https://huggingface.co/papers/{pid}")
        if len(out) >= max_n:
            break
    return "\n".join(out)

date_str = datetime.now().strftime("%Y-%m-%d")
msg = (
    f"HF Daily Papers ({date_str})\n\n"
    f"Generation\n{fmt(sections['gen'], max_n=10) or '- (none)'}\n\n"
    f"Efficient\n{fmt(sections['eff'], max_n=10) or '- (none)'}\n\n"
    f"(auto)"
)
print(msg)
PY
)

"$OPENCLAW_BIN" message send --channel telegram --target "$TELEGRAM_TARGET" --message "$MSG" --silent >/dev/null
