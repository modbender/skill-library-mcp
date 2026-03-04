#!/usr/bin/env python3
"""
server.py — Interactive AI phone call server (Flask webhook for Twilio)
Handles real-time back-and-forth: Twilio STT → GPT brain → ElevenLabs TTS

Run: python3 server.py
Then start a call via interactive_call.py
"""
import os, uuid, subprocess, tempfile, requests
from openai import OpenAI
from flask import Flask, request, Response, send_file
from twilio.twiml.voice_response import VoiceResponse, Gather

app = Flask(__name__)

# ── Config ───────────────────────────────────────────────────────────────────
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
OPENAI_API_KEY     = os.environ.get("OPENAI_API_KEY", "")
PUBLIC_URL         = os.environ.get("CALLER_PUBLIC_URL", "")
MASTER_PHONE       = os.environ.get("MASTER_PHONE", "")
DEFAULT_VOICE      = os.environ.get("CALLER_VOICE_ID", "tyepWYJJwJM9TTFIg5U7")

# In-memory state per call SID
conversations = {}   # call_sid → [{role, content}]
personas      = {}   # call_sid → system_prompt string
audio_files   = {}   # filename → path on disk

PORT = int(os.environ.get("CALLER_PORT", 5050))


# ── Helpers ──────────────────────────────────────────────────────────────────

def tts(text: str, voice_id: str = DEFAULT_VOICE) -> str:
    """Generate audio via ElevenLabs, serve it locally, return URL path."""
    r = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        headers={"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"},
        json={
            "text": text,
            "model_id": "eleven_turbo_v2_5",
            "voice_settings": {"stability": 0.45, "similarity_boost": 0.8, "style": 0.5}
        }
    )
    r.raise_for_status()
    fname = f"audio_{uuid.uuid4().hex[:8]}.mp3"
    path  = f"/tmp/{fname}"
    with open(path, "wb") as f:
        f.write(r.content)
    audio_files[fname] = path
    print(f"🎙️  TTS: {text[:60]}...")
    return f"{PUBLIC_URL}/audio/{fname}"


def gpt_reply(call_sid: str, user_said: str) -> str:
    """Get the AI caller's next line from GPT."""
    conversations[call_sid].append({"role": "user", "content": user_said})
    client = OpenAI(api_key=OPENAI_API_KEY)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=120,
        messages=[{"role": "system", "content": personas.get(call_sid, "")}] + conversations[call_sid]
    )
    reply = resp.choices[0].message.content.strip()
    conversations[call_sid].append({"role": "assistant", "content": reply})
    return reply


def send_summary(call_sid: str):
    """Generate call summary and send via iMessage."""
    convo = conversations.get(call_sid, [])
    if not convo:
        return
    transcript = "\n".join(
        f"{'Caller' if m['role']=='assistant' else 'Recipient'}: {m['content']}"
        for m in convo
    )
    client = OpenAI(api_key=OPENAI_API_KEY)
    summary = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=120,
        messages=[
            {"role": "system", "content": "Summarize this phone call in 2-3 sentences. Was the goal achieved? Any key details (time, name, outcome)?"},
            {"role": "user", "content": transcript}
        ]
    ).choices[0].message.content.strip()

    log_path = f"/tmp/call_{call_sid[:8]}.txt"
    with open(log_path, "w") as f:
        f.write(f"SUMMARY\n{summary}\n\nTRANSCRIPT\n{transcript}")
    print(f"📋  Summary: {summary}")

    msg = f"📞 Call summary:\n\n{summary}"
    subprocess.run(["imsg", "send", "--to", MASTER_PHONE, "--text", msg], capture_output=True)


# ── Routes ───────────────────────────────────────────────────────────────────

@app.route("/audio/<filename>")
def serve_audio(filename):
    path = audio_files.get(filename) or f"/tmp/{filename}"
    if os.path.exists(path):
        return send_file(path, mimetype="audio/mpeg")
    return ("Not found", 404)


@app.route("/static-audio/<filename>")
def serve_static_audio(filename):
    """Serve pre-generated audio from the script directory."""
    base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, "..", "assets", filename)
    if os.path.exists(path):
        return send_file(os.path.abspath(path), mimetype="audio/mpeg")
    return ("Not found", 404)


@app.route("/call/start", methods=["GET", "POST"])
def call_start():
    call_sid = request.values.get("CallSid", "unknown")
    opening  = request.values.get("opening", "Hi there! I'm calling to speak with you.")
    persona  = request.values.get("persona", "You are making a friendly phone call. Be concise, warm, and natural.")

    personas[call_sid]      = persona
    conversations[call_sid] = [{"role": "assistant", "content": opening}]

    audio_url = tts(opening)
    resp = VoiceResponse()
    gather = Gather(
        input="speech",
        action=f"{PUBLIC_URL}/call/respond",
        method="POST",
        speech_timeout="auto",
        language="en-US"
    )
    gather.play(audio_url)
    resp.append(gather)
    resp.redirect(f"{PUBLIC_URL}/call/start")
    return Response(str(resp), mimetype="text/xml")


@app.route("/call/respond", methods=["POST"])
def call_respond():
    call_sid  = request.values.get("CallSid", "unknown")
    user_said = request.values.get("SpeechResult", "").strip()

    if not user_said:
        resp = VoiceResponse()
        gather = Gather(input="speech", action=f"{PUBLIC_URL}/call/respond",
                        method="POST", speech_timeout="auto")
        gather.play(tts("Sorry, I didn't catch that — could you say that again?"))
        resp.append(gather)
        return Response(str(resp), mimetype="text/xml")

    print(f"👂  Heard: {user_said}")
    ai_reply  = gpt_reply(call_sid, user_said)
    audio_url = tts(ai_reply)

    ending = any(p in ai_reply.lower() for p in
                 ["thank you", "goodbye", "bye", "see you", "take care",
                  "look forward", "all set", "confirmed", "have a great"])

    resp = VoiceResponse()
    if ending:
        resp.play(audio_url)
        resp.hangup()
    else:
        gather = Gather(input="speech", action=f"{PUBLIC_URL}/call/respond",
                        method="POST", speech_timeout="auto", language="en-US")
        gather.play(audio_url)
        resp.append(gather)
    return Response(str(resp), mimetype="text/xml")


@app.route("/call/status", methods=["POST"])
def call_status():
    call_sid = request.values.get("CallSid", "unknown")
    status   = request.values.get("CallStatus", "")
    print(f"📵  Call ended: {status}")
    if status in ("completed", "busy", "no-answer", "failed"):
        send_summary(call_sid)
    return ("", 204)


if __name__ == "__main__":
    if not PUBLIC_URL:
        print("⚠️  Set CALLER_PUBLIC_URL (e.g. https://abc.loca.lt)")
    print(f"🚀  Phone caller server on port {PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=False)
