#!/bin/bash
# install-service.sh — kakaotalk 스킬 launchd 서비스 등록
# 실행: bash scripts/install-service.sh
set -euo pipefail

LABEL="com.yeomyeonggeori.kakaotalk"
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_PATH="$SKILL_DIR/scripts/server.py"
LOG_DIR="${KAKAOTALK_LOG_DIR:-$HOME/.openclaw/logs}"
LOG_FILE="$LOG_DIR/kakaotalk.log"
ERR_FILE="$LOG_DIR/kakaotalk.err.log"
PLIST_PATH="$HOME/Library/LaunchAgents/${LABEL}.plist"
ENV_FILE="$HOME/.openclaw/.env"

# ─── 환경변수 로드 ─────────────────────────────────────────────────────────────
if [[ -f "$ENV_FILE" ]]; then
  # GEMINI_API_KEY, KAKAO_CALLBACK_SECRET 추출
  GEMINI_API_KEY_VAL=$(grep -E '^GEMINI_API_KEY=' "$ENV_FILE" | cut -d= -f2- | tr -d '"' || true)
  KAKAO_SECRET_VAL=$(grep -E '^KAKAO_CALLBACK_SECRET=' "$ENV_FILE" | cut -d= -f2- | tr -d '"' || true)
else
  GEMINI_API_KEY_VAL=""
  KAKAO_SECRET_VAL=""
fi

# ─── 사전 확인 ─────────────────────────────────────────────────────────────────
if [[ ! -f "$SCRIPT_PATH" ]]; then
  echo "❌ server.py 없음: $SCRIPT_PATH"
  exit 1
fi

PYTHON3=$(command -v python3 || true)
if [[ -z "$PYTHON3" ]]; then
  echo "❌ python3 미설치"
  exit 1
fi

mkdir -p "$LOG_DIR"
mkdir -p "$HOME/Library/LaunchAgents"

# ─── 기존 서비스 언로드 ───────────────────────────────────────────────────────
if launchctl list | grep -q "$LABEL" 2>/dev/null; then
  echo "🔄 기존 서비스 언로드 중..."
  launchctl unload "$PLIST_PATH" 2>/dev/null || true
fi

# ─── plist 생성 ───────────────────────────────────────────────────────────────
cat > "$PLIST_PATH" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${LABEL}</string>

  <key>ProgramArguments</key>
  <array>
    <string>${PYTHON3}</string>
    <string>-u</string>
    <string>${SCRIPT_PATH}</string>
  </array>

  <key>EnvironmentVariables</key>
  <dict>
    <key>KAKAOTALK_PORT</key>
    <string>8401</string>
    <key>OLLAMA_HOST</key>
    <string>http://localhost:11434</string>
    <key>GEMINI_API_KEY</key>
    <string>${GEMINI_API_KEY_VAL}</string>
    <key>KAKAO_CALLBACK_SECRET</key>
    <string>${KAKAO_SECRET_VAL}</string>
    <key>PATH</key>
    <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
  </dict>

  <key>WorkingDirectory</key>
  <string>${SKILL_DIR}</string>

  <!-- 서비스 유지: 비정상 종료 시 자동 재시작 -->
  <key>KeepAlive</key>
  <dict>
    <key>SuccessfulExit</key>
    <false/>
  </dict>

  <!-- 로그 -->
  <key>StandardOutPath</key>
  <string>${LOG_FILE}</string>
  <key>StandardErrorPath</key>
  <string>${ERR_FILE}</string>

  <!-- 부팅 후 자동 실행 -->
  <key>RunAtLoad</key>
  <true/>

  <!-- 충돌 복구: 10초 후 재시작 -->
  <key>ThrottleInterval</key>
  <integer>10</integer>
</dict>
</plist>
PLIST

chmod 644 "$PLIST_PATH"
echo "✅ plist 생성: $PLIST_PATH"

# ─── 서비스 등록 + 시작 ───────────────────────────────────────────────────────
launchctl load -w "$PLIST_PATH"
echo "✅ launchd 서비스 등록 완료: $LABEL"
sleep 2

# ─── 상태 확인 ─────────────────────────────────────────────────────────────────
if launchctl list | grep -q "$LABEL"; then
  PID=$(launchctl list | grep "$LABEL" | awk '{print $1}')
  echo "✅ 서비스 실행 중 (PID: $PID)"
else
  echo "⚠️  서비스 시작 실패. 로그 확인: $ERR_FILE"
  exit 1
fi

# ─── 웹훅 헬스체크 ────────────────────────────────────────────────────────────
sleep 1
echo ""
echo "🔍 헬스체크 (POST /kakao 준비 대기)..."
if curl -sf http://localhost:8401/health > /dev/null 2>&1; then
  echo "✅ 서버 응답 정상"
else
  echo "⚠️  서버 아직 시작 중... 잠시 후 확인: curl http://localhost:8401/health"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  카카오톡 채널 웹훅 서버 설치 완료!"
echo ""
echo "  웹훅 URL (로컬): http://localhost:8401/kakao"
echo "  외부 노출:        bash scripts/ngrok-setup.sh"
echo ""
echo "  서비스 관리:"
echo "    중지: launchctl unload ~/Library/LaunchAgents/${LABEL}.plist"
echo "    시작: launchctl load   ~/Library/LaunchAgents/${LABEL}.plist"
echo "    로그: tail -f $LOG_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
