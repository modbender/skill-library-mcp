#!/usr/bin/env python3
"""
FlowConcierge — AI phone receptionist for any business. Free.

Give it a website URL or a knowledge base file.
It spins up a VAPI voice assistant, connects a phone number (auto-bought via Twilio),
logs every call to HubSpot CRM, and sends SMS follow-ups.

Usage:
  flowconcierge setup <url> [--name "My Business"] [--vapi-key KEY]
                            [--twilio-sid SID --twilio-token TOKEN]
  flowconcierge setup --kb knowledge_base.md [--name "My Business"]
  flowconcierge webhook [--port 8080] [--hubspot-key KEY]
                        [--twilio-sid SID --twilio-token TOKEN]
                        [--twilio-from +1...] [--sms-followup]
                        [--business-name "My Business"]
  flowconcierge list   [--vapi-key KEY]
  flowconcierge delete <assistant-id> [--vapi-key KEY]
"""

import sys
import os
import json
import base64
import argparse
import urllib.request
import urllib.error
import urllib.parse
import time
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread


# ─── VAPI client ──────────────────────────────────────────────────────────────
class VAPIClient:
    BASE = "https://api.vapi.ai"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def _req(self, method: str, path: str, body: dict = None) -> dict:
        url = f"{self.BASE}{path}"
        data = json.dumps(body).encode() if body else None
        req = urllib.request.Request(
            url, data=data, method=method,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            err = e.read().decode()
            raise RuntimeError(f"VAPI {method} {path} → {e.code}: {err}")

    def create_knowledge_base(self, name: str, content: str) -> str:
        result = self._req("POST", "/knowledge-base", {
            "name": name,
            "provider": "canonical",
            "chunkPlan": {"enabled": True, "maxChunkSize": 1500},
            "documents": [{"content": content, "name": f"{name} Knowledge Base"}]
        })
        return result["id"]

    def create_assistant(self, name: str, system_prompt: str,
                         kb_id: str = None, language: str = "en",
                         webhook_url: str = None) -> dict:
        body = {
            "name": f"FlowConcierge — {name}",
            "firstMessage": f"Thank you for calling {name}. How can I help you today?",
            "model": {
                "provider": "openai",
                "model": "gpt-4o-mini",
                "messages": [{"role": "system", "content": system_prompt}],
                **({"knowledgeBaseId": kb_id} if kb_id else {}),
            },
            "voice": {
                "provider": "11labs",
                "voiceId": "21m00Tcm4TlvDq8ikWAM",  # Rachel — warm, professional
            },
            "transcriber": {"provider": "deepgram", "language": language},
            "endCallMessage": f"Thank you for calling {name}. Have a wonderful day!",
            "recordingEnabled": False,
            **({"serverUrl": webhook_url} if webhook_url else {}),
        }
        return self._req("POST", "/assistant", body)

    def connect_phone_number(self, phone: str, assistant_id: str, provider: str = "twilio",
                              account_sid: str = None, auth_token: str = None) -> dict:
        body: dict = {
            "number": phone,
            "assistantId": assistant_id,
            "name": f"FlowConcierge — {phone}",
        }
        if provider == "twilio" and account_sid and auth_token:
            body["provider"] = "twilio"
            body["twilioAccountSid"] = account_sid
            body["twilioAuthToken"] = auth_token
        return self._req("POST", "/phone-number", body)

    def list_assistants(self) -> list:
        return self._req("GET", "/assistant") or []

    def delete_assistant(self, assistant_id: str):
        return self._req("DELETE", f"/assistant/{assistant_id}")


# ─── Twilio client ─────────────────────────────────────────────────────────────
class TwilioClient:
    BASE = "https://api.twilio.com/2010-04-01"

    def __init__(self, account_sid: str, auth_token: str):
        self.sid = account_sid
        self.token = auth_token
        creds = base64.b64encode(f"{account_sid}:{auth_token}".encode()).decode()
        self.auth_header = f"Basic {creds}"

    def _req(self, method: str, path: str, form_data: dict = None) -> dict:
        url = f"{self.BASE}{path}"
        data = urllib.parse.urlencode(form_data).encode() if form_data else None
        req = urllib.request.Request(
            url, data=data, method=method,
            headers={
                "Authorization": self.auth_header,
                "Content-Type": "application/x-www-form-urlencoded",
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            err = e.read().decode()
            raise RuntimeError(f"Twilio {method} {path} → {e.code}: {err}")

    def find_available_number(self, area_code: str = None) -> str:
        params = "?VoiceEnabled=true&SmsEnabled=true&Limit=1"
        if area_code:
            params += f"&AreaCode={area_code}"
        result = self._req("GET", f"/Accounts/{self.sid}/AvailablePhoneNumbers/US/Local.json{params}")
        numbers = result.get("available_phone_numbers", [])
        if not numbers:
            raise RuntimeError("No available phone numbers found")
        return numbers[0]["phone_number"]

    def buy_number(self, phone_number: str) -> dict:
        return self._req("POST", f"/Accounts/{self.sid}/IncomingPhoneNumbers.json",
                         {"PhoneNumber": phone_number})

    def send_sms(self, from_number: str, to_number: str, body: str) -> dict:
        return self._req("POST", f"/Accounts/{self.sid}/Messages.json", {
            "From": from_number,
            "To": to_number,
            "Body": body,
        })


# ─── HubSpot client ────────────────────────────────────────────────────────────
class HubSpotClient:
    BASE = "https://api.hubapi.com"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def _req(self, method: str, path: str, body: dict = None) -> dict:
        url = f"{self.BASE}{path}"
        data = json.dumps(body).encode() if body else None
        req = urllib.request.Request(
            url, data=data, method=method,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            err = e.read().decode()
            raise RuntimeError(f"HubSpot {method} {path} → {e.code}: {err}")

    def upsert_contact(self, phone: str, name: str = None) -> str:
        """Create or update a contact by phone. Returns contact ID."""
        props: dict = {"phone": phone, "hs_lead_status": "NEW"}
        if name:
            props["firstname"] = name
        try:
            result = self._req("POST", "/crm/v3/objects/contacts", {"properties": props})
            return result["id"]
        except RuntimeError as e:
            if "409" in str(e):
                # Already exists — search for it
                search = self._req("POST", "/crm/v3/objects/contacts/search", {
                    "filterGroups": [{"filters": [{"propertyName": "phone", "operator": "EQ", "value": phone}]}],
                    "limit": 1
                })
                results = search.get("results", [])
                if results:
                    return results[0]["id"]
            raise

    def log_call_note(self, contact_id: str, note_body: str) -> dict:
        ts = int(time.time() * 1000)
        note = self._req("POST", "/crm/v3/objects/notes", {
            "properties": {
                "hs_note_body": note_body,
                "hs_timestamp": str(ts),
            }
        })
        # Associate note with contact
        note_id = note["id"]
        self._req("PUT", f"/crm/v3/objects/notes/{note_id}/associations/contacts/{contact_id}/202", {})
        return note


# ─── Web scraping (3-tier cascade) ────────────────────────────────────────────
def scrape_site(url: str) -> str:
    try:
        from scrapling import Fetcher, StealthyFetcher, DynamicFetcher
    except ImportError:
        print("❌ Scrapling not installed. Run: pip install scrapling")
        sys.exit(1)

    print(f"  🌐 Scraping {url}...")
    for tier, label, fn in [
        (1, "plain HTTP",   lambda: Fetcher().get(url, timeout=15, follow_redirects=True)),
        (2, "stealth mode", lambda: StealthyFetcher().fetch(url, timeout=30, headless=True)),
        (3, "full JS",      lambda: DynamicFetcher().fetch(url, timeout=45, headless=True)),
    ]:
        try:
            print(f"  Tier {tier}: {label}...")
            page = fn()
            content = str(getattr(page, "markdown", None) or page or "")
            if len(content) > 200:
                print(f"  ✅ Got {len(content):,} chars")
                return content
        except Exception as e:
            print(f"  Tier {tier} failed: {e}")

    return f"Business website: {url}\n\nPlease answer caller questions accurately."


def build_system_prompt(name: str, kb_content: str = "") -> str:
    return f"""You are a friendly, professional AI receptionist for {name}.

Your role:
- Answer caller questions warmly and accurately
- Provide information about the business (hours, location, services, pricing)
- Help callers find what they need
- Take messages when appropriate
- Transfer to a human when the caller requests it or when you cannot help

Always be concise, warm, and honest. Never guess — say "I don't have that information."

Business Information:
{kb_content[:4000]}
""".strip()


# ─── State ────────────────────────────────────────────────────────────────────
STATE_FILE = Path.home() / ".flowconcierge" / "assistants.json"


def load_state() -> dict:
    STATE_FILE.parent.mkdir(exist_ok=True)
    return json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {}


def save_state(state: dict):
    STATE_FILE.parent.mkdir(exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


# ─── Webhook server ────────────────────────────────────────────────────────────
def make_webhook_handler(hubspot_key: str, twilio_sid: str, twilio_token: str,
                          twilio_from: str, sms_followup: bool, business_name: str):
    hs = HubSpotClient(hubspot_key) if hubspot_key else None
    tw = TwilioClient(twilio_sid, twilio_token) if (twilio_sid and twilio_token) else None

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass  # suppress default access log

        def do_POST(self):
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)
            self.send_response(200)
            self.end_headers()

            try:
                payload = json.loads(raw)
            except Exception:
                return

            msg_type = payload.get("message", {}).get("type", "")
            if msg_type != "end-of-call-report":
                return

            msg = payload.get("message", {})
            caller_phone = msg.get("call", {}).get("customer", {}).get("number", "")
            summary = msg.get("analysis", {}).get("summary", "")
            transcript = msg.get("transcript", "")

            print(f"\n📞 Call ended — {caller_phone or 'unknown caller'}")
            if summary:
                print(f"   Summary: {summary[:120]}...")

            # HubSpot logging
            if hs and caller_phone:
                try:
                    contact_id = hs.upsert_contact(caller_phone)
                    note_body = f"FlowConcierge call — {business_name}\n\nSummary: {summary}\n\nTranscript:\n{transcript[:2000]}"
                    hs.log_call_note(contact_id, note_body)
                    print(f"   ✅ Logged to HubSpot (contact {contact_id})")
                except Exception as e:
                    print(f"   ⚠️  HubSpot error: {e}")

            # SMS follow-up
            if sms_followup and tw and caller_phone and twilio_from:
                try:
                    one_liner = summary.split(".")[0] if summary else "Thanks for calling"
                    sms_body = f"Thanks for calling {business_name}! {one_liner}. Reply with any questions."
                    tw.send_sms(twilio_from, caller_phone, sms_body)
                    print(f"   ✅ SMS sent to {caller_phone}")
                except Exception as e:
                    print(f"   ⚠️  SMS error: {e}")

    return Handler


# ─── Commands ──────────────────────────────────────────────────────────────────
def cmd_setup(args):
    vapi_key = args.vapi_key or os.environ.get("VAPI_API_KEY")
    if not vapi_key:
        print("❌ VAPI API key required. Set VAPI_API_KEY or pass --vapi-key")
        sys.exit(1)

    vapi = VAPIClient(vapi_key)
    tw = TwilioClient(args.twilio_sid, args.twilio_token) if (args.twilio_sid and args.twilio_token) else None

    # Knowledge base
    if args.kb:
        kb_path = Path(args.kb)
        kb_content = kb_path.read_text()
        business_name = args.name or kb_path.stem.replace("-", " ").title()
        print(f"📄 Using KB: {kb_path} ({len(kb_content):,} chars)")
    elif args.url:
        kb_content = scrape_site(args.url)
        business_name = args.name or args.url.split("//")[-1].split("/")[0].replace("www.", "").split(".")[0].title()
    else:
        print("❌ Provide a URL or --kb file")
        sys.exit(1)

    print(f"\n🦞 Setting up FlowConcierge for: {business_name}")

    # Upload KB
    print("\n📚 Uploading knowledge base to VAPI...")
    kb_id = vapi.create_knowledge_base(business_name, kb_content)
    print(f"   ✅ KB: {kb_id}")

    # Create assistant
    print("\n🤖 Creating voice assistant...")
    assistant = vapi.create_assistant(
        name=business_name,
        system_prompt=build_system_prompt(business_name, kb_content),
        kb_id=kb_id,
        language=args.lang,
        webhook_url=args.webhook_url,
    )
    assistant_id = assistant["id"]
    print(f"   ✅ Assistant: {assistant_id}")

    # Phone number
    phone_number = args.phone
    if not phone_number and tw:
        print("\n📞 Buying a Twilio phone number...")
        phone_number = tw.find_available_number(args.area_code)
        bought = tw.buy_number(phone_number)
        print(f"   ✅ Purchased: {phone_number}")

    if phone_number:
        print(f"\n🔗 Connecting {phone_number} to assistant...")
        vapi.connect_phone_number(
            phone_number, assistant_id,
            provider="twilio" if tw else "vapi",
            account_sid=args.twilio_sid,
            auth_token=args.twilio_token,
        )
        print(f"   ✅ Connected!")

    # Save state
    state = load_state()
    state[assistant_id] = {
        "name": business_name,
        "created": datetime.now().isoformat(),
        "kb_id": kb_id,
        "phone": phone_number,
        "url": getattr(args, "url", None),
    }
    save_state(state)

    print(f"""
{'='*52}
✅  FlowConcierge is live for {business_name}!

    Assistant ID:    {assistant_id}
    Knowledge Base:  {kb_id}
    Phone number:    {phone_number or 'not connected'}

Next: start the webhook to log calls to HubSpot:
    flowconcierge webhook --hubspot-key <KEY> --sms-followup
{'='*52}
""")


def cmd_webhook(args):
    port = args.port
    print(f"🦞 FlowConcierge webhook server starting on port {port}...")
    print(f"   HubSpot CRM: {'✅' if args.hubspot_key else '❌ (no key)'}")
    print(f"   SMS follow-up: {'✅' if args.sms_followup else '❌'}")
    print(f"   Business: {args.business_name or '(auto from call)'}")
    print(f"\nListening for VAPI call events at http://localhost:{port}")
    print("Point your VAPI assistant's serverUrl here (use ngrok for public URL).\n")

    handler = make_webhook_handler(
        hubspot_key=args.hubspot_key or os.environ.get("HUBSPOT_API_KEY", ""),
        twilio_sid=args.twilio_sid or os.environ.get("TWILIO_ACCOUNT_SID", ""),
        twilio_token=args.twilio_token or os.environ.get("TWILIO_AUTH_TOKEN", ""),
        twilio_from=args.twilio_from or os.environ.get("TWILIO_FROM_NUMBER", ""),
        sms_followup=args.sms_followup,
        business_name=args.business_name or "the business",
    )
    server = HTTPServer(("0.0.0.0", port), handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nWebhook server stopped.")


def cmd_list(args):
    vapi_key = args.vapi_key or os.environ.get("VAPI_API_KEY")
    if not vapi_key:
        print("❌ VAPI_API_KEY required")
        sys.exit(1)
    state = load_state()
    vapi = VAPIClient(vapi_key)
    assistants = [a for a in vapi.list_assistants() if "FlowConcierge" in a.get("name", "")]
    if not assistants:
        print("No FlowConcierge assistants found.")
        return
    print(f"\n🦞 FlowConcierge Assistants ({len(assistants)})\n")
    for a in assistants:
        local = state.get(a["id"], {})
        print(f"  {a['name']}")
        print(f"    ID:    {a['id']}")
        print(f"    Phone: {local.get('phone', 'none')}")
        print(f"    URL:   {local.get('url', 'N/A')}")
        print()


def cmd_delete(args):
    vapi_key = args.vapi_key or os.environ.get("VAPI_API_KEY")
    if not vapi_key:
        print("❌ VAPI_API_KEY required")
        sys.exit(1)
    VAPIClient(vapi_key).delete_assistant(args.assistant_id)
    state = load_state()
    state.pop(args.assistant_id, None)
    save_state(state)
    print(f"✅ Deleted {args.assistant_id}")


# ─── CLI ──────────────────────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser(
        description="FlowConcierge — AI phone receptionist for any business. Free.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="command")

    # setup
    s = sub.add_parser("setup", help="Create a FlowConcierge assistant")
    s.add_argument("url", nargs="?", help="Business website URL")
    s.add_argument("--kb", help="Existing knowledge base file")
    s.add_argument("--name", help="Business name")
    s.add_argument("--lang", default="en")
    s.add_argument("--vapi-key")
    s.add_argument("--twilio-sid")
    s.add_argument("--twilio-token")
    s.add_argument("--phone", help="Existing phone number to connect")
    s.add_argument("--area-code", help="Preferred area code for auto-bought number")
    s.add_argument("--webhook-url", help="VAPI server URL for call events")

    # webhook
    w = sub.add_parser("webhook", help="Start call event webhook server")
    w.add_argument("--port", type=int, default=8080)
    w.add_argument("--hubspot-key")
    w.add_argument("--twilio-sid")
    w.add_argument("--twilio-token")
    w.add_argument("--twilio-from", help="Your Twilio number for SMS")
    w.add_argument("--sms-followup", action="store_true")
    w.add_argument("--business-name")

    # list
    ls = sub.add_parser("list", help="List active assistants")
    ls.add_argument("--vapi-key")

    # delete
    d = sub.add_parser("delete", help="Delete an assistant")
    d.add_argument("assistant_id")
    d.add_argument("--vapi-key")

    args = p.parse_args()
    cmds = {"setup": cmd_setup, "webhook": cmd_webhook, "list": cmd_list, "delete": cmd_delete}
    if args.command in cmds:
        cmds[args.command](args)
    else:
        p.print_help()


if __name__ == "__main__":
    main()
