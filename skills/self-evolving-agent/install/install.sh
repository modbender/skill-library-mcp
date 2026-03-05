#!/usr/bin/env bash
# ============================================================
# install.sh — Self-Evolving Agent v5.0 Stream Monitor 설치
#
# 역할: LaunchAgent(macOS) 또는 systemd(Linux) 서비스를
#       실제 설치 경로에 맞게 자동 구성하여 설치.
#
# 사용법:
#   bash install/install.sh          # 자동 OS 감지
#   bash install/install.sh --uninstall  # 제거
#   bash install/install.sh --dry-run    # 실제 변경 없이 미리보기
#
# 변경 이력:
#   v5.0 (2026-02-18) — 신규 구현
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
MONITOR_SCRIPT="$SKILL_DIR/scripts/v5/stream-monitor.sh"

R=$'\033[0;31m'; G=$'\033[0;32m'; Y=$'\033[1;33m'
C=$'\033[0;36m'; B=$'\033[1m';    N=$'\033[0m'

UNINSTALL=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --uninstall) UNINSTALL=true; shift ;;
    --dry-run)   DRY_RUN=true; shift ;;
    --help|-h)
      echo "Usage: $0 [--uninstall] [--dry-run]"
      exit 0 ;;
    *) echo "Unknown: $1" >&2; exit 1 ;;
  esac
done

run() {
  if [[ "$DRY_RUN" == true ]]; then
    echo -e "  ${Y}[dry-run]${N} $*"
  else
    eval "$*"
  fi
}

# ── OS 감지 ────────────────────────────────────────────────
OS="$(uname -s)"

echo -e "${B}🔧 Self-Evolving Agent v5.0 — Stream Monitor 설치${N}"
echo "스킬 디렉토리: $SKILL_DIR"
echo "모니터 스크립트: $MONITOR_SCRIPT"
echo ""

# ── macOS LaunchAgent ──────────────────────────────────────
install_macos() {
  local plist_src="$SCRIPT_DIR/com.sea.monitor.plist"
  local plist_dst="$HOME/Library/LaunchAgents/com.sea.monitor.plist"
  local launch_agents_dir="$HOME/Library/LaunchAgents"

  if [[ "$UNINSTALL" == true ]]; then
    echo -e "${Y}🗑️  LaunchAgent 제거...${N}"
    if launchctl list | grep -q "com.sea.monitor" 2>/dev/null; then
      run "launchctl unload '$plist_dst' 2>/dev/null || true"
      echo -e "  ${G}✅ LaunchAgent 언로드됨${N}"
    fi
    if [[ -f "$plist_dst" ]]; then
      run "rm -f '$plist_dst'"
      echo -e "  ${G}✅ plist 파일 제거됨${N}"
    fi
    echo -e "${G}✅ 제거 완료${N}"
    return
  fi

  echo -e "${C}macOS LaunchAgent 설치...${N}"

  # 템플릿 복사 + 경로 치환
  run "mkdir -p '$launch_agents_dir'"

  if [[ "$DRY_RUN" == false ]]; then
    sed \
      "s|/Users/Shared/openclaw/skills/self-evolving-agent/scripts/v5/stream-monitor.sh|$MONITOR_SCRIPT|g" \
      "s|/Users/Shared|$HOME|g" \
      "$plist_src" > "$plist_dst"
    echo -e "  ${G}✅ plist 복사됨: $plist_dst${N}"
  else
    echo -e "  ${Y}[dry-run]${N} $plist_src → $plist_dst (경로 치환 포함)"
  fi

  # 기존 서비스 언로드
  if launchctl list | grep -q "com.sea.monitor" 2>/dev/null; then
    run "launchctl unload '$plist_dst' 2>/dev/null || true"
  fi

  # 로드
  run "launchctl load '$plist_dst'"
  echo -e "  ${G}✅ LaunchAgent 로드됨${N}"

  echo ""
  echo -e "${G}✅ 설치 완료!${N}"
  echo ""
  echo "상태 확인: launchctl list | grep sea.monitor"
  echo "로그 확인: tail -f /tmp/sea-monitor.stdout.log"
  echo "CLI 확인:  sea monitor status"
}

# ── Linux systemd ──────────────────────────────────────────
install_linux() {
  local service_src="$SCRIPT_DIR/sea-monitor.service"
  local systemd_dir="$HOME/.config/systemd/user"
  local service_dst="$systemd_dir/sea-monitor.service"

  if [[ "$UNINSTALL" == true ]]; then
    echo -e "${Y}🗑️  systemd 서비스 제거...${N}"
    run "systemctl --user stop sea-monitor 2>/dev/null || true"
    run "systemctl --user disable sea-monitor 2>/dev/null || true"
    if [[ -f "$service_dst" ]]; then
      run "rm -f '$service_dst'"
      echo -e "  ${G}✅ service 파일 제거됨${N}"
    fi
    run "systemctl --user daemon-reload"
    echo -e "${G}✅ 제거 완료${N}"
    return
  fi

  echo -e "${C}Linux systemd 사용자 서비스 설치...${N}"

  run "mkdir -p '$systemd_dir'"

  if [[ "$DRY_RUN" == false ]]; then
    sed \
      "s|%h/openclaw/skills/self-evolving-agent/scripts/v5/stream-monitor.sh|$MONITOR_SCRIPT|g" \
      "$service_src" > "$service_dst"
    echo -e "  ${G}✅ service 파일 복사됨: $service_dst${N}"
  else
    echo -e "  ${Y}[dry-run]${N} $service_src → $service_dst (경로 치환 포함)"
  fi

  run "systemctl --user daemon-reload"
  run "systemctl --user enable sea-monitor"
  run "systemctl --user start sea-monitor"

  echo ""
  echo -e "${G}✅ 설치 완료!${N}"
  echo ""
  echo "상태 확인: systemctl --user status sea-monitor"
  echo "로그 확인: journalctl --user -u sea-monitor -f"
  echo "CLI 확인:  sea monitor status"
}

# ── 진입점 ─────────────────────────────────────────────────
[[ "$DRY_RUN" == true ]] && echo -e "${Y}⚠️  dry-run 모드 (실제 변경 없음)${N}\n"

# 모니터 스크립트 존재 확인
if [[ ! -f "$MONITOR_SCRIPT" ]]; then
  echo -e "${R}❌ stream-monitor.sh 없음: $MONITOR_SCRIPT${N}"
  echo "스킬이 올바르게 설치되어 있는지 확인하세요."
  exit 1
fi

case "$OS" in
  Darwin) install_macos ;;
  Linux)  install_linux ;;
  *)
    echo -e "${R}지원하지 않는 OS: $OS${N}"
    echo "macOS(Darwin) 또는 Linux만 지원합니다."
    echo ""
    echo "수동 설치:"
    echo "  macOS: ~/Library/LaunchAgents/com.sea.monitor.plist"
    echo "  Linux: ~/.config/systemd/user/sea-monitor.service"
    exit 1 ;;
esac
