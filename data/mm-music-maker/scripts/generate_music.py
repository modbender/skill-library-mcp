import argparse
import os
import sys
import requests

from utils_audio import hex_to_bytes, save_bytes, download_url

API_URL = "https://api.minimaxi.com/v1/music_generation"


def build_prompt_from_fields(args):
    fields = []
    def add(label, value):
        if value:
            fields.append(f"{label}: {value}")

    add("Genre", args.genre)
    add("Mood", args.mood)
    add("Tempo", args.tempo or (f"{args.bpm} BPM" if args.bpm else None))
    add("Key", args.key)
    add("Instruments", args.instruments)
    add("Vocals", args.vocals)
    add("Use case", args.use_case)
    add("Structure", args.structure)
    add("Avoid", args.avoid)
    add("References", args.references)

    if not fields:
        return None
    return "\n".join(fields)


def build_payload(args):
    payload = {
        "model": args.model,
        "lyrics": args.lyrics,
    }
    prompt = args.prompt
    if prompt is None:
        prompt = build_prompt_from_fields(args)
    if prompt is not None:
        payload["prompt"] = prompt

    if args.output_format:
        payload["output_format"] = args.output_format

    if args.stream:
        payload["stream"] = True

    audio_setting = {}
    if args.sample_rate:
        audio_setting["sample_rate"] = args.sample_rate
    if args.bitrate:
        audio_setting["bitrate"] = args.bitrate
    if args.format:
        audio_setting["format"] = args.format
    if args.aigc_watermark is not None:
        audio_setting["aigc_watermark"] = args.aigc_watermark

    if audio_setting:
        payload["audio_setting"] = audio_setting

    return payload


def main():
    parser = argparse.ArgumentParser(description="Generate music with MiniMax Music API")
    parser.add_argument("--lyrics", required=True, help="Lyrics text (use \\n for line breaks)")
    parser.add_argument("--prompt", default=None, help="Style/scene prompt (optional for music-2.5)")
    parser.add_argument("--model", default="music-2.5", help="Model name (default: music-2.5)")
    parser.add_argument("--genre", default=None, help="Genre/subgenre (e.g., 1980s synthwave)")
    parser.add_argument("--mood", default=None, help="Mood/emotion (e.g., nostalgic, uplifting)")
    parser.add_argument("--tempo", default=None, help="Tempo description (e.g., upbeat, slow groove)")
    parser.add_argument("--bpm", type=int, default=None, help="Tempo in BPM (e.g., 120)")
    parser.add_argument("--key", default=None, help="Musical key (e.g., A minor)")
    parser.add_argument("--instruments", default=None, help="Key instruments or textures")
    parser.add_argument("--vocals", default=None, help="Vocal style or 'Instrumental only'")
    parser.add_argument("--use-case", dest="use_case", default=None, help="Usage context (e.g., game, ad, meditation)")
    parser.add_argument("--structure", default=None, help="Song structure (e.g., Intro/Verse/Chorus/Bridge)")
    parser.add_argument("--avoid", default=None, help="Negative prompt (e.g., no vocals, avoid reverb)")
    parser.add_argument("--references", default=None, help="Style references (artists/songs)")
    parser.add_argument("--output", required=True, help="Output file path (e.g., ./music.mp3)")
    parser.add_argument("--output-format", choices=["hex", "url"], default="hex", help="Response format")
    parser.add_argument("--stream", action="store_true", help="Enable streaming (hex only)")
    parser.add_argument("--sample-rate", type=int, default=None)
    parser.add_argument("--bitrate", type=int, default=None)
    parser.add_argument("--format", dest="format", default=None, help="Audio format, e.g., mp3")
    parser.add_argument("--aigc-watermark", type=lambda v: v.lower() == "true", default=None)
    parser.add_argument("--download", action="store_true", help="Download if output_format=url")
    args = parser.parse_args()

    api_key = os.getenv("MINIMAX_MUSIC_API_KEY")
    if not api_key:
        print("MINIMAX_MUSIC_API_KEY is not set", file=sys.stderr)
        sys.exit(1)

    if args.stream and args.output_format != "hex":
        print("When --stream is true, output_format must be hex", file=sys.stderr)
        sys.exit(1)

    if args.prompt is None:
        auto_prompt = build_prompt_from_fields(args)
        if auto_prompt:
            print("[info] Built prompt from fields:\n" + auto_prompt)
    payload = build_payload(args)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    resp = requests.post(API_URL, json=payload, headers=headers, timeout=120)
    resp.raise_for_status()
    data = resp.json()

    base_resp = data.get("base_resp", {})
    if base_resp.get("status_code") != 0:
        raise RuntimeError(f"API error: {base_resp}")

    audio_data = data.get("data", {}).get("audio")
    if not audio_data:
        raise RuntimeError("No audio data returned")

    if args.output_format == "hex":
        audio_bytes = hex_to_bytes(audio_data)
        saved = save_bytes(audio_bytes, args.output)
        print(saved)
        return

    # output_format == url
    if args.download:
        saved = download_url(audio_data, args.output)
        print(saved)
    else:
        # print URL for manual download
        print(audio_data)


if __name__ == "__main__":
    main()
