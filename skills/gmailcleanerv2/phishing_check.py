"""
phishing_check.py — Detección local de phishing (sin IA, sin tokens).

Uso: python3 phishing_check.py --emails-file emails.json
"""
import re, json, argparse

SHORTENERS = {"bit.ly","tinyurl.com","t.co","goo.gl","ow.ly","buff.ly","is.gd","cutt.ly"}
SPOOFED    = {"paypal":"paypa1","google":"g00gle","amazon":"amaz0n","apple":"app1e",
              "microsoft":"micros0ft","netflix":"netfl1x"}
URGENCY    = ["urgent","suspended","immediately","verify","limited time","click here",
              "urgente","suspendida","inmediatamente","verifica","haz clic"]
CREDS      = ["password","contraseña","credit card","tarjeta","cuenta bancaria","login","pin","clave"]
DANGER_EXT = {".exe",".bat",".js",".vbs",".ps1",".scr"}

def check(email):
    indicators=[]; body=email.get("cuerpo","").lower(); rem=email.get("remitente","").lower()
    for url in re.findall(r'https?://[^\s<>"]+', body):
        domain=re.sub(r'^https?://','',url).split('/')[0]
        if domain in SHORTENERS: indicators.append(f"URL acortada: {domain}")
    for legit,fake in SPOOFED.items():
        if fake in rem: indicators.append(f"Remitente spoofed: {fake} (parece {legit})")
        if legit in body and fake in body: indicators.append(f"Dominio falso en cuerpo: {fake}")
    if any(kw in body for kw in URGENCY) and any(kw in body for kw in CREDS):
        indicators.append("Urgencia + solicitud credenciales")
    for adj in email.get("adjuntos",[]):
        if any(adj.get("filename","").lower().endswith(ext) for ext in DANGER_EXT):
            indicators.append(f"Adjunto peligroso: {adj['filename']}")
    return {"id":email.get("id"),"asunto":email.get("asunto"),"remitente":email.get("remitente"),
            "es_phishing":len(indicators)>0,"indicadores":indicators}

if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--emails-file",required=True); a=p.parse_args()
    emails=json.load(open(a.emails_file)); results=[check(e) for e in emails]
    flagged=[r for r in results if r["es_phishing"]]
    print(f"⚠️  {len(flagged)}/{len(emails)} correos con indicadores de phishing\n")
    for r in flagged:
        print(f"  🚨 {r['asunto'][:60]} — {r['remitente'][:40]}")
        for ind in r["indicadores"]: print(f"     → {ind}")
    print(json.dumps(results,ensure_ascii=False,indent=2))
