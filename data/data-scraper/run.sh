#!/bin/bash
# data-scraper/run.sh
# 웹페이지 데이터 수집 (curl 기반)

set -e

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
EVENTS_DIR="${EVENTS_DIR:-$WORKSPACE/events}"
MEMORY_DIR="${MEMORY_DIR:-$WORKSPACE/memory}"

URL=""
FORMAT="text"

# 인자 파싱
while [[ $# -gt 0 ]]; do
  case "$1" in
    --url)
      URL="$2"
      shift 2
      ;;
    --format)
      FORMAT="$2"
      shift 2
      ;;
    *)
      echo "❌ 알 수 없는 옵션: $1"
      echo "사용법: run.sh --url URL [--format text|html]"
      exit 1
      ;;
  esac
done

# URL 필수 체크
if [ -z "$URL" ]; then
  echo "❌ URL이 필요합니다."
  echo "사용법: run.sh --url URL [--format text|html]"
  exit 1
fi

echo "🔍 스크래핑 시작: $URL"

# curl로 페이지 다운로드
TMP_FILE=$(mktemp)
if ! curl -s -L -A "Mozilla/5.0" "$URL" > "$TMP_FILE"; then
  echo "❌ URL 접근 실패: $URL"
  rm -f "$TMP_FILE"
  exit 1
fi

# 형식에 따라 출력
if [ "$FORMAT" = "html" ]; then
  cat "$TMP_FILE"
else
  # HTML 태그 제거 (간단한 텍스트 추출)
  # lynx 설치되어 있으면 사용, 아니면 sed로 처리
  if command -v lynx &> /dev/null; then
    lynx -dump -nolist "$TMP_FILE"
  else
    # 간단한 HTML 태그 제거
    sed -e 's/<[^>]*>//g' \
        -e 's/&nbsp;/ /g' \
        -e 's/&lt;/</g' \
        -e 's/&gt;/>/g' \
        -e 's/&amp;/\&/g' \
        -e '/^\s*$/d' \
        "$TMP_FILE"
  fi
fi

# 임시 파일 삭제
rm -f "$TMP_FILE"

# 이벤트 생성
mkdir -p "$EVENTS_DIR"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%S+09:00")
EVENT_FILE="$EVENTS_DIR/scrape-result-$(date +%Y-%m-%d-%H%M%S).json"

cat > "$EVENT_FILE" <<EOF
{
  "type": "scrape-result",
  "source": "data-scraper",
  "timestamp": "$TIMESTAMP",
  "data": {
    "url": "$URL",
    "format": "$FORMAT",
    "note": "스크래핑 완료. 출력은 stdout 참고."
  },
  "consumers": ["daily-report"]
}
EOF

echo "" >&2
echo "✅ 이벤트 생성: $EVENT_FILE" >&2

exit 0
