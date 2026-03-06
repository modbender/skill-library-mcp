#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
VOICE_DIR="$WORKSPACE/voice-input"
VENV="${VENV_PATH:-$WORKSPACE/.venv-faster-whisper}"
SERVICE_FILE="$HOME/.config/systemd/user/openclaw-transcribe.service"
PYTHON_BIN="${PYTHON_BIN:-python3}"
TRANSCRIBE_PORT="${TRANSCRIBE_PORT:-18790}"
MODEL_SIZE="${WHISPER_MODEL_SIZE:-medium}"
DEVICE="${WHISPER_DEVICE:-cpu}"
COMPUTE_TYPE="${WHISPER_COMPUTE_TYPE:-int8}"
ALLOWED_ORIGIN="${TRANSCRIBE_ALLOWED_ORIGIN:-https://127.0.0.1:8443}"
LANGUAGE="${WHISPER_LANGUAGE:-auto}"
FW_VERSION="${FASTER_WHISPER_VERSION:-1.1.1}"

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "missing dependency: $1" >&2
    exit 2
  }
}

need_cmd "$PYTHON_BIN"
need_cmd gst-launch-1.0

mkdir -p "$VOICE_DIR" "$HOME/.config/systemd/user"

if [[ ! -d "$VENV" ]]; then
  "$PYTHON_BIN" -m venv "$VENV"
fi

"$VENV/bin/pip" install --upgrade pip >/dev/null
"$VENV/bin/pip" install "faster-whisper==${FW_VERSION}" >/dev/null

cat > "$VOICE_DIR/transcribe-server.py" <<PY
#!/usr/bin/env python3
import json, tempfile, os, subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from faster_whisper import WhisperModel

PORT=int(os.getenv('TRANSCRIBE_PORT','${TRANSCRIBE_PORT}'))
MODEL_SIZE=os.getenv('WHISPER_MODEL_SIZE','${MODEL_SIZE}')
DEVICE=os.getenv('WHISPER_DEVICE','${DEVICE}')
COMPUTE=os.getenv('WHISPER_COMPUTE_TYPE','${COMPUTE_TYPE}')
ALLOWED_ORIGIN=os.getenv('TRANSCRIBE_ALLOWED_ORIGIN','${ALLOWED_ORIGIN}')
LANGUAGE=os.getenv('WHISPER_LANGUAGE','${LANGUAGE}')

print(f'[transcribe] Loading model {MODEL_SIZE} ({DEVICE}/{COMPUTE})...')
model=WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE)
print(f'[transcribe] Model loaded.')
print(f'[transcribe] Language: {LANGUAGE} (auto = auto-detect)')
print(f'[transcribe] Listening on http://127.0.0.1:{PORT}')

def to_wav(src, dst):
    subprocess.check_call([
      'gst-launch-1.0','-q','filesrc',f'location={src}','!','decodebin','!','audioconvert','!','audioresample','!','wavenc','!','filesink',f'location={dst}'
    ])

class H(BaseHTTPRequestHandler):
    def _cors(self):
      self.send_header('Access-Control-Allow-Origin',ALLOWED_ORIGIN)
      self.send_header('Vary','Origin')
      self.send_header('Access-Control-Allow-Methods','POST, OPTIONS')
      self.send_header('Access-Control-Allow-Headers','Content-Type')
    def do_OPTIONS(self):
      self.send_response(204); self._cors(); self.end_headers()
    def do_POST(self):
      if self.path != '/transcribe':
        self.send_response(404); self.end_headers(); return
      n=int(self.headers.get('Content-Length','0'))
      b=self.rfile.read(n)
      with tempfile.TemporaryDirectory() as d:
        src=os.path.join(d,'in.bin'); wav=os.path.join(d,'in.wav')
        open(src,'wb').write(b)
        try:
          to_wav(src,wav)
          lang_arg={'language': LANGUAGE} if LANGUAGE != 'auto' else {}
          segs,info=model.transcribe(wav, **lang_arg)
          text=' '.join(s.text.strip() for s in segs).strip()
          out=json.dumps({'text':text}).encode()
          self.send_response(200); self._cors(); self.send_header('Content-Type','application/json'); self.end_headers(); self.wfile.write(out)
        except Exception as e:
          out=json.dumps({'error':str(e)}).encode()
          self.send_response(500); self._cors(); self.send_header('Content-Type','application/json'); self.end_headers(); self.wfile.write(out)

HTTPServer(('127.0.0.1',PORT),H).serve_forever()
PY
chmod +x "$VOICE_DIR/transcribe-server.py"

cat > "$SERVICE_FILE" <<UNIT
[Unit]
Description=OpenClaw Voice Transcription Server (faster-whisper)
After=network.target

[Service]
Type=simple
Environment=TRANSCRIBE_PORT=${TRANSCRIBE_PORT}
Environment=WHISPER_MODEL_SIZE=${MODEL_SIZE}
Environment=WHISPER_DEVICE=${DEVICE}
Environment=WHISPER_COMPUTE_TYPE=${COMPUTE_TYPE}
Environment=TRANSCRIBE_ALLOWED_ORIGIN=${ALLOWED_ORIGIN}
Environment=WHISPER_LANGUAGE=${LANGUAGE}
ExecStart=${VENV}/bin/python ${VOICE_DIR}/transcribe-server.py
Restart=always
RestartSec=2

[Install]
WantedBy=default.target
UNIT

systemctl --user daemon-reload
systemctl --user enable --now openclaw-transcribe.service
systemctl --user restart openclaw-transcribe.service

echo "deploy:ok workspace=${WORKSPACE} model=${MODEL_SIZE} port=${TRANSCRIBE_PORT}"
