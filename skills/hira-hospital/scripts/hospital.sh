#!/bin/bash
# 건강보험심사평가원 병원정보 조회 스크립트

set -euo pipefail

# API 키 읽기
API_KEY=$(cat ~/.config/data-go-kr/api_key 2>/dev/null || echo "")
if [ -z "$API_KEY" ]; then
    echo '{"error": "API key not found at ~/.config/data-go-kr/api_key"}' >&2
    exit 1
fi

# 파라미터
SIDO_CD="${1:-110000}"  # 시도코드 (기본: 서울)
HOSP_TYPE="${2:-병원}"  # 병원 종류
PAGE_NO="${3:-1}"
NUM_OF_ROWS="${4:-100}"

# API 호출
URL="https://apis.data.go.kr/B551182/hospInfoServicev2/getHospBasisList"

# 디버그 정보
echo "시도: $SIDO_CD | 종별: $HOSP_TYPE" >&2

# 요청 실행
RESPONSE=$(curl -s -G "$URL" \
    --data-urlencode "serviceKey=$API_KEY" \
    --data "sidoCd=$SIDO_CD" \
    --data "pageNo=$PAGE_NO" \
    --data "numOfRows=$NUM_OF_ROWS")

# XML을 JSON으로 변환
if command -v python3 &> /dev/null; then
    echo "$RESPONSE" | python3 -c "
import sys
import json
import xml.etree.ElementTree as ET

try:
    xml_str = sys.stdin.read()
    root = ET.fromstring(xml_str)
    
    # 헤더 파싱
    header = {}
    header_elem = root.find('.//header')
    if header_elem:
        for child in header_elem:
            header[child.tag] = child.text
    
    # 바디 파싱
    body = {}
    body_elem = root.find('.//body')
    if body_elem:
        for child in body_elem:
            if child.tag != 'items':
                body[child.tag] = child.text
    
    # 아이템 파싱
    items = []
    items_elem = root.find('.//items')
    if items_elem:
        for item in items_elem.findall('item'):
            item_dict = {}
            for child in item:
                item_dict[child.tag] = child.text
            # 종별 필터링
            if '$HOSP_TYPE' == '병원' or item_dict.get('clCdNm', '').find('$HOSP_TYPE') >= 0:
                items.append(item_dict)
    
    result = {
        'response': {
            'header': header,
            'body': {
                **body,
                'items': items
            }
        }
    }
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
except Exception as e:
    print(json.dumps({'error': str(e), 'raw': xml_str[:500]}, ensure_ascii=False, indent=2))
"
else
    # python3 없으면 XML 그대로 출력
    echo "$RESPONSE"
fi
