#!/usr/bin/env python3
"""
카카오톡 채널 웹훅 서버
카카오 i 오픈빌더 v2 호환

아키텍처:
  카카오톡 채널 → 오픈빌더 웹훅 → 이 서버(포트 8401) → Ollama(qwen3:8b) → Gemini fallback

환경변수:
  KAKAOTALK_PORT           기본 8401
  OLLAMA_HOST              기본 http://localhost:11434
  OLLAMA_MODEL             기본 qwen3:8b
  GEMINI_API_KEY           Gemini 2.5 Flash Lite fallback용
  KAKAO_CALLBACK_SECRET    웹훅 서명 검증 (선택)
  KAKAOTALK_PERSONA_NAME   AI 이름 (기본 "AI 비서")
  KAKAOTALK_SYSTEM_PROMPT  시스템 프롬프트 (기본값 사용 or 직접 지정)
  KAKAOTALK_LOG_DIR        로그 디렉터리 (기본 ~/.openclaw/logs)

Python 3.9+ / stdlib only
"""
from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import re
import sys
import threading
import urllib.request
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

# ─── 설정 ─────────────────────────────────────────────────────────────────────

PORT = int(os.environ.get("PORT", os.environ.get("KAKAOTALK_PORT", 8401)))  # Railway는 PORT 자동 주입
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen3:8b")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
KAKAO_SECRET = os.environ.get("KAKAO_CALLBACK_SECRET", "")
PERSONA_NAME = os.environ.get("KAKAOTALK_PERSONA_NAME", "AI 비서")
GEMINI_MODEL = os.environ.get("KAKAOTALK_GEMINI_MODEL", "gemini-2.5-flash")

_default_log_dir = Path.home() / ".openclaw" / "logs"
LOG_DIR = Path(os.environ.get("KAKAOTALK_LOG_DIR", str(_default_log_dir)))
LOG_FILE = LOG_DIR / "kakaotalk.log"

TEXT_LIMIT = 900          # 카카오 SimpleText 최대 1000자, 안전 마진
MAX_HISTORY = 20          # 최대 10턴 (user+assistant = 20 messages)
RESPONSE_TIMEOUT = 4.0    # 콜백 없는 경우 동기 대기 시간 (4초)
OLLAMA_TIMEOUT = 90       # Ollama 최대 대기 시간
CALLBACK_TIMEOUT = 14     # 콜백 모드: useCallback 후 카카오 제한 15초, 안전 마진 14초
FORCE_SYNC = os.environ.get("KAKAOTALK_FORCE_SYNC", "false").lower() == "true"  # 콜백 무시하고 동기 강제
USE_GEMINI_FIRST = os.environ.get("KAKAOTALK_USE_GEMINI_FIRST", "false").lower() == "true"

# ─── 시스템 프롬프트 (환경변수로 완전 교체 가능) ──────────────────────────────

_DEFAULT_SYSTEM_PROMPT = f"""너는 {PERSONA_NAME}이야. 순우리말 "즐거운". 여명거리 CEO 김여명의 AI 비서.

**정체성**: 챗봇 아님. 스타트업 COO처럼 빠르고 실용적인 오른팔.
**말투**: 카톡처럼. 반말 OK. 친근하고 자연스럽게. 빈말 금지 ("좋은 질문이에요!" ❌).
**핵심 원칙**: 바로 본론. 장황한 서론 없이. 근거 있는 추천. 먼저 해결.

**전문 분야**:
- 스타트업/창업/투자/IR (Pre-A, TIPS, Global TIPS, 데모데이)
- 한국 정부지원사업 (TIPS ₩5억, Global TIPS ₩50억, 창진원, 중기부)
- 사업계획서, 피칭 전략, 투자자 커뮤니케이션
- 코딩 (Python, TypeScript, Node.js), 문서 작성
- 뭐든 물어봐 — 모르면 솔직하게 말하고 전문가 추천

**회사 컨텍스트** (여명거리):
- 제품: K-Startup AI (k-startup.ai), autoke, Factsheet AI, EquityOS
- TIPS 선정 ₩5억 (2025.09~2027.09)
- Pre-A 진행 중 ($2M @ $20M)
- 파트너: 배민, Factsheet, VentureSquare

**응답 규칙**:
- 카톡이라 **500자 이내**로 짧게
- 줄바꿈 적절히 활용
- 숫자/데이터 있으면 반드시 포함
- 확신 없는 건 "확인 필요" 명시"""

