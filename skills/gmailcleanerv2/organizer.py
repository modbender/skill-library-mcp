"""
organizer.py — Operaciones de organización sobre correos de Gmail.
Mejora de actions.py con: batch por query, audit log, undo, move.

Uso:
  python3 organizer.py --action trash   --query "in:spam older_than:7d" --max 500
  python3 organizer.py --action archive --query "in:inbox older_than:180d"
  python3 organizer.py --action read    --ids "ID1,ID2"
  python3 organizer.py --action move    --move-to "Facturas" --query "from:billing@"
  python3 organizer.py --undo
"""
import sys, json, argparse
from datetime import datetime
from googleapiclient.discovery import build
from auth import authenticate

AUDIT = "email_audit.log"

def _log(action, count, detail):
    line=f"{datetime.now().strftime('%Y-%m-%d %H:%M')} | {action:<8} | {count:>5} correos | {detail}\n"
    open(AUDIT,"a").write(line); print(f"  ✓ {line.strip()}", file=sys.stderr)

def _svc(): return build("gmail","v1",credentials=authenticate())

def _ids_from_query(svc, q, maxr):
    res=svc.users().messages().list(userId="me",q=q,maxResults=maxr).execute()
    return [m["id"] for m in res.get("messages",[])]

MODS = {
    "read":   {"removeLabelIds":["UNREAD"]},
    "unread": {"addLabelIds":["UNREAD"]},
    "star":   {"addLabelIds":["STARRED"]},
    "unstar": {"removeLabelIds":["STARRED"]},
}

def do_action(svc, ids, action, move_to=None):
    ok=0
    for mid in ids:
        try:
            if   action=="trash":   svc.users().messages().trash(userId="me",id=mid).execute()
            elif action=="untrash": svc.users().messages().untrash(userId="me",id=mid).execute()
            elif action=="archive": svc.users().messages().modify(userId="me",id=mid,
                                        body={"removeLabelIds":["INBOX"]}).execute()
            elif action=="move" and move_to:
                                    svc.users().messages().modify(userId="me",id=mid,
                                        body={"addLabelIds":[move_to],"removeLabelIds":["INBOX"]}).execute()
            elif action=="delete":  svc.users().messages().delete(userId="me",id=mid).execute()
            elif action in MODS:    svc.users().messages().modify(userId="me",id=mid,body=MODS[action]).execute()
            ok+=1
        except Exception as e: print(f"  ✗ {mid}: {e}", file=sys.stderr)
    return ok

def undo_last():
    if not open(AUDIT).read().strip(): print("Audit log vacío."); return
    last=open(AUDIT).readlines()[-1].strip()
    print(f"Última acción: {last}")
    print("Sugerencia para deshacer TRASH: python3 organizer.py --action untrash --query 'in:trash newer_than:1d'")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--action",choices=["trash","untrash","archive","read","unread","star","unstar","move","delete"])
    p.add_argument("--ids");  p.add_argument("--query"); p.add_argument("--move-to")
    p.add_argument("--max",type=int,default=500); p.add_argument("--undo",action="store_true")
    a=p.parse_args()
    if a.undo: undo_last(); sys.exit(0)
    svc=_svc()
    ids=[i.strip() for i in a.ids.split(",")] if a.ids else \
        _ids_from_query(svc,a.query,a.max) if a.query else []
    if not ids: print("❌ Proporciona --ids o --query"); sys.exit(1)
    print(f"📋 {len(ids)} correos — {a.action}", file=sys.stderr)
    ok=do_action(svc,ids,a.action,a.move_to)
    _log(a.action.upper(),ok,a.query or f"{len(ids)} IDs")
    print(f"✅ {ok}/{len(ids)} procesados.")
