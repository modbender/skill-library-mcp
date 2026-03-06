"""Audio pipeline: mic capture, wake word detection, speech-to-text."""

import logging
import random
import struct
import threading
import time
import wave
import winsound
from pathlib import Path

import numpy as np
import sounddevice as sd

from config import (
    ASSETS_DIR,
    PORCUPINE_ACCESS_KEY,
    PORCUPINE_MODEL_PATH,
    SAMPLE_RATE,
    SILENCE_TIMEOUT,
    WAKE_SENSITIVITY,
    WHISPER_MODEL,
)

log = logging.getLogger(__name__)

# Lazy-loaded globals
_porcupine = None
_whisper_model = None

# Mic suppression: when True, the audio callback drops all frames.
# This prevents the mic from picking up speaker output (chime, thinking, TTS).
_mic_suppressed = False
_suppress_lock = threading.Lock()


def suppress_mic():
    """Suppress mic input (call before playing any audio through speakers)."""
    global _mic_suppressed
    with _suppress_lock:
        _mic_suppressed = True


def unsuppress_mic():
    """Re-enable mic input (call after speaker audio finishes)."""
    global _mic_suppressed
    with _suppress_lock:
        _mic_suppressed = False


def _get_porcupine():
    global _porcupine
    if _porcupine is None:
        import pvporcupine
        keyword_paths = None
        keywords = None

        if PORCUPINE_MODEL_PATH and Path(PORCUPINE_MODEL_PATH).exists():
            keyword_paths = [PORCUPINE_MODEL_PATH]
            log.info("Using wake word model: %s", PORCUPINE_MODEL_PATH)
        else:
            keywords = ["hey google"]
            log.warning(
                "No custom wake word model found. Using built-in 'hey google'. "
                "Set PORCUPINE_MODEL_PATH in .env to use a custom wake word."
            )

        _porcupine = pvporcupine.create(
            access_key=PORCUPINE_ACCESS_KEY,
            keyword_paths=keyword_paths,
            keywords=keywords,
            sensitivities=[WAKE_SENSITIVITY],
        )
    return _porcupine


def _get_whisper():
    global _whisper_model
    if _whisper_model is None:
        from faster_whisper import WhisperModel
        log.info("Loading Whisper model '%s' (first load may download ~150MB)...", WHISPER_MODEL)
        _whisper_model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
        log.info("Whisper model loaded")
    return _whisper_model


# --- Sound libraries ---

_chime_sounds: list[Path] = []
_thinking_sounds: list[Path] = []


def _load_chime_sounds():
    global _chime_sounds
    sounds_dir = ASSETS_DIR / "chime_sounds"
    if sounds_dir.exists():
        _chime_sounds = sorted(sounds_dir.glob("*.wav"))
        log.info("Loaded %d chime sounds", len(_chime_sounds))
    if not _chime_sounds:
        fallback = ASSETS_DIR / "chime.wav"
        if fallback.exists():
            _chime_sounds = [fallback]


def _load_thinking_sounds():
    global _thinking_sounds
    sounds_dir = ASSETS_DIR / "thinking_sounds"
    if sounds_dir.exists():
        _thinking_sounds = sorted(sounds_dir.glob("*.wav"))
        log.info("Loaded %d thinking sounds", len(_thinking_sounds))
    if not _thinking_sounds:
        fallback = ASSETS_DIR / "thinking.wav"
        if fallback.exists():
            _thinking_sounds = [fallback]


def play_chime():
    """Play a random chime sound. Suppresses mic while playing."""
    if not _chime_sounds:
        _load_chime_sounds()

    if _chime_sounds:
        sound = random.choice(_chime_sounds)
        try:
            log.debug("Playing chime: %s", sound.name)
            suppress_mic()
            # SND_FILENAME = play from file, blocking (no SND_ASYNC)
            # so we know exactly when it's done
            winsound.PlaySound(str(sound), winsound.SND_FILENAME)
        except Exception as e:
            log.debug("Could not play chime: %s", e)
        finally:
            # Small buffer after playback for speaker echo to die
            time.sleep(0.15)
            unsuppress_mic()
    else:
        suppress_mic()
        winsound.Beep(880, 150)
        time.sleep(0.1)
        unsuppress_mic()


_thinking_thread = None
_thinking_stop = threading.Event()


