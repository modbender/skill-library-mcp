"""
responder.py — Genera borradores, envía correos, gestiona templates y follow-ups.
Basado en actions.py original (borrar_spam/guardar_prompts/crear_borradores) + mejoras.

Uso:
  python3 responder.py --action draft          --email-id <ID> [--thread-file thread.json]
  python3 responder.py --action create-draft   --to e@mail.com --subject "Re: X" --body-file draft.txt
  python3 responder.py --action send-draft     --draft-id <DRAFT_ID>
  python3 responder.py --action use-template   --template acuse_recibo --to e@mail.com
  python3 responder.py --action list-templates
  python3 responder.py --action followup-check --days 5
  python3 responder.py --action save-prompts   --emails-file analysis.json
"""
import os, sys, json, base64, argparse
from datetime import datetime
from email.mime.text import MIMEText
from googleapiclient.discovery import build
import anthropic
from auth import authenticate

MODEL     = os.environ.get("ANTHROPIC_MODEL","claude-sonnet-4-20250514")
TEMPLATES_FILE = "email_templates.json"
PROMPTS_FILE   = "prompts_detectados.md"

DEFAULT_TEMPLATES = {
    "acuse_recibo":         "Hola,\n\nGracias por tu mensaje. Lo revisaré y te responderé a la brevedad.\n\nSaludos,\n[Tu nombre]",
    "confirmacion_reunion": "Hola,\n\nConfirmo mi asistencia. Hasta entonces.\n\nSaludos,\n[Tu nombre]",
    "fuera_oficina":        "Gracias por tu mensaje. Estoy fuera de la oficina. Responderé a mi regreso.\n\nSaludos,\n[Tu nombre]",
    "solicitar_info":       "Hola,\n\nGracias por contactarme. ¿Podrías darme más detalles sobre el tema?\n\nQuedo atento,\n[Tu nombre]",
    "cotizacion_recibida":  "Hola,\n\nHemos recibido tu cotización y la analizaremos. Te contactaremos pronto.\n\nGracias,\n[Tu nombre]",
}

def _svc():    return build("gmail","v1",credentials=authenticate())
def _client(): return anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

def _get_templates():
    return json.load(open(TEMPLATES_FILE)) if os.path.exists(TEMPLATES_FILE) else DEFAULT_TEMPLATES

# ── Generar borrador con IA (basado en actions.py generar_borrador_respuesta) ──
def generar_borrador(email, hilo=None):
    ctx=""
    if hilo:
        ctx="\n\nHistorial del hilo:\n"+"\n---\n".join([
            f"De: {m.get('remitente','')}\n{m.get('cuerpo','')[:600]}" for m in hilo])
    resp=_client().messages.create(model=MODEL,max_tokens=500,messages=[{"role":"user","content":
        f"""Eres asistente de email profesional. Redacta respuesta concisa (máx 150 palabras).
Solo el cuerpo, sin asunto ni encabezados. Coincidir idioma y tono del hilo.{ctx}

Correo a responder:
De: {email.get('remitente','')}
Asunto: {email.get('asunto','')}
Mensaje: {email.get('cuerpo','')[:1000]}"""}])
    return resp.content[0].text.strip()

# ── Crear borrador en Gmail (basado en actions.py _crear_draft_gmail) ──
def crear_draft(svc, to, subject, body, reply_to_id=None):
    msg=MIMEText(body); msg["to"]=to
    msg["subject"]=subject if subject.startswith("Re:") else f"Re: {subject}"
    if reply_to_id: msg["In-Reply-To"]=reply_to_id; msg["References"]=reply_to_id
    raw=base64.urlsafe_b64encode(msg.as_bytes()).decode()
    draft=svc.users().drafts().create(userId="me",body={"message":{"raw":raw}}).execute()
    return draft["id"]