SYSTEM_PROMPT = os.environ.get("KAKAOTALK_SYSTEM_PROMPT", _DEFAULT_SYSTEM_PROMPT)

# ─── 빠른 응답 버튼 ───────────────────────────────────────────────────────────

QUICK_REPLIES = [
    {"label": "다시 물어보기", "action": "message", "messageText": "다시 물어보기"},
    {"label": "처음으로",      "action": "message", "messageText": "처음으로"},
]

# ─── 인메모리 저장소 ──────────────────────────────────────────────────────────

# user_id → {"history": [{"role": ..., "content": ...}, ...]}
sessions: dict[str, dict] = {}

# user_id → {"response": str | None, "ready": bool}
pending_responses: dict[str, dict] = {}

_lock = threading.Lock()

# ─── 로깅 ─────────────────────────────────────────────────────────────────────

def _log(msg: str) -> None:
    """파일 + stdout 동시 출력."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

# ─── 보안: 서명 검증 ──────────────────────────────────────────────────────────

def _verify_signature(body: bytes, signature: str) -> bool:
    """KAKAO_CALLBACK_SECRET 기반 HMAC-SHA1 검증. 시크릿 없으면 스킵."""
    if not KAKAO_SECRET:
        return True
    expected = hmac.new(
        KAKAO_SECRET.encode("utf-8"),
        body,
        hashlib.sha1,
    ).hexdigest()
    return hmac.compare_digest(expected, signature or "")

# ─── LLM 호출 ─────────────────────────────────────────────────────────────────

def _strip_thinking_tags(text: str) -> str:
    """<think>...</think> 태그 제거 (qwen3 thinking mode)."""
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


def _call_ollama(messages: list[dict]) -> str:
    """Ollama chat API 호출 (qwen3:8b)."""
    payload = json.dumps({
        "model": "qwen3:8b",
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_predict": 600,
        },
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{OLLAMA_HOST}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=OLLAMA_TIMEOUT) as resp:
        data = json.load(resp)
        text = data["message"]["content"].strip()
        return _strip_thinking_tags(text)


def _call_gemini(messages: list[dict]) -> str:
    """Gemini 2.5 Flash Lite fallback 호출."""
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY 미설정")

    # 시스템 프롬프트를 첫 user 메시지에 prepend
    contents = []
    for msg in messages:
        if msg["role"] == "system":
            # Gemini에는 system role 없음 — 첫 user에 합치거나 별도 처리
            continue
        role = "user" if msg["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": msg["content"]}]})

    # 시스템 프롬프트를 systemInstruction으로 전달
    system_msgs = [m for m in messages if m["role"] == "system"]
    system_instruction = system_msgs[0]["content"] if system_msgs else SYSTEM_PROMPT

    payload = json.dumps({
        "system_instruction": {"parts": [{"text": system_instruction}]},
        "contents": contents,
        "generationConfig": {
            "maxOutputTokens": 600,
            "temperature": 0.7,
        },
    }).encode("utf-8")

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    )
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()


def _get_llm_response(user_id: str, utterance: str, history: list[dict]) -> str | None:
    """LLM 응답 생성. USE_GEMINI_FIRST=true면 Gemini 우선, 아니면 Ollama → Gemini."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history[-MAX_HISTORY:])
    messages.append({"role": "user", "content": utterance})

    if USE_GEMINI_FIRST:
        # Gemini 우선 (빠른 응답)
        try:
            response = _call_gemini(messages)
            _log(f"✅ Gemini 응답 완료: user={user_id}, len={len(response)}")
            return response
        except Exception as e:
            _log(f"⚠️ Gemini 실패: {e} — Ollama fallback 시도")
        try:
            response = _call_ollama(messages)
            _log(f"✅ Ollama 응답 완료: user={user_id}, len={len(response)}")
            return response
        except Exception as e:
            _log(f"❌ Ollama 실패: {e}")
            return None
    else:
        # Ollama 우선 (로컬 기본값)
        try:
            response = _call_ollama(messages)
            _log(f"✅ Ollama 응답 완료: user={user_id}, len={len(response)}")
            return response
        except Exception as e:
            _log(f"⚠️ Ollama 실패: {e} — Gemini fallback 시도")
        try:
            response = _call_gemini(messages)
            _log(f"✅ Gemini 응답 완료: user={user_id}, len={len(response)}")
            return response
        except Exception as e:
            _log(f"❌ Gemini 실패: {e}")
            return None

# ─── 카카오 응답 포맷 ─────────────────────────────────────────────────────────

def _kakao_response(text: str, include_quick_replies: bool = True) -> dict:
    """카카오 오픈빌더 v2 응답 딕셔너리 생성."""
    # 900자 제한 자동 트런케이트
    if len(text) > TEXT_LIMIT:
        text = text[: TEXT_LIMIT - 3] + "..."

    result: dict = {
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": text}}],
        },
    }

    if include_quick_replies:
        result["template"]["quickReplies"] = QUICK_REPLIES

    return result


def _kakao_use_callback() -> dict:
    """AI 챗봇 콜백 모드: 즉시 반환 (5초 제한 우회)."""
    return {"version": "2.0", "useCallback": True}


def _send_callback(callback_url: str, text: str) -> None:
    """LLM 완료 후 카카오 콜백 URL로 실제 응답 전송."""
    try:
        # 콜백 모드에서는 quickReplies 없이 전송 (카카오 콜백 스펙)
        payload = json.dumps(_kakao_response(text, include_quick_replies=False),
                             ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            callback_url,
            data=payload,
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            _log(f"📤 콜백 전송 완료: status={resp.status}, url={callback_url[:60]}")
    except Exception as e:
        _log(f"❌ 콜백 전송 실패: {e}")

# ─── HTTP 핸들러 ──────────────────────────────────────────────────────────────

class KakaoWebhookHandler(BaseHTTPRequestHandler):
    """카카오 i 오픈빌더 웹훅 요청 처리."""

    # 기본 httpd 로그 억제
    def log_message(self, fmt, *args):  # noqa: N802
        pass

    def _send_json(self, data: dict, status: int = 200) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # ── GET /health ──────────────────────────────────────────────────────────

    def do_GET(self):  # noqa: N802
        if self.path in ("/health", "/"):
            with _lock:
                active_sessions = len(sessions)
                pending = len(pending_responses)
            self._send_json({
                "status": "ok",
                "port": PORT,
                "active_sessions": active_sessions,
                "pending_responses": pending,
            })
        elif self.path in ("/kakao", "/kakao/"):
            # 카카오 오픈빌더 스킬 URL 검증용 GET 요청 응답
            self._send_json({"status": "ok"})
        else:
            self.send_response(404)
            self.end_headers()

    # ── POST /kakao ───────────────────────────────────────────────────────────

    def do_POST(self):  # noqa: N802
        # 항상 200 반환 (카카오 요구사항)
        try:
            self._handle_post()
        except Exception as e:
            _log(f"❌ 핸들러 예외: {e}")
            self._send_json(_kakao_response("일시적 오류가 발생했어요. 잠시 후 다시 시도해주세요 😊"))

    def _handle_post(self) -> None:
        # 바디 읽기
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(content_length)
        except Exception as e:
            _log(f"❌ 바디 읽기 실패: {e}")
            self._send_json(_kakao_response("요청을 읽을 수 없어요."))
            return

        # 서명 검증 (선택)
        signature = self.headers.get("X-Kakao-Signature", "")
        if not _verify_signature(body_bytes, signature):
            _log("⚠️ 서명 검증 실패 — 요청 무시")
            self._send_json(_kakao_response("인증 실패."))
            return

        # JSON 파싱
        try:
            body = json.loads(body_bytes.decode("utf-8"))
        except json.JSONDecodeError as e:
            _log(f"❌ JSON 파싱 실패: {e}")
            self._send_json(_kakao_response("잘못된 요청 형식이에요."))
            return

        # utterance / user_id / callbackUrl 추출
        user_request = body.get("userRequest", {})
        utterance = user_request.get("utterance", "").strip()
        user_id = user_request.get("user", {}).get("id", "unknown")
        callback_url = user_request.get("callbackUrl", "")  # AI 챗봇 모드에서만 존재

        _log(f"📩 user={user_id[:12]}... | utterance={utterance[:60]} | callback={'✅' if callback_url else '❌'}")

        if not utterance:
            self._send_json(_kakao_response("메시지를 입력해주세요 😊"))
            return

        # ── 세션 초기화 명령 ──────────────────────────────────────────────────
        RESET_TRIGGERS = {"처음으로", "처음부터", "시작", "안녕", "안녕하세요", "ㅎㅇ", "ㅎㅇㅎㅇ", "hi", "hello", "hey", "/reset"}
        if utterance.lower() in RESET_TRIGGERS:
            with _lock:
                sessions.pop(user_id, None)
                pending_responses.pop(user_id, None)
            welcome = (
                f"안녕하세요! 저는 {PERSONA_NAME}이에요 🙌\n\n"
                "무엇이든 물어보세요!"
            )
            self._send_json(_kakao_response(welcome))
            return

        # ── "다시 물어보기" — 캐시된 결과 반환 ─────────────────────────────
        if utterance == "다시 물어보기":
            with _lock:
                pending = pending_responses.get(user_id)

            if pending is None:
                self._send_json(_kakao_response("이전 질문이 없어요. 새로 질문해주세요 😊"))
                return

            if not pending.get("ready"):
                self._send_json(_kakao_response("아직 생각 중이에요! 잠시 후 다시 눌러주세요 🤔"))
                return

            # 준비 완료
            cached_text = pending.get("response") or ""
            with _lock:
                pending_responses.pop(user_id, None)

            if cached_text:
                self._send_json(_kakao_response(cached_text))
            else:
                self._send_json(_kakao_response("응답 생성에 실패했어요. 다시 질문해주세요 😊"))
            return

        # ── 일반 질문 처리 ────────────────────────────────────────────────────
        with _lock:
            if user_id not in sessions:
                sessions[user_id] = {"history": []}
            history = list(sessions[user_id]["history"])

        # 결과 홀더 준비
        result_holder: dict = {"response": None, "ready": False}
        event = threading.Event()

        with _lock:
            pending_responses[user_id] = result_holder

        # 캡처 (클로저용)
        _utterance = utterance
        _user_id = user_id
        _callback_url = callback_url

        def llm_task() -> None:
            """백그라운드 LLM 호출 + 세션 업데이트 + 콜백 전송."""
            response = _get_llm_response(_user_id, _utterance, history)
            result_holder["response"] = response
            result_holder["ready"] = True
            event.set()

            # 세션 히스토리 업데이트
            with _lock:
                if _user_id in sessions:
                    sess_hist = sessions[_user_id]["history"]
                    sess_hist.append({"role": "user", "content": _utterance})
                    sess_hist.append({"role": "assistant", "content": response or ""})
                    if len(sess_hist) > MAX_HISTORY:
                        sessions[_user_id]["history"] = sess_hist[-MAX_HISTORY:]

            # ── 콜백 모드: LLM 완료 시 카카오로 직접 push (FORCE_SYNC=true면 건너뜀) ──
            if _callback_url and not FORCE_SYNC:
                if response:
                    _send_callback(_callback_url, response)
                else:
                    _send_callback(_callback_url, "응답 생성에 실패했어요. 다시 질문해주세요 😊")

        thread = threading.Thread(target=llm_task, daemon=True)
        thread.start()

        # ── 콜백 모드 (FORCE_SYNC=true 이면 건너뜀) ─────────────────────────
        if callback_url and not FORCE_SYNC:
            # 즉시 useCallback 반환 → 카카오가 LLM 완료 후 콜백 URL로 자동 수신
            _log(f"⚡ 콜백 모드 활성화: user={user_id[:12]}...")
            self._send_json(_kakao_use_callback())
            return

        # ── 동기 모드 (콜백 없는 경우 / 테스트) ─────────────────────────────
        event.wait(timeout=RESPONSE_TIMEOUT)

        if result_holder["ready"] and result_holder["response"]:
            with _lock:
                pending_responses.pop(user_id, None)
            self._send_json(_kakao_response(result_holder["response"]))
        else:
            _log(f"⏳ 타임아웃: user={user_id[:12]}... — 백그라운드 계속 실행 중")
            thinking_msg = (
                f"{PERSONA_NAME}이 생각 중이에요... 잠시만요 🤔\n\n"
                "답변이 준비되면 '다시 물어보기'를 눌러주세요!"
            )
            self._send_json(_kakao_response(thinking_msg))

# ─── 메인 ─────────────────────────────────────────────────────────────────────

def main() -> None:
    _log(f"🚀 카카오 채널 웹훅 서버 시작 — 포트 {PORT}")
    _log(f"   Ollama: {OLLAMA_HOST}")
    _log(f"   Gemini: {'설정됨' if GEMINI_API_KEY else '미설정'}")
    _log(f"   서명검증: {'활성화' if KAKAO_SECRET else '비활성화(선택사항)'}")
    _log(f"   로그: {LOG_FILE}")

    server = HTTPServer(("0.0.0.0", PORT), KakaoWebhookHandler)
    _log(f"   웹훅 엔드포인트: POST http://0.0.0.0:{PORT}/kakao")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        _log("🛑 서버 종료")
        server.server_close()


if __name__ == "__main__":
    main()
