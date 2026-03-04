#!/usr/bin/env python3
import os, sys, json, base64, subprocess, threading, queue, tempfile

DEVICE = os.environ.get("RT_DEVICE", ":0")
LANG_CODE = os.environ.get("RT_LANG", "")
TTS_ENGINE = os.environ.get("RT_TTS", "none")
VOICE_ID = os.environ.get("RT_VOICE_ID", "")
API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
MODEL_ID = "scribe_v2_realtime"
AUDIO_FORMAT = "pcm_16000"

if not API_KEY:
    print("Error: ELEVENLABS_API_KEY not set", file=sys.stderr)
    sys.exit(1)

WS_URL = f"wss://api.elevenlabs.io/v1/speech-to-text/realtime?model_id={MODEL_ID}&audio_format={AUDIO_FORMAT}&include_timestamps=true"
if LANG_CODE:
    WS_URL += f"&language_code={LANG_CODE}"

sample_rate = 16000
bytes_per_sample = 2
chunk_ms = 200
bytes_per_ms = int(sample_rate * bytes_per_sample / 1000)
chunk_bytes = bytes_per_ms * chunk_ms

# ffmpeg mic capture (continuous)
ffmpeg_cmd = [
    "ffmpeg", "-hide_banner", "-loglevel", "error",
    "-f", "avfoundation", "-i", DEVICE,
    "-ac", "1", "-ar", str(sample_rate), "-f", "s16le", "pipe:1"
]
ffmpeg = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

# websocat websocket
ws = subprocess.Popen([
    "websocat", WS_URL, "-t", "-H", f"xi-api-key: {API_KEY}"
], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)

q = queue.Queue()

def reader():
    for line in ws.stdout:
        q.put(line.strip())

threading.Thread(target=reader, daemon=True).start()


def tts_say(text):
    # Use -- to avoid option injection
    subprocess.Popen(["say", "--", text])


def tts_elevenlabs(text):
    if not VOICE_ID:
        print("[tts] No ELEVENLABS_VOICE_ID set", file=sys.stderr)
        return False
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tmp.close()
    tts_cmd = [
        "curl", "-s", "-X", "POST",
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream",
        "-H", f"xi-api-key: {API_KEY}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps({"text": text})
    ]
    with open(tmp.name, "wb") as f:
        subprocess.run(tts_cmd, stdout=f, stderr=subprocess.DEVNULL)

    # Validate MP3 header (avoid AudioFileOpen errors on bad payloads)
    try:
        if os.path.getsize(tmp.name) < 4:
            return False
        with open(tmp.name, "rb") as f:
            head = f.read(3)
        if head not in (b"ID3", b"\xff\xfb", b"\xff\xf3", b"\xff\xf2"):
            return False
        subprocess.Popen(["afplay", tmp.name])
        return True
    except Exception:
        return False


def speak(text):
    if not text:
        return
    if TTS_ENGINE == "say":
        tts_say(text)
    elif TTS_ENGINE == "elevenlabs":
        ok = tts_elevenlabs(text)
        if not ok:
            # Fallback to say so user hears *something*
            tts_say(text)

chunk = ffmpeg.stdout.read(chunk_bytes)
count = 0
last_text = ""
while chunk:
    next_chunk = ffmpeg.stdout.read(chunk_bytes)
    count += 1
    # Force periodic commits so we actually receive committed transcripts
    commit = True if (count % 10 == 0) else False
    b64 = base64.b64encode(chunk).decode("ascii")
    msg = {
        "message_type": "input_audio_chunk",
        "audio_base_64": b64,
        "commit": commit,
        "sample_rate": sample_rate,
    }
    try:
        ws.stdin.write(json.dumps(msg) + "\n")
        ws.stdin.flush()
    except Exception:
        break

    while not q.empty():
        try:
            data = json.loads(q.get())
        except Exception:
            continue
        mtype = data.get("message_type", "")
        if mtype in ("committed_transcript", "committed_transcript_with_timestamps"):
            text = data.get("text", "")
            if text and text != last_text:
                last_text = text
                print(text, flush=True)
                speak(text)

    chunk = next_chunk
