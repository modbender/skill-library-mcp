#!/usr/bin/env python3
"""
Solo Leveling System — Twilio Voice Call Integration
Makes phone calls with TTS messages. Config stored in twilio-config.json.
Usage:
  python3 twilio_call.py "Your message here"
  python3 twilio_call.py --type wake|gym|sleep|emergency "Optional custom message"
"""

import json
import sys
import os
import urllib.request
import urllib.parse
import base64

CONFIG_PATH = os.environ.get(
    "TWILIO_CONFIG",
    os.path.expanduser("~/.openclaw/workspace/solo-leveling-data/twilio-config.json")
)

PRESET_MESSAGES = {
    "wake": (
        "<speak>"
        "<prosody rate='slow'>"
        "Attention, Hunter. This is The System. "
        "It is 6:30 A.M. Your daily quests have been issued. "
        "Rise now, or face the consequences. "
        "The gym awaits. Your stats will not improve themselves. "
        "You have 15 minutes before this is logged as a failure. "
        "The System is watching."
        "</prosody>"
        "</speak>"
    ),
    "gym": (
        "<speak>"
        "<prosody rate='slow'>"
        "Hunter. You have not checked in at the gym. "
        "Your Strength stat is stagnating. "
        "Every minute of delay is weakness you are choosing. "
        "Report to the gym immediately, or accept the penalty. "
        "The System does not repeat itself."
        "</prosody>"
        "</speak>"
    ),
    "sleep": (
        "<speak>"
        "<prosody rate='slow'>"
        "Attention, Hunter. It is 10:45 P.M. "
        "You have 15 minutes until the sleep deadline. "
        "Put down the phone. Close the laptop. "
        "Your Vitality stat depends on this. "
        "The System will verify compliance at 11:30. "
        "Do not disappoint The System."
        "</prosody>"
        "</speak>"
    ),
    "emergency": (
        "<speak>"
        "<prosody rate='slow'>"
        "Emergency Quest issued. "
        "Hunter, your performance has triggered a critical alert. "
        "The System has detected prolonged inactivity or repeated failures. "
        "Respond immediately via Telegram, or penalties will escalate. "
        "This is not a request. This is The System."
        "</prosody>"
        "</speak>"
    ),
}


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def make_call(message, config=None, use_ssml=False):
    """Place a phone call via Twilio REST API with TTS message."""
    if config is None:
        config = load_config()

    account_sid = config["account_sid"]
    auth_token = config["auth_token"]
    from_number = config["twilio_number"]
    to_number = config["target_number"]
    voice = config.get("tts_voice", "Polly.Brian")
    language = config.get("tts_language", "en-GB")

    if not to_number:
        print("ERROR: No target phone number configured.")
        sys.exit(1)

    # Build TwiML
    if use_ssml:
        say_content = f'<Say voice="{voice}" language="{language}">{message}</Say>'
    else:
        say_content = f'<Say voice="{voice}" language="{language}">{message}</Say>'

    twiml = f'<Response>{say_content}<Pause length="1"/>{say_content}</Response>'

    # Twilio API call
    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Calls.json"

    data = urllib.parse.urlencode({
        "To": to_number,
        "From": from_number,
        "Twiml": twiml,
    }).encode()

    # Basic auth
    credentials = base64.b64encode(f"{account_sid}:{auth_token}".encode()).decode()

    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Basic {credentials}")

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            print(f"Call initiated: SID={result.get('sid')}")
            print(f"Status: {result.get('status')}")
            print(f"To: {to_number}")
            return result
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"ERROR: Twilio API returned {e.code}")
        print(error_body)
        sys.exit(1)


if __name__ == "__main__":
    call_type = None
    custom_message = None

    args = sys.argv[1:]
    if not args:
        print("Usage: twilio_call.py [--type wake|gym|sleep|emergency] [message]")
        sys.exit(1)

    if args[0] == "--type" and len(args) >= 2:
        call_type = args[1]
        custom_message = " ".join(args[2:]) if len(args) > 2 else None
    else:
        custom_message = " ".join(args)

    if call_type and call_type in PRESET_MESSAGES:
        message = custom_message or PRESET_MESSAGES[call_type]
        use_ssml = custom_message is None
    elif custom_message:
        message = custom_message
        use_ssml = False
    else:
        print(f"Unknown call type: {call_type}")
        print(f"Available: {', '.join(PRESET_MESSAGES.keys())}")
        sys.exit(1)

    make_call(message, use_ssml=use_ssml)
