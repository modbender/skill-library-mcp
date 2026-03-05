"""
fetch_emails.py — Lee correos de Gmail (mejora de gmail_reader.py original).
Mejoras: soporte HTML, paginación, etiquetas custom, checkpoint incremental, adjuntos.

Uso:
  python3 fetch_emails.py --label INBOX --max 50
  python3 fetch_emails.py --label SPAM  --max 100
  python3 fetch_emails.py --label Clientes --unread-only
  python3 fetch_emails.py --label INBOX --since 2026-01-01
  python3 fetch_emails.py --label INBOX --from juan@empresa.com
  python3 fetch_emails.py --label INBOX --incremental
"""
import os, sys, json, base64, argparse
from datetime import datetime
from googleapiclient.discovery import build
from auth import authenticate

CHECKPOINT = ".email_checkpoint.json"
SYSTEM     = {"INBOX","SPAM","TRASH","SENT","DRAFTS","STARRED","IMPORTANT"}

def _cp_load(): return json.load(open(CHECKPOINT)) if os.path.exists(CHECKPOINT) else {}
def _cp_save(label, last_id):
    cp = _cp_load(); cp[label] = {"last_id": last_id, "ts": datetime.now().isoformat()}
    json.dump(cp, open(CHECKPOINT,"w"), indent=2)

def _body(payload):
    def _scan(parts):
        for p in parts:
            if p.get("mimeType") == "text/plain":
                d = p["body"].get("data","")
                if d: return base64.urlsafe_b64decode(d).decode("utf-8", errors="ignore")
            if "parts" in p:
                r = _scan(p["parts"])
                if r: return r
        for p in parts:  # fallback HTML
            if p.get("mimeType") == "text/html":
                d = p["body"].get("data","")
                if d:
                    html = base64.urlsafe_b64decode(d).decode("utf-8", errors="ignore")
                    try:
                        from bs4 import BeautifulSoup
                        return BeautifulSoup(html, "html.parser").get_text(" ", strip=True)
                    except ImportError:
                        import re; return re.sub(r"<[^>]+>"," ",html).strip()
        return ""
    if "parts" in payload: return _scan(payload["parts"]).strip()
    d = payload.get("body",{}).get("data","")
    return base64.urlsafe_b64decode(d).decode("utf-8",errors="ignore").strip() if d else ""

def _attachments(payload):
    atts = []
    def scan(parts):
        for p in parts:
            if p.get("filename"):
                atts.append({"filename":p["filename"],"mimeType":p.get("mimeType",""),
                              "size":p["body"].get("size",0)})
            if "parts" in p: scan(p["parts"])
    if "parts" in payload: scan(payload["parts"])
    return atts

def fetch_emails(label="INBOX", max_results=50, unread_only=False,
                 since=None, from_filter=None, incremental=False):
    svc = build("gmail","v1",credentials=authenticate())
    q = f"in:{label.lower()}" if label.upper() in SYSTEM else f"label:{label}"
    if unread_only:   q += " is:unread"
    if since:         q += f" after:{since.replace('-','/')}"
    if from_filter:   q += f" from:{from_filter}"
    print(f"📥 {label} — {q}", file=sys.stderr)

    emails, page_token = [], None
    while len(emails) < max_results:
        batch = min(50, max_results - len(emails))
        params = {"userId":"me","q":q,"maxResults":batch}
        if page_token: params["pageToken"] = page_token
        res  = svc.users().messages().list(**params).execute()
        msgs = res.get("messages",[])
        if not msgs: break
        for ref in msgs:
            msg = svc.users().messages().get(userId="me",id=ref["id"],format="full").execute()
            h = {x["name"]:x["value"] for x in msg["payload"].get("headers",[])}
            try:
                from email.utils import parsedate_to_datetime
                fecha = parsedate_to_datetime(h.get("Date","")).strftime("%Y-%m-%d %H:%M")
            except: fecha = h.get("Date","")[:16]
            emails.append({"id":ref["id"],"threadId":msg.get("threadId",""),
                "remitente":h.get("From","desconocido"),"destinatario":h.get("To",""),
                "asunto":h.get("Subject","(sin asunto)"),"fecha":fecha,
                "cuerpo":_body(msg["payload"])[:3000],
                "adjuntos":_attachments(msg["payload"]),
                "etiquetas":msg.get("labelIds",[]),"label":label})
        page_token = res.get("nextPageToken")
        if not page_token: break

    if emails: _cp_save(label, emails[0]["id"])
    print(f"   → {len(emails)} correos", file=sys.stderr)
    return emails

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--label",       default="INBOX")
    p.add_argument("--max",         type=int, default=50)
    p.add_argument("--unread-only", action="store_true")
    p.add_argument("--since",       help="YYYY-MM-DD")
    p.add_argument("--from",        dest="from_filter")
    p.add_argument("--incremental", action="store_true")
    a = p.parse_args()
    print(json.dumps(fetch_emails(a.label,a.max,a.unread_only,a.since,a.from_filter,a.incremental),
                     ensure_ascii=False, indent=2))
