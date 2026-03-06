#!/bin/bash
# 병원 통합 검색 스크립트 (이름/지역/종별/진료과목)
# 사용법:
#   ./hospital_search.sh --name "서울대" 
#   ./hospital_search.sh --sido 110000 --type 01
#   ./hospital_search.sh --sido 410000 --name "용인"
#   ./hospital_search.sh --dgsbjtCd 01    (진료과목코드: 01=내과)

set -euo pipefail

API_KEY=$(cat ~/.config/data-go-kr/api_key 2>/dev/null || echo "")
if [ -z "$API_KEY" ]; then
    echo '{"error": "API key not found"}' >&2
    exit 1
fi

# 기본값
SIDO_CD=""
SGGU_CD=""
HOSP_NAME=""
CL_CD=""
DGSBJ_CD=""
PAGE_NO="1"
NUM_OF_ROWS="20"

# 파라미터 파싱
while [[ $# -gt 0 ]]; do
    case "$1" in
        --sido)    SIDO_CD="$2"; shift 2 ;;
        --sggu)    SGGU_CD="$2"; shift 2 ;;
        --name)    HOSP_NAME="$2"; shift 2 ;;
        --type)    CL_CD="$2"; shift 2 ;;
        --dgsbjtCd) DGSBJ_CD="$2"; shift 2 ;;
        --page)    PAGE_NO="$2"; shift 2 ;;
        --rows)    NUM_OF_ROWS="$2"; shift 2 ;;
        *) shift ;;
    esac
done

URL="https://apis.data.go.kr/B551182/hospInfoServicev2/getHospBasisList"

# 동적 파라미터 구성
PARAMS="serviceKey=${API_KEY}&pageNo=${PAGE_NO}&numOfRows=${NUM_OF_ROWS}&_type=json"
[ -n "$SIDO_CD" ] && PARAMS="${PARAMS}&sidoCd=${SIDO_CD}"
[ -n "$SGGU_CD" ] && PARAMS="${PARAMS}&sgguCd=${SGGU_CD}"
[ -n "$CL_CD" ] && PARAMS="${PARAMS}&clCd=${CL_CD}"
[ -n "$DGSBJ_CD" ] && PARAMS="${PARAMS}&dgsbjtCd=${DGSBJ_CD}"

# yadmNm은 URL 인코딩 필요
if [ -n "$HOSP_NAME" ]; then
    ENCODED_NAME=$(python3 -c "import urllib.parse; print(urllib.parse.quote('${HOSP_NAME}'))")
    PARAMS="${PARAMS}&yadmNm=${ENCODED_NAME}"
fi

RESPONSE=$(curl -s "${URL}?${PARAMS}")

echo "$RESPONSE" | python3 -c "
import sys, json

try:
    data = json.load(sys.stdin)
    body = data.get('response', {}).get('body', {})
    items = body.get('items', {})
    
    if isinstance(items, dict):
        item_list = items.get('item', [])
        if isinstance(item_list, dict):
            item_list = [item_list]
    elif isinstance(items, str) and items == '':
        item_list = []
    else:
        item_list = []
    
    # 간결한 출력
    hospitals = []
    for h in item_list:
        hospitals.append({
            'name': h.get('yadmNm', ''),
            'ykiho': h.get('ykiho', ''),
            'type': h.get('clCdNm', ''),
            'addr': h.get('addr', ''),
            'tel': h.get('telno', ''),
            'url': h.get('hospUrl', ''),
            'doctors': h.get('drTotCnt', ''),
            'lon': h.get('XPos', ''),
            'lat': h.get('YPos', ''),
        })
    
    result = {
        'totalCount': body.get('totalCount', 0),
        'page': body.get('pageNo', 1),
        'hospitals': hospitals
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
except Exception as e:
    raw = sys.stdin.read() if hasattr(sys.stdin, 'read') else ''
    print(json.dumps({'error': str(e)}, ensure_ascii=False, indent=2))
"
