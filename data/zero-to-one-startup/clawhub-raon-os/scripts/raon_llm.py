#!/usr/bin/env python3
"""
raon_llm.py — Raon OS 범용 LLM 클라이언트
Python 3.9+ compatible

Provider 자동 감지: OpenRouter → Gemini → Anthropic → OpenAI → Ollama

사용법:
    from raon_llm import chat, embed, cosine_sim, detect_provider

    result = chat([{"role": "user", "content": "안녕"}])
    vec    = embed("텍스트")
    sim    = cosine_sim(vec1, vec2)

환경변수 우선순위:
    RAON_LLM_PROVIDER   강제 프로바이더 (openrouter/gemini/anthropic/openai/ollama)
    RAON_MODEL          강제 모델명 (예: "gpt-4o", "claude-opus-4-5")

API 키 (감지 순서):
    OPENROUTER_API_KEY  → 1순위 (OpenClaw 지원 모든 모델)
    GEMINI_API_KEY      → 2순위
    ANTHROPIC_API_KEY   → 3순위
    OPENAI_API_KEY      → 4순위
    없으면 Ollama localhost 자동 사용

설정 파일: ~/.openclaw/.env 자동 로드 (환경변수가 이미 설정된 경우 우선)
"""

from __future__ import annotations  # Python 3.9 compatibility

import json
import math
import os
import sys
import urllib.request
import urllib.error
from typing import Optional


# ─── .env 자동 로드 ──────────────────────────────────────────────────────────
# 환경변수가 이미 설정되어 있으면 .env보다 우선 (os.environ.setdefault 사용)

_ENV_FILE = os.path.expanduser("~/.openclaw/.env")
if os.path.exists(_ENV_FILE):
    try:
        with open(_ENV_FILE) as _f:
            for _line in _f:
                _line = _line.strip()
                if _line and not _line.startswith("#") and "=" in _line:
                    _k, _v = _line.split("=", 1)
                    os.environ.setdefault(_k.strip(), _v.strip())
    except Exception:
        pass


# ─── 상수 ────────────────────────────────────────────────────────────────────

PROVIDER_ORDER = ["openrouter", "gemini", "anthropic", "openai", "ollama"]

# 프로바이더별 기본 모델 (RAON_MODEL 환경변수로 전체 override 가능)
_DEFAULT_MODELS: dict = {
    "openrouter": "google/gemini-2.5-flash",
    "gemini":     "gemini-2.5-flash",
    "anthropic":  "claude-3-5-haiku-latest",
    "openai":     "gpt-4o-mini",
    "ollama":     "qwen3:8b",
}

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")


# ─── 내부 헬퍼 ───────────────────────────────────────────────────────────────

def _key(name: str) -> str:
    """환경변수 값 반환 (없으면 빈 문자열)."""
    return os.environ.get(name, "")


def _resolve_model(provider: str) -> str:
    """
    모델 결정 우선순위:
    1. RAON_MODEL 환경변수 (전체 override)
    2. Ollama: OLLAMA_MODEL 환경변수
    3. 프로바이더 기본값
    """
    override = _key("RAON_MODEL")
    if override:
        return override
    if provider == "ollama":
        return _key("OLLAMA_MODEL") or _DEFAULT_MODELS["ollama"]
    return _DEFAULT_MODELS.get(provider, "")


def _post_json(url: str, payload: dict, headers: dict, timeout: int = 120) -> dict:
    """JSON POST 요청 → 응답 dict 반환. 오류 시 예외 raise."""
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={
        "Content-Type": "application/json",
        **headers,
    })
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


# ─── Provider 감지 ───────────────────────────────────────────────────────────

def detect_provider() -> str:
    """
    Chat LLM 프로바이더 자동 감지.

    우선순위:
      RAON_LLM_PROVIDER(강제) → OPENROUTER → GEMINI → ANTHROPIC → OPENAI → ollama

    반환: "openrouter" | "gemini" | "anthropic" | "openai" | "ollama"
    """
    forced = _key("RAON_LLM_PROVIDER").lower().strip()
    if forced in PROVIDER_ORDER:
        return forced

    if _key("OPENROUTER_API_KEY"):
        return "openrouter"
    if _key("GEMINI_API_KEY"):
        return "gemini"
    if _key("ANTHROPIC_API_KEY"):
        return "anthropic"
    if _key("OPENAI_API_KEY"):
        return "openai"
    return "ollama"


