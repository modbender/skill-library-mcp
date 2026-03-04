#!/usr/bin/env python3
"""Trigger an outbound phone call via ElevenLabs Conversational AI + Twilio."""
import sys
import os
import json
import re
import urllib.request
import urllib.error

AGENT_ID = os.environ.get("ELEVENLABS_AGENT_ID", "")
API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
PHONE_NUMBER_ID = os.environ.get("ELEVENLABS_PHONE_NUMBER_ID", "")

API_URL = "https://api.elevenlabs.io/v1/convai/twilio/outbound-call"


def make_call(to_number: str, first_message: str = "", context: str = "") -> dict:
    """Place an outbound call to the given phone number.

    Args:
        to_number: Phone number in E.164 format (+1XXXXXXXXXX for US).
        first_message: Optional custom greeting for this call.
        context: Optional context to pass as a dynamic variable.
    """
    if not API_KEY:
        return {"error": "ELEVENLABS_API_KEY not set. Add it to your .env file."}
    if not AGENT_ID:
        return {"error": "ELEVENLABS_AGENT_ID not set. Add it to your .env file."}
    if not PHONE_NUMBER_ID:
        return {"error": "ELEVENLABS_PHONE_NUMBER_ID not set. Add it to your .env file."}

    # Validate E.164 format (US numbers: +1 followed by 10 digits)
    if not re.match(r'^\+1\d{10}$', to_number):
        return {"error": f"Invalid US phone number: {to_number}. Use +1XXXXXXXXXX format (E.164)."}

    payload = {
        "agent_id": AGENT_ID,
        "agent_phone_number_id": PHONE_NUMBER_ID,
        "to_number": to_number,
    }

    # Add optional overrides if provided
    client_data = {}
    if first_message:
        client_data["conversation_config_override"] = {
            "agent": {"first_message": first_message}
        }
    if context:
        client_data["dynamic_variables"] = {"call_context": context}
    if client_data:
        payload["conversation_initiation_client_data"] = client_data

    data = json.dumps(payload).encode()
    req = urllib.request.Request(API_URL, data=data, headers={
        "xi-api-key": API_KEY,
        "Content-Type": "application/json",
    })

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            # ElevenLabs may return HTTP 200 with an error in the body
            if not result.get("success", True) or "error" in result:
                return {"error": result.get("error", result.get("message", "Unknown API error"))}
            return {
                "success": True,
                "conversation_id": result.get("conversation_id", ""),
                "call_sid": result.get("callSid", ""),
                "message": result.get("message", "Call initiated"),
            }
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        return {"error": f"ElevenLabs API error (HTTP {e.code}): {body}"}
    except urllib.error.URLError as e:
        return {"error": f"Network error: {e.reason}"}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: call.py <phone_number> [first_message] [context]"}))
        sys.exit(1)

    to = sys.argv[1]
    first_msg = sys.argv[2] if len(sys.argv) > 2 else ""
    ctx = sys.argv[3] if len(sys.argv) > 3 else ""

    result = make_call(to, first_msg, ctx)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get("success") else 1)
