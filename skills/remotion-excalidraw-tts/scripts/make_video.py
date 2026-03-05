#!/usr/bin/env python3

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def run(cmd, cwd=None):
    print(f"+ {' '.join(cmd)}", flush=True)
    subprocess.check_call(cmd, cwd=cwd)


def check_bin(name):
    if shutil.which(name) is None:
        raise SystemExit(f"Missing required binary: {name}")


def ffprobe_duration_seconds(path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        text=True,
    ).strip()
    return float(out)


def patch_root_duration(root_tsx: Path, duration_in_frames: int):
    s = root_tsx.read_text(encoding="utf-8")
    # Replace durationInFrames={...}
    s2, n = re.subn(
        r"durationInFrames=\{[^}]+\}",
        f"durationInFrames={{{duration_in_frames}}}",
        s,
        count=1,
    )
    if n == 0:
        raise SystemExit(f"Could not find durationInFrames in {root_tsx}")
    root_tsx.write_text(s2, encoding="utf-8")


def make_voiceover_mp3_say(voiceover_text: Path, out_mp3: Path, voice: str, rate: int):
    out_aiff = out_mp3.with_suffix(".aiff")
    if out_aiff.exists():
        out_aiff.unlink()
    if out_mp3.exists():
        out_mp3.unlink()

    run(["say", "-v", voice, "-r", str(rate), "-f", str(voiceover_text), "-o", str(out_aiff)])
    run([
        "ffmpeg",
        "-y",
        "-i",
        str(out_aiff),
        "-codec:a",
        "libmp3lame",
        "-b:a",
        "128k",
        str(out_mp3),
    ])


def make_voiceover_mp3_openai(voiceover_text: Path, out_mp3: Path, model: str, voice: str):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY is required for --tts-backend openai")

    # https://platform.openai.com/docs/api-reference/audio/createSpeech
    # We use curl to avoid Python deps.
    text = voiceover_text.read_text(encoding="utf-8")
    if out_mp3.exists():
        out_mp3.unlink()

    cmd = [
        "curl",
        "-sS",
        "-X",
        "POST",
        "https://api.openai.com/v1/audio/speech",
        "-H",
        f"Authorization: Bearer {api_key}",
        "-H",
        "Content-Type: application/json",
        "-d",
        "{}",
        "--output",
        str(out_mp3),
    ]

    payload = {
        "model": model,
        "voice": voice,
        "format": "mp3",
        "input": text,
    }

    import json as _json

    cmd[cmd.index("{}") if "{}" in cmd else -3] = _json.dumps(payload, ensure_ascii=False)
    run(cmd)


def make_voiceover_mp3_elevenlabs(voiceover_text: Path, out_mp3: Path, voice_id: str, model_id: str):
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        raise SystemExit("ELEVENLABS_API_KEY is required for --tts-backend elevenlabs")
    if not voice_id:
        raise SystemExit("--elevenlabs-voice-id is required for --tts-backend elevenlabs")

    text = voiceover_text.read_text(encoding="utf-8")
    if out_mp3.exists():
        out_mp3.unlink()

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    payload = {
        "text": text,
        "model_id": model_id,
        "output_format": "mp3_44100_128",
    }

    import json as _json

    run([
        "curl",
        "-sS",
        "-X",
        "POST",
        url,
        "-H",
        f"xi-api-key: {api_key}",
        "-H",
        "Content-Type: application/json",
        "-H",
        "Accept: audio/mpeg",
        "-d",
        _json.dumps(payload, ensure_ascii=False),
        "--output",
        str(out_mp3),
    ])


