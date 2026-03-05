"""ElevenLabs text-to-speech playback."""

import io
import logging
import os
import tempfile
import wave
import winsound

import numpy as np

from config import ELEVENLABS_API_KEY, ELEVENLABS_MODEL_ID, ELEVENLABS_VOICE_ID

log = logging.getLogger(__name__)

_client = None
_interrupted = False


def _get_client():
    global _client
    if _client is None:
        from elevenlabs.client import ElevenLabs
        _client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    return _client


def _decode_mp3_to_wav(mp3_bytes: bytes) -> str | None:
    """Decode MP3 bytes to a temporary WAV file using av (PyAV). Returns path."""
    try:
        import av

        container = av.open(io.BytesIO(mp3_bytes), format="mp3")
        audio_stream = container.streams.audio[0]

        samples = []
        sample_rate = None

        for frame in container.decode(audio_stream):
            if sample_rate is None:
                sample_rate = frame.sample_rate
            arr = frame.to_ndarray()
            if arr.ndim > 1:
                arr = arr.mean(axis=0)
            samples.append(arr.flatten())

        container.close()

        if not samples or sample_rate is None:
            return None

        audio = np.concatenate(samples)

        if audio.dtype in (np.float32, np.float64):
            audio = np.clip(audio, -1.0, 1.0)
            audio_int16 = (audio * 32767).astype(np.int16)
        else:
            audio_int16 = audio.astype(np.int16)

        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp_path = tmp.name
        tmp.close()

        with wave.open(tmp_path, "w") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_int16.tobytes())

        return tmp_path

    except Exception as e:
        log.error("MP3 decode error: %s", e)
        return None


def speak(text: str):
    """Convert text to speech and play it. Blocks until done or interrupted."""
    global _interrupted
    _interrupted = False

    if not ELEVENLABS_API_KEY:
        log.warning("No ElevenLabs API key configured. Skipping TTS.")
        return

    if not text.strip():
        return

    try:
        client = _get_client()
        log.debug("Generating speech for: %s", text[:80])

        audio_stream = client.text_to_speech.convert(
            text=text,
            voice_id=ELEVENLABS_VOICE_ID,
            model_id=ELEVENLABS_MODEL_ID,
            output_format="mp3_44100_128",
        )

        mp3_bytes = b"".join(audio_stream)

        if _interrupted:
            log.debug("TTS interrupted before playback")
            return

        wav_path = _decode_mp3_to_wav(mp3_bytes)
        if not wav_path:
            log.error("Failed to decode TTS audio")
            return

        if _interrupted:
            os.unlink(wav_path)
            return

        try:
            log.info("Speaking response...")
            winsound.PlaySound(wav_path, winsound.SND_FILENAME)
            log.debug("Playback finished")
        finally:
            try:
                os.unlink(wav_path)
            except OSError:
                pass

    except Exception as e:
        log.error("TTS error: %s", e)


def interrupt():
    """Stop current TTS playback."""
    global _interrupted
    _interrupted = True
    try:
        winsound.PlaySound(None, winsound.SND_PURGE)
    except Exception:
        pass
    log.debug("TTS playback interrupted")