def play_thinking():
    """Play one random thinking sound, suppressing mic during playback."""
    global _thinking_thread
    stop_thinking()

    if not _thinking_sounds:
        _load_thinking_sounds()
    if not _thinking_sounds:
        return

    _thinking_stop.clear()

    def _play():
        sound = random.choice(_thinking_sounds)
        try:
            log.debug("Playing thinking sound: %s", sound.name)
            suppress_mic()
            winsound.PlaySound(str(sound), winsound.SND_FILENAME)
        except Exception:
            pass
        finally:
            time.sleep(0.15)
            unsuppress_mic()
        # Wait silently until stopped (response arrives)
        _thinking_stop.wait()

    _thinking_thread = threading.Thread(target=_play, daemon=True)
    _thinking_thread.start()


def stop_thinking():
    """Stop the thinking sound."""
    global _thinking_thread
    _thinking_stop.set()
    try:
        winsound.PlaySound(None, winsound.SND_PURGE)
    except Exception:
        pass
    _thinking_thread = None


class AudioPipeline:
    """Manages the mic stream, wake word detection, recording, and transcription."""

    def __init__(self):
        self._running = False
        self._paused = False
        self._wake_callback = None
        self._stream = None
        self._recording = False
        self._recorded_frames: list[np.ndarray] = []
        self._silence_start = 0.0
        self._recording_start = 0.0
        self._got_speech = False

    def start(self, on_wake):
        """Start the audio pipeline. Calls on_wake() when wake word is detected."""
        self._wake_callback = on_wake
        self._running = True
        self._paused = False

        porcupine = _get_porcupine()
        frame_length = porcupine.frame_length

        log.info("Audio pipeline started (frame_length=%d, rate=%d)", frame_length, SAMPLE_RATE)

        self._stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="int16",
            blocksize=frame_length,
            callback=self._audio_callback,
        )
        self._stream.start()

    def stop(self):
        self._running = False
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        global _porcupine
        if _porcupine is not None:
            _porcupine.delete()
            _porcupine = None

    def pause(self):
        self._paused = True

    def resume(self):
        self._paused = False

    def _audio_callback(self, indata, frames, time_info, status):
        """Called by sounddevice for each audio frame."""
        if not self._running or self._paused:
            return

        # Drop frames while speaker is playing to prevent self-hearing
        if _mic_suppressed:
            return

        pcm = indata[:, 0]  # mono int16

        if self._recording:
            self._recorded_frames.append(pcm.copy())

            rms = np.sqrt(np.mean(pcm.astype(np.float32) ** 2))
            elapsed = time.monotonic() - self._recording_start

            # Grace period: ignore silence for the first 2 seconds
            if elapsed < 2.0:
                if rms >= 300:
                    self._got_speech = True
                return

            # After grace period, apply silence detection
            if rms < 300:
                if self._silence_start == 0:
                    self._silence_start = time.monotonic()
                elif time.monotonic() - self._silence_start > SILENCE_TIMEOUT:
                    self._recording = False
                    log.debug("Silence detected, stopping recording (got_speech=%s)", self._got_speech)
            else:
                self._got_speech = True
                self._silence_start = 0
        else:
            # Feed to Porcupine for wake word detection
            try:
                porcupine = _get_porcupine()
                pcm_list = struct.unpack(f"{len(pcm)}h", pcm.tobytes())
                result = porcupine.process(pcm_list)
                if result >= 0:
                    log.info("Wake word detected!")
                    if self._wake_callback:
                        threading.Thread(
                            target=self._wake_callback, daemon=True
                        ).start()
            except Exception as e:
                log.debug("Porcupine error: %s", e)

    def start_recording(self):
        """Begin recording audio (called after wake word or hotkey)."""
        self._recorded_frames = []
        self._silence_start = 0
        self._recording_start = time.monotonic()
        self._got_speech = False
        self._recording = True
        log.debug("Recording started (2s grace period)")

    def stop_recording(self) -> np.ndarray | None:
        self._recording = False
        if not self._recorded_frames:
            return None
        audio = np.concatenate(self._recorded_frames)
        self._recorded_frames = []
        return audio

    def wait_for_silence(self, timeout: float = 15.0) -> bool:
        start = time.monotonic()
        while self._recording and (time.monotonic() - start) < timeout:
            time.sleep(0.1)
        return not self._recording

    @property
    def is_recording(self) -> bool:
        return self._recording


def transcribe(audio: np.ndarray) -> str:
    """Transcribe int16 audio array to text using faster-whisper."""
    model = _get_whisper()
    audio_float = audio.astype(np.float32) / 32768.0
    segments, info = model.transcribe(audio_float, beam_size=1, language="en")
    text = " ".join(seg.text.strip() for seg in segments).strip()
    log.info("Transcribed (%s): %s", f"{info.duration:.1f}s", text)
    return text
