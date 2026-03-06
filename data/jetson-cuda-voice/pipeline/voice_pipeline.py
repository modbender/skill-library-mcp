#!/usr/bin/env python3
"""
Jetson CUDA Voice Pipeline — Local, Low-Latency, Fully Offline
Wake word → VAD+STT (streaming, same mic pipe) → LLM → Piper TTS

Key design decisions:
- arecord stream is NEVER restarted between wake word and command.
  The same pipe feeds wake word detection AND command transcription,
  eliminating the ~1s gap that caused "I didn't catch that."
- Dynamic ambient noise calibration on every wake word trigger.
- Conversation history (10 turns) for natural follow-up questions.
- ReSpeaker LED feedback: blue=listening, cyan=thinking, off=done, red=error.
- Piper TTS is hot-loaded at startup (no subprocess cold start).
- Mic is flushed after TTS playback to prevent echo → wake word loop.

Hardware tested on: NVIDIA Jetson Xavier NX (sm_72, JetPack 5.1.4)
Mic: ReSpeaker USB Mic Array v1.0 (2886:0007) — S24_3LE format, hw:Array,0
Speaker: Any ALSA device (tested with Creative MUVO 2c, hw:C2c,0)
"""

import os, io, time, wave, signal, re, subprocess, threading, sys
import numpy as np, requests, logging

sys.path.insert(0, os.path.dirname(__file__))
import led

# ─────────────────────────────────────────────────────────────────────────────
# Config — override via environment variables
# ─────────────────────────────────────────────────────────────────────────────
HOME             = os.path.expanduser("~")
MIC_DEVICE       = os.environ.get("VOICE_MIC",     "hw:Array,0")     # ReSpeaker USB name
SPEAKER_DEVICE   = os.environ.get("VOICE_SPEAKER", "hw:C2c,0")       # adjust for your speaker
SAMPLE_RATE      = 16000
CHANNELS         = 2
BYTES_PER_SAMPLE = 3            # S24_3LE
CHUNK_SAMPLES    = 512          # ~32ms (openWakeWord required)
FRAME_BYTES      = CHUNK_SAMPLES * BYTES_PER_SAMPLE * CHANNELS

# openWakeWord — built-in models dir (set by pip install)
import importlib.util as _ilu
_OWW_SPEC        = _ilu.find_spec("openwakeword")
_OWW_MODELS_DIR  = os.path.join(os.path.dirname(_OWW_SPEC.origin),
                                "resources", "models") if _OWW_SPEC else ""
_CUSTOM_MODELS_DIR = os.environ.get("VOICE_WAKEWORD_DIR",
                                    os.path.join(HOME, ".local", "share", "wakewords"))

def _find_wake_models() -> list:
    """Return all .onnx model paths to load (builtin hey_jarvis + custom)."""
    import glob
    builtin = [os.path.join(_OWW_MODELS_DIR, "hey_jarvis_v0.1.onnx")]
    custom  = glob.glob(f"{_CUSTOM_MODELS_DIR}/*.onnx") if os.path.isdir(_CUSTOM_MODELS_DIR) else []
    return [p for p in builtin if os.path.exists(p)] + custom

WAKE_THRESHOLD   = float(os.environ.get("VOICE_WAKE_THRESHOLD", "0.5"))

# Piper TTS voices
PIPER_VOICES_DIR = os.environ.get("PIPER_VOICES_DIR",
                                  os.path.join(HOME, ".local", "share", "piper", "voices"))
PIPER_VOICE_EN   = os.path.join(PIPER_VOICES_DIR, "en_US-lessac-medium.onnx")
PIPER_VOICE_EL   = os.path.join(PIPER_VOICES_DIR, "el_GR-rapunzelina-medium.onnx")

# LLM via OpenRouter (or any OpenAI-compatible API)
LLM_URL          = os.environ.get("VOICE_LLM_URL",  "https://openrouter.ai/api/v1/chat/completions")
LLM_API_KEY      = os.environ.get("OPENROUTER_API_KEY", "")
LLM_MODEL        = os.environ.get("VOICE_LLM_MODEL", "anthropic/claude-3.5-haiku")
LLM_TIMEOUT      = int(os.environ.get("VOICE_LLM_TIMEOUT", "30"))

