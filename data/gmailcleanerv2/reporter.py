"""
scripts/reporter.py — Genera informes de actividad de correo.
Basado en reporter.py original + estadísticas de spam + exportación Markdown.
"""
import os, sys, json, argparse
from datetime import datetime
from collections import defaultdict
from googleapiclient.discovery import build
from auth import authenticate

AUDIT_LOG   = os.path.expanduser("~/.openclaw/workspace/email_audit.log")
PROMPTS_LOG = os.path.expanduser("~/.openclaw/workspace/prompts_log.md")


def _svc(): return build("gmail","v1",credentials=authenticate())


def _search(svc, query, max_results=200):
    res  = svc.users().messages().list(userId="me",q=query,maxResults=max_results).execute()
    msgs = res.get("messages",[])
    result = []
    for ref in msgs:
        msg = svc.users().messages().get(userId="me",id=ref["id"],format="metadata",
              metadataHeaders=["From","Subject","Date"]).execute()
        h = {x["name"]:x["value"] for x in msg["payload"].get("headers",[])}
        result.append({"id":ref["id"],"remitente":h.get("From",""),"asunto":h.get("Subject",""),"fecha":h.get("Date","")[:16]})
    return result


def generate_report(svc, period="day"):
    n = 1 if period=="day" else 7
    print(f"\n{'═'*50}", file=sys.stderr)
    print(f"📬 RESUMEN {'HOY' if period=='day' else 'SEMANA'} — {datetime.now().strftime('%d %b %Y')}")
    print('═'*50)

    inbox = _search(svc, f"in:inbox newer_than:{n}d", 200)
    spam  = _search(svc, f"in:spam newer_than:{n}d",  200)
    sent  = _search(svc, f"in:sent newer_than:{n}d",  100)
    pend  = _search(svc, f"in:sent older_than:5d newer_than:30d", 50)

    print(f"Recibidos: {len(inbox):>3}  │  Enviados: {len(sent):>3}  │  Pendientes: {len(pend):>3}")
    print(f"Spam:      {len(spam):>3}")

    # Top remitentes
    if inbox:
        cnt = defaultdict(int)
        for e in inbox: cnt[e["remitente"]] += 1
        top = sorted(cnt.items(), key=lambda x:-x[1])[:5]
        print("\nTop remitentes:")
        for i,(rem,n_) in enumerate(top,1): print(f"  {i}. {rem[:50]} ({n_})")

    # Sin respuesta
    if pend:
        print(f"\nPendientes de respuesta ({len(pend)}):")
        for e in pend[:5]:
            print(f"  • {e['remitente'][:35]} — \"{e['asunto'][:40]}\"")

    # Spam top senders
    if spam:
        cnt = defaultdict(int)
        for e in spam: cnt[e["remitente"]] += 1
        top_spam = sorted(cnt.items(), key=lambda x:-x[1])[:3]
        print(f"\n🗑️  Top spam remitentes:")
        for rem,n_ in top_spam: print(f"  • {rem[:50]} ({n_})")

    print('═'*50)
    return {"inbox":inbox,"spam":spam,"sent":sent,"pending":pend}


def save_report_md(data, period, output_path):
    inbox,spam,sent,pend = data["inbox"],data["spam"],data["sent"],data["pending"]
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# 📬 Informe de Correo — {'Hoy' if period=='day' else 'Semana'} ({fecha})\n",
        f"| Categoría | Total |",
        f"|-----------|-------|",
        f"| 📥 Recibidos | {len(inbox)} |",
        f"| 📤 Enviados | {len(sent)} |",
        f"| 🗑️ Spam | {len(spam)} |",
        f"| 📋 Sin respuesta | {len(pend)} |\n",
    ]
    if pend:
        lines += ["\n## Pendientes de respuesta\n"]
        for e in pend: lines.append(f"- **{e['remitente']}** — {e['asunto']}")
    if spam:
        lines += ["\n## Top remitentes spam\n"]
        cnt = defaultdict(int)
        for e in spam: cnt[e["remitente"]] += 1
        for rem,n_ in sorted(cnt.items(),key=lambda x:-x[1])[:10]:
            lines.append(f"- {rem} ({n_})")
    with open(output_path,"w",encoding="utf-8") as f: f.write("\n".join(lines))
    print(f"💾 Informe guardado en: {output_path}")


def show_audit(last=20):
    if not os.path.exists(AUDIT_LOG):
        print("Audit log vacío."); return
    lines = open(AUDIT_LOG).readlines()
    print(f"\n📋 Últimas {min(last,len(lines))} acciones:")
    for line in lines[-last:]: print(f"  {line.strip()}")


def undo_last():
    if not os.path.exists(AUDIT_LOG):
        print("Audit log vacío."); return
    lines = [l for l in open(AUDIT_LOG).readlines() if l.strip()]
    if not lines: print("Nada que deshacer."); return
    last = lines[-1]
    print(f"Última acción: {last.strip()}")
    if "TRASH" in last:
        print("Para restaurar, busca en papelera:")
        print("  gog gmail search 'in:trash newer_than:1d' --max 100 --json --no-input")
        print("  Luego: gog gmail untrash <ID>")
    elif "MOVE" in last or "LABEL" in last:
        print("Para deshacer un MOVE, usa email-organizer con la etiqueta origen.")
    else:
        print("Esta acción puede no ser reversible directamente.")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--period", choices=["day","week"], default="day")
    p.add_argument("--spam-only", action="store_true")
    p.add_argument("--output", help="Guardar como .md")
    p.add_argument("--audit", action="store_true")
    p.add_argument("--last", type=int, default=20)
    p.add_argument("--undo", action="store_true")
    a = p.parse_args()

    if a.audit:   show_audit(a.last)
    elif a.undo:  undo_last()
    else:
        svc  = _svc()
        data = generate_report(svc, a.period)
        if a.output: save_report_md(data, a.period, a.output)
