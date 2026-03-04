"""fetch_thread.py — Lee un hilo completo de Gmail por threadId"""
import json, base64, argparse
from googleapiclient.discovery import build
from auth import authenticate

def _body(payload):
    if "parts" in payload:
        for p in payload["parts"]:
            if p.get("mimeType")=="text/plain":
                d=p["body"].get("data","")
                if d: return base64.urlsafe_b64decode(d).decode("utf-8",errors="ignore")
    d=payload.get("body",{}).get("data","")
    return base64.urlsafe_b64decode(d).decode("utf-8",errors="ignore").strip() if d else ""

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--thread-id", required=True)
    tid = p.parse_args().thread_id
    svc = build("gmail","v1",credentials=authenticate())
    thread = svc.users().threads().get(userId="me",id=tid,format="full").execute()
    msgs = []
    for msg in thread.get("messages",[]):
        h = {x["name"]:x["value"] for x in msg["payload"].get("headers",[])}
        msgs.append({"id":msg["id"],"remitente":h.get("From",""),"destinatario":h.get("To",""),
                     "asunto":h.get("Subject",""),"fecha":h.get("Date",""),
                     "cuerpo":_body(msg["payload"])[:3000]})
    print(json.dumps({"threadId":tid,"messages":msgs}, ensure_ascii=False, indent=2))
