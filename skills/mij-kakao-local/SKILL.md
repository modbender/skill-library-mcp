# Kakao Local API Skill

**OpenClaw Skill for Kakao Local (Places & Address) API**

## 개요

카카오 로컬 API를 호출하여 주소 정규화 및 장소 검색을 수행하는 OpenClaw Skill입니다.

## 요구사항

- Windows
- PowerShell 5.0+
- curl.exe (Windows 10+ 기본 포함)
- Kakao Developers REST API Key

## API Key 설정

**중요**: API Key는 스킬 파라미터로 전달하지 않습니다 (로그 노출 방지).

### 방법 1: 환경변수 (권장)

```powershell
# 사용자 환경변수로 영구 설정
[Environment]::SetEnvironmentVariable("KAKAO_REST_API_KEY", "your_rest_api_key_here", "User")

# 또는 현재 세션에만 임시 설정
$env:KAKAO_REST_API_KEY = "your_rest_api_key_here"
```

### 방법 2: Config 파일

`skills/kakao-local/data/config.json` (create this file) 생성:

```json
{
  "api_key": "your_rest_api_key_here"
}
```

**⚠️ 주의**: `config.json`은 `.gitignore`에 추가하여 커밋 금지

### API Key 발급

1. [Kakao Developers](https://developers.kakao.com/) 접속
2. 내 애플리케이션 → 앱 추가
3. 앱 키 → REST API 키 복사

## 스킬 함수

### 1. NormalizeAddress (주소 정규화)

사용자가 입력한 주소를 정규화하여 도로명/지번 주소와 좌표로 변환합니다.

**API 엔드포인트**: `GET https://dapi.kakao.com/v2/local/search/address.json`

**입력 파라미터**:
- `-Action "NormalizeAddress"` (필수)
- `-Query "주소 문자열"` (필수)
- `-Size 3` (선택, 기본값: 3)

**출력 형식**:
```json
{
  "ok": true,
  "action": "NormalizeAddress",
  "query": "서울 강남구 테헤란로 152",
  "count": 2,
  "candidates": [
    {
      "roadAddress": "서울 강남구 테헤란로 152",
      "jibunAddress": "서울 강남구 역삼동 737",
      "x": "127.036557561809",
      "y": "37.4985995780801",
      "region": {
        "region1": "서울",
        "region2": "강남구",
        "region3": "역삼동"
      },
      "buildingName": "강남파이낸스센터",
      "zoneNo": "06236"
    }
  ],
  "raw": {}
}
```

**사용 예시**:
```powershell
.\scripts\kakao_local.ps1 -Action NormalizeAddress -Query "판교역로 235"
.\scripts\kakao_local.ps1 -Action NormalizeAddress -Query "서울 강남구" -Size 5
```

### 2. SearchPlace (키워드 장소 검색)

키워드로 장소를 검색합니다. 위치 기반 반경 검색과 카테고리 필터링을 지원합니다.

**API 엔드포인트**: `GET https://dapi.kakao.com/v2/local/search/keyword.json`

**입력 파라미터**:
- `-Action "SearchPlace"` (필수)
- `-Query "검색 키워드"` (필수)
- `-Size 5` (선택, 기본값: 5, 최대: 15)
- `-Page 1` (선택, 기본값: 1, 최대: 45)
- `-X "127.027"` (선택, 중심 경도)
- `-Y "37.498"` (선택, 중심 위도)
- `-Radius 1000` (선택, 검색 반경(m), 최대: 20000)
- `-CategoryGroupCode "CE7"` (선택, 카테고리 그룹 코드)

**카테고리 그룹 코드**:
- MT1: 대형마트
- CS2: 편의점
- PS3: 어린이집, 유치원
- SC4: 학교
- AC5: 학원
- PK6: 주차장
- OL7: 주유소, 충전소
- SW8: 지하철역
- BK9: 은행
- CT1: 문화시설
- AG2: 중개업소
- PO3: 공공기관
- AT4: 관광명소
- AD5: 숙박
- FD6: 음식점
- CE7: 카페
- HP8: 병원
- PM9: 약국

**출력 형식**:
```json
{
  "ok": true,
  "action": "SearchPlace",
  "query": "대형카페",
  "count": 5,
  "totalCount": 128,
  "isEnd": false,
  "items": [
    {
      "id": "8739036",
      "name": "스타벅스 강남점",
      "roadAddress": "서울 강남구 테헤란로 152",
      "jibunAddress": "서울 강남구 역삼동 737",
      "x": "127.036557561809",
      "y": "37.4985995780801",
      "phone": "02-1234-5678",
      "categoryName": "음식점 > 카페",
      "placeUrl": "http://place.map.kakao.com/8739036",
      "distance": "245"
    }
  ],
  "raw": {}
}
```

**사용 예시**:
```powershell
# 기본 검색
.\scripts\kakao_local.ps1 -Action SearchPlace -Query "대형카페"

# 개수 지정
.\scripts\kakao_local.ps1 -Action SearchPlace -Query "브런치 맛집" -Size 10

# 위치 기반 반경 검색
.\scripts\kakao_local.ps1 -Action SearchPlace -Query "카페" -X "127.027" -Y "37.498" -Radius 1000

# 카테고리 필터링
.\scripts\kakao_local.ps1 -Action SearchPlace -Query "카페" -CategoryGroupCode "CE7" -Size 15

# 페이지네이션
.\scripts\kakao_local.ps1 -Action SearchPlace -Query "주차 가능한 카페" -Page 2 -Size 10
```

## 에러 처리

### API Key 없음
```json
{
  "ok": false,
  "errorType": "MissingApiKey",
  "message": "Set KAKAO_REST_API_KEY env var or create config.json",
  "setupGuide": "https://developers.kakao.com/"
}
```

### API Key 잘못됨 (401/403)
```json
{
  "ok": false,
  "errorType": "InvalidApiKey",
  "message": "Invalid or expired API key",
  "statusCode": 401
}
```

### API 호출 실패
```json
{
  "ok": false,
  "errorType": "ApiError",
  "message": "Failed to call Kakao API",
  "details": "..."
}
```

### 결과 없음
```json
{
  "ok": true,
  "action": "SearchPlace",
  "query": "존재하지않는장소12345",
  "count": 0,
  "items": []
}
```

## 통합 예시 (상위 에이전트/챗봇)

```powershell
# 주소 정규화 후 즐겨찾기 저장
$result = .\skills\kakao-local\scripts\kakao_local.ps1 -Action NormalizeAddress -Query "홍대입구역"
$data = $result | ConvertFrom-Json

if ($data.ok -and $data.count -gt 0) {
    $best = $data.candidates[0]

    # 즐겨찾기에 추가
    $places = Get-Content ".\skills\kakao-local\data\places.json" -Raw | ConvertFrom-Json
    $places | Add-Member -NotePropertyName "홍대" -NotePropertyValue @{
        roadAddress = $best.roadAddress
        x = $best.x
        y = $best.y
        savedAt = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
    } -Force
    $places | ConvertTo-Json -Depth 10 | Out-File ".\skills\kakao-local\data\places.json" -Encoding UTF8

    Write-Host "✅ 즐겨찾기 저장: 홍대 → $($best.roadAddress)"
}

# 장소 검색 후 상위 3개 추천
$result = .\skills\kakao-local\scripts\kakao_local.ps1 -Action SearchPlace -Query "주차 가능한 카페" -Size 10
$data = $result | ConvertFrom-Json

if ($data.ok -and $data.count -gt 0) {
    Write-Host "`n🌟 추천 장소 TOP 3:"
    $top3 = $data.items | Select-Object -First 3
    $index = 1
    foreach ($place in $top3) {
        Write-Host "`n[$index] $($place.name)"
        Write-Host "    📍 $($place.roadAddress)"
        Write-Host "    📞 $($place.phone)"
        Write-Host "    🔗 $($place.placeUrl)"
        $index++
    }

    # 캐시에 저장 (중복 검색 방지)
    $cache = @{
        query = $data.query
        timestamp = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
        ttl = 3600  # 1시간
        results = $data.items
    }
    $cache | ConvertTo-Json -Depth 10 | Out-File ".\skills\kakao-local\data\cache.json" -Encoding UTF8
}
```

## 테스트 시나리오

### 1. 주소 정규화 테스트
```powershell
.\scripts\kakao_local.ps1 -Action NormalizeAddress -Query "서울 강남구 테헤란로 152"
# 기대: 도로명/지번 주소와 좌표 출력
```

### 2. 장소 검색 테스트
```powershell
.\scripts\kakao_local.ps1 -Action SearchPlace -Query "대형카페" -Size 5
# 기대: 5개 카페 목록 출력
```

### 3. API Key 미설정 테스트
```powershell
# 환경변수 임시 제거
$backup = $env:KAKAO_REST_API_KEY
$env:KAKAO_REST_API_KEY = $null

