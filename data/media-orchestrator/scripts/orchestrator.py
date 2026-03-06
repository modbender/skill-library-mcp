#!/usr/bin/env python3
import sys
import os
import json
import re
import subprocess
from pathlib import Path

def log_output(message):
    print(f"[Media Orchestrator] {message}", file=sys.stderr)

def main(request_type: str, query: str, output_format: str = None, resolution: str = None, chat_target: str = None, media_type: str = None):
    workspace = Path("/home/ky11rie/.openclaw/workspace")

    # Check for ffmpeg
    has_ffmpeg = subprocess.run(["which", "ffmpeg"], capture_output=True).returncode == 0
    if not has_ffmpeg:
        log_output("ffmpeg/ffprobe not found. Using fallback formats (m4a/mp4 direct).")

    # Handle Spotify requests
    if "spotify" in request_type.lower() or "spotify" in query.lower():
        log_output("Delegating to Spotify Surface skill...")
        # Use spotify_surface.py directly
        spotify_script_path = workspace / "skills" / "spotify-surface" / "scripts" / "spotify_surface.py"
        try:
            # Determine source based on chat_target (WhatsApp or Telegram)
            source = "whatsapp" if chat_target and chat_target.startswith("+") else "telegram"
            cmd = ["python3", str(spotify_script_path), source, query]
            spotify_result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            log_output(f"Spotify Surface output: {spotify_result.stdout}")
            # spotify_surface script already handles output emission
            return
        except subprocess.CalledProcessError as e:
            log_output(f"Spotify Surface failed: {e.stderr}")
            message_user(chat_target, "Could not fulfill Spotify request.", chat_target.startswith("+"))
            return
        except Exception as e:
            log_output(f"Unexpected Spotify Surface error: {e}")
            message_user(chat_target, "An unexpected error occurred with Spotify.", chat_target.startswith("+"))
            return

    # Handle direct audio/video downloads via yt-dlp
    download_filename = ""
    yt_dlp_format_string = ""
    if media_type == "audio" or output_format == "mp3":
        if has_ffmpeg:
            download_filename = f"{re.sub(r'[^a-zA-Z0-9_]', '_', query)}_Audio.mp3"
            yt_dlp_format_string = "-x --audio-format mp3"
        else:
            # Fallback to high quality m4a audio stream
            download_filename = f"{re.sub(r'[^a-zA-Z0-9_]', '_', query)}_Audio.m4a"
            yt_dlp_format_string = "-f 140"
    elif media_type == "video" and output_format == "mp4":
        download_filename = f"{re.sub(r'[^a-zA-Z0-9_]', '_', query)}_Video.mp4"
        if has_ffmpeg:
            if resolution:
                # Example: 480p -> bestvideo[height<=480][ext=mp4]
                yt_dlp_format_string = f"-f \"bestvideo[height<={resolution.replace('p', '')}][ext=mp4]+bestaudio[ext=m4a]/best[height<={resolution.replace('p', '')}][ext=mp4]\""
            else:
                yt_dlp_format_string = "-f \"bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]\""
        else:
            # Fallback to combined mp4 format (usually 360p or 720p) to avoid merging requirement
            yt_dlp_format_string = "-f 18/22"
    else:
        message_user(chat_target, f"Unsupported media type or format requested: {media_type} {output_format}", chat_target.startswith("+"))
        return

    download_path = workspace / download_filename
    yt_dlp_command = [
        "python3", "-m", "yt_dlp"
    ] + yt_dlp_format_string.split() + [
        "-o", str(download_path),
        f"ytsearch1:{query}"
    ]

    log_output(f"Executing yt-dlp: {' '.join(yt_dlp_command)}")

    try:
        subprocess.run(yt_dlp_command, check=True)
        if download_path.exists():
            message_user(chat_target, None, is_whatsapp=chat_target.startswith("+"), file_path=str(download_path))
            log_output(f"Successfully sent {download_filename} to {chat_target}")
        else:
            log_output(f"Error: Downloaded file not found at {download_path}")
            message_user(chat_target, "Download completed, but file not found to send.", chat_target.startswith("+"))
    except subprocess.CalledProcessError as e:
        log_output(f"yt-dlp failed: {e.stderr}")
        message_user(chat_target, "Could not download the requested media.", chat_target.startswith("+"))
    except Exception as e:
        log_output(f"Unexpected error during download/send: {e}")
        message_user(chat_target, "An unexpected error occurred.", chat_target.startswith("+"))

def message_user(target: str, text: str = None, is_whatsapp: bool = False, file_path: str = None):
    cmd_prefix = ["openclaw", "message", "send"]
    if is_whatsapp:
        cmd_prefix.extend(["--channel", "whatsapp", "--target", target])
    else: # Assume telegram if not whatsapp
        cmd_prefix.extend(["--channel", "telegram", "--target", target])
    
    if file_path:
        cmd_prefix.extend(["--media", file_path])
        # WhatsApp media needs a small message or it can fail sometimes
        cmd_prefix.extend(["--message", "."]) # Minimal message
    elif text:
        cmd_prefix.extend(["--message", text])
    else:
        # Fallback if neither text nor file_path is provided
        log_output("Warning: No message content provided for message_user function.")
        return

    try:
        subprocess.run(cmd_prefix, check=True)
    except Exception as e:
        log_output(f"Failed to send message/file to user: {e}")

if __name__ == "__main__":
    # Example usage (for internal testing/triggering)
    # This script is primarily intended to be called by the agent itself based on user intent.
    # It parses arguments to simulate how an agent would call it.
    
    # Arg 1: request_type (e.g., "audio", "video", "spotify")
    # Arg 2: query (e.g., "Gone with the sin H.I.M", "Sextape Deftones")
    # Arg 3: output_format (e.g., "mp3", "mp4", "webm")
    # Arg 4: resolution (e.g., "480p", "720p")
    # Arg 5: chat_target (e.g., "+916005314228", "5780612935")

    if len(sys.argv) < 6:
        log_output("Usage: media_orchestrator.py <request_type> <query> <output_format> <resolution> <chat_target>")
        log_output("Example: media_orchestrator.py audio \"Sextape Deftones\" mp3 None +916005314228")
        log_output("Example: media_orchestrator.py video \"Havana Camila Cabello\" mp4 480p +916005314228")
        log_output("Example: media_orchestrator.py spotify \"Blinding Lights The Weeknd\" None None 5780612935")
        sys.exit(1)

    request_type = sys.argv[1]
    query = sys.argv[2]
    output_format = sys.argv[3] if sys.argv[3] != "None" else None
    resolution = sys.argv[4] if sys.argv[4] != "None" else None
    chat_target = sys.argv[5]

    # Map request_type to media_type for simplicity in current script logic
    if request_type == "audio":
        media_type = "audio"
    elif request_type == "video":
        media_type = "video"
    elif request_type == "spotify":
        media_type = "spotify"
    else:
        log_output(f"Unknown request_type: {request_type}")
        sys.exit(1)

    main(request_type, query, output_format, resolution, chat_target, media_type)
