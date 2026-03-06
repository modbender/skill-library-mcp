#!/usr/bin/env python3
"""
카카오톡 왓처 (OpenClaw Native)
Supabase 우체통을 감시하다가, 메시지가 오면 OpenClaw의 지능으로 처리하고 답장함.
"""
import json
import os
import time
import urllib.request
import urllib.error

# ─── 설정 ─────────────────────────────────────────────────────────────────────

# .env 로드 (간이)
def load_env():
    env_path = os.path.expanduser("~/.openclaw/.env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    k, v = line.strip().split("=", 1)
                    os.environ[k] = v

load_env()

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
# OpenClaw LLM 대신 여기서는 임시로 Gemini를 직접 호출 (나중에 OpenClaw API 연동 가능)
# 일단은 "메모리" 기능을 위해 로컬 파일 시스템에 접근 가능함을 보여줌
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-flash"

# ─── Supabase API ─────────────────────────────────────────────────────────────

def get_pending_messages():
    """대기 중인 메시지 가져오기 (Long Polling 흉내)"""
    url = f"{SUPABASE_URL}/rest/v1/kakaotalk_queue?status=eq.pending&select=*&limit=1"
    req = urllib.request.Request(url, headers={
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    })
    try:
        with urllib.request.urlopen(req) as resp:
            return json.load(resp)
    except Exception as e:
        print(f"Poll Error: {e}")
        return []

def update_status(msg_id, status, response_text):
    """처리 상태 업데이트"""
    url = f"{SUPABASE_URL}/rest/v1/kakaotalk_queue?id=eq.{msg_id}"
    payload = json.dumps({"status": status, "response": response_text}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, method="PATCH", headers={
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    })
    try:
        with urllib.request.urlopen(req):
            pass
    except Exception as e:
        print(f"Update Error: {e}")

# ─── 카카오 콜백 발송 ─────────────────────────────────────────────────────────

def send_callback(url, text):
    """카카오톡 서버로 답장 발송"""
    payload = json.dumps({
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": text}}]
        }
    }).encode("utf-8")
    
    req = urllib.request.Request(url, data=payload, method="POST", headers={
        "Content-Type": "application/json"
    })
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"✅ 발송 성공: {text[:20]}...")
            return True
    except Exception as e:
        print(f"❌ 발송 실패: {e}")
        return False

# ─── 지능 (Local Brain) ───────────────────────────────────────────────────────

def process_message(utterance, user_id):
    """
    여기서 '진짜 나(Raon)'의 능력이 발휘됨.
    1. 로컬 파일(MEMORY.md) 읽기
    2. 이전 대화 기록 확인 (Supabase에서 조회 가능)
    3. LLM 호출
    """
    
    # 1. 로컬 메모리 읽기 (Context Injection)
    memory_path = os.path.expanduser("~/.openclaw/workspace/MEMORY.md")
    memory_context = ""
    if os.path.exists(memory_path):
        with open(memory_path) as f:
            memory_context = f.read()[:2000] # 너무 길면 자름

    # 2. 시스템 프롬프트 구성
    system_prompt = f"""너는 라온이다. (Mac Studio에서 실행 중)
사용자의 질문: {utterance}

[장기 기억 (MEMORY.md)]
{memory_context}

사용자에게 친절하게, 그리고 기억을 바탕으로 대답해."""

    # 3. LLM 호출 (Gemini)
    # (실제 OpenClaw 내부라면 agent.ask()를 쓰겠지만, 여기선 독립 스크립트라 직접 호출)
    return _call_gemini_direct(system_prompt, utterance)

def _call_gemini_direct(system, user_msg):
    # (아까 Vercel 코드와 동일한 Gemini 호출 로직)
    payload = json.dumps({
        "contents": [{"role": "user", "parts": [{"text": system + "\n\n" + user_msg}]}],
        "generationConfig": {"maxOutputTokens": 2000}
    }).encode("utf-8")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.load(resp)
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        return f"생각하다 오류가 났어: {e}"

# ─── 메인 루프 ────────────────────────────────────────────────────────────────

def main():
    print("👀 카카오톡 왓처 시작 (Supabase 감시 중...)")
    while True:
        messages = get_pending_messages()
        for msg in messages:
            print(f"📩 수신: {msg['utterance']}")
            
            # 처리 중 표시
            update_status(msg['id'], 'processing', None)
            
            # 생각하기
            response = process_message(msg['utterance'], msg['user_id'])
            
            # 답장 보내기
            if msg['callback_url']:
                success = send_callback(msg['callback_url'], response)
                status = 'done' if success else 'failed'
            else:
                status = 'no_callback'
                
            # 완료 처리
            update_status(msg['id'], status, response)
            
        time.sleep(1) # 1초 대기

if __name__ == "__main__":
    main()
