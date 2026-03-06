"""
imap_fetch.py — Lee correos vía IMAP genérico (Outlook, Yahoo, servidor propio).
Variables: IMAP_USER, IMAP_PASSWORD

Uso:
  python3 imap_fetch.py --host imap.outlook.com --folder INBOX --max 50
  python3 imap_fetch.py --host imap.gmail.com   --folder SPAM  --max 30
"""
import imaplib, email, json, argparse, os
from email.header import decode_header

def _str(s):
    if not s: return ""
    return " ".join((b.decode(enc or "utf-8",errors="ignore") if isinstance(b,bytes) else b)
                    for b,enc in decode_header(s))

def _body(msg):
    if msg.is_multipart():
        for p in msg.walk():
            if p.get_content_type()=="text/plain":
                pl=p.get_payload(decode=True)
                if pl: return pl.decode(p.get_content_charset() or "utf-8",errors="ignore")[:3000]
    pl=msg.get_payload(decode=True)
    return pl.decode(msg.get_content_charset() or "utf-8",errors="ignore")[:3000] if pl else ""

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--host",     required=True)
    p.add_argument("--user",     default=os.environ.get("IMAP_USER"))
    p.add_argument("--password", default=os.environ.get("IMAP_PASSWORD"))
    p.add_argument("--folder",   default="INBOX")
    p.add_argument("--max",      type=int, default=50)
    a=p.parse_args()

    mail=imaplib.IMAP4_SSL(a.host)
    mail.login(a.user, a.password)
    mail.select(a.folder)
    _,data=mail.search(None,"ALL")
    ids=data[0].split()[-a.max:]
    emails=[]
    for eid in reversed(ids):
        _,md=mail.fetch(eid,"(RFC822)")
        msg=email.message_from_bytes(md[0][1])
        emails.append({"id":eid.decode(),"remitente":_str(msg.get("From","")),
                       "destinatario":_str(msg.get("To","")),"asunto":_str(msg.get("Subject","(sin asunto)")),
                       "fecha":msg.get("Date",""),"cuerpo":_body(msg),"label":a.folder})
    mail.logout()
    print(json.dumps(emails, ensure_ascii=False, indent=2))
