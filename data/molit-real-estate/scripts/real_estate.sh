#!/bin/bash
# 국토부 아파트 매매 실거래가 조회
# Usage: real_estate.sh [법정동코드5자리] [계약년월YYYYMM] [결과수]
set -e

LAWD_CD=${1:-11680}
DEAL_YMD=${2:-$(date +%Y%m)}
NUM=${3:-10}

python3 -c "
import urllib.request, urllib.parse, sys, json, xml.etree.ElementTree as ET

key = open('/home/scott/.config/data-go-kr/api_key').read().strip()
base = 'https://apis.data.go.kr/1613000/RTMSDataSvcAptTrade/getRTMSDataSvcAptTrade'
params = urllib.parse.urlencode({
    'serviceKey': key,
    'LAWD_CD': '${LAWD_CD}',
    'DEAL_YMD': '${DEAL_YMD}',
    'pageNo': '1',
    'numOfRows': '${NUM}'
})
url = f'{base}?{params}'
try:
    with urllib.request.urlopen(url, timeout=15) as r:
        data = r.read().decode()
    root = ET.fromstring(data)
    items = root.findall('.//item')
    result = []
    for item in items:
        result.append({
            'aptNm': item.findtext('aptNm','').strip(),
            'dealAmount': item.findtext('dealAmount','').strip(),
            'excluUseAr': item.findtext('excluUseAr','').strip(),
            'floor': item.findtext('floor','').strip(),
            'buildYear': item.findtext('buildYear','').strip(),
            'dealYear': item.findtext('dealYear',''),
            'dealMonth': item.findtext('dealMonth',''),
            'dealDay': item.findtext('dealDay','').strip(),
            'dealingGbn': item.findtext('dealingGbn','').strip(),
        })
    print(json.dumps(result, ensure_ascii=False, indent=2))
except Exception as e:
    print(json.dumps({'error': str(e)}))
"