# ── Guardar prompts (basado en actions.py guardar_prompts) ──
def guardar_prompts(emails_con_prompts, ruta=PROMPTS_FILE):
    if not emails_con_prompts: print("ℹ️  No hay prompts."); return
    es_nuevo=not os.path.exists(ruta)
    with open(ruta,"a",encoding="utf-8") as f:
        if es_nuevo: f.write("# 🔍 Prompts Detectados en Correos\n\n")
        f.write(f"\n---\n## Sesión: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        for e in emails_con_prompts:
            f.write(f"### 📧 {e['asunto']}\n**De:** {e['remitente']}  \n**Fecha:** {e.get('fecha','')}  \n\n")
            f.write(f"**Prompt:**\n```\n{e.get('prompt_texto',e.get('cuerpo',''))[:500]}\n```\n\n")
    print(f"💾 {len(emails_con_prompts)} prompt/s → {ruta}")

# ── Borradores batch (basado en actions.py crear_borradores) ──
def crear_borradores_batch(svc, emails_importantes):
    creados=0
    print(f"\n✍️  Generando borradores para {len(emails_importantes)} correos...")
    for email in emails_importantes:
        try:
            cuerpo=generar_borrador(email)
            did=crear_draft(svc,email["remitente"],email["asunto"],cuerpo,email.get("id"))
            print(f"   ✓ {email['asunto'][:50]} (Draft: {did[:12]}...)")
            creados+=1
        except Exception as e: print(f"   ✗ {e}")
    print(f"  → {creados}/{len(emails_importantes)} borradores creados.")
    return creados

# ── Entry point ─────────────────────────────────────────────────
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--action",default="draft",
        choices=["draft","create-draft","send-draft","followup-check","list-templates","use-template","save-prompts"])
    p.add_argument("--email-id"); p.add_argument("--thread-file"); p.add_argument("--to")
    p.add_argument("--subject"); p.add_argument("--body-file"); p.add_argument("--reply-to")
    p.add_argument("--draft-id"); p.add_argument("--template"); p.add_argument("--days",type=int,default=5)
    p.add_argument("--emails-file")
    a=p.parse_args(); svc=_svc()

    if a.action=="list-templates":
        print(json.dumps(_get_templates(),ensure_ascii=False,indent=2))

    elif a.action=="followup-check":
        res=svc.users().messages().list(userId="me",
            q=f"in:sent older_than:{a.days}d newer_than:30d",maxResults=50).execute()
        for ref in res.get("messages",[])[:10]:
            msg=svc.users().messages().get(userId="me",id=ref["id"],format="metadata",
                metadataHeaders=["To","Subject"]).execute()
            h={x["name"]:x["value"] for x in msg["payload"].get("headers",[])}
            print(f"  • Para: {h.get('To','')[:40]}  |  {h.get('Subject','')[:50]}")

    elif a.action=="create-draft":
        body=open(a.body_file).read() if a.body_file else input("Cuerpo: ")
        did=crear_draft(svc,a.to,a.subject,body,a.reply_to)
        print(f"✅ Borrador creado (ID: {did})")

    elif a.action=="send-draft":
        print("⚠️  ¿Confirmas el envío? (s/n): ",end="")
        if input().strip().lower() in("s","si","sí"):
            result=svc.users().drafts().send(userId="me",body={"id":a.draft_id}).execute()
            print(f"✅ Enviado (ID: {result.get('id')})")
        else: print("Cancelado.")

    elif a.action=="use-template":
        t=_get_templates().get(a.template)
        if not t: print(f"❌ Plantilla '{a.template}' no encontrada"); sys.exit(1)
        did=crear_draft(svc,a.to,a.subject or "Respuesta",t)
        print(f"✅ Borrador con plantilla '{a.template}' (ID: {did})")

    elif a.action=="save-prompts":
        emails=json.load(open(a.emails_file))
        guardar_prompts([e for e in emails if e.get("tiene_prompt")])

    else:  # draft — generar y mostrar
        if not a.email_id: print("❌ --email-id requerido"); sys.exit(1)
        hilo=json.load(open(a.thread_file)).get("messages",[]) if a.thread_file else None
        msg=svc.users().messages().get(userId="me",id=a.email_id,format="full").execute()
        h={x["name"]:x["value"] for x in msg["payload"].get("headers",[])}
        import base64 as b64
        body=""
        if "parts" in msg["payload"]:
            for part in msg["payload"]["parts"]:
                if part.get("mimeType")=="text/plain":
                    d=part["body"].get("data","")
                    if d: body=b64.urlsafe_b64decode(d).decode("utf-8",errors="ignore"); break
        email={"id":a.email_id,"remitente":h.get("From",""),"asunto":h.get("Subject",""),"cuerpo":body[:1500]}
        borrador=generar_borrador(email,hilo)
        print(f"\n{'─'*60}\nPara: {email['remitente']}\nAsunto: Re: {email['asunto']}\n\n{borrador}\n{'─'*60}")
