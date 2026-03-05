#!/usr/bin/env python3
"""MiniMax Speech 2.8 HTTP helpers for TTS and voice catalog lookups."""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests


def fail(message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)


def ensure_api_key() -> str:
    api_key = os.getenv("MINIMAX_API_KEY")
    if not api_key:
        fail("Please set MINIMAX_API_KEY with your MiniMax API key before running this script.")
    return api_key


def decode_audio(audio_payload: str, output_format: str) -> bytes:
    if output_format == "hex":
        return bytes.fromhex(audio_payload)
    if output_format == "base64":
        return base64.b64decode(audio_payload)
    if output_format == "url":
        resp = requests.get(audio_payload, timeout=60)
        resp.raise_for_status()
        return resp.content
    fail(f"Unsupported output format: {output_format}")


def build_voice_setting(args: argparse.Namespace) -> Dict[str, Any]:
    voice_setting: Dict[str, Any] = {}
    if args.voice_id:
        voice_setting["voice_id"] = args.voice_id
    if args.speed is not None:
        voice_setting["speed"] = args.speed
    if args.vol is not None:
        voice_setting["vol"] = args.vol
    if args.pitch is not None:
        voice_setting["pitch"] = args.pitch
    return voice_setting


def build_audio_setting(args: argparse.Namespace) -> Dict[str, Any]:
    return {
        "sample_rate": args.sample_rate,
        "bitrate": args.bitrate,
        "format": args.audio_format,
        "channel": args.channel,
    }


def build_voice_modify(args: argparse.Namespace) -> Dict[str, Any]:
    voice_modify: Dict[str, Any] = {}
    if args.voice_modify_pitch is not None:
        voice_modify["pitch"] = args.voice_modify_pitch
    if args.voice_modify_intensity is not None:
        voice_modify["intensity"] = args.voice_modify_intensity
    if args.voice_modify_timbre is not None:
        voice_modify["timbre"] = args.voice_modify_timbre
    if args.voice_modify_effects:
        voice_modify["sound_effects"] = args.voice_modify_effects
    return voice_modify


def parse_key_value_list(entries: Optional[List[str]]) -> Dict[str, List[str]]:
    parsed: Dict[str, List[str]] = {}
    if not entries:
        return parsed
    for entry in entries:
        if "=" not in entry:
            fail(f"Pronunciation entries and timbre weights must use KEY=VALUE syntax: {entry}")
        key, value = entry.split("=", 1)
        parsed.setdefault(key.strip(), []).append(value.strip())
    return parsed


def parse_timbre_weights(entries: Optional[List[str]]) -> List[Dict[str, Any]]:
    weights: List[Dict[str, Any]] = []
    if not entries:
        return weights
    for entry in entries:
        if "=" not in entry:
            fail(f"Each timbre weight must be in voice_id=weight format: {entry}")
        voice_id, weight = entry.split("=", 1)
        try:
            numeric_weight = float(weight)
        except ValueError as exc:
            fail(f"Weight must be a number: {entry} ({exc})")
        weights.append({"voice_id": voice_id.strip(), "weight": numeric_weight})
    return weights


def run_tts(args: argparse.Namespace) -> None:
    api_key = ensure_api_key()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload: Dict[str, Any] = {
        "model": args.model,
        "text": args.text,
        "stream": args.stream,
        "output_format": args.output_format,
    }
    if args.language_boost:
        payload["language_boost"] = args.language_boost
    voice_setting = build_voice_setting(args)
    if voice_setting:
        payload["voice_setting"] = voice_setting
    audio_setting = build_audio_setting(args)
    payload["audio_setting"] = audio_setting
    voice_modify = build_voice_modify(args)
    if voice_modify:
        payload["voice_modify"] = voice_modify
    if args.pronunciation:
        payload["pronunciation_dict"] = parse_key_value_list(args.pronunciation)
    timbre_weights = parse_timbre_weights(args.timbre_weight)
    if timbre_weights:
        payload["timbre_weights"] = timbre_weights
    try:
        response = requests.post(args.endpoint, headers=headers, json=payload, timeout=args.timeout)
        response.raise_for_status()
    except requests.RequestException as exc:
        fail(f"TTS request failed: {exc}")
    data = response.json()
    audio_payload = data.get("data", {}).get("audio")
    if not audio_payload:
        fail(f"No audio payload returned: {json.dumps(data)}")
    audio_bytes = decode_audio(audio_payload, args.output_format)
    out_file = Path(args.output or f"minimax_tts_output.{args.audio_format}")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_bytes(audio_bytes)
    print(f"Saved TTS audio to {out_file} (format: {args.audio_format})")
    if args.print_response:
        print("Response metadata:")
        print(json.dumps(data.get("extra_info", {}), indent=2))


