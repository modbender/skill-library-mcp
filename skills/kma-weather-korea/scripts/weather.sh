#!/bin/bash
# 기상청 단기예보 API 조회 스크립트

set -euo pipefail

# API 키 읽기
API_KEY=$(cat ~/.config/data-go-kr/api_key 2>/dev/null || echo "")
if [ -z "$API_KEY" ]; then
    echo '{"error": "API key not found at ~/.config/data-go-kr/api_key"}' >&2
    exit 1
fi

# 기본값
API_TYPE="${1:-ncst}"
NX="${2:-60}"  # 서울 종로구
NY="${3:-127}"

# 현재 날짜/시각
NOW=$(date +"%Y%m%d %H%M")
BASE_DATE=$(echo $NOW | cut -d' ' -f1)
CURRENT_TIME=$(echo $NOW | cut -d' ' -f2)
CURRENT_HOUR=$(echo $CURRENT_TIME | cut -c1-2)
CURRENT_MIN=$(echo $CURRENT_TIME | cut -c3-4)

# base_time 계산 함수
get_base_time_ncst() {
    # 초단기실황: 매시 정각, 10분 후 조회 가능
    local hour=$1
    local min=$2
    
    if [ $min -lt 10 ]; then
        # 아직 발표 전 → 이전 시간
        hour=$((10#$hour - 1))
        if [ $hour -lt 0 ]; then
            hour=23
            BASE_DATE=$(date -d "$BASE_DATE -1 day" +%Y%m%d)
        fi
    fi
    
    printf "%02d00" $hour
}

get_base_time_fcst() {
    # 초단기예보: 매 30분, 10분 후 조회 가능
    local hour=$1
    local min=$2
    
    if [ $min -lt 40 ]; then
        # 30분 발표분 조회 가능
        if [ $min -ge 10 ]; then
            printf "%02d30" $hour
        else
            # 이전 시간 30분
            hour=$((10#$hour - 1))
            if [ $hour -lt 0 ]; then
                hour=23
                BASE_DATE=$(date -d "$BASE_DATE -1 day" +%Y%m%d)
            fi
            printf "%02d30" $hour
        fi
    else
        # 정각 발표분 조회 가능
        printf "%02d00" $((10#$hour + 1))
    fi
}

get_base_time_short() {
    # 단기예보: 0200, 0500, 0800, 1100, 1400, 1700, 2000, 2300
    local hour=$1
    local times=(02 05 08 11 14 17 20 23)
    
    for time in "${times[@]}"; do
        if [ $((10#$hour)) -ge $((10#$time)) ]; then
            BASE_TIME="${time}00"
        fi
    done
    
    echo $BASE_TIME
}

# API 엔드포인트 선택
case "$API_TYPE" in
    ncst|실황)
        ENDPOINT="getUltraSrtNcst"
        BASE_TIME=$(get_base_time_ncst $CURRENT_HOUR $CURRENT_MIN)
        ;;
    fcst|초단기|예보)
        ENDPOINT="getUltraSrtFcst"
        BASE_TIME=$(get_base_time_fcst $CURRENT_HOUR $CURRENT_MIN)
        ;;
    short|단기)
        ENDPOINT="getVilageFcst"
        BASE_TIME=$(get_base_time_short $CURRENT_HOUR)
        ;;
    version|버전)
        ENDPOINT="getFcstVersion"
        BASE_TIME="0000"
        ;;
    *)
        echo '{"error": "Invalid API type. Use: ncst, fcst, short, version"}' >&2
        exit 1
        ;;
esac

# API 호출
URL="https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/${ENDPOINT}"

PARAMS="serviceKey=${API_KEY}"
PARAMS="${PARAMS}&pageNo=1"
PARAMS="${PARAMS}&numOfRows=1000"
PARAMS="${PARAMS}&dataType=JSON"
PARAMS="${PARAMS}&base_date=${BASE_DATE}"
PARAMS="${PARAMS}&base_time=${BASE_TIME}"
PARAMS="${PARAMS}&nx=${NX}"
PARAMS="${PARAMS}&ny=${NY}"

# 디버그 정보 (stderr로 출력)
echo "API: $ENDPOINT | Date: $BASE_DATE | Time: $BASE_TIME | Grid: ($NX,$NY)" >&2

# 요청 실행
RESPONSE=$(curl -s -G "$URL" --data-urlencode "serviceKey=$API_KEY" \
    --data "pageNo=1" \
    --data "numOfRows=1000" \
    --data "dataType=JSON" \
    --data "base_date=$BASE_DATE" \
    --data "base_time=$BASE_TIME" \
    --data "nx=$NX" \
    --data "ny=$NY")

# 응답 출력
echo "$RESPONSE" | jq '.'