# Whisper GPU server (whisper.cpp built with CUDA sm_72)
WHISPER_URL      = os.environ.get("WHISPER_URL", "http://127.0.0.1:8181/inference")

# VAD thresholds — dynamic per-trigger calibration overrides these at runtime.
# These are safe fallbacks for a noisy room (fans, AC, Jetson itself).
SPEECH_START_RMS  = int(os.environ.get("VOICE_SPEECH_RMS",  "400"))
SILENCE_BELOW_RMS = int(os.environ.get("VOICE_SILENCE_RMS", "250"))
PRE_SPEECH_TIMEOUT_S = 4.0
SILENCE_CUTOFF_S     = 0.6
MAX_UTTERANCE_S      = 6.0

# ─────────────────────────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────────────────────────
LOG_FILE = os.environ.get("VOICE_LOG", "/tmp/voice-pipeline.log")
log = logging.getLogger("jetson.voice")
log.setLevel(logging.INFO)
_fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
for h in (logging.FileHandler(LOG_FILE), logging.StreamHandler()):
    h.setFormatter(_fmt)
    log.addHandler(h)

# ─────────────────────────────────────────────────────────────────────────────
# Audio helpers
# ─────────────────────────────────────────────────────────────────────────────
def s24le_to_int16_mono(data: bytes) -> np.ndarray:
    """Convert S24_3LE stereo bytes → mono int16 numpy array."""
    raw = np.frombuffer(data, dtype=np.uint8)
    n   = len(raw) // (3 * CHANNELS)
    if n == 0:
        return np.zeros(0, dtype=np.int16)
    raw  = raw[:n * 3 * CHANNELS].reshape(n, CHANNELS, 3)
    left = raw[:, 0, :]
    vals = (left[:,0].astype(np.int32)
            | (left[:,1].astype(np.int32) << 8)
            | (left[:,2].astype(np.int32) << 16))
    vals = np.where(vals >= 2**23, vals - 2**24, vals)
    return (vals >> 8).astype(np.int16)


def _detect_greek(text: str) -> bool:
    return any('\u0370' <= c <= '\u03ff' or '\u1f00' <= c <= '\u1fff' for c in text)


