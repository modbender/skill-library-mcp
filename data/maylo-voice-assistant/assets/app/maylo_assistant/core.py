from __future__ import annotations

import argparse
import json
import os
import queue
import subprocess
import threading
import time
import uuid
import wave
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Deque, Iterable, Optional

import numpy as np
import sounddevice as sd
import webrtcvad
from faster_whisper import WhisperModel
from openwakeword.model import Model as OWWModel

# silence urllib3 LibreSSL warning (common on macOS Python builds)
import warnings

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = ROOT / "models"
RECORDINGS_DIR = ROOT / "recordings"
BRIDGE_DIR = ROOT / "bridge"
REQ_PATH = BRIDGE_DIR / "request.json"
RESP_PATH = BRIDGE_DIR / "response.json"

SAMPLE_RATE = 16000
CHANNELS = 1

# openWakeWord works best with 80ms (1280 samples @ 16k)
WAKE_BLOCK_SAMPLES = int(os.getenv("MAYLO_WAKE_BLOCK_SAMPLES", "1280"))

# Wake word thresholding
WAKEWORD_THRESHOLD = float(os.getenv("MAYLO_WAKE_THRESHOLD", "0.55"))
WAKEWORD_COOLDOWN_SEC = float(os.getenv("MAYLO_WAKE_COOLDOWN", "2.5"))

# Recording / VAD
VAD_AGGRESSIVENESS = int(os.getenv("MAYLO_VAD_MODE", "2"))  # 0-3
VAD_FRAME_MS = 20  # webrtcvad supports 10/20/30 ms
VAD_FRAME_SAMPLES = int(SAMPLE_RATE * VAD_FRAME_MS / 1000)
MAX_RECORD_SEC = float(os.getenv("MAYLO_MAX_RECORD_SEC", "15"))
PRE_ROLL_SEC = float(os.getenv("MAYLO_PRE_ROLL_SEC", "0.7"))
END_SILENCE_SEC = float(os.getenv("MAYLO_END_SILENCE_SEC", "0.9"))

# Whisper
WHISPER_MODEL_SIZE = os.getenv("MAYLO_WHISPER_MODEL", "small")
WHISPER_COMPUTE_TYPE = os.getenv("MAYLO_WHISPER_COMPUTE", "int8")

# TTS
SAY_VOICE = os.getenv("MAYLO_SAY_VOICE", "Yelda")


@dataclass
class WakewordConfig:
    model_paths: list[str]
    model_names: list[str]


def ensure_dirs() -> None:
    MODELS_DIR.mkdir(exist_ok=True)
    RECORDINGS_DIR.mkdir(exist_ok=True)
    BRIDGE_DIR.mkdir(exist_ok=True)


def pick_wakeword_model() -> WakewordConfig:
    """Prefer a custom `models/maylo.onnx` if present, else fallback to builtin hey_jarvis."""
    custom = MODELS_DIR / "maylo.onnx"
    if custom.exists():
        return WakewordConfig(model_paths=[str(custom)], model_names=["maylo"])
    return WakewordConfig(model_paths=[], model_names=["hey_jarvis"])  # builtin


def say(text: str) -> None:
    text = (text or "").strip()
    if not text:
        return
    subprocess.run(["say", "-v", SAY_VOICE, text], check=False)


def write_wav(path: Path, pcm_int16: np.ndarray, sample_rate: int = SAMPLE_RATE) -> None:
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # int16
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_int16.tobytes())


def normalize_float_to_int16(x: np.ndarray) -> np.ndarray:
    # sounddevice gives float32 in [-1, 1]
    x = np.clip(x, -1.0, 1.0)
    return (x * 32767.0).astype(np.int16)


class AudioStream:
    """Single-producer callback -> queue consumer.

    We run the InputStream with an 80ms block (1280 samples @ 16k) for robust wake-word.
    For VAD we internally re-chunk into 20ms frames.
    """

    def __init__(self):
        self.q: "queue.Queue[np.ndarray]" = queue.Queue(maxsize=200)

    def callback(self, indata, frames, time_info, status):
        if status:
            # avoid spam; status can be printed when debugging
            pass
        try:
            self.q.put_nowait(indata[:, 0].copy())
        except queue.Full:
            # drop if overloaded
            pass


def _iter_vad_frames(float_block: np.ndarray) -> Iterable[np.ndarray]:
    """Yield 20ms float frames from a wake block."""
    n = len(float_block)
    i = 0
    while i + VAD_FRAME_SAMPLES <= n:
        yield float_block[i : i + VAD_FRAME_SAMPLES]
        i += VAD_FRAME_SAMPLES


