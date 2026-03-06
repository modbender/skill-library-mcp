#!/usr/bin/env python3
"""YouTube Uploader for OpenClaw — upload videos and thumbnails via OAuth2."""

import argparse
import json
import os
import socket
import stat
import subprocess
import sys
import threading
import webbrowser
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

# ---------------------------------------------------------------------------
# Dependency bootstrap
# ---------------------------------------------------------------------------

REQUIRED_PACKAGES = [
    ("googleapiclient", "google-api-python-client"),
    ("google_auth_oauthlib", "google-auth-oauthlib"),
    ("google.auth.transport.requests", "google-auth-httplib2"),
]


VENV_DIR = Path.home() / ".openclaw" / "youtube" / ".venv"


def _in_venv() -> bool:
    """Check if running inside our dedicated venv."""
    return any(str(VENV_DIR) in p for p in sys.path)


def ensure_dependencies():
    """Install missing Google API packages into a dedicated venv."""
    venv_python = VENV_DIR / "bin" / "python3"

    # If running outside the venv and it exists, re-exec into it directly
    if venv_python.exists() and not _in_venv():
        os.execv(str(venv_python), [str(venv_python), *sys.argv])

    # Check if imports are available
    missing = []
    for module_name, pip_name in REQUIRED_PACKAGES:
        try:
            __import__(module_name)
        except ImportError:
            missing.append(pip_name)
    if not missing:
        return

    # Create venv if needed (first run)
    if not venv_python.exists():
        print("Creating virtual environment for YouTube skill...", file=sys.stderr)
        subprocess.check_call([sys.executable, "-m", "venv", str(VENV_DIR)])

    print(f"Installing dependencies: {', '.join(missing)}", file=sys.stderr)
    subprocess.check_call([str(venv_python), "-m", "pip", "install", "--quiet", *missing])

    # Re-exec inside the venv so imports resolve
    os.execv(str(venv_python), [str(venv_python), *sys.argv])


ensure_dependencies()

from google.auth.transport.requests import Request  # noqa: E402
from google.oauth2.credentials import Credentials  # noqa: E402
from google_auth_oauthlib.flow import InstalledAppFlow  # noqa: E402
from googleapiclient.discovery import build  # noqa: E402
from googleapiclient.http import MediaFileUpload  # noqa: E402

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]

DEFAULT_DIR = Path.home() / ".openclaw" / "youtube"
CHANNELS_FILE = "channels.json"

VALID_PRIVACY = ("private", "unlisted", "public")
THUMBNAIL_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif"}
THUMBNAIL_MAX_BYTES = 2 * 1024 * 1024  # 2 MB

# ---------------------------------------------------------------------------
# Storage helpers
# ---------------------------------------------------------------------------


def get_storage_dir() -> Path:
    d = DEFAULT_DIR
    d.mkdir(parents=True, exist_ok=True)
    return d


def load_channels() -> dict:
    path = get_storage_dir() / CHANNELS_FILE
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def save_channels(channels: dict):
    path = get_storage_dir() / CHANNELS_FILE
    with open(path, "w") as f:
        json.dump(channels, f, indent=2)
    # Restrict permissions to owner only
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)


def get_credentials(channel_id: str | None, channels: dict) -> tuple[Credentials, str]:
    """Resolve credentials for a channel. Returns (creds, channel_id)."""
    if not channels:
        print("Error: No authenticated channels. Run 'auth' first.", file=sys.stderr)
        sys.exit(1)

    if channel_id:
        if channel_id not in channels:
            print(f"Error: Channel {channel_id} not found. Run 'channels' to list.", file=sys.stderr)
            sys.exit(1)
        entry = channels[channel_id]
    else:
        channel_id = next(iter(channels))
        entry = channels[channel_id]
        print(f"Using channel: {entry.get('title', channel_id)} ({channel_id})", file=sys.stderr)

    creds = Credentials(
        token=entry["token"],
        refresh_token=entry["refresh_token"],
        token_uri=entry["token_uri"],
        client_id=entry["client_id"],
        client_secret=entry["client_secret"],
        scopes=SCOPES,
    )

    # Auto-refresh if expired
    if creds.expired and creds.refresh_token:
        print("Token expired, refreshing...", file=sys.stderr)
        creds.refresh(Request())
        entry["token"] = creds.token
        entry["expiry"] = creds.expiry.isoformat() if creds.expiry else None
        save_channels(channels)

    return creds, channel_id


