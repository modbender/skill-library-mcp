#!/usr/bin/env python3
"""Read PDF, video, and audio files using Gemini API.

Usage:
    gemini_read.py <file> <prompt> [--model MODEL] [--output PATH]

Examples:
    gemini_read.py paper.pdf "Summarize this paper"
    gemini_read.py lecture.mp4 "List the key points" -m 3-pro
    gemini_read.py recording.m4a "Transcribe this audio" --output transcript.txt
"""
import argparse, os, sys, mimetypes, time

# Only these file extensions are allowed (prevents uploading arbitrary files)
ALLOWED_EXTENSIONS = {
    ".pdf",
    ".mp4", ".webm", ".mov", ".avi", ".mkv",
    ".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac",
}

MIME_MAP = {
    ".pdf": "application/pdf",
    ".mp4": "video/mp4", ".webm": "video/webm",
    ".mov": "video/quicktime", ".avi": "video/x-msvideo",
    ".mkv": "video/x-matroska",
    ".mp3": "audio/mpeg", ".wav": "audio/wav",
    ".m4a": "audio/mp4", ".ogg": "audio/ogg",
    ".flac": "audio/flac", ".aac": "audio/aac",
}

# Short aliases -> full model names
MODEL_ALIASES = {
    "3-flash":   "gemini-3-flash-preview",
    "3-pro":     "gemini-3-pro-preview",
    "3.1-pro":   "gemini-3.1-pro-preview",
    "2.5-flash": "gemini-2.5-flash",
    "2.5-pro":   "gemini-2.5-pro",
}

# Sensitive paths that should never be read or written
SENSITIVE_PATTERNS = (
    ".ssh", ".gnupg", ".env", ".git/config", ".netrc",
    "id_rsa", "id_ed25519", ".pem", ".key", "credentials",
    "/etc/shadow", "/etc/passwd",
)

def resolve_model(name: str) -> str:
    return MODEL_ALIASES.get(name, name)

def detect_mime(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext in MIME_MAP:
        return MIME_MAP[ext]
    guess, _ = mimetypes.guess_type(path)
    return guess or "application/octet-stream"

def is_sensitive_path(path: str) -> bool:
    """Check if a path looks like it contains sensitive data."""
    # Resolve symlinks to catch indirect access
    try:
        resolved = os.path.realpath(path).lower()
    except OSError:
        return True  # If we can't resolve, err on the side of caution
    normalized = os.path.abspath(path).lower()
    return any(p in resolved or p in normalized for p in SENSITIVE_PATTERNS)

def main():
    aliases = ", ".join(f"{k}" for k in MODEL_ALIASES)
    parser = argparse.ArgumentParser(description="Read files with Gemini API")
    parser.add_argument("file", help="Path to file (PDF, video, audio)")
    parser.add_argument("prompt", help="Question or instruction about the file")
    parser.add_argument("--model", "-m", default="3-flash",
                        help=f"Model alias or full name (default: 3-flash). Aliases: {aliases}")
    parser.add_argument("--output", "-o", default=None, help="Save output to file")
    args = parser.parse_args()

    src = os.path.abspath(args.file)
    if not os.path.exists(src):
        print(f"Error: file not found: {src}", file=sys.stderr)
        sys.exit(1)

    # Validate file extension
    ext = os.path.splitext(src)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        print(f"Error: unsupported file type '{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}", file=sys.stderr)
        sys.exit(1)

    # Block symlinks (could point to sensitive files)
    if os.path.islink(src):
        print(f"Error: refusing to follow symlink: {src}", file=sys.stderr)
        sys.exit(1)

    # Block sensitive file paths
    if is_sensitive_path(src):
        print(f"Error: refusing to upload potentially sensitive file: {src}", file=sys.stderr)
        sys.exit(1)

    # Validate output path if specified
    if args.output:
        out_abs = os.path.abspath(args.output)
        if is_sensitive_path(out_abs):
            print(f"Error: refusing to write to sensitive path: {out_abs}", file=sys.stderr)
            sys.exit(1)

    mime = detect_mime(src)
    size_mb = os.path.getsize(src) / (1024 * 1024)
    model = resolve_model(args.model)
    print(f"File: {os.path.basename(src)} ({size_mb:.1f} MB, {mime})", file=sys.stderr)
    print(f"Model: {model}", file=sys.stderr)

    # Strip quotes from API key if present (common in .env files)
    key = os.environ.get("GEMINI_API_KEY", "")
    if key.startswith('"') and key.endswith('"'):
        os.environ["GEMINI_API_KEY"] = key.strip('"')

    from google import genai

    client = genai.Client()

    # Upload file
    print("Uploading...", file=sys.stderr, end=" ", flush=True)
    uploaded = client.files.upload(file=src, config={"mime_type": mime})
    print(f"done ({uploaded.name})", file=sys.stderr)

    # For video/audio, wait for processing
    if mime.startswith(("video/", "audio/")):
        print("Processing media...", file=sys.stderr, end=" ", flush=True)
        while uploaded.state.name == "PROCESSING":
            time.sleep(2)
            uploaded = client.files.get(name=uploaded.name)
        if uploaded.state.name == "FAILED":
            print(f"\nError: file processing failed", file=sys.stderr)
            sys.exit(1)
        print("done", file=sys.stderr)

    # Generate content
    print("Generating...", file=sys.stderr, flush=True)
    response = client.models.generate_content(
        model=model,
        contents=[uploaded, args.prompt],
    )

    output = response.text.strip() if response.text else "(no response)"

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Saved to {args.output}", file=sys.stderr)
    else:
        print(output)

    # Cleanup uploaded file from Gemini servers
    try:
        client.files.delete(name=uploaded.name)
    except Exception:
        pass

if __name__ == "__main__":
    main()
