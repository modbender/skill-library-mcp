#!/usr/bin/env python3
"""
Generate natural dual-speaker TTS via Gemini and export MP3.

Input supports:
- Speaker labels (e.g., "Callie: ...", "Nick: ...")
- [F1]/[M2] block format
"""

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from urllib import error, request


def get_api_key() -> str:
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("NANO_BANANA_KEY")
    if not key:
        raise RuntimeError("Set GEMINI_API_KEY (or NANO_BANANA_KEY)")
    return key


def normalize_dialogue(text: str, female_name: str, male_name: str) -> str:
    t = text.strip()

    # [F1] ... [M2] -> Name: ...
    if re.search(r"^\[(F|M)\d+\]", t, re.M):
        pat = re.compile(r"^\[(F|M)\d+\]\n", re.M)
        ms = list(pat.finditer(t))
        lines = []
        for i, m in enumerate(ms):
            start = m.end()
            end = ms[i + 1].start() if i + 1 < len(ms) else len(t)
            content = t[start:end].strip().replace("\n", " ")
            speaker = female_name if m.group(1) == "F" else male_name
            if content:
                lines.append(f"{speaker}: {content}")
        return "\n".join(lines)

    # already labeled
    if re.search(r"^\w[^:]{0,30}:", t, re.M):
        return t

    # fallback single narrator
    return f"{female_name}: {t}"


def call_gemini_tts(
    dialogue_text: str,
    model: str,
    female_name: str,
    female_voice: str,
    male_name: str,
    male_voice: str,
    timeout_seconds: int,
    retries: int,
) -> bytes:
    key = get_api_key()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    prompt = (
        "You are voicing a Korean web drama scene (realistic K-drama style). "
        "Act naturalistic and restrained: no announcer tone, no exaggerated acting, no forced cuteness. "
        "Keep pauses subtle and human. "
        "IMPORTANT: Ignore and DO NOT speak any stage directions in parentheses/brackets (e.g., '(...)', '[...]'). "
        "Speak ONLY the dialogue content after each 'Speaker:' label. "
        "Do not read markdown symbols.\n\n"
        + dialogue_text
    )

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "multiSpeakerVoiceConfig": {
                    "speakerVoiceConfigs": [
                        {
                            "speaker": female_name,
                            "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": female_voice}},
                        },
                        {
                            "speaker": male_name,
                            "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": male_voice}},
                        },
                    ]
                }
            },
        },
    }

    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": key,
        },
    )

    last_err = None
    for attempt in range(1, retries + 1):
        try:
            with request.urlopen(req, timeout=timeout_seconds) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            try:
                b64 = data["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
            except Exception as e:
                raise RuntimeError(f"Unexpected Gemini response: {data}") from e
            # SECURITY NOTE: base64 decode is used ONLY for Gemini API audio response.
            # The API returns PCM audio data as base64-encoded string in JSON.
            # This is a standard practice for binary data in JSON responses.
            return base64.b64decode(b64)

        except error.HTTPError as e:
            last_err = e
            # retry for 429/5xx
            if e.code in (429, 500, 502, 503, 504) and attempt < retries:
                time.sleep(min(8, 1.5 * attempt))
                continue
            raise
        except Exception as e:
            last_err = e
            if attempt < retries:
                time.sleep(min(8, 1.5 * attempt))
                continue
            raise

    raise RuntimeError(f"Gemini TTS failed after retries: {last_err}")


def to_wav_and_mp3(pcm_bytes: bytes, out_prefix: Path):
    pcm = out_prefix.with_suffix(".pcm")
    wav = out_prefix.with_suffix(".wav")
    mp3 = out_prefix.with_suffix(".mp3")

    pcm.write_bytes(pcm_bytes)

    subprocess.run(
        ["ffmpeg", "-y", "-f", "s16le", "-ar", "24000", "-ac", "1", "-i", str(pcm), str(wav)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=600,
    )
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(wav), "-codec:a", "libmp3lame", "-q:a", "4", str(mp3)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=600,
    )
    return pcm, wav, mp3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-file", help="dialogue text file")
    ap.add_argument("--text", help="dialogue text")
    ap.add_argument("--outdir", default=".")
    ap.add_argument("--basename", default="podcast_dualvoice")
    ap.add_argument("--model", default="gemini-2.5-flash-preview-tts")
    ap.add_argument("--female-name", default="Callie")
    # NOTE: voice mapping calibrated from user feedback (2026-02-10)
    # Callie(female) -> Kore, Nick(male) -> Puck
    ap.add_argument("--female-voice", default="Kore")
    ap.add_argument("--male-name", default="Nick")
    ap.add_argument("--male-voice", default="Puck")
    ap.add_argument("--timeout-seconds", type=int, default=120)
    ap.add_argument("--retries", type=int, default=3)
    ap.add_argument("--keep-intermediate", action="store_true")
    args = ap.parse_args()

    if not args.input_file and not args.text:
        print("Provide --input-file or --text", file=sys.stderr)
        sys.exit(1)

    if args.input_file:
        raw = Path(args.input_file).read_text(encoding="utf-8", errors="ignore")
    else:
        raw = args.text

    dialogue = normalize_dialogue(raw, args.female_name, args.male_name)
    pcm_bytes = call_gemini_tts(
        dialogue,
        model=args.model,
        female_name=args.female_name,
        female_voice=args.female_voice,
        male_name=args.male_name,
        male_voice=args.male_voice,
        timeout_seconds=args.timeout_seconds,
        retries=args.retries,
    )

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    out_prefix = outdir / args.basename

    pcm, wav, mp3 = to_wav_and_mp3(pcm_bytes, out_prefix)

    if not args.keep_intermediate:
        pcm.unlink(missing_ok=True)
        wav.unlink(missing_ok=True)

    print(f"MP3={mp3.resolve()}")


if __name__ == "__main__":
    main()