def main():
    parser = argparse.ArgumentParser(description="Render Remotion MP4 from Excalidraw + TTS")
    parser.add_argument("--diagram", required=True, help="Path to .excalidraw")
    parser.add_argument("--voiceover-text", required=True, help="Path to voiceover text file")
    parser.add_argument("--out", required=True, help="Output MP4 path")

    parser.add_argument("--voiceover-mp3", default=None, help="Optional existing voiceover mp3 (skip TTS)")

    parser.add_argument(
        "--tts-backend",
        default="say",
        choices=["say", "openai", "elevenlabs"],
        help="TTS backend to generate voiceover.mp3 when --voiceover-mp3 is not provided",
    )

    # say
    parser.add_argument("--voice", default="Tingting", help="macOS say voice")
    parser.add_argument("--rate", type=int, default=220, help="macOS say rate")

    # OpenAI TTS
    parser.add_argument("--openai-model", default="gpt-4o-mini-tts", help="OpenAI TTS model")
    parser.add_argument("--openai-voice", default="alloy", help="OpenAI TTS voice")

    # ElevenLabs TTS
    parser.add_argument("--elevenlabs-voice-id", default=None, help="ElevenLabs voice ID (required for elevenlabs backend)")
    parser.add_argument("--elevenlabs-model", default="eleven_multilingual_v2", help="ElevenLabs model_id")

    # storyboard
    parser.add_argument("--storyboard-json", default=None, help="Optional storyboard.json to drive scenes/camera/focus/subtitles")

    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--workdir", default=None, help="Optional working directory (default: temp)")

    args = parser.parse_args()

    diagram = Path(args.diagram).expanduser().resolve()
    voiceover_text = Path(args.voiceover_text).expanduser().resolve()
    out_mp4 = Path(args.out).expanduser().resolve()

    if not diagram.exists():
        raise SystemExit(f"diagram not found: {diagram}")
    if not voiceover_text.exists():
        raise SystemExit(f"voiceover text not found: {voiceover_text}")

    check_bin("ffmpeg")
    check_bin("ffprobe")
    check_bin("npm")
    check_bin("npx")

    template_dir = Path(__file__).resolve().parents[1] / "assets" / "template" / "remotion-project"
    if not template_dir.exists():
        raise SystemExit(f"template dir not found: {template_dir}")

    if args.voiceover_mp3 is None:
        if args.tts_backend == "say":
            check_bin("say")
        check_bin("curl")

    if args.workdir:
        workdir = Path(args.workdir).expanduser().resolve()
        workdir.mkdir(parents=True, exist_ok=True)
        project_dir = workdir / "remotion-excalidraw-tts"
        if project_dir.exists():
            shutil.rmtree(project_dir)
    else:
        tmp = tempfile.TemporaryDirectory(prefix="remotion-excalidraw-tts-")
        project_dir = Path(tmp.name) / "project"

    shutil.copytree(template_dir, project_dir)

    public_dir = project_dir / "public"
    public_dir.mkdir(exist_ok=True)

    shutil.copy2(diagram, public_dir / "diagram.excalidraw")
    shutil.copy2(voiceover_text, public_dir / "voiceover.txt")

    if args.storyboard_json:
        shutil.copy2(Path(args.storyboard_json).expanduser().resolve(), public_dir / "storyboard.json")

    voiceover_mp3 = public_dir / "voiceover.mp3"
    if args.voiceover_mp3:
        shutil.copy2(Path(args.voiceover_mp3).expanduser().resolve(), voiceover_mp3)
    else:
        if args.tts_backend == "say":
            make_voiceover_mp3_say(public_dir / "voiceover.txt", voiceover_mp3, args.voice, args.rate)
        elif args.tts_backend == "openai":
            make_voiceover_mp3_openai(public_dir / "voiceover.txt", voiceover_mp3, args.openai_model, args.openai_voice)
        elif args.tts_backend == "elevenlabs":
            make_voiceover_mp3_elevenlabs(public_dir / "voiceover.txt", voiceover_mp3, args.elevenlabs_voice_id, args.elevenlabs_model)
        else:
            raise SystemExit(f"Unknown --tts-backend: {args.tts_backend}")

    duration_s = ffprobe_duration_seconds(voiceover_mp3)
    duration_frames = int(duration_s * args.fps + 0.5)

    patch_root_duration(project_dir / "src" / "Root.tsx", duration_frames)

    # install deps
    run(["npm", "i"], cwd=str(project_dir))

    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    render_out = project_dir / "out" / "render.mp4"

    run([
        "npx",
        "remotion",
        "render",
        "OpenClawMemory",
        str(render_out),
        "--log=warn",
    ], cwd=str(project_dir))

    shutil.copy2(render_out, out_mp4)
    print(f"\nOK: {out_mp4}\nDuration: {duration_s:.2f}s ({duration_frames} frames @ {args.fps}fps)")


if __name__ == "__main__":
    main()
