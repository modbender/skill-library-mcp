"""
rules_engine.py — Motor de reglas de archivo automático para Gmail.
Guarda reglas en rules.json y las aplica a lotes de correos.

Uso:
  python3 rules_engine.py --create
  python3 rules_engine.py --list
  python3 rules_engine.py --apply --emails-file emails.json
"""
import json, os, argparse, uuid
from googleapiclient.discovery import build
from auth import authenticate

RULES = "rules.json"
def _load(): return json.load(open(RULES)) if os.path.exists(RULES) else []
def _save(r): json.dump(r,open(RULES,"w"),ensure_ascii=False,indent=2)

def matches(email, rule):
    rem=email.get("remitente","").lower(); asunto=email.get("asunto","").lower()
    c=rule.get("condiciones",{})
    return (any(kw.lower() in rem for kw in c.get("remitente_contiene",[])) or
            any(kw.lower() in asunto for kw in c.get("asunto_contiene",[])) or
            any(kw.lower() in rem+asunto+email.get("cuerpo","").lower() for kw in c.get("cualquier_campo",[])))

def apply_rules(emails):
    rules=[r for r in _load() if r.get("activa",True)]
    if not rules: print("Sin reglas activas."); return
    svc=build("gmail","v1",credentials=authenticate())
    n=0
    for email in emails:
        for rule in rules:
            if matches(email,rule):
                acc=rule.get("accion",{}); body={}
                if acc.get("mover_a"):    body["addLabelIds"]=[acc["mover_a"]]; body["removeLabelIds"]=["INBOX"]
                if acc.get("marcar_como")=="leído": body.setdefault("removeLabelIds",[]).append("UNREAD")
                if body:
                    svc.users().messages().modify(userId="me",id=email["id"],body=body).execute()
                    print(f"  ✓ [{rule['nombre']}] {email.get('asunto','')[:60]}")
                    n+=1; break
    print(f"\n✅ {n} correos procesados por reglas.")

def create_rule():
    print("=== Nueva regla ===")
    nombre=input("Nombre: "); rem=input("Remitente contiene (coma-sep, vacío para omitir): ")
    asunto=input("Asunto contiene (coma-sep, vacío para omitir): ")
    mover=input("Mover a carpeta: "); marcar=input("Marcar como (leído / vacío): ")
    rule={"id":f"rule_{uuid.uuid4().hex[:6]}","nombre":nombre,
          "condiciones":{"remitente_contiene":[k.strip() for k in rem.split(",") if k.strip()],
                         "asunto_contiene":[k.strip() for k in asunto.split(",") if k.strip()]},
          "accion":{"mover_a":mover,"marcar_como":marcar or None},"activa":True}
    rules=_load(); rules.append(rule); _save(rules)
    print(f"✅ Regla '{nombre}' guardada.")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--create",action="store_true"); p.add_argument("--apply",action="store_true")
    p.add_argument("--list",action="store_true");   p.add_argument("--emails-file")
    a=p.parse_args()
    if a.create:     create_rule()
    elif a.list:     print(json.dumps(_load(),ensure_ascii=False,indent=2))
    elif a.apply:    apply_rules(json.load(open(a.emails_file)))