def detect_embed_provider() -> str:
    """
    임베딩 프로바이더 자동 감지.

    우선순위: Gemini → OpenAI → Ollama → "none" (BM25 폴백)
    """
    if _key("GEMINI_API_KEY"):
        return "gemini"
    if _key("OPENAI_API_KEY"):
        return "openai"
    if _ollama_available():
        return "ollama"
    return "none"


def _ollama_available() -> bool:
    """Ollama 서버 응답 여부 확인 (3초 타임아웃)."""
    try:
        urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=3)
        return True
    except Exception:
        return False


# ─── Chat 구현 (프로바이더별) ────────────────────────────────────────────────

def _chat_openrouter(messages: list, model: str, system: Optional[str]) -> str:
    """OpenRouter — OpenAI 호환 API, 모든 주요 모델 지원."""
    full = []
    if system:
        full.append({"role": "system", "content": system})
    full.extend(messages)
    r = _post_json(
        "https://openrouter.ai/api/v1/chat/completions",
        {"model": model, "messages": full},
        {
            "Authorization": f"Bearer {_key('OPENROUTER_API_KEY')}",
            "HTTP-Referer": "https://k-startup.ai",
            "X-Title": "Raon OS",
        },
    )
    return r["choices"][0]["message"]["content"]


def _chat_gemini(messages: list, model: str, system: Optional[str]) -> str:
    """Google Gemini — generateContent API."""
    contents = []
    for m in messages:
        role = "user" if m["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": m["content"]}]})
    payload: dict = {"contents": contents}
    if system:
        payload["system_instruction"] = {"parts": [{"text": system}]}
    r = _post_json(
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={_key('GEMINI_API_KEY')}",
        payload,
        {},
    )
    return r["candidates"][0]["content"]["parts"][0]["text"]


def _chat_anthropic(messages: list, model: str, system: Optional[str]) -> str:
    """Anthropic Claude — Messages API."""
    payload: dict = {
        "model": model,
        "max_tokens": 4096,
        "messages": messages,
    }
    if system:
        payload["system"] = system
    r = _post_json(
        "https://api.anthropic.com/v1/messages",
        payload,
        {
            "x-api-key": _key("ANTHROPIC_API_KEY"),
            "anthropic-version": "2023-06-01",
        },
    )
    return r["content"][0]["text"]


def _chat_openai(messages: list, model: str, system: Optional[str]) -> str:
    """OpenAI — Chat Completions API."""
    full = []
    if system:
        full.append({"role": "system", "content": system})
    full.extend(messages)
    r = _post_json(
        "https://api.openai.com/v1/chat/completions",
        {"model": model, "messages": full},
        {"Authorization": f"Bearer {_key('OPENAI_API_KEY')}"},
    )
    return r["choices"][0]["message"]["content"]


def _chat_ollama(messages: list, model: str, system: Optional[str]) -> str:
    """Ollama — /api/chat (로컬 LLM)."""
    full = []
    if system:
        full.append({"role": "system", "content": system})
    full.extend(messages)
    r = _post_json(
        f"{OLLAMA_URL}/api/chat",
        {
            "model": model,
            "messages": full,
            "stream": False,
            "options": {"temperature": 0.3, "num_predict": 4096},
        },
        {},
        timeout=300,
    )
    # /api/chat → message.content, 일부 버전은 response 필드
    return r.get("message", {}).get("content", r.get("response", ""))


_CHAT_FN: dict = {
    "openrouter": _chat_openrouter,
    "gemini":     _chat_gemini,
    "anthropic":  _chat_anthropic,
    "openai":     _chat_openai,
    "ollama":     _chat_ollama,
}


def chat(
    messages: list,
    model: Optional[str] = None,
    system: Optional[str] = None,
    provider: Optional[str] = None,
) -> Optional[str]:
    """
    LLM Chat 호출. 실패 시 None 반환.

    Args:
        messages:  [{"role": "user"|"assistant", "content": "..."}]
        model:     모델명 (None → RAON_MODEL 환경변수 or 프로바이더 기본값)
        system:    시스템 프롬프트
        provider:  강제 지정 (None → detect_provider() 자동감지)

    Returns:
        LLM 응답 문자열, 실패 시 None
    """
    prov = (provider or detect_provider()).lower().strip()
    mdl  = model or _resolve_model(prov)
    fn   = _CHAT_FN.get(prov)
    if fn is None:
        print(f"[raon_llm] ⚠️ 알 수 없는 프로바이더: {prov}", file=sys.stderr)
        return None
    try:
        return fn(messages, mdl, system)
    except Exception as e:
        print(f"[raon_llm] ⚠️ {prov}/{mdl} 호출 실패: {e}", file=sys.stderr)
        return None


