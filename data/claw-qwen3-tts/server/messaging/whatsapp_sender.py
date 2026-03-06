"""
whatsapp_sender.py — Send audio as WhatsApp PTT voice messages.

Uses the WhatsApp Business API (Meta Graph API) to upload audio
and send it as a native voice message.

Requirements:
    - Audio must be OGG/Opus format for voice message display
    - WhatsApp Business API access (phone_number_id + access_token)
"""

import os
from pathlib import Path
from typing import Optional

import httpx

from audio_converter import convert_to_ogg_opus


GRAPH_API_BASE = "https://graph.facebook.com/v21.0"


async def send_voice_message(
    audio_path: str,
    phone_number_id: str,
    recipient: str,
    access_token: str,
) -> dict:
    """
    Send an audio file as a WhatsApp voice message (PTT).

    Steps:
        1. Convert audio to OGG/Opus if needed
        2. Upload media to WhatsApp Business API
        3. Send audio message with the media ID

    Args:
        audio_path: Path to the audio file
        phone_number_id: WhatsApp Business phone number ID
        recipient: Recipient phone number (E.164 format, e.g. "+14155551234")
        access_token: Meta Graph API access token

    Returns:
        dict with WhatsApp API response

    Raises:
        FileNotFoundError: If audio file doesn't exist
        RuntimeError: If upload or sending fails
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    if not phone_number_id:
        raise ValueError("WhatsApp phone_number_id is required")
    if not recipient:
        raise ValueError("Recipient phone number is required")
    if not access_token:
        raise ValueError("WhatsApp access_token is required")

    # Normalize recipient (strip spaces, ensure no leading 00)
    recipient = recipient.strip().replace(" ", "")
    if recipient.startswith("00"):
        recipient = "+" + recipient[2:]

    # Convert to OGG/Opus if needed
    ogg_path = audio_path
    if not audio_path.lower().endswith(".ogg"):
        ogg_path = str(Path(audio_path).with_suffix(".ogg"))
        convert_to_ogg_opus(audio_path, ogg_path)

    headers = {"Authorization": f"Bearer {access_token}"}

    async with httpx.AsyncClient(timeout=60) as client:
        # Step 1: Upload media
        upload_url = f"{GRAPH_API_BASE}/{phone_number_id}/media"

        with open(ogg_path, "rb") as f:
            upload_response = await client.post(
                upload_url,
                headers=headers,
                data={"messaging_product": "whatsapp", "type": "audio/ogg; codecs=opus"},
                files={"file": (Path(ogg_path).name, f, "audio/ogg; codecs=opus")},
            )

        if upload_response.status_code != 200:
            raise RuntimeError(
                f"WhatsApp media upload failed (HTTP {upload_response.status_code}): "
                f"{upload_response.text}"
            )

        media_id = upload_response.json().get("id")
        if not media_id:
            raise RuntimeError("WhatsApp media upload did not return a media ID")

        # Step 2: Send audio message
        send_url = f"{GRAPH_API_BASE}/{phone_number_id}/messages"

        message_data = {
            "messaging_product": "whatsapp",
            "to": recipient,
            "type": "audio",
            "audio": {"id": media_id},
        }

        send_response = await client.post(
            send_url,
            headers={**headers, "Content-Type": "application/json"},
            json=message_data,
        )

    # Clean up converted file if we created one
    if ogg_path != audio_path and os.path.exists(ogg_path):
        os.remove(ogg_path)

    if send_response.status_code not in (200, 201):
        raise RuntimeError(
            f"WhatsApp send failed (HTTP {send_response.status_code}): "
            f"{send_response.text}"
        )

    return send_response.json()
