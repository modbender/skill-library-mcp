#!/usr/bin/env python3
"""
Supabase 클라이언트 — 로컬 모드 전용
SUPABASE_URL + SUPABASE_SERVICE_KEY 환경변수가 있을 때만 동작.

⚠️  ClawHub 배포 주의사항:
    이 모듈은 사용자 본인의 Supabase 키를 사용합니다.
    RAON_API_URL이 설정된 SaaS 모드에서는 이 모듈을 직접 사용하지 않음.
    피드백은 RAON_API_URL/v1/feedback 으로 라우팅됨.
"""

import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path


def _load_env():
    """~/.openclaw/.env 또는 .env 파일에서 환경변수 로드 (미설정 키만)"""
    for env_path in [
        Path.home() / ".openclaw" / ".env",
        Path(__file__).parent.parent / ".env",
    ]:
        if not env_path.exists():
            continue
        try:
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = val
        except Exception:
            pass


_load_env()

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")

# SSRF 방지: SUPABASE_URL이 허용된 Supabase 도메인인지 검증
def _is_valid_supabase_url(url: str) -> bool:
    from urllib.parse import urlparse
    try:
        h = (urlparse(url).hostname or "").lower()
        return h.endswith(".supabase.co") or h.endswith(".supabase.com")
    except Exception:
        return False

if SUPABASE_URL and not _is_valid_supabase_url(SUPABASE_URL):
    import sys
    print(f"[supabase-client] ⚠️  SUPABASE_URL 도메인 검증 실패 (SSRF 방지): {SUPABASE_URL[:40]}", file=sys.stderr)
    SUPABASE_URL = ""

_available = bool(SUPABASE_URL and SUPABASE_SERVICE_KEY)

if _available:
    print(
        f"[supabase-client] 로컬 Supabase 연결됨: {SUPABASE_URL[:40]}...",
        file=sys.stderr,
    )

# Cloudflare가 Python urllib의 기본 User-Agent를 차단하므로 curl UA 사용
_UA = "curl/8.7.1"


def is_available() -> bool:
    """Supabase 설정 여부 반환"""
    return _available


def _request(method: str, table: str, data=None, extra_headers: dict = None):
    """Supabase REST API 요청"""
    if not _available:
        return None
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
        "User-Agent": _UA,  # Cloudflare 차단 우회
    }
    if extra_headers:
        headers.update(extra_headers)
    body = json.dumps(data, ensure_ascii=False).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:  # nosec B310
            resp_body = resp.read()
            if resp_body:
                return json.loads(resp_body.decode("utf-8"))
            return {}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        print(f"[supabase-client] HTTP {e.code}: {err_body[:200]}", file=sys.stderr)
        return None
    except Exception as ex:
        print(f"[supabase-client] 요청 실패: {ex}", file=sys.stderr)
        return None


def insert_evaluation(
    evaluation_id: str,
    session_id: str,
    mode: str,
    input_text: str,
    result_text: str,
    score,
    duration_sec: float,
    model: str,
) -> bool:
    """raon_evaluations 테이블에 UPSERT (중복 id는 무시)"""
    if not _available:
        return False
    row = {
        "id": evaluation_id,
        "session_id": session_id or "",
        "mode": mode,
        "input_text": (input_text or "")[:500],
        "result_text": result_text or "",
        "score": score,  # jsonb
        "duration_sec": round(duration_sec, 3) if duration_sec else None,
        "model": model,
    }
    result = _request(
        "POST", "raon_evaluations", row,
        extra_headers={"Prefer": "resolution=ignore-duplicates,return=minimal"},
    )
    return result is not None


def insert_feedback(
    evaluation_id: str,
    rating: int,
    comment: str = "",
) -> bool:
    """raon_feedback 테이블에 INSERT"""
    if not _available:
        return False
    row = {
        "evaluation_id": evaluation_id,
        "rating": rating,
        "comment": comment or "",
    }
    result = _request("POST", "raon_feedback", row)
    return result is not None
