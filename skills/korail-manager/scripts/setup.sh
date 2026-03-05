#!/bin/bash
set -e

# 스크립트의 위치를 기준으로 프로젝트 루트로 이동
cd "$(dirname "$0")/.."

echo "🔨 대장간(가상 환경) 건설을 시작하옵니다..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ 대장간 건설 완료."
else
    echo "ℹ️ 대장간이 이미 존재하옵니다."
fi

echo "📦 필요한 부품(의존성)을 설치하옵니다..."
./venv/bin/pip install -r requirements.txt

echo ""
echo "🎉 모든 준비가 완료되었나이다!"
echo ""
echo "📋 사용 가능한 명령:"
echo "  [KTX]"
echo "    venv/bin/python scripts/search.py --dep \"서울\" --arr \"부산\" --date \"20260210\""
echo "    venv/bin/python scripts/watch.py --dep \"서울\" --arr \"부산\" --date \"20260210\" --start-time 9 --end-time 18 --interval 300"
echo "    venv/bin/python scripts/cancel.py [--date \"20260210\"]"
echo ""
echo "  [SRT]"
echo "    venv/bin/python scripts/srt_search.py --dep \"수서\" --arr \"대전\" --date \"20260210\""
echo "    venv/bin/python scripts/srt_watch.py --dep \"수서\" --arr \"대전\" --date \"20260210\" --start-time 9 --end-time 18 --interval 300"
echo "    venv/bin/python scripts/cancel_srt.py [--date \"20260210\"]"
