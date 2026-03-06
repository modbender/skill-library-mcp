#!/usr/bin/env python3
"""
voice_bridge.py — Voice-first interaction via Whisper skill integration.

Transcribes audio input and routes commands to the appropriate proactive-claw
action. Works standalone or as a bridge called by the whisper skill.

Usage:
  python3 voice_bridge.py --transcribe /path/to/audio.wav
  python3 voice_bridge.py --route "move my sprint review to next Monday"
  python3 voice_bridge.py --record --seconds 10           # record + transcribe
  python3 voice_bridge.py --check-whisper                 # check if whisper skill available

Whisper skill integration:
  If the 'whisper' skill is installed at ~/.openclaw/workspace/skills/whisper/,
  this bridge calls it for transcription. Otherwise falls back to the
  openai-whisper Python package if installed, then to os speech recognition.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

if sys.version_info < (3, 8):
    print(json.dumps({"error": "python_version_too_old", "detail": "Python 3.8+ required."}))
    sys.exit(1)

SKILL_DIR = Path.home() / ".openclaw/workspace/skills/proactive-claw"
WHISPER_SKILL_DIR = Path.home() / ".openclaw/workspace/skills/whisper"
CONFIG_FILE = SKILL_DIR / "config.json"
sys.path.insert(0, str(SKILL_DIR / "scripts"))

# ── Intent routing table ──────────────────────────────────────────────────────
# Maps regex patterns to (script, flag_template) pairs.
# {1}, {2} etc. are replaced with captured groups.

# ── Intent routing table ──────────────────────────────────────────────────────
# Maps regex patterns to (script, args_template) pairs.
# args_template is a list of arguments. Placeholders {1}, {2} refer to regex
# capture groups. {0} refers to the full (cleaned) command text.
#
# IMPORTANT: We never build a shell string. Untrusted text is passed as a single
# argument where needed, and we reject suspicious metacharacters to reduce risk
# of command/flag injection into downstream scripts.

INTENTS = [
    # Calendar moves
    (r"move (.+?) to (.+)", "cal_editor.py", ["--move", "{1}", "{2}"]),
    (r"reschedule (.+?) (?:to|for) (.+)", "cal_editor.py", ["--move", "{1}", "{2}"]),

    # Find free time
    (r"(?:find|show|when(?:'s| is)) (?:free|available)(?: time)?(?: (?:on|this|next) (.+))?",
     "cal_editor.py", ["--find-free", "{1}"]),
    (r"(?:any )?free time (?:on |this |next )?(.+)", "cal_editor.py", ["--find-free", "{1}"]),

    # Read calendar
    (r"(?:what(?:'s| is) on|read|show) (?:my )?(?:calendar )?(?:for )?(.+)",
     "cal_editor.py", ["--read", "{1}"]),
    (r"(?:what(?:'s| is) happening|any events?) (.+)", "cal_editor.py", ["--read", "{1}"]),

    # Energy / focus
    (r"(?:when(?:'s| is| are) (?:my )?best (?:time|energy|focus)|suggest focus)",
     "energy_predictor.py", ["--suggest-focus-time"]),
    (r"(?:schedule|create|add|block) focus (?:blocks?|time)",
     "energy_predictor.py", ["--block-focus-week"]),
    (r"check (?:my )?energy (?:for )?(.+)", "energy_predictor.py", ["--analyse"]),

    # Conflicts
    (r"(?:any )?conflicts?(?:.+)?", "conflict_detector.py", []),
    (r"fix (?:my )?(?:schedule|conflicts?)", "cal_editor.py", ["--reschedule-conflict"]),

    # Action items
    (r"(?:open|show|list) action items?", "memory.py", ["--open-actions"]),
    (r"(?:open|stale) actions?", "memory.py", ["--open-actions"]),

    # Weekly digest
    (r"(?:weekly )?digest|weekly summary|recap", "intelligence_loop.py", ["--weekly-digest"]),

    # Contacts
    (r"(?:tell me about|who is|look up|lookup) (.+)", "relationship_memory.py", ["--lookup", "{1}"]),
    (r"(?:attendee brief|who(?:'s| is) (?:in|at|coming to)) (.+)",
     "relationship_memory.py", ["--brief", "{1}"]),
    (r"stale contacts?", "relationship_memory.py", ["--stale"]),

    # Policy (pass whole command as ONE argument)
    (r"(?:always|never|suppress|boost|block|add buffer) .+",
     "policy_engine.py", ["--parse", "{0}"]),
]


def load_config() -> dict:
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def check_whisper_skill() -> dict:
    """Check which transcription backend is available."""
    backends = []

    # 1. OpenClaw whisper skill
    whisper_main = WHISPER_SKILL_DIR / "scripts" / "transcribe.py"
    if whisper_main.exists():
        backends.append({"name": "whisper_skill", "path": str(whisper_main), "available": True})

    # 2. openai-whisper Python package
    try:
        import importlib.util
        spec = importlib.util.find_spec("whisper")
        if spec:
            backends.append({"name": "openai_whisper", "path": spec.origin, "available": True})
    except Exception:
        pass

    # 3. whisper CLI
    whisper_cli = shutil.which("whisper")
    if whisper_cli:
        backends.append({"name": "whisper_cli", "path": whisper_cli, "available": True})

    # 4. ffmpeg (required for any audio processing)
    ffmpeg = shutil.which("ffmpeg")

    return {
        "status": "ok",
        "backends": backends,
        "preferred": backends[0]["name"] if backends else None,
        "ffmpeg_available": bool(ffmpeg),
        "can_transcribe": bool(backends),
        "recommendation": (
            "Install openai-whisper: pip install openai-whisper"
            if not backends else f"Using: {backends[0]['name']}"
        ),
    }


def transcribe_audio(audio_path: str) -> dict:
    """Transcribe an audio file using the best available backend."""
    path = Path(audio_path)
    if not path.exists():
        return {"status": "error", "message": f"File not found: {audio_path}"}

    whisper_info = check_whisper_skill()
    if not whisper_info["can_transcribe"]:
        return {
            "status": "no_backend",
            "message": "No transcription backend available. " + whisper_info["recommendation"],
        }

    preferred = whisper_info["preferred"]

    # Try OpenClaw whisper skill first
    if preferred == "whisper_skill":
        try:
            result = subprocess.run(
                [sys.executable, str(WHISPER_SKILL_DIR / "scripts/transcribe.py"),
                 "--file", str(path)],
                capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return {"status": "ok", "text": data.get("text", ""), "backend": "whisper_skill"}
        except Exception as e:
            pass  # fall through to next backend

    # Try openai-whisper Python package
    if any(b["name"] == "openai_whisper" for b in whisper_info["backends"]):
        try:
            import whisper as _whisper  # type: ignore
            model = _whisper.load_model("base")
            result_data = model.transcribe(str(path))
            return {
                "status": "ok",
                "text": result_data.get("text", "").strip(),
                "backend": "openai_whisper",
                "language": result_data.get("language", ""),
            }
        except Exception as e:
            pass  # fall through

    # Try whisper CLI
    if any(b["name"] == "whisper_cli" for b in whisper_info["backends"]):
        try:
            result = subprocess.run(
                ["whisper", str(path), "--output_format", "json", "--output_dir", "/tmp"],
                capture_output=True, text=True, timeout=180)
            json_out = Path("/tmp") / (path.stem + ".json")
            if json_out.exists():
                data = json.loads(json_out.read_text())
                text = " ".join(s.get("text", "") for s in data.get("segments", []))
                return {"status": "ok", "text": text.strip(), "backend": "whisper_cli"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    return {"status": "error", "message": "All transcription backends failed."}


def record_audio(seconds: int = 10) -> dict:
    """Record audio from the default microphone. Returns path to recorded file."""
    output_path = SKILL_DIR / "tmp_recording.wav"

    # Try sox (rec command)
    if shutil.which("rec"):
        try:
            subprocess.run(
                ["rec", "-r", "16000", "-c", "1", "-b", "16", str(output_path),
                 "trim", "0", str(seconds)],
                check=True, timeout=seconds + 5)
            return {"status": "ok", "path": str(output_path)}
        except Exception as e:
            pass

    # Try ffmpeg with default input
    if shutil.which("ffmpeg"):
        try:
            # macOS: avfoundation input; Linux: pulse/alsa
            if sys.platform == "darwin":
                input_device = "avfoundation"
                input_arg = ":0"  # default mic
            else:
                input_device = "pulse"
                input_arg = "default"
            subprocess.run(
                ["ffmpeg", "-y", "-f", input_device, "-i", input_arg,
                 "-t", str(seconds), "-ar", "16000", "-ac", "1", str(output_path)],
                check=True, timeout=seconds + 10, capture_output=True)
            return {"status": "ok", "path": str(output_path)}
        except Exception as e:
            return {"status": "error", "message": f"ffmpeg recording failed: {e}"}

    # Try Python sounddevice
    try:
        import sounddevice as sd  # type: ignore
        import scipy.io.wavfile as wav  # type: ignore
        import numpy as np  # type: ignore
        sample_rate = 16000
        recording = sd.rec(int(seconds * sample_rate), samplerate=sample_rate,
                           channels=1, dtype=np.int16)
        sd.wait()
        wav.write(str(output_path), sample_rate, recording)
        return {"status": "ok", "path": str(output_path)}
    except ImportError:
        pass
    except Exception as e:
        return {"status": "error", "message": str(e)}

    return {
        "status": "error",
        "message": "No recording backend available. Install sox (brew install sox) or ffmpeg.",
    }


def _looks_suspicious(text: str) -> bool:
    """
    Conservative check to reduce risk of command/flag injection into downstream scripts.
    We do NOT execute a shell, but we still reject common metacharacters that could
    alter meaning if a downstream component ever mishandles arguments.
    """
    if not text:
        return True
    # reject control chars / newlines
    if any(ord(c) < 32 for c in text):
        return True
    # reject obvious shell metacharacters
    if re.search(r"[;&|`$<>\\]", text):
        return True
    return False


def _fill_arg(template: str, groups: dict) -> str:
    # Fill placeholders like "{1}", "{2}", "{0}".
    out = template
    for k, v in groups.items():
        out = out.replace(f"{{{k}}}", v)
    return out


def route_command(text: str) -> dict:
    """
    Match a transcribed command to a proactive-claw script and run it safely.

    Security notes:
    - We never invoke a shell (shell=False).
    - We never split untrusted text into flags.
    - Captured text is passed as a single argument where applicable.
    - We reject suspicious metacharacters to reduce risk of injection into downstream code.
    """
    text_clean = text.strip()
    if _looks_suspicious(text_clean):
        return {
            "status": "rejected",
            "reason": "suspicious_input",
            "message": "Command contained suspicious characters. Please rephrase without special symbols.",
            "text": text,
        }

    text_clean = text_clean.lower()
    text_clean = re.sub(r"[.,!?;]$", "", text_clean).strip()

    for pattern, script_name, args_template in INTENTS:
        m = re.search(pattern, text_clean, re.IGNORECASE)
        if not m:
            continue

        # Build placeholder map: {0} full text, {1..N} groups
        groups = {"0": text_clean}
        for i, g in enumerate(m.groups(), start=1):
            val = (g or "").strip()
            if not val:
                val = "this week"
            # Reject suspicious content in captured groups too
            if _looks_suspicious(val):
                return {
                    "status": "rejected",
                    "reason": "suspicious_capture",
                    "message": "Captured phrase contained suspicious characters. Please rephrase.",
                    "text": text,
                }
            groups[str(i)] = val

        script_path = str(SKILL_DIR / "scripts" / script_name)

        # Fill args template WITHOUT ever splitting user text
        filled_args = [_fill_arg(a, groups) for a in args_template]
        cmd = [sys.executable, script_path] + filled_args

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                try:
                    data = json.loads(result.stdout)
                except Exception:
                    data = {"raw_output": result.stdout.strip()}
                return {
                    "status": "ok",
                    "intent_matched": pattern,
                    "script": script_name,
                    "command": " ".join(filled_args),
                    "result": data,
                }
            return {
                "status": "script_error",
                "intent_matched": pattern,
                "script": script_name,
                "stderr": result.stderr.strip()[:500],
            }
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "script": script_name}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    return {
        "status": "no_match",
        "message": f"Couldn't route: '{text}'. Try: 'move X to Y', 'show free time tomorrow', 'read calendar this week'.",
        "text": text,
    }
def transcribe_and_route(audio_path: str) -> dict:
    """Full pipeline: transcribe audio then route command."""
    transcription = transcribe_audio(audio_path)
    if transcription.get("status") != "ok":
        return transcription
    text = transcription.get("text", "")
    if not text:
        return {"status": "empty", "message": "Transcription returned empty text."}
    routing = route_command(text)
    routing["transcription"] = text
    return routing


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--transcribe", metavar="AUDIO_FILE",
                        help="Transcribe an audio file")
    parser.add_argument("--route", metavar="TEXT",
                        help="Route a text command to the appropriate script")
    parser.add_argument("--record", action="store_true",
                        help="Record from microphone then transcribe and route")
    parser.add_argument("--seconds", type=int, default=10,
                        help="Recording length for --record (default 10)")
    parser.add_argument("--check-whisper", action="store_true",
                        help="Check available transcription backends")
    args = parser.parse_args()

    if args.check_whisper:
        print(json.dumps(check_whisper_skill(), indent=2))
    elif args.transcribe:
        print(json.dumps(transcribe_audio(args.transcribe), indent=2))
    elif args.route:
        print(json.dumps(route_command(args.route), indent=2))
    elif args.record:
        rec = record_audio(args.seconds)
        if rec.get("status") != "ok":
            print(json.dumps(rec, indent=2))
        else:
            print(json.dumps(transcribe_and_route(rec["path"]), indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()