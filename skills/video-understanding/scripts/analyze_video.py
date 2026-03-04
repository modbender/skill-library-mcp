# /// script
# requires-python = ">=3.10"
# dependencies = ["google-genai>=1.0.0"]
# ///
"""Download a video and analyze it with Google Gemini."""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time

from google import genai
from google.genai import types

YOUTUBE_PATTERNS = [
    r"(?:https?://)?(?:www\.)?youtube\.com/watch\?v=",
    r"(?:https?://)?youtu\.be/",
    r"(?:https?://)?(?:www\.)?youtube\.com/shorts/",
]

DEFAULT_PROMPT = """Analyze this video and return a JSON object with the following fields:

1. "transcript": Full verbatim transcript of all spoken words, with timestamps in [MM:SS] format at natural paragraph breaks.
2. "description": Detailed description of the video including: what is shown visually, who appears on screen (describe them if unnamed), the setting/environment, any text/UI/graphics shown on screen, and the overall flow from start to finish.
3. "summary": A concise 2-3 sentence summary of what the video is about.
4. "duration_seconds": Estimated duration in seconds.
5. "speakers": List of speakers identified (by name if mentioned, otherwise descriptive labels like "male presenter").

Return ONLY valid JSON, no markdown fences."""

QUESTION_ADDENDUM = """

Additionally, answer the following question about the video:

6. "answer": {question}

Return ONLY valid JSON, no markdown fences."""


def is_youtube_url(url: str) -> bool:
    return any(re.search(p, url) for p in YOUTUBE_PATTERNS)


def download_video(url: str, output_path: str, max_size_mb: int = 500) -> str:
    """Download video using yt-dlp. Returns the actual output file path."""
    cmd = [
        "yt-dlp",
        "-f", "bestvideo+bestaudio/best",
        "--merge-output-format", "mp4",
        "--remux-video", "mp4",
        "--no-playlist",
        "--max-filesize", f"{max_size_mb}M",
        "-o", output_path,
        url,
    ]
    print(f"Downloading: {url}", file=sys.stderr)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"yt-dlp stderr: {result.stderr}", file=sys.stderr)
        raise RuntimeError(f"yt-dlp failed (exit {result.returncode}): {result.stderr[:500]}")

    if not os.path.exists(output_path):
        base_dir = os.path.dirname(output_path)
        base_name = os.path.basename(output_path).replace(".%(ext)s", "")
        for f in os.listdir(base_dir):
            if f.startswith(base_name) and f.endswith(".mp4"):
                return os.path.join(base_dir, f)
        for f in os.listdir(base_dir):
            if f.endswith(".mp4"):
                return os.path.join(base_dir, f)
        raise RuntimeError(f"Downloaded file not found in {base_dir}")

    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"Downloaded: {size_mb:.1f} MB", file=sys.stderr)
    return output_path


def upload_to_gemini(client: genai.Client, file_path: str) -> types.File:
    """Upload file to Gemini and wait for processing."""
    print("Uploading to Gemini...", file=sys.stderr)
    uploaded = client.files.upload(file=file_path)
    print(f"Uploaded: {uploaded.name} (state: {uploaded.state})", file=sys.stderr)

    while uploaded.state == "PROCESSING":
        time.sleep(3)
        uploaded = client.files.get(name=uploaded.name)
        print(f"  Processing... (state: {uploaded.state})", file=sys.stderr)

    if uploaded.state == "FAILED":
        raise RuntimeError(f"Gemini processing failed for {uploaded.name}")

    print(f"Ready: {uploaded.name}", file=sys.stderr)
    return uploaded


def build_prompt(question: str | None = None) -> str:
    """Build the analysis prompt, optionally with a custom question."""
    prompt = DEFAULT_PROMPT
    if question:
        prompt += QUESTION_ADDENDUM.format(question=question)
    return prompt


def analyze_with_file(
    client: genai.Client,
    gemini_file: types.File,
    prompt: str,
    model: str,
) -> str:
    """Analyze using an uploaded Gemini file."""
    print(f"Analyzing with {model}...", file=sys.stderr)
    response = client.models.generate_content(
        model=model,
        contents=[
            types.Content(
                parts=[
                    types.Part.from_uri(
                        file_uri=gemini_file.uri,
                        mime_type=gemini_file.mime_type,
                    ),
                    types.Part.from_text(text=prompt),
                ]
            )
        ],
    )
    return response.text


def analyze_youtube(
    client: genai.Client,
    url: str,
    prompt: str,
    model: str,
) -> str:
    """Analyze a YouTube video directly by URL (no download needed)."""
    print(f"Analyzing YouTube URL directly with {model}...", file=sys.stderr)
    response = client.models.generate_content(
        model=model,
        contents=[
            types.Content(
                parts=[
                    types.Part.from_uri(file_uri=url, mime_type="video/mp4"),
                    types.Part.from_text(text=prompt),
                ]
            )
        ],
    )
    return response.text


def format_output(raw_text: str) -> str:
    """Try to parse as JSON and pretty-print; fall back to raw text."""
    # Strip markdown fences if present
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*\n?", "", cleaned)
        cleaned = re.sub(r"\n?```\s*$", "", cleaned)

    try:
        data = json.loads(cleaned)
        return json.dumps(data, indent=2, ensure_ascii=False)
    except json.JSONDecodeError:
        return raw_text


def main():
    parser = argparse.ArgumentParser(description="Download and analyze video with Gemini")
    parser.add_argument("url", help="Video URL (Loom, YouTube, etc.)")
    parser.add_argument("--question", "-q", help="Additional question to answer about the video")
    parser.add_argument("--prompt", "-p", help="Override the entire prompt (ignores --question)")
    parser.add_argument("--model", "-m", default="gemini-2.5-flash")
    parser.add_argument("--output", "-o", help="Save analysis to file (or mp4 with --download-only)")
    parser.add_argument("--keep", action="store_true", help="Keep downloaded video file")
    parser.add_argument("--download-only", action="store_true", help="Only download, skip analysis")
    parser.add_argument("--max-size", type=int, default=500, help="Max video size in MB")
    parser.add_argument("--raw", action="store_true", help="Output raw text instead of JSON")
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key and not args.download_only:
        print("Error: GEMINI_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    # Build prompt
    if args.prompt:
        prompt = args.prompt
    else:
        prompt = build_prompt(args.question)

    client = genai.Client(api_key=api_key) if api_key else None

    # YouTube shortcut: pass URL directly to Gemini
    if is_youtube_url(args.url) and not args.download_only:
        print("Detected YouTube URL — passing directly to Gemini (no download)", file=sys.stderr)
        result = analyze_youtube(client, args.url, prompt, args.model)
        output = result if args.raw else format_output(result)
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"Analysis saved to: {args.output}", file=sys.stderr)
        else:
            print(output)
        return

    # Download for non-YouTube
    if args.download_only and args.output:
        video_path = args.output
    else:
        tmp_dir = tempfile.mkdtemp()
        video_path = os.path.join(tmp_dir, "video.%(ext)s")

    try:
        video_path = download_video(args.url, video_path, args.max_size)

        if args.download_only:
            print(f"Video saved to: {video_path}")
            return

        gemini_file = upload_to_gemini(client, video_path)

        try:
            result = analyze_with_file(client, gemini_file, prompt, args.model)
            output = result if args.raw else format_output(result)

            if args.output:
                with open(args.output, "w") as f:
                    f.write(output)
                print(f"Analysis saved to: {args.output}", file=sys.stderr)
            else:
                print(output)
        finally:
            try:
                client.files.delete(name=gemini_file.name)
                print(f"Cleaned up Gemini file: {gemini_file.name}", file=sys.stderr)
            except Exception as e:
                print(f"Warning: couldn't delete Gemini file: {e}", file=sys.stderr)
    finally:
        if not args.keep and not args.download_only and os.path.exists(video_path):
            os.unlink(video_path)
            print("Cleaned up local video file", file=sys.stderr)


if __name__ == "__main__":
    main()