def run_voices(args: argparse.Namespace) -> None:
    api_key = ensure_api_key()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {"voice_type": args.voice_type}
    try:
        response = requests.post(args.endpoint, headers=headers, json=payload, timeout=args.timeout)
        response.raise_for_status()
    except requests.RequestException as exc:
        fail(f"Voice catalog request failed: {exc}")
    if args.output:
        Path(args.output).write_text(json.dumps(response.json(), indent=2))
        print(f"Saved voice catalog to {args.output}")
        return
    if args.print_response:
        print(json.dumps(response.json(), indent=2))
    else:
        print(json.dumps(response.json(), indent=2))


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="MiniMax Speech 2.8 CLI helpers")
    subparsers = parser.add_subparsers(dest="command", required=True)

    tts_parser = subparsers.add_parser("tts", help="Synthesize speech via MiniMax Speech 2.8 HTTP API")
    tts_parser.add_argument("--text", required=True, help="Text to convert to speech (max 10k chars)")
    tts_parser.add_argument("--model", default="speech-2.8-hd", choices=[
        "speech-2.8-hd",
        "speech-2.8-turbo",
        "speech-2.6-hd",
        "speech-2.6-turbo",
        "speech-02-hd",
        "speech-02-turbo",
        "speech-01-hd",
        "speech-01-turbo",
    ])
    tts_parser.add_argument("--voice-id", help="MiniMax voice_id (system voice or cloned voice)")
    tts_parser.add_argument("--speed", type=float, help="Speech rate (default: 1.0)")
    tts_parser.add_argument("--vol", type=float, help="Volume level (default: 1.0)")
    tts_parser.add_argument("--pitch", type=float, help="Pitch modifier (0 is neutral)")
    tts_parser.add_argument("--language-boost", help="Language boost, e.g. English, Chinese, auto")
    tts_parser.add_argument("--sample-rate", type=int, default=32000, help="Audio sample rate (Hz)")
    tts_parser.add_argument("--bitrate", type=int, default=128000, help="Audio bitrate (bps)")
    tts_parser.add_argument("--audio-format", dest="audio_format", default="mp3",
                             choices=["mp3", "wav", "flac"], help="Output format")
    tts_parser.add_argument("--channel", type=int, default=1, choices=[1, 2], help="Audio channels")
    tts_parser.add_argument("--voice-modify-pitch", type=float, help="Voice modify pitch offset")
    tts_parser.add_argument("--voice-modify-intensity", type=float, help="Voice modify intensity")
    tts_parser.add_argument("--voice-modify-timbre", type=float, help="Voice modify timbre")
    tts_parser.add_argument("--voice-modify-effects", help="Space-separated sound effects to apply")
    tts_parser.add_argument("--pronunciation", action="append",
                             help="Add pronunciation override in KEY=VALUE form (can repeat)")
    tts_parser.add_argument("--timbre-weight", action="append",
                             help="Mix voices via voice_id=weight (repeat up to 4 times)")
    tts_parser.add_argument("--stream", action="store_true", help="Enable streaming response")
    tts_parser.add_argument("--output-format", dest="output_format", default="hex",
                             choices=["hex", "url", "base64"],
                             help="How the API returns audio data")
    tts_parser.add_argument("--output", help="Override output file path")
    tts_parser.add_argument("--endpoint", default="https://api.minimax.io/v1/t2a_v2",
                             help="Override MiniMax T2A endpoint")
    tts_parser.add_argument("--timeout", type=int, default=120,
                             help="HTTP timeout in seconds")
    tts_parser.add_argument("--print-response", action="store_true",
                             help="Print the full API response metadata")
    tts_parser.set_defaults(func=run_tts)

    voices_parser = subparsers.add_parser("voices", help="List voices through MiniMax catalog")
    voices_parser.add_argument("--voice-type", default="all", choices=["system", "voice_cloning", "voice_generation", "all"],
                               help="Voice category")
    voices_parser.add_argument("--endpoint", default="https://api.minimax.io/v1/get_voice",
                               help="Override the catalog endpoint")
    voices_parser.add_argument("--output", help="Save JSON catalog to a file")
    voices_parser.add_argument("--timeout", type=int, default=30,
                               help="HTTP timeout in seconds")
    voices_parser.add_argument("--print-response", action="store_true",
                               help="Pretty print the catalog response on stdout")
    voices_parser.set_defaults(func=run_voices)

    return parser


def main() -> None:
    parser = get_parser()
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()
