#!/usr/bin/env bash
set -euo pipefail

DATA_DIR="$HOME/.openclaw/workspace/data/todo"
LOG="$DATA_DIR/tasks.jsonl"
mkdir -p "$DATA_DIR"
touch "$LOG"

# 입력은 한 줄로 들어온다고 가정
TEXT="${1:-}"

# 간단 파싱: owner: / due: 패턴이 있으면 추출
OWNER="$(echo "$TEXT" | sed -n 's/.*owner:\([^/]*\).*/\1/p' | xargs || true)"
DUE="$(echo "$TEXT" | sed -n 's/.*due:\([^/]*\).*/\1/p' | xargs || true)"

TITLE="$(echo "$TEXT" | sed 's/\/ *owner:.*//; s/\/ *due:.*//;' | xargs)"

ID="$(date +%y%m%d-%H%M%S)-$RANDOM"
TS="$(date -Iseconds)"

# JSON 기록
python3 - <<PY >> "$LOG"
import json
event = {
  "id": "$ID",
  "ts": "$TS",
  "title": "$TITLE",
  "owner": "$OWNER" if "$OWNER" else None,
  "due": "$DUE" if "$DUE" else None,
  "status": "draft" if (not "$OWNER" or not "$DUE") else "open",
  "raw": "$TEXT"
}
print(json.dumps(event, ensure_ascii=False))
PY

# 결과 출력(텔레그램으로 보여줄 문구)
if [ -z "$OWNER" ] || [ -z "$DUE" ]; then
  echo "✅ 임시 저장(draft) 완료: $ID
- 제목: $TITLE
- 담당: ${OWNER:-미정}
- 납기: ${DUE:-미정}

담당자(owner)와 납기(due)를 알려줘야 확정 저장(open)할 수 있어!
예) /todo $TITLE / owner:홍길동 / due:내일 18:00"
else
  echo "✅ 저장 완료(open): $ID
- 제목: $TITLE
- 담당: $OWNER
- 납기: $DUE"
fi