def record_utterance(
    stream: AudioStream,
    pre_roll: Optional[Iterable[np.ndarray]] = None,
) -> np.ndarray:
    """Record one utterance and stop on end-of-speech.

    `pre_roll` should be an iterable of recent float blocks (wake-sized blocks) that will
    be appended before the detected speech start.
    """

    vad = webrtcvad.Vad(VAD_AGGRESSIVENESS)

    pre_roll_frames = int(PRE_ROLL_SEC * 1000 / VAD_FRAME_MS)
    end_silence_frames = int(END_SILENCE_SEC * 1000 / VAD_FRAME_MS)
    max_frames = int(MAX_RECORD_SEC * 1000 / VAD_FRAME_MS)

    # ring contains 20ms frames
    ring: Deque[np.ndarray] = deque(maxlen=max(pre_roll_frames, 1))
    recorded: list[np.ndarray] = []

    # seed ring buffer from passed pre-roll blocks
    if pre_roll:
        for blk in pre_roll:
            for f in _iter_vad_frames(blk):
                ring.append(f)

    in_speech = False
    silence_run = 0
    frames_seen = 0

    while frames_seen < max_frames:
        block = stream.q.get()
        for frame in _iter_vad_frames(block):
            frames_seen += 1
            ring.append(frame)

            pcm16 = normalize_float_to_int16(frame)
            is_speech = vad.is_speech(pcm16.tobytes(), SAMPLE_RATE)

            if not in_speech:
                if is_speech:
                    in_speech = True
                    recorded.extend(list(ring))  # include pre-roll
                    recorded.append(frame)
                    silence_run = 0
            else:
                recorded.append(frame)
                if is_speech:
                    silence_run = 0
                else:
                    silence_run += 1
                    if silence_run >= end_silence_frames:
                        # stop after enough trailing silence
                        frames_seen = max_frames
                        break

    if not recorded:
        # fallback (rare): return what we have
        recorded = list(ring)

    return np.concatenate(recorded, axis=0)


def bridge_request(text: str) -> str:
    req_id = uuid.uuid4().hex[:12]
    payload = {"id": req_id, "ts": time.time(), "text": text, "lang": "tr"}
    REQ_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return req_id


def bridge_wait_response(req_id: str, timeout_sec: float = 60.0) -> Optional[str]:
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        if RESP_PATH.exists():
            try:
                data = json.loads(RESP_PATH.read_text(encoding="utf-8"))
            except Exception:
                data = None

            if (
                isinstance(data, dict)
                and data.get("id") == req_id
                and isinstance(data.get("text"), str)
            ):
                return data["text"].strip()
        time.sleep(0.2)
    return None


