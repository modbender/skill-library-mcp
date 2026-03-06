"""
telegram_sender.py — Send audio as Telegram PTT voice messages.

Uses the Telegram Bot API's sendVoice method to deliver audio
as native inline voice messages (with waveform visualization).

Requirements:
    - Audio must be OGG/Opus format for PTT display
    - Bot token + chat_id required
"""

import os
from pathlib import Path
from typing import Optional

import httpx

from audio_converter import convert_to_ogg_opus


async def send_voice_message(
    audio_path: str,
    bot_token: str,
    chat_id: str,
    caption: Optional[str] = None,
    duration: Optional[int] = None,
) -> dict:
    """
    Send an audio file as a Telegram voice message (PTT).

    The audio is automatically converted to OGG/Opus if not already
    in that format, then sent via the Telegram Bot API sendVoice method.

    Args:
        audio_path: Path to the audio file
        bot_token: Telegram Bot API token
        chat_id: Target chat ID
        caption: Optional caption text
        duration: Optional duration in seconds

    Returns:
        dict with Telegram API response

    Raises:
        FileNotFoundError: If audio file doesn't exist
        RuntimeError: If sending fails
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    if not bot_token:
        raise ValueError("Telegram bot_token is required")

    if not chat_id:
        raise ValueError("Telegram chat_id is required")

    # Convert to OGG/Opus if needed
    ogg_path = audio_path
    if not audio_path.lower().endswith(".ogg"):
        ogg_path = str(Path(audio_path).with_suffix(".ogg"))
        convert_to_ogg_opus(audio_path, ogg_path)

    # Send via Telegram Bot API
    url = f"https://api.telegram.org/bot{bot_token}/sendVoice"

    async with httpx.AsyncClient(timeout=60) as client:
        with open(ogg_path, "rb") as f:
            data = {"chat_id": chat_id}
            if caption:
                data["caption"] = caption
            if duration:
                data["duration"] = str(duration)

            files = {"voice": (Path(ogg_path).name, f, "audio/ogg")}

            response = await client.post(url, data=data, files=files)

    # Clean up converted file if we created one
    if ogg_path != audio_path and os.path.exists(ogg_path):
        os.remove(ogg_path)

    if response.status_code != 200:
        error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
        raise RuntimeError(
            f"Telegram API error (HTTP {response.status_code}): "
            f"{error_data.get('description', response.text)}"
        )

    return response.json()
