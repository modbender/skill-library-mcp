# kakao_local.ps1\n\n`powershell\n<#
.SYNOPSIS
    Kakao Local API Skill for OpenClaw

.DESCRIPTION
    카카오 로컬 API를 curl.exe로 호출하여 주소 정규화 및 장소 검색 수행

.PARAMETER Action
    수행할 작업: NormalizeAddress, SearchPlace

.PARAMETER Query
    검색 쿼리 (주소 또는 키워드) - 필수

.PARAMETER Size
    결과 개수 (기본값: NormalizeAddress=3, SearchPlace=5)

.PARAMETER Page
    페이지 번호 (기본값: 1)

.PARAMETER X
    중심 좌표 경도 (선택)

.PARAMETER Y
    중심 좌표 위도 (선택)

.PARAMETER Radius
    검색 반경(m) (기본값: 20000)

.PARAMETER CategoryGroupCode
    카테고리 그룹 코드 (선택)

.PARAMETER Output
    출력 형식 (기본값: json, 고정)

.EXAMPLE
    .\kakao_local.ps1 -Action NormalizeAddress -Query "서울 강남구 테헤란로 152"

.EXAMPLE
    .\kakao_local.ps1 -Action SearchPlace -Query "대형카페" -Size 10

.EXAMPLE
    .\kakao_local.ps1 -Action SearchPlace -Query "카페" -X "127.027" -Y "37.498" -Radius 1000
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("NormalizeAddress", "SearchPlace")]
    [string]$Action,

    [Parameter(Mandatory=$true)]
    [string]$Query,

    [Parameter(Mandatory=$false)]
    [int]$Size = 0,

    [Parameter(Mandatory=$false)]
    [int]$Page = 1,

    [Parameter(Mandatory=$false)]
    [string]$X,

    [Parameter(Mandatory=$false)]
    [string]$Y,

    [Parameter(Mandatory=$false)]
    [int]$Radius = 20000,

    [Parameter(Mandatory=$false)]
    [string]$CategoryGroupCode,

    [Parameter(Mandatory=$false)]
    [string]$Output = "json"
)

# UTF-8 출력 강제 설정 (PS 5.x 인코딩 깨짐 방지: BOM 없는 UTF-8)
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$OutputEncoding = $utf8NoBom
[Console]::OutputEncoding = $utf8NoBom

# ============================================
# API Key 로드 함수
# ============================================
function Get-ApiKey {
    # 1순위: 환경변수 (User)
    $apiKey = [Environment]::GetEnvironmentVariable("KAKAO_REST_API_KEY", "User")
    if (-not [string]::IsNullOrEmpty($apiKey)) {
        return $apiKey
    }

    # 2순위: 환경변수 (Process)
    $apiKey = [Environment]::GetEnvironmentVariable("KAKAO_REST_API_KEY", "Process")
    if (-not [string]::IsNullOrEmpty($apiKey)) {
        return $apiKey
    }

    $apiKey = $env:KAKAO_REST_API_KEY
    if (-not [string]::IsNullOrEmpty($apiKey)) {
        return $apiKey
    }

    # 3순위: config.json 파일
    $configPath = Join-Path $PSScriptRoot "..\data\config.json"
    if (Test-Path $configPath) {
        try {
            $config = Get-Content $configPath -Raw -Encoding UTF8 | ConvertFrom-Json
            if ($config.api_key -and $config.api_key -ne "your_rest_api_key_here") {
                return $config.api_key
            }
        }
        catch {
            # 파일 읽기 실패 시 무시
        }
    }

    return $null
}

# ============================================
# curl.exe로 API 호출 함수
# ============================================
function Invoke-KakaoApiWithCurl {
    param(
        [string]$Endpoint,
        [hashtable]$Params,
        [string]$ApiKey
    )

    try {
        # URL 인코딩된 쿼리 문자열 생성
        $queryParts = @()
        foreach ($key in $Params.Keys) {
            $value = [System.Uri]::EscapeDataString($Params[$key])
            $queryParts += "${key}=${value}"
        }
        $queryString = $queryParts -join "&"

        $url = "${Endpoint}?${queryString}"

        # curl.exe 명령 실행 (PowerShell의 curl 별칭 회피)
        $curlPath = "curl.exe"

        # 헤더 설정
        $authHeader = "Authorization: KakaoAK ${ApiKey}"

        # curl.exe 실행
        $response = & $curlPath -s -X GET $url -H $authHeader -H "Content-Type: application/json;charset=UTF-8"

        # HTTP 상태 코드 확인을 위한 재호출 (헤더 포함)
        $statusLine = & $curlPath -s -I -X GET $url -H $authHeader | Select-String "HTTP/"

        # JSON 파싱
        if ($response) {
            $jsonResponse = $response | ConvertFrom-Json

            # 에러 응답 확인
            if ($jsonResponse.errorType -or $jsonResponse.error) {
                return @{
                    success = $false
                    statusCode = 401
                    response = $jsonResponse
                }
            }

            return @{
                success = $true
                statusCode = 200
                response = $jsonResponse
            }
        }
        else {
            throw "Empty response from API"
        }
    }
    catch {
        return @{
            success = $false
            statusCode = 0
            error = $_.Exception.Message
        }
    }
}

