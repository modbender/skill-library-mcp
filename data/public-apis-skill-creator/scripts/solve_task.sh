#!/usr/bin/env bash
# 根据功能自动推荐免费 API，并生成可执行示例。
# 可选 --try 会尝试对首个无需认证的直连 URL 发起一次 GET 探测。
# Usage:
#   solve_task.sh "weather in beijing"
#   solve_task.sh "exchange rate" --try
#   solve_task.sh "weather api" --pick 2
#   solve_task.sh "weather api" --make-skill --skill-name weather-api-skill --pick 2

set -euo pipefail

QUERY="${1:-}"
shift || true
TRY=0
TOP=3
PICK=1
MAKE_SKILL=0
SKILL_NAME=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --try) TRY=1; shift ;;
    --top) TOP="$2"; shift 2 ;;
    --pick) PICK="$2"; shift 2 ;;
    --make-skill) MAKE_SKILL=1; shift ;;
    --skill-name) SKILL_NAME="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 2 ;;
  esac
done

if [[ -z "$QUERY" ]]; then
  echo "Usage: solve_task.sh <query> [--top N] [--pick N] [--try] [--make-skill --skill-name <name>]"
  exit 1
fi

if ! [[ "$PICK" =~ ^[0-9]+$ ]] || [[ "$PICK" -lt 1 ]]; then
  echo "❌ --pick 必须是 >=1 的整数"
  exit 2
fi

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JSON=$(bash "$BASE_DIR/search_api.sh" "$QUERY" --top "$TOP" --json)

python3 - <<'PY' "$QUERY" "$JSON" "$PICK"
import json, sys
query = sys.argv[1]
results = json.loads(sys.argv[2])
pick = int(sys.argv[3])
if not results:
    print('❌ 没找到可用 API')
    sys.exit(1)

print(f"🎯 需求: {query}\n")
print("默认推荐 API（优先免费/免鉴权/HTTPS）：\n")
for i, a in enumerate(results, 1):
    print(f"{i}. {a['name']}  (score={a['score']})")
    print(f"   - 描述: {a['description']}")
    print(f"   - 认证: {a['auth']} | HTTPS: {a['https']} | CORS: {a['cors']}")
    print(f"   - 文档: {a.get('link','')}")

if pick > len(results):
    print(f"\n⚠️ --pick={pick} 超出范围，回退到 1")
    pick = 1

best = results[pick-1]
print(f"\n✅ 选中第 {pick} 个 API:", best['name'])
print("下一步: 用 gen_usage.sh 生成最小可用调用模板。")
PY

BEST_NAME=$(python3 - <<'PY' "$JSON" "$PICK"
import json,sys
r=json.loads(sys.argv[1]); p=int(sys.argv[2])
p = 1 if p < 1 or p > len(r) else p
print(r[p-1]['name'])
PY
)
BEST_LINK=$(python3 - <<'PY' "$JSON" "$PICK"
import json,sys
r=json.loads(sys.argv[1]); p=int(sys.argv[2])
p = 1 if p < 1 or p > len(r) else p
print(r[p-1].get('link',''))
PY
)
BEST_AUTH=$(python3 - <<'PY' "$JSON" "$PICK"
import json,sys
r=json.loads(sys.argv[1]); p=int(sys.argv[2])
p = 1 if p < 1 or p > len(r) else p
print(r[p-1].get('auth','No'))
PY
)

echo
if [[ -n "$BEST_LINK" ]]; then
  bash "$BASE_DIR/gen_usage.sh" --name "$BEST_NAME" --url "$BEST_LINK" --auth "$BEST_AUTH"
else
  echo "# ${BEST_NAME} 使用示例"
  echo "未找到可直接调用 URL（仅文档入口），请先打开文档选定 endpoint。"
fi

if [[ "$TRY" -eq 1 && -n "$BEST_LINK" ]]; then
  if [[ "$BEST_AUTH" =~ ^(No|None|)$ ]] && [[ "$BEST_LINK" =~ ^https?:// ]]; then
    echo
    echo "🧪 探测首选 API: $BEST_LINK"
    code=$(curl -s -o /tmp/public_api_probe.out -w '%{http_code}' "$BEST_LINK" || true)
    echo "HTTP: $code"
    head -c 500 /tmp/public_api_probe.out || true
    echo
  else
    echo
    echo "🧪 跳过探测：首选 API 需要鉴权或无直连 URL。"
  fi
fi

if [[ "$MAKE_SKILL" -eq 1 ]]; then
  if [[ -z "$SKILL_NAME" ]]; then
    echo "❌ --make-skill 需要配合 --skill-name <name>"
    exit 2
  fi
  echo
  echo "🧩 正在生成 skill: $SKILL_NAME"
  bash "$BASE_DIR/create_skill.sh" \
    --skill-name "$SKILL_NAME" \
    --api-name "$BEST_NAME" \
    --api-url "$BEST_LINK" \
    --auth "$BEST_AUTH" \
    --desc "Auto-generated skill from public-apis-helper for ${BEST_NAME}."
fi