from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request

# ─── 설정 ─────────────────────────────────────────────────────────────────────

# [모드 1] Relay Mode (로컬 연결용)
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")

# [모드 2] Basic Mode (단순 챗봇용)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("KAKAOTALK_GEMINI_MODEL", "gemini-2.5-flash-lite")
SYSTEM_PROMPT = os.environ.get("KAKAOTALK_SYSTEM_PROMPT", "너는 유능한 AI 비서다. 마크다운 없이 500자 이내로 답해라.")

TEXT_LIMIT = 900
QUICK_REPLIES = [
    {"label": "다시 물어보기", "action": "message", "messageText": "다시 물어보기"},
    {"label": "처음으로",      "action": "message", "messageText": "처음으로"},
]

# ─── 헬퍼 함수 ────────────────────────────────────────────────────────────────

def _save_to_queue(user_id: str, utterance: str, callback_url: str) -> bool:
    """[Relay Mode] 메시지를 Supabase 대기열에 저장"""
    url = f"{SUPABASE_URL}/rest/v1/kakaotalk_queue"
    payload = json.dumps({
        "user_id": user_id,
        "utterance": utterance,
        "callback_url": callback_url,
        "status": "pending"
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Prefer": "return=minimal"
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status in (200, 201)
    except Exception as e:
        print(f"DB Error: {e}")
        return False

def _call_gemini(messages: list[dict]) -> str:
    """[Basic Mode] Gemini 직접 호출"""
    if not GEMINI_API_KEY:
        return "설정 오류: GEMINI_API_KEY 또는 SUPABASE_URL 중 하나는 필수입니다."

    contents = []
    for msg in messages:
        role = "model" if msg["role"] == "assistant" else "user"
        contents.append({"role": role, "parts": [{"text": msg["content"]}]})

    payload = json.dumps({
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": contents,
        "generationConfig": {"maxOutputTokens": 600, "temperature": 0.7},
    }).encode("utf-8")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=9) as resp:
            data = json.load(resp)
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        return f"Gemini 오류: {str(e)}"

def _kakao_response(text: str) -> dict:
    if len(text) > TEXT_LIMIT:
        text = text[: TEXT_LIMIT - 3] + "..."
    return {
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": text}}],
            "quickReplies": QUICK_REPLIES
        },
    }

# ─── Vercel 핸들러 ────────────────────────────────────────────────────────────

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(content_length)
            body = json.loads(body_bytes.decode("utf-8"))

            user_request = body.get("userRequest", {})
            utterance = user_request.get("utterance", "").strip()
            user_id = user_request.get("user", {}).get("id", "unknown")
            callback_url = user_request.get("callbackUrl", "")

            # 모드 결정
            is_relay_mode = bool(SUPABASE_URL and SUPABASE_KEY)

            if is_relay_mode:
                # [Relay Mode] 로컬 처리를 위해 DB 저장
                if not callback_url:
                    # 콜백 모드가 아니면 에러 (Relay는 비동기 필수)
                    self._send_json(_kakao_response("AI 챗봇(콜백) 설정을 켜주세요."))
                    return
                
                if _save_to_queue(user_id, utterance, callback_url):
                    self._send_json({"version": "2.0", "useCallback": True})
                else:
                    self._send_json(_kakao_response("시스템 오류 (DB 연결 실패)"))
            else:
                # [Basic Mode] Vercel에서 즉시 답변
                response_text = _call_gemini([{"role": "user", "content": utterance}])
                self._send_json(_kakao_response(response_text))

        except Exception as e:
            self._send_json(_kakao_response(f"오류 발생: {str(e)}"))

    def do_GET(self):
        mode = "relay" if (SUPABASE_URL and SUPABASE_KEY) else "basic"
        self._send_json({"status": "ok", "mode": mode, "platform": "vercel"})

    def _send_json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