# ============================================
# 주소 정규화 함수
# ============================================
function Invoke-NormalizeAddress {
    param(
        [string]$Query,
        [int]$Size,
        [string]$ApiKey
    )

    # Size 기본값 설정
    if ($Size -eq 0) {
        $Size = 3
    }

    $params = @{
        query = $Query
        size = $Size.ToString()
    }

    $result = Invoke-KakaoApiWithCurl -Endpoint "https://dapi.kakao.com/v2/local/search/address.json" -Params $params -ApiKey $ApiKey

    if (-not $result.success) {
        # API 에러 처리
        if ($result.statusCode -eq 401 -or $result.statusCode -eq 403) {
            return @{
                ok = $false
                errorType = "InvalidApiKey"
                message = "Invalid or expired API key"
                statusCode = $result.statusCode
            } | ConvertTo-Json -Compress
        }
        else {
            return @{
                ok = $false
                errorType = "ApiError"
                message = "Failed to call Kakao API"
                details = $result.error
            } | ConvertTo-Json -Compress
        }
    }

    $apiResponse = $result.response

    # 응답 데이터 가공
    $candidates = @()
    foreach ($doc in $apiResponse.documents) {
        $candidate = @{
            roadAddress = ""
            jibunAddress = ""
            x = $doc.x
            y = $doc.y
            region = @{}
            buildingName = ""
            zoneNo = ""
        }

        # 지번 주소
        if ($doc.address) {
            $candidate.jibunAddress = $doc.address.address_name
            $candidate.region = @{
                region1 = $doc.address.region_1depth_name
                region2 = $doc.address.region_2depth_name
                region3 = $doc.address.region_3depth_name
            }
        }

        # 도로명 주소
        if ($doc.road_address) {
            $candidate.roadAddress = $doc.road_address.address_name
            $candidate.buildingName = $doc.road_address.building_name
            $candidate.zoneNo = $doc.road_address.zone_no
        }
        else {
            $candidate.roadAddress = $candidate.jibunAddress
        }

        $candidates += $candidate
    }

    # 출력 규격에 맞춘 결과
    $output = @{
        ok = $true
        action = "NormalizeAddress"
        query = $Query
        count = $candidates.Count
        candidates = $candidates
        raw = $apiResponse
    }

    return $output | ConvertTo-Json -Depth 10 -Compress
}

# ============================================
# 장소 검색 함수
# ============================================
function Invoke-SearchPlace {
    param(
        [string]$Query,
        [int]$Size,
        [int]$Page,
        [string]$X,
        [string]$Y,
        [int]$Radius,
        [string]$CategoryGroupCode,
        [string]$ApiKey
    )

    # Size 기본값 설정
    if ($Size -eq 0) {
        $Size = 5
    }

    $params = @{
        query = $Query
        size = $Size.ToString()
        page = $Page.ToString()
    }

    # 선택적 파라미터 추가
    if ($X -and $Y) {
        $params.Add("x", $X)
        $params.Add("y", $Y)
        $params.Add("radius", $Radius.ToString())
    }

    if ($CategoryGroupCode) {
        $params.Add("category_group_code", $CategoryGroupCode)
    }

    $result = Invoke-KakaoApiWithCurl -Endpoint "https://dapi.kakao.com/v2/local/search/keyword.json" -Params $params -ApiKey $ApiKey

    if (-not $result.success) {
        # API 에러 처리
        if ($result.statusCode -eq 401 -or $result.statusCode -eq 403) {
            return @{
                ok = $false
                errorType = "InvalidApiKey"
                message = "Invalid or expired API key"
                statusCode = $result.statusCode
            } | ConvertTo-Json -Compress
        }
        else {
            return @{
                ok = $false
                errorType = "ApiError"
                message = "Failed to call Kakao API"
                details = $result.error
            } | ConvertTo-Json -Compress
        }
    }

    $apiResponse = $result.response

    # 응답 데이터 가공
    $items = @()
    foreach ($doc in $apiResponse.documents) {
        $item = @{
            id = $doc.id
            name = $doc.place_name
            roadAddress = $doc.road_address_name
            jibunAddress = $doc.address_name
            x = $doc.x
            y = $doc.y
            phone = $doc.phone
            categoryName = $doc.category_name
            placeUrl = $doc.place_url
            distance = $doc.distance
        }

        $items += $item
    }

    # 출력 규격에 맞춘 결과
    $output = @{
        ok = $true
        action = "SearchPlace"
        query = $Query
        count = $items.Count
        totalCount = $apiResponse.meta.total_count
        isEnd = $apiResponse.meta.is_end
        items = $items
        raw = $apiResponse
    }

    return $output | ConvertTo-Json -Depth 10 -Compress
}

# ============================================
# 메인 실행 로직
# ============================================

# API Key 확인
$apiKey = Get-ApiKey

if ([string]::IsNullOrEmpty($apiKey)) {
    $errorOutput = @{
        ok = $false
        errorType = "MissingApiKey"
        message = "Set KAKAO_REST_API_KEY env var or create config.json"
        setupGuide = "https://developers.kakao.com/"
        instructions = @(
            "Method 1: Environment Variable",
            '  [Environment]::SetEnvironmentVariable("KAKAO_REST_API_KEY", "your_key", "User")',
            "",
            "Method 2: Config File",
            "  Path: skills/kakao-local/data/config.json",
            '  Content: {"api_key": "your_rest_api_key_here"}'
        )
    }

    Write-Output ($errorOutput | ConvertTo-Json -Depth 10 -Compress)
    exit 1
}

# Action 실행
switch ($Action) {
    "NormalizeAddress" {
        $result = Invoke-NormalizeAddress -Query $Query -Size $Size -ApiKey $apiKey
        Write-Output $result
    }
    "SearchPlace" {
        $result = Invoke-SearchPlace -Query $Query -Size $Size -Page $Page -X $X -Y $Y -Radius $Radius -CategoryGroupCode $CategoryGroupCode -ApiKey $apiKey
        Write-Output $result
    }
}
\n`\n