# ---------------------------------------------------------------------------
# OAuth2 callback server
# ---------------------------------------------------------------------------


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Minimal HTTP handler to capture OAuth2 redirect."""

    auth_code: str | None = None

    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        code = query.get("code")
        if code:
            OAuthCallbackHandler.auth_code = code[0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"<html><body><h2>Authentication successful!</h2>"
                b"<p>You can close this tab and return to the terminal.</p>"
                b"</body></html>"
            )
        else:
            error = query.get("error", ["unknown"])[0]
            self.send_response(400)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(f"<html><body><h2>Error: {error}</h2></body></html>".encode())

    def log_message(self, format, *args):
        pass  # Suppress server logs


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------


def cmd_auth(args):
    """Authenticate a YouTube channel via OAuth2."""
    client_secret_path = Path(args.client_secret).expanduser()
    if not client_secret_path.exists():
        print(f"Error: Client secret file not found: {client_secret_path}", file=sys.stderr)
        sys.exit(1)

    # Copy client_secret to storage dir for future refreshes
    stored_secret = get_storage_dir() / "client_secret.json"
    if client_secret_path.resolve() != stored_secret.resolve():
        import shutil
        shutil.copy2(client_secret_path, stored_secret)
        os.chmod(stored_secret, stat.S_IRUSR | stat.S_IWUSR)

    port = find_free_port()
    redirect_uri = f"http://127.0.0.1:{port}"

    flow = InstalledAppFlow.from_client_secrets_file(
        str(client_secret_path),
        scopes=SCOPES,
        redirect_uri=redirect_uri,
    )

    auth_url, _ = flow.authorization_url(
        access_type="offline",
        prompt="consent",
    )

    # Start callback server
    server = HTTPServer(("127.0.0.1", port), OAuthCallbackHandler)
    server_thread = threading.Thread(target=server.handle_request, daemon=True)
    server_thread.start()

    print(f"Opening browser for authentication...", file=sys.stderr)
    print(f"If the browser doesn't open, visit: {auth_url}", file=sys.stderr)
    webbrowser.open(auth_url)

    # Wait for callback
    server_thread.join(timeout=120)
    server.server_close()

    if not OAuthCallbackHandler.auth_code:
        print("Error: Did not receive authorization code.", file=sys.stderr)
        sys.exit(1)

    flow.fetch_token(code=OAuthCallbackHandler.auth_code)
    creds = flow.credentials

    # Get channel info
    youtube = build("youtube", "v3", credentials=creds)
    response = youtube.channels().list(part="snippet", mine=True).execute()

    if not response.get("items"):
        print("Error: No YouTube channel found for this account.", file=sys.stderr)
        sys.exit(1)

    channel = response["items"][0]
    channel_id = channel["id"]
    channel_title = channel["snippet"]["title"]

    # Save credentials
    channels = load_channels()
    channels[channel_id] = {
        "title": channel_title,
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "expiry": creds.expiry.isoformat() if creds.expiry else None,
        "authenticated_at": datetime.now(timezone.utc).isoformat(),
    }
    save_channels(channels)

    result = {"channelId": channel_id, "title": channel_title, "status": "authenticated"}
    print(json.dumps(result, indent=2))


def cmd_channels(args):
    """List authenticated channels (without tokens)."""
    channels = load_channels()
    if not channels:
        print("No authenticated channels. Run 'auth' first.", file=sys.stderr)
        sys.exit(1)

    result = []
    for cid, entry in channels.items():
        result.append({
            "channelId": cid,
            "title": entry.get("title", "Unknown"),
            "authenticatedAt": entry.get("authenticated_at", "Unknown"),
        })
    print(json.dumps(result, indent=2))


def cmd_upload(args):
    """Upload a video to YouTube."""
    video_path = Path(args.file).expanduser()
    if not video_path.exists():
        print(f"Error: Video file not found: {video_path}", file=sys.stderr)
        sys.exit(1)

    if args.privacy not in VALID_PRIVACY:
        print(f"Error: Invalid privacy '{args.privacy}'. Must be one of: {', '.join(VALID_PRIVACY)}", file=sys.stderr)
        sys.exit(1)

    if args.publish_at and args.privacy != "private":
        print("Error: --publish-at requires --privacy private.", file=sys.stderr)
        sys.exit(1)

    channels = load_channels()
    creds, channel_id = get_credentials(args.channel_id, channels)
    youtube = build("youtube", "v3", credentials=creds)

    body = {
        "snippet": {
            "title": args.title,
            "description": args.description or "",
            "tags": [t.strip() for t in args.tags.split(",")] if args.tags else [],
            "categoryId": str(args.category),
        },
        "status": {
            "privacyStatus": args.privacy,
            "selfDeclaredMadeForKids": args.made_for_kids,
        },
    }

    if args.publish_at:
        body["status"]["publishAt"] = args.publish_at

    # Detect MIME type
    ext = video_path.suffix.lower()
    mime_map = {
        ".mp4": "video/mp4",
        ".mov": "video/quicktime",
        ".avi": "video/x-msvideo",
        ".wmv": "video/x-ms-wmv",
        ".flv": "video/x-flv",
        ".webm": "video/webm",
        ".mkv": "video/x-matroska",
        ".3gp": "video/3gpp",
    }
    mime_type = mime_map.get(ext, "video/*")

    media = MediaFileUpload(
        str(video_path),
        mimetype=mime_type,
        resumable=True,
        chunksize=10 * 1024 * 1024,  # 10 MB chunks
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    print(f"Uploading {video_path.name}...", file=sys.stderr)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            pct = int(status.progress() * 100)
            print(f"Upload progress: {pct}%", file=sys.stderr)

    video_id = response["id"]
    result = {
        "videoId": video_id,
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "channelId": channel_id,
        "title": args.title,
        "privacy": args.privacy,
    }
    print(json.dumps(result, indent=2))


def cmd_thumbnail(args):
    """Upload a custom thumbnail for a video."""
    thumb_path = Path(args.file).expanduser()
    if not thumb_path.exists():
        print(f"Error: Thumbnail file not found: {thumb_path}", file=sys.stderr)
        sys.exit(1)

    ext = thumb_path.suffix.lower()
    if ext not in THUMBNAIL_EXTENSIONS:
        print(
            f"Error: Unsupported thumbnail format '{ext}'. Supported: {', '.join(THUMBNAIL_EXTENSIONS)}",
            file=sys.stderr,
        )
        sys.exit(1)

    file_size = thumb_path.stat().st_size
    if file_size > THUMBNAIL_MAX_BYTES:
        print(
            f"Error: Thumbnail too large ({file_size} bytes). Maximum is {THUMBNAIL_MAX_BYTES} bytes (2 MB).",
            file=sys.stderr,
        )
        sys.exit(1)

    mime_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".bmp": "image/bmp",
        ".gif": "image/gif",
    }

    channels = load_channels()
    creds, channel_id = get_credentials(args.channel_id, channels)
    youtube = build("youtube", "v3", credentials=creds)

    media = MediaFileUpload(str(thumb_path), mimetype=mime_map[ext])

    print(f"Uploading thumbnail for video {args.video_id}...", file=sys.stderr)

    response = youtube.thumbnails().set(
        videoId=args.video_id,
        media_body=media,
    ).execute()

    result = {
        "videoId": args.video_id,
        "channelId": channel_id,
        "thumbnailUrl": response.get("items", [{}])[0].get("default", {}).get("url", ""),
        "status": "set",
    }
    print(json.dumps(result, indent=2))


def cmd_refresh(args):
    """Manually refresh OAuth2 token for a channel."""
    channels = load_channels()
    creds, channel_id = get_credentials(args.channel_id, channels)

    if creds.refresh_token:
        creds.refresh(Request())
        channels[channel_id]["token"] = creds.token
        channels[channel_id]["expiry"] = creds.expiry.isoformat() if creds.expiry else None
        save_channels(channels)
        print(json.dumps({"channelId": channel_id, "status": "refreshed"}, indent=2))
    else:
        print("Error: No refresh token available. Re-run 'auth'.", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="YouTube Uploader for OpenClaw",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # auth
    p_auth = sub.add_parser("auth", help="Authenticate a YouTube channel")
    p_auth.add_argument(
        "--client-secret",
        default=str(DEFAULT_DIR / "client_secret.json"),
        help="Path to Google OAuth2 client_secret.json",
    )
    p_auth.set_defaults(func=cmd_auth)

    # channels
    p_channels = sub.add_parser("channels", help="List authenticated channels")
    p_channels.set_defaults(func=cmd_channels)

    # upload
    p_upload = sub.add_parser("upload", help="Upload a video")
    p_upload.add_argument("--file", required=True, help="Path to video file")
    p_upload.add_argument("--title", required=True, help="Video title")
    p_upload.add_argument("--description", default="", help="Video description")
    p_upload.add_argument("--tags", default="", help="Comma-separated tags")
    p_upload.add_argument("--category", type=int, default=22, help="Category ID (default: 22)")
    p_upload.add_argument("--privacy", default="private", choices=VALID_PRIVACY, help="Privacy status")
    p_upload.add_argument("--publish-at", default=None, help="Scheduled publish time (ISO 8601)")
    p_upload.add_argument("--made-for-kids", action="store_true", help="Mark as made for kids")
    p_upload.add_argument("--channel-id", default=None, help="Target channel ID")
    p_upload.set_defaults(func=cmd_upload)

    # thumbnail
    p_thumb = sub.add_parser("thumbnail", help="Upload a custom thumbnail")
    p_thumb.add_argument("--video-id", required=True, help="YouTube video ID")
    p_thumb.add_argument("--file", required=True, help="Path to thumbnail image")
    p_thumb.add_argument("--channel-id", default=None, help="Target channel ID")
    p_thumb.set_defaults(func=cmd_thumbnail)

    # refresh
    p_refresh = sub.add_parser("refresh", help="Refresh OAuth2 token")
    p_refresh.add_argument("--channel-id", default=None, help="Target channel ID")
    p_refresh.set_defaults(func=cmd_refresh)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
