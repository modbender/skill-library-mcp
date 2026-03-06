#!/bin/bash
# 병원 상세정보 통합 조회 스크립트 (curl 기반, 병렬 호출)
# 사용법: ./hospital_detail.sh <ykiho> [항목]
# 항목: all(기본), subject, detail, transport, nursing, equipment, specialist
# 예시: ./hospital_detail.sh "JDQ4MTg4MSM1..." all

set -euo pipefail

YKIHO="${1:-}"
ITEMS="${2:-all}"

if [ -z "$YKIHO" ]; then
    echo '{"error": "Usage: hospital_detail.sh <ykiho> [all|subject|detail|transport|nursing|equipment|specialist]"}' >&2
    exit 1
fi

API_KEY=$(cat ~/.config/data-go-kr/api_key)
BASE="https://apis.data.go.kr/B551182/MadmDtlInfoService2.7"
TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT

# 엔드포인트 매핑
declare -A EP_MAP=(
    [subject]="getDgsbjtInfo2.7"
    [detail]="getDtlInfo2.7"
    [specialist]="getSpcSbjtSdrInfo2.7"
    [transport]="getTrnsprtInfo2.7"
    [equipment]="getEqpInfo2.7"
    [nursing]="getNursigGrdInfo2.7"
)

if [ "$ITEMS" = "all" ]; then
    SELECTED="subject detail specialist transport equipment nursing"
else
    SELECTED=$(echo "$ITEMS" | tr ',' ' ')
fi

# 병렬로 curl 호출
for key in $SELECTED; do
    ep="${EP_MAP[$key]:-}"
    [ -z "$ep" ] && continue
    curl -s --max-time 20 -G "${BASE}/${ep}" \
        --data-urlencode "serviceKey=${API_KEY}" \
        --data-urlencode "ykiho=${YKIHO}" \
        --data "_type=json" \
        --data "numOfRows=100" \
        -o "${TMPDIR}/${key}.json" &
done
wait

# 결과 합치기
python3 - "$YKIHO" "$TMPDIR" $SELECTED << 'PYEOF'
import json, sys, os, glob

ykiho = sys.argv[1]
tmpdir = sys.argv[2]
selected = sys.argv[3:]

label_map = {
    'subject': '진료과목',
    'detail': '세부정보',
    'specialist': '전문의',
    'transport': '교통',
    'equipment': '시설장비',
    'nursing': '간호등급',
}

result = {'ykiho': ykiho}

for key in selected:
    label = label_map.get(key, key)
    fpath = os.path.join(tmpdir, f'{key}.json')
    if not os.path.exists(fpath):
        result[label] = {'error': 'no_response'}
        continue
    try:
        with open(fpath) as f:
            data = json.load(f)
        body = data.get('response', {}).get('body', {})
        items = body.get('items', {})
        if isinstance(items, dict):
            il = items.get('item', [])
            if isinstance(il, dict):
                il = [il]
        elif isinstance(items, str) and items == '':
            il = []
        else:
            il = []
        result[label] = il
    except Exception as e:
        result[label] = {'error': str(e)}

print(json.dumps(result, ensure_ascii=False, indent=2))
PYEOF