def prompt_to_messages(prompt: str) -> list:
    """단순 프롬프트 문자열 → messages 형식 변환."""
    return [{"role": "user", "content": prompt}]


# ─── 임베딩 구현 ─────────────────────────────────────────────────────────────

def _embed_gemini(text: str) -> list:
    """Gemini text-embedding-004 (768차원)."""
    r = _post_json(
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"text-embedding-004:embedContent?key={_key('GEMINI_API_KEY')}",
        {
            "model": "models/text-embedding-004",
            "content": {"parts": [{"text": text[:2000]}]},
        },
        {},
        timeout=30,
    )
    return r["embedding"]["values"]


def _embed_openai(text: str) -> list:
    """OpenAI text-embedding-3-small (1536차원)."""
    r = _post_json(
        "https://api.openai.com/v1/embeddings",
        {"model": "text-embedding-3-small", "input": text[:8000]},
        {"Authorization": f"Bearer {_key('OPENAI_API_KEY')}"},
        timeout=30,
    )
    return r["data"][0]["embedding"]


def _embed_ollama(text: str) -> list:
    """Ollama /api/embed (EMBED_MODEL 환경변수, 기본 bge-m3)."""
    model = _key("EMBED_MODEL") or "bge-m3"
    r = _post_json(
        f"{OLLAMA_URL}/api/embed",
        {"model": model, "input": text},
        {},
        timeout=60,
    )
    embs = r.get("embeddings", [])
    return embs[0] if embs else []


def embed(text: str) -> list:
    """
    텍스트 임베딩. 프로바이더 없으면 [] 반환 (→ BM25 폴백).

    우선순위: Gemini → OpenAI → Ollama → []
    """
    if _key("GEMINI_API_KEY"):
        try:
            return _embed_gemini(text)
        except Exception as e:
            print(f"[raon_llm] ⚠️ Gemini embed 실패: {e}", file=sys.stderr)

    if _key("OPENAI_API_KEY"):
        try:
            return _embed_openai(text)
        except Exception as e:
            print(f"[raon_llm] ⚠️ OpenAI embed 실패: {e}", file=sys.stderr)

    if _ollama_available():
        try:
            return _embed_ollama(text)
        except Exception as e:
            print(f"[raon_llm] ⚠️ Ollama embed 실패: {e}", file=sys.stderr)

    return []


# ─── Cosine 유사도 (pure Python, numpy 의존성 없음) ───────────────────────────

def cosine_sim(a: list, b: list) -> float:
    """코사인 유사도. pure Python 구현 (numpy 불필요)."""
    if not a or not b:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na  = math.sqrt(sum(x * x for x in a))
    nb  = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb) if na * nb else 0.0


# ─── CLI (디버그 / 연결 테스트) ───────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="raon_llm — LLM 연결 테스트")
    parser.add_argument("--detect", action="store_true",
                        help="프로바이더 감지 결과만 출력")
    parser.add_argument("--provider", help="강제 프로바이더 (테스트용)")
    parser.add_argument("--model", help="강제 모델명 (테스트용)")
    parser.add_argument("--prompt", default="",
                        help="Chat 테스트 프롬프트")
    parser.add_argument("--embed", dest="embed_text", metavar="TEXT",
                        help="임베딩 테스트 텍스트")
    args = parser.parse_args()

    # 항상 감지 결과 출력
    prov  = detect_provider()
    eprov = detect_embed_provider()
    mdl   = args.model or _resolve_model(prov)
    print(f"✅ Chat  프로바이더 : {prov}  (모델: {mdl})")
    print(f"✅ Embed 프로바이더 : {eprov}")

    if args.detect:
        sys.exit(0)

    if args.embed_text:
        vec = embed(args.embed_text)
        if vec:
            print(f"\n✅ 임베딩 성공: 차원={len(vec)}, "
                  f"첫 5값={[round(x, 4) for x in vec[:5]]}")
        else:
            print("\n⚠️ 임베딩 실패 — BM25 모드로 동작합니다")

    elif args.prompt:
        result = chat(
            prompt_to_messages(args.prompt),
            model=args.model,
            provider=args.provider,
        )
        if result:
            print(f"\n{result}")
        else:
            print("\n⚠️ LLM 호출 실패")

    else:
        parser.print_help()
