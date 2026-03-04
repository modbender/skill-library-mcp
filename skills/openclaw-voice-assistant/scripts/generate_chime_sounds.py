"""Generate natural wake word response sounds using ElevenLabs TTS.

Creates short audio clips (yep!, yes?, hi!, etc.) in the configured voice
and saves them as WAV files in assets/chime_sounds/.
Run this after changing ELEVENLABS_VOICE_ID in .env.
"""

import io
import os
import sys
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

PHRASES = [
    "Yep!",
    "Yes?",
    "Hi!",
    "Hm?",
    "Yeah?",
    "Mhm?",
    "Hey!",
    "What's up?",
]


def _mp3_to_wav(mp3_bytes: bytes, out_path: Path) -> Path | None:
    import av
    container = av.open(io.BytesIO(mp3_bytes), format="mp3")
    stream = container.streams.audio[0]
    samples, sr = [], None
    for frame in container.decode(stream):
        if sr is None:
            sr = frame.sample_rate
        arr = frame.to_ndarray()
        if arr.ndim > 1:
            arr = arr.mean(axis=0)
        samples.append(arr.flatten())
    container.close()
    if not samples or sr is None:
        return None
    audio = np.concatenate(samples)
    if audio.dtype in (np.float32, np.float64):
        audio = (np.clip(audio, -1.0, 1.0) * 32767).astype(np.int16)
    with wave.open(str(out_path), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(audio.tobytes())
    return out_path


def generate():
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent / ".env")

    api_key = os.getenv("ELEVENLABS_API_KEY")
    voice_id = os.getenv("ELEVENLABS_VOICE_ID")
    model_id = os.getenv("ELEVENLABS_MODEL_ID", "eleven_v3")

    from elevenlabs.client import ElevenLabs
    client = ElevenLabs(api_key=api_key)

    out_dir = Path(__file__).resolve().parent / "assets" / "chime_sounds"
    out_dir.mkdir(parents=True, exist_ok=True)

    for i, phrase in enumerate(PHRASES):
        print(f"  [{i+1}/{len(PHRASES)}] {phrase!r}")
        try:
            stream = client.text_to_speech.convert(
                text=phrase, voice_id=voice_id, model_id=model_id,
                output_format="mp3_44100_128",
            )
            path = _mp3_to_wav(b"".join(stream), out_dir / f"chime_{i:02d}.wav")
            print(f"    -> {path or 'FAILED'}")
        except Exception as e:
            print(f"    -> ERROR: {e}")

    print(f"\nDone! {len(list(out_dir.glob('*.wav')))} chime sounds")


if __name__ == "__main__":
    generate()