.\scripts\kakao_local.ps1 -Action SearchPlace -Query "카페"
# 기대: {"ok": false, "errorType": "MissingApiKey", ...}

# 복구
$env:KAKAO_REST_API_KEY = $backup
```

### 4. 잘못된 API Key 테스트
```powershell
$env:KAKAO_REST_API_KEY = "invalid_key_12345"
.\scripts\kakao_local.ps1 -Action SearchPlace -Query "카페"
# 기대: {"ok": false, "errorType": "InvalidApiKey", ...}
```

## 파일 구조

```
skills/kakao-local/
  ├── SKILL.md                    # 이 파일 (스킬 명세)
  ├── README.md                   # Quick Start
  ├── .gitignore                  # config.json 보호
  ├── scripts/
  │   └── kakao_local.ps1         # 메인 스킬 스크립트
  └── data/
      ├── config.json.template    # API Key 설정 템플릿
      ├── places.json             # 즐겨찾기 (선택)
      └── cache.json              # 검색 캐시 (선택)
```

## 라이선스

MIT License

---

## Publish-safe packaging note

This registry upload is "text-only" compatible: script sources are embedded under `references/` as Markdown.

To use the skill locally:
1) Copy `references/kakao_local.ps1.md` content into a file: `scripts/kakao_local.ps1`
2) Copy `references/config.json.template.md` content into: `data/config.json.template`
3) Set API key via env var `KAKAO_REST_API_KEY` (recommended) or create `data/config.json` (gitignored).
