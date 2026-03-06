#!/bin/bash
# ngrok-setup.sh — kakaotalk 로컬 테스트용 ngrok 터널 도우미
# 실행: bash scripts/ngrok-setup.sh [포트]
set -euo pipefail

PORT="${1:-8401}"
LABEL="com.yeomyeonggeori.kakaotalk"
LOG_DIR="/Users/tomas/.openclaw/workspace/logs"
NGROK_LOG="$LOG_DIR/ngrok-kakaotalk.log"

mkdir -p "$LOG_DIR"

# ─── ngrok 설치 확인 ──────────────────────────────────────────────────────────
if ! command -v ngrok &>/dev/null; then
  echo "❌ ngrok 미설치"
  echo ""
  echo "  설치 방법:"
  echo "    brew install ngrok/ngrok/ngrok"
  echo "    ngrok config add-authtoken <YOUR_TOKEN>   # https://dashboard.ngrok.com"
  exit 1
fi

# ─── 서버 실행 여부 확인 ──────────────────────────────────────────────────────
if ! curl -sf "http://localhost:${PORT}/health" > /dev/null 2>&1; then
  echo "⚠️  서버가 포트 ${PORT}에서 실행 중이지 않습니다."
  echo ""
  read -r -p "  지금 서버를 시작할까요? (서비스 미설치 시 직접 실행) [y/N] " confirm
  if [[ "$confirm" =~ ^[Yy]$ ]]; then
    # launchd 서비스가 있으면 사용, 없으면 직접 실행
    if launchctl list | grep -q "$LABEL" 2>/dev/null; then
      launchctl start "$LABEL"
      echo "✅ launchd 서비스 시작"
    else
      SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
      echo "🚀 server.py 직접 실행 (백그라운드)..."
      # shellcheck disable=SC2094
      nohup python3 "$SCRIPT_DIR/server.py" >> "$NGROK_LOG" 2>&1 &
      echo "   PID: $!"
    fi
    sleep 2
  fi
fi

# ─── 기존 ngrok 종료 ──────────────────────────────────────────────────────────
if pgrep -f "ngrok http ${PORT}" > /dev/null 2>&1; then
  echo "🔄 기존 ngrok 프로세스 종료..."
  pkill -f "ngrok http ${PORT}" || true
  sleep 1
fi

# ─── ngrok 터널 시작 ──────────────────────────────────────────────────────────
echo "🌐 ngrok 터널 시작 (포트 ${PORT})..."
echo "   로그: $NGROK_LOG"
echo ""

# 백그라운드로 ngrok 실행
nohup ngrok http "$PORT" --log=stdout >> "$NGROK_LOG" 2>&1 &
NGROK_PID=$!
echo "   ngrok PID: $NGROK_PID"

# ngrok API에서 공개 URL 가져오기 (최대 10초 대기)
PUBLIC_URL=""
for i in $(seq 1 20); do
  sleep 0.5
  PUBLIC_URL=$(curl -sf http://127.0.0.1:4040/api/tunnels 2>/dev/null \
    | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    tunnels = d.get('tunnels', [])
    for t in tunnels:
        if t.get('proto') == 'https':
            print(t['public_url'])
            break
except:
    pass
" 2>/dev/null || true)
  if [[ -n "$PUBLIC_URL" ]]; then
    break
  fi
done

echo ""
if [[ -n "$PUBLIC_URL" ]]; then
  WEBHOOK_URL="${PUBLIC_URL}/kakao"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "  ✅ ngrok 터널 활성화!"
  echo ""
  echo "  웹훅 URL (카카오 오픈빌더에 입력):  "
  echo "    $WEBHOOK_URL"
  echo ""
  echo "  테스트 curl:"
  echo "    curl -X POST $WEBHOOK_URL \\"
  echo "      -H 'Content-Type: application/json' \\"
  echo "      -d '{\"userRequest\":{\"utterance\":\"안녕\",\"user\":{\"id\":\"test\"}},\"bot\":{\"id\":\"bot\"},\"intent\":{\"name\":\"폴백\"}}'"
  echo ""
  echo "  ngrok 대시보드: http://127.0.0.1:4040"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
else
  echo "⚠️  공개 URL을 가져오지 못했습니다. 직접 확인:"
  echo "   http://127.0.0.1:4040/api/tunnels"
  echo "   또는 ngrok 로그: tail -f $NGROK_LOG"
fi

echo ""
echo "  종료: kill $NGROK_PID  또는  pkill -f 'ngrok http ${PORT}'"