class MayloAssistant:
    def __init__(self):
        ensure_dirs()

        ww = pick_wakeword_model()
        if ww.model_paths:
            # IMPORTANT: openwakeword may mutate the passed-in list; keep our label/key separate
            self.wake_name = ww.model_names[0]
            self.wake_label = f"custom models/maylo.onnx (label={self.wake_name})"
            self.oww = OWWModel(wakeword_models=list(ww.model_paths), inference_framework="onnx")
        else:
            # IMPORTANT: openwakeword may mutate the passed-in list (e.g., resolving names to paths)
            self.wake_name = ww.model_names[0]  # e.g., 'hey_jarvis'
            self.wake_label = f"builtin {self.wake_name}"
            self.oww = OWWModel(wakeword_models=list(ww.model_names), inference_framework="onnx")

        self.whisper = WhisperModel(
            WHISPER_MODEL_SIZE, device="cpu", compute_type=WHISPER_COMPUTE_TYPE
        )

        self.stream = AudioStream()
        self._last_trigger = 0.0
        # inhibit wake-word while we are speaking/just spoke (avoid feedback loops)
        self._inhibit_wake_until = 0.0

        # last ~1.2s of audio blocks for robust pre-roll
        self._recent_blocks: Deque[np.ndarray] = deque(
            maxlen=int(float(os.getenv("MAYLO_RECENT_SEC", "1.2")) * SAMPLE_RATE / WAKE_BLOCK_SAMPLES)
            + 1
        )

        # status hooks (for Web UI)
        self.on_state = None  # callable(state: str, payload: dict)

    def _emit(self, state: str, **payload):
        if callable(self.on_state):
            try:
                self.on_state(state, payload)
            except Exception:
                pass

    def listen_forever(self, *, mode: str = "full") -> None:
        """Modes: wake | record | asr | full

        - wake: only detect wake word and print.
        - record: wake + record + save WAV.
        - asr: wake + record + whisper.
        - full: wake + record + whisper + bridge + say.
        """

        print(f"Wakeword: {self.wake_label} | threshold={WAKEWORD_THRESHOLD} | block={WAKE_BLOCK_SAMPLES}")
        print(f"Whisper: {WHISPER_MODEL_SIZE} (compute={WHISPER_COMPUTE_TYPE})")
        print("Ready. Say: 'Hey Jarvis, ...' (or your custom model if installed)")

        self._emit("idle")

        input_device = os.getenv("MAYLO_INPUT_DEVICE")
        if input_device is not None and str(input_device).strip() != "":
            try:
                input_device = int(str(input_device).strip())
            except Exception:
                pass

        wake_debug = os.getenv("MAYLO_WAKE_DEBUG", "0") == "1"
        _debug_i = 0

        sd_device = None
        if isinstance(input_device, int):
            try:
                info = sd.query_devices(input_device)
                if int(info.get('max_input_channels', 0)) >= CHANNELS:
                    sd_device = input_device
                else:
                    print(f"[WARN] MAYLO_INPUT_DEVICE={input_device} has max_input_channels={info.get('max_input_channels')} (need {CHANNELS}); using default device")
            except Exception as e:
                print(f"[WARN] Could not query MAYLO_INPUT_DEVICE={input_device}: {e}; using default device")

        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            blocksize=WAKE_BLOCK_SAMPLES,
            dtype="float32",
            callback=self.stream.callback,
            device=sd_device,
        ):
            while True:
                block = self.stream.q.get()
                self._recent_blocks.append(block)

                pcm16 = normalize_float_to_int16(block)
                pred = self.oww.predict(pcm16)

                # Prefer direct prediction dict; fall back to prediction_buffer
                score = None
                if isinstance(pred, dict):
                    if self.wake_name in pred:
                        score = float(pred[self.wake_name])
                    else:
                        # try fuzzy match (some versions use names like hey_jarvis_v0.1)
                        for k, v in pred.items():
                            if self.wake_name.replace("hey_", "") in str(k):
                                score = float(v)
                                self.wake_name = k  # align buffer key
                                break

                if score is None:
                    try:
                        scores = list(self.oww.prediction_buffer[self.wake_name])
                        score = float(scores[-1]) if scores else 0.0
                    except Exception:
                        score = 0.0
                else:
                    # keep buffer in sync for later code paths
                    score = float(score)

                if wake_debug:
                    _debug_i += 1
                    if _debug_i == 10:
                        print(f"[WAKE_DEBUG] pred_keys={list(pred.keys()) if isinstance(pred, dict) else type(pred)} wake_name={self.wake_name}")
                    if _debug_i % 10 == 0:
                        # quick signal sanity check
                        x = block.astype(np.float32)
                        rms = float(np.sqrt(np.mean(np.square(x))))
                        peak = float(np.max(np.abs(x)))
                        print(f"[WAKE_DEBUG] score={score:.6f} rms={rms:.4f} peak={peak:.4f}")

                now = time.time()
                if now < self._inhibit_wake_until:
                    continue

                if score >= WAKEWORD_THRESHOLD and (now - self._last_trigger) > WAKEWORD_COOLDOWN_SEC:
                    self._last_trigger = now
                    # short inhibit right after wake as well
                    self._inhibit_wake_until = now + float(os.getenv("MAYLO_WAKE_INHIBIT_SEC", "1.2"))
                    ts = time.strftime("%Y-%m-%d %H:%M:%S")
                    print(f"\n[WAKE] {ts} {self.wake_name} score={score:.2f}")
                    self._emit("wake", model=self.wake_name, score=score, ts=time.time())

                    if mode == "wake":
                        continue

                    # give immediate feedback WITHOUT polluting the recording
                    # Default: no TTS here (to avoid the mic hearing itself). Use UI state instead.
                    feedback = os.getenv("MAYLO_WAKE_FEEDBACK", "none")  # none|tts|beep
                    self._emit("listening")

                    if feedback == "tts":
                        self._emit("speaking")
                        say("Dinliyorum")
                        # give time for speakers to stop ringing and let the mic settle
                        time.sleep(float(os.getenv("MAYLO_POST_TTS_SLEEP", "0.6")))
                        self._emit("listening")
                    elif feedback == "beep":
                        # short system beep (usually less likely to be transcribed)
                        try:
                            subprocess.run(["/usr/bin/afplay", "/System/Library/Sounds/Ping.aiff"], check=False)
                        except Exception:
                            pass
                        time.sleep(0.2)

                    # Reset pre-roll so we don't include our own feedback audio
                    self._recent_blocks.clear()

                    audio = record_utterance(self.stream, pre_roll=[])
                    pcm16_full = normalize_float_to_int16(audio)

                    wav_path = RECORDINGS_DIR / f"utterance_{int(time.time())}.wav"
                    write_wav(wav_path, pcm16_full)
                    print(f"Saved: {wav_path}")

                    if mode == "record":
                        self._emit("idle")
                        continue

                    self._emit("processing")
                    segments, info = self.whisper.transcribe(
                        str(wav_path), language="tr", vad_filter=True, beam_size=5
                    )
                    text = " ".join([s.text.strip() for s in segments]).strip()
                    print(f"[ASR] {text}")
                    self._emit("transcript", text=text, wav=str(wav_path))

                    if mode == "asr":
                        self._emit("idle")
                        continue

                    if not text:
                        self._emit("speaking")
                        say("Anlayamadım. Tekrar eder misin?")
                        self._emit("idle")
                        continue

                    req_id = bridge_request(text)
                    print(f"[BRIDGE] request id={req_id} -> {REQ_PATH}")
                    self._emit("bridge_request", id=req_id, text=text)

                    reply = bridge_wait_response(req_id)
                    if reply is None:
                        print("[BRIDGE] timeout waiting for response.json")
                        self._emit("speaking")
                        say("Bir sorun oldu. Cevabı alamadım.")
                        self._emit("idle")
                        continue

                    print(f"[MILO] {reply}")
                    self._emit("reply", text=reply)
                    self._emit("speaking")
                    # inhibit wake for a bit while/after speaking to avoid feedback loops
                    self._inhibit_wake_until = time.time() + float(os.getenv("MAYLO_POST_SAY_INHIBIT_SEC", "4.0"))
                    say(reply)
                    self._emit("idle")

    def run_once_from_pcm16(
        self,
        pcm16_full: np.ndarray,
        *,
        sample_rate: int = SAMPLE_RATE,
        source: str = "web",
    ) -> Optional[str]:
        """Run the full pipeline (ASR -> bridge -> say) for externally provided audio.

        `pcm16_full` must be mono int16 samples at 16kHz.
        Returns transcript text (or None).
        """
        pcm16_full = np.asarray(pcm16_full, dtype=np.int16).reshape(-1)
        if pcm16_full.size == 0:
            self._emit("idle")
            return None

        wav_path = RECORDINGS_DIR / f"{source}_{int(time.time())}.wav"
        write_wav(wav_path, pcm16_full, sample_rate=sample_rate)
        print(f"[{source.upper()}] Saved: {wav_path}")

        self._emit("processing")
        segments, info = self.whisper.transcribe(
            str(wav_path), language="tr", vad_filter=True, beam_size=5
        )
        text = " ".join([s.text.strip() for s in segments]).strip()
        print(f"[ASR] {text}")
        self._emit("transcript", text=text, wav=str(wav_path))

        if not text:
            self._emit("speaking")
            say("Anlayamadım. Tekrar eder misin?")
            self._emit("idle")
            return None

        req_id = bridge_request(text)
        print(f"[BRIDGE] request id={req_id} -> {REQ_PATH}")
        self._emit("bridge_request", id=req_id, text=text)

        reply = bridge_wait_response(req_id)
        if reply is None:
            print("[BRIDGE] timeout waiting for response.json")
            self._emit("speaking")
            say("Bir sorun oldu. Cevabı alamadım.")
            self._emit("idle")
            return text

        print(f"[MILO] {reply}")
        self._emit("reply", text=reply)
        self._emit("speaking")
        say(reply)
        self._emit("idle")
        return text

    def run_once_ptt(self) -> Optional[str]:
        """Push-to-talk (server microphone): record -> ASR -> bridge -> say."""
        self._emit("listening")
        self._emit("speaking")
        say("Dinliyorum")

        audio = record_utterance(self.stream, pre_roll=list(self._recent_blocks))
        pcm16_full = normalize_float_to_int16(audio)
        return self.run_once_from_pcm16(pcm16_full, sample_rate=SAMPLE_RATE, source="ptt")


def cli():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--mode",
        choices=["wake", "record", "asr", "full"],
        default=os.getenv("MAYLO_MODE", "full"),
        help="Pipeline stage for step-by-step testing",
    )
    args = p.parse_args()
    a = MayloAssistant()
    a.listen_forever(mode=args.mode)


if __name__ == "__main__":
    cli()