def strip_markdown(text: str) -> str:
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`[^`]+`', '', text)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', text)
    text = re.sub(r'_{1,3}([^_]+)_{1,3}', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    text = re.sub(r'^\s*[-*+•]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


# ─────────────────────────────────────────────────────────────────────────────
# Audio output
# ─────────────────────────────────────────────────────────────────────────────
def _aplay(wav_bytes: bytes):
    plug = 'plughw:' + SPEAKER_DEVICE.replace('hw:', '')
    subprocess.run(['aplay', '-q', '-D', plug, '-'],
                   input=wav_bytes, capture_output=True, timeout=120)


def _drain_mic(seconds: float):
    """Read and discard `seconds` of mic audio to flush echo."""
    proc = subprocess.Popen(
        ['arecord', '-D', MIC_DEVICE, '-f', 'S24_3LE',
         '-r', str(SAMPLE_RATE), '-c', str(CHANNELS), '-t', 'raw', '-q'],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
    )
    n = int(seconds * SAMPLE_RATE / CHUNK_SAMPLES)
    try:
        for _ in range(n):
            proc.stdout.read(FRAME_BYTES)
    finally:
        proc.terminate(); proc.wait()


def play_beep():
    """Two-tone confirmation beep (660Hz → 880Hz) to signal ready-to-listen."""
    rate = 22050
    dur  = 0.2
    t    = np.linspace(0, dur, int(rate * dur), False)
    tone = np.concatenate([np.sin(2*np.pi*660*t[:len(t)//2]),
                           np.sin(2*np.pi*880*t[len(t)//2:])])
    pcm  = (tone * 14000).astype(np.int16)
    buf  = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(rate)
        wf.writeframes(pcm.tobytes())
    _aplay(buf.getvalue())


# ─────────────────────────────────────────────────────────────────────────────
# Piper TTS (offline, hot-loaded)
# ─────────────────────────────────────────────────────────────────────────────
_piper_en = None
_piper_el = None

def load_piper():
    global _piper_en, _piper_el
    from piper import PiperVoice
    log.info("Loading Piper EN...")
    t0 = time.time()
    _piper_en = PiperVoice.load(PIPER_VOICE_EN, config_path=PIPER_VOICE_EN+".json", use_cuda=False)
    log.info(f"✅ Piper EN ({time.time()-t0:.1f}s)")
    if os.path.exists(PIPER_VOICE_EL):
        log.info("Loading Piper EL...")
        t0 = time.time()
        _piper_el = PiperVoice.load(PIPER_VOICE_EL, config_path=PIPER_VOICE_EL+".json", use_cuda=False)
        log.info(f"✅ Piper EL ({time.time()-t0:.1f}s)")


def speak(text: str):
    text = strip_markdown(text)
    if not text or len(text) < 2:
        return
    if len(text) > 180:
        text = text[:175].rsplit(' ', 1)[0] + "."
    log.info(f"🔊 ({len(text)}ch): {text[:80]}{'…' if len(text)>80 else ''}")
    voice = _piper_el if (_detect_greek(text) and _piper_el) else _piper_en
    if not voice:
        log.error("Piper not loaded"); return
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        voice.synthesize_wav(text, wf)
    _aplay(buf.getvalue())


# ─────────────────────────────────────────────────────────────────────────────
# Ambient noise calibration + VAD
# ─────────────────────────────────────────────────────────────────────────────
def _measure_ambient(stream, n_chunks: int = 15) -> float:
    """
    Sample ~480ms of audio right after the beep (before user speaks).
    Returns median per-chunk RMS — the real ambient floor for this moment.
    Thresholds derived from this are per-trigger, adapting to changing
    conditions (different rooms, fans, AC, time of day).
    """
    rms_values = []
    for _ in range(n_chunks):
        data = stream.read(FRAME_BYTES)
        if not data or len(data) < FRAME_BYTES:
            break
        chunk = s24le_to_int16_mono(data)
        rms_values.append(float(np.sqrt(np.mean(chunk.astype(np.float64) ** 2))))
    if not rms_values:
        return SILENCE_BELOW_RMS
    rms_values.sort()
    return rms_values[len(rms_values) // 2]


def transcribe_stream(stream, speech_rms: float = None, silence_rms: float = None) -> str:
    """
    VAD-based audio capture followed by whisper.cpp GPU HTTP inference.

    Hysteresis design: the zone between silence_threshold and speech_threshold
    is neutral — it doesn't advance silence count OR reset it. This prevents
    fan noise / ambient spikes from extending recordings indefinitely.

    After speech ends, requires SILENCE_CUTOFF_S of sustained quiet before
    cutting off — adapts cleanly to slow speakers and brief pauses.
    """
    speech_threshold  = speech_rms  if speech_rms  is not None else SPEECH_START_RMS
    silence_threshold = silence_rms if silence_rms is not None else SILENCE_BELOW_RMS

    PRE_SPEECH_CHUNKS = int(PRE_SPEECH_TIMEOUT_S * SAMPLE_RATE / CHUNK_SAMPLES)
    MAX_CHUNKS        = int(MAX_UTTERANCE_S       * SAMPLE_RATE / CHUNK_SAMPLES)
    QUIET_NEEDED      = int(SILENCE_CUTOFF_S      * SAMPLE_RATE / CHUNK_SAMPLES)

    speech_started = False
    pre_wait       = 0
    quiet_streak   = 0
    audio_bytes    = bytearray()

    log.info(f"   VAD: speech>{speech_threshold:.0f} silence<{silence_threshold:.0f} "
             f"cutoff={SILENCE_CUTOFF_S}s timeout={PRE_SPEECH_TIMEOUT_S}s")

    for i in range(MAX_CHUNKS):
        data = stream.read(FRAME_BYTES)
        if not data or len(data) < FRAME_BYTES:
            break

        chunk = s24le_to_int16_mono(data)
        audio_bytes.extend(chunk.tobytes())
        rms = float(np.sqrt(np.mean(chunk.astype(np.float64) ** 2)))

        if i % 16 == 0:
            tag = "SPEECH" if rms > speech_threshold else ("quiet" if rms < silence_threshold else "~")
            log.info(f"   [{i*32:4d}ms] rms={rms:5.0f} [{tag}]")

        if not speech_started:
            if rms > speech_threshold:
                speech_started = True
                quiet_streak   = 0
            else:
                pre_wait += 1
                if pre_wait >= PRE_SPEECH_CHUNKS:
                    log.info("   (no speech — timeout)")
                    break
        else:
            if rms > speech_threshold:
                quiet_streak = 0
            elif rms < silence_threshold:
                quiet_streak += 1

        if speech_started and quiet_streak >= QUIET_NEEDED:
            log.info(f"   silence cutoff at {i*32}ms")
            break

    if not speech_started or not audio_bytes:
        return ""

    log.info("   Sending to whisper-server (GPU)...")
    try:
        wav_io = io.BytesIO()
        with wave.open(wav_io, 'wb') as wf:
            wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SAMPLE_RATE)
            wf.writeframes(audio_bytes)
        wav_io.seek(0)
        resp = requests.post(
            WHISPER_URL,
            files={"file": ("audio.wav", wav_io, "audio/wav")},
            data={"temperature": "0.0", "response_format": "json", "language": "auto"},
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json().get("text", "").strip()
    except Exception as e:
        log.error(f"Whisper inference failed: {e}")
        return ""


# ─────────────────────────────────────────────────────────────────────────────
# LLM (OpenRouter or any OpenAI-compatible endpoint)
# ─────────────────────────────────────────────────────────────────────────────
_chat_history: list[dict] = []

def _local_context() -> str:
    from datetime import datetime, timezone, timedelta
    tz  = timezone(timedelta(hours=int(os.environ.get("VOICE_UTC_OFFSET", "0"))))
    now = datetime.now(tz).strftime("%A, %H:%M")
    return f"Current local time: {now}."


def ask_llm(message: str) -> str:
    """Send to LLM with rolling 10-turn conversation history."""
    global _chat_history
    if not LLM_API_KEY:
        log.error("OPENROUTER_API_KEY not set — set the env var")
        return "LLM API key not configured."

    system = (
        f"You are a voice assistant. "
        f"Answer in 1-2 short spoken sentences — no greetings, no markdown, no lists. "
        + _local_context()
    )
    _chat_history.append({"role": "user", "content": message})
    if len(_chat_history) > 20:
        _chat_history = _chat_history[-20:]

    try:
        resp = requests.post(
            LLM_URL,
            headers={"Authorization": f"Bearer {LLM_API_KEY}",
                     "Content-Type": "application/json"},
            json={"model":    LLM_MODEL,
                  "messages": [{"role": "system", "content": system}] + _chat_history,
                  "max_tokens": 100},
            timeout=LLM_TIMEOUT + 10,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("choices"):
            reply = data["choices"][0]["message"]["content"].strip()
            _chat_history.append({"role": "assistant", "content": reply})
            return reply
        log.error(f"Unexpected LLM response: {data}")
        return "Sorry, something went wrong."
    except requests.Timeout:
        return "That took too long, please try again."
    except Exception as e:
        log.error(f"LLM error: {e}")
        return "Sorry, I can't reach the LLM right now."


def warmup():
    try:
        log.info("⏳ Warming up LLM connection...")
        t0 = time.time()
        ask_llm("say OK")
        log.info(f"✅ LLM ready ({time.time()-t0:.1f}s)")
    except Exception as e:
        log.warning(f"LLM warmup failed (non-fatal): {e}")


# ─────────────────────────────────────────────────────────────────────────────
# Main pipeline
# ─────────────────────────────────────────────────────────────────────────────
class VoicePipeline:
    def __init__(self):
        self.running   = False
        self.oww_model = None
        self._oww_keys = []
        self._arecord  = None

    def _load_models(self):
        load_piper()
        wake_models = _find_wake_models()
        log.info(f"Loading openWakeWord ({len(wake_models)} models)...")
        for p in wake_models:
            log.info(f"   {os.path.basename(p)}")
        from openwakeword.model import Model
        self.oww_model = Model(wakeword_model_paths=wake_models)
        self.oww_model.predict(np.zeros(CHUNK_SAMPLES, dtype=np.float32))
        self._oww_keys = list(self.oww_model.prediction_buffer.keys())
        log.info(f"✅ openWakeWord ready — wake words: {self._oww_keys}")
        led.init()
        warmup()

    def _reset_oww(self):
        for key in self.oww_model.prediction_buffer:
            self.oww_model.prediction_buffer[key].clear()

    def _check_wake(self, preds: dict) -> tuple[bool, str]:
        for key, score in preds.items():
            if score > WAKE_THRESHOLD:
                return True, key
        return False, ""

    def _signal_handler(self, signum, _):
        log.info(f"Signal {signum} — stopping")
        self.running = False
        if self._arecord and self._arecord.poll() is None:
            self._arecord.kill()

    def run(self):
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT,  self._signal_handler)
        self.running = True
        self._load_models()
        log.info("🎙️  Ready — say 'Hey Jarvis'")

        while self.running:
            try:
                self._arecord = subprocess.Popen(
                    ['arecord', '-D', MIC_DEVICE, '-f', 'S24_3LE',
                     '-r', str(SAMPLE_RATE), '-c', str(CHANNELS), '-t', 'raw', '-q'],
                    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                )
                log.info("🔴 Listening...")

                while self.running and self._arecord.poll() is None:
                    data = self._arecord.stdout.read(FRAME_BYTES)
                    if not data or len(data) < FRAME_BYTES:
                        continue

                    chunk = s24le_to_int16_mono(data)
                    preds = self.oww_model.predict(chunk)
                    triggered, wake_key = self._check_wake(preds)

                    if triggered:
                        log.info(f"🎯 Wake word! [{wake_key}] score={preds[wake_key]:.3f}")

                        # Beep confirmation (non-blocking — mic keeps buffering)
                        beep_t = threading.Thread(target=play_beep, daemon=True)
                        beep_t.start()
                        beep_t.join()

                        # Drain beep echo from mic buffer (speaker pickup)
                        discard = int(SAMPLE_RATE * 0.3) * 3 * CHANNELS
                        try:
                            self._arecord.stdout.read(discard)
                        except Exception:
                            pass

                        # Measure live ambient noise floor (~480ms, median RMS)
                        ambient = _measure_ambient(self._arecord.stdout)
                        s_thresh = max(SPEECH_START_RMS,  ambient * 3.5)
                        q_thresh = max(ambient * 1.3, ambient + 40)
                        log.info(f"   🎚️  Ambient={ambient:.0f} → speech>{s_thresh:.0f} silence<{q_thresh:.0f}")

                        led.listen()  # 🔵 blue

                        log.info("🎙️  Listening for command...")
                        t0       = time.time()
                        raw_text = transcribe_stream(self._arecord.stdout,
                                                     speech_rms=s_thresh,
                                                     silence_rms=q_thresh)
                        text = re.sub(r'\[.*?\]', '', raw_text).strip()
                        text = re.sub(r'\(.*?\)', '', text).strip()
                        log.info(f"   STT {time.time()-t0:.1f}s: '{text}'")

                        if text:
                            log.info(f"🤖 → LLM: {text}")
                            led.think()   # 🔵 cyan
                            t0  = time.time()
                            rep = ask_llm(text)
                            log.info(f"   ← {time.time()-t0:.1f}s: {rep[:80]}")
                            speak(rep)
                            led.off()     # ⚫ done
                        else:
                            led.error()   # 🔴 red
                            speak("I didn't catch that — please try again after the beep.")
                            led.off()
                            play_beep()
                            _drain_mic(0.3)

                        self._reset_oww()
                        log.info("🔄 Resuming...")
                        break

                if self._arecord and self._arecord.poll() is None:
                    self._arecord.kill()
                    try:
                        self._arecord.stdout.read()
                    except Exception:
                        pass
                    try:
                        self._arecord.wait(timeout=2.0)
                    except Exception:
                        pass
                self._arecord = None
                if self.running:
                    time.sleep(3.0)  # acoustic echo decay before next listen cycle

            except Exception as e:
                log.error(f"Pipeline error: {e}", exc_info=True)
                time.sleep(2)

        log.info("👋 Stopped")


if __name__ == "__main__":
    VoicePipeline().run()
