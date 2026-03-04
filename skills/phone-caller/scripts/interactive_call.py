#!/usr/bin/env python3
"""
interactive_call.py — Launch a live AI phone conversation via Twilio webhook
Usage: python3 interactive_call.py --to "+13105551234" --url "https://abc.loca.lt"
       --persona "You are calling to book a dinner reservation for 2 at 8pm."
       --opening "Hi! I'd like to make a reservation for this evening..."
"""
import os, argparse
from twilio.rest import Client

TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN  = os.environ.get("TWILIO_AUTH_TOKEN", "")
TWILIO_FROM        = os.environ.get("TWILIO_PHONE_NUMBER", "")


def main():
    parser = argparse.ArgumentParser(description="Start an interactive AI phone call")
    parser.add_argument("--to",      required=True, help="Phone number to call")
    parser.add_argument("--url",     required=True, help="Public server URL (no trailing slash)")
    parser.add_argument("--persona", default="You are making a friendly, helpful phone call. Be concise and natural.",
                        help="System prompt describing the caller's goal and personality")
    parser.add_argument("--opening", default="Hello! I'm calling to have a quick chat.",
                        help="The caller's opening line")
    args = parser.parse_args()

    url = args.url.rstrip("/")

    import urllib.parse
    params = urllib.parse.urlencode({
        "persona": args.persona,
        "opening": args.opening
    })

    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    call = client.calls.create(
        from_=TWILIO_FROM,
        to=args.to,
        url=f"{url}/call/start?{params}",
        method="POST",
        status_callback=f"{url}/call/status",
        status_callback_method="POST",
        status_callback_event=["completed", "busy", "no-answer", "failed"]
    )
    print(f"📞  Call initiated → {args.to}")
    print(f"    SID: {call.sid} | Status: {call.status}")


if __name__ == "__main__":
    main()
