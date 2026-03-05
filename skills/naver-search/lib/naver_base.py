import os
import sys
import json
import site

# 유저 사이트 패키지 경로 추가 (하드코딩 제거)
user_site = site.getusersitepackages()
if user_site not in sys.path:
    sys.path.insert(0, user_site)

try:
    import serpapi
except ImportError:
    print("Error: serpapi package not installed. Run: pip install serpapi", file=sys.stderr)
    sys.exit(1)

def get_api_key():
    """환경 변수 또는 .env 파일에서 API 키 로드"""
    api_key = os.environ.get("SERPAPI_API_KEY")

    if not api_key:
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        if os.path.exists(env_path):
            # .env 파일 보안 강화 안내 (chmod 600 권장)
            # 실제 운영 환경이라면 여기서 파일 권한 체크 로직을 넣을 수 있음
            with open(env_path, "r") as f:
                for line in f:
                    if line.startswith("SERPAPI_API_KEY="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
    return api_key

def clean_dict(obj):
    """표준 JSON 자료형만 남기도록 재귀적으로 정제"""
    if hasattr(obj, 'to_dict'):
        return clean_dict(obj.to_dict())
    elif isinstance(obj, dict):
        return {str(k): clean_dict(v) for k, v in obj.items() if not str(k).startswith('_')}
    elif isinstance(obj, list):
        return [clean_dict(x) for x in obj]
    elif isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    else:
        # 그 외 객체는 문자열로 변환 (RLock 등 방지)
        return str(obj)

def perform_search(params):
    """실제 SerpAPI 호출 수행 (재시도 로직 포함)"""
    api_key = get_api_key()
    if not api_key:
        print("Error: SERPAPI_API_KEY not found.", file=sys.stderr)
        sys.exit(1)
    
    params["api_key"] = api_key
    
    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            results = serpapi.search(**params)
            # SerpResults 객체의 핵심 데이터만 추출 (직렬화 오류 원인 차단)
            if hasattr(results, 'data'):
                return clean_dict(results.data)
            return clean_dict(results)
        except Exception as e:
            if attempt < max_retries:
                continue
            return {"error": f"Search failed after {max_retries} retries: {str(e)}"}

def format_output(results, format_type, compact_formatter):
    """포맷에 따른 최종 출력 제어"""
    if "error" in results:
        return f"❌ 오류 발생: {results['error']}"

    if format_type == "json" or format_type == "full":
        return json.dumps(results, indent=2, ensure_ascii=False)
    
    return compact_formatter(results)
