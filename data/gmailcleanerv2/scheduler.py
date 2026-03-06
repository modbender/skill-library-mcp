"""
scripts/scheduler.py — Agente de correo periódico (fallback sin OpenClaw).
Orquesta: leer → analizar → accionar → notificar.
Basado en agent.py original con soporte --once y --auto.
"""
import os, sys, time, argparse
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from fetch_emails import fetch_emails
from analyzer    import analyze_all
from organizer   import do_action, _svc

NOTIFY_THRESHOLD = int(os.environ.get("NOTIFY_THRESHOLD","7"))


def run_once(auto=False, action_filter=None):
    print(f"\n🚀 [{datetime.now().strftime('%H:%M')}] Agente de correo iniciando...")

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY no configurada."); sys.exit(1)
    if not os.environ.get("GOG_ACCOUNT") and not os.path.exists("token.json"):
        print("❌ Configurar GOG_ACCOUNT o ejecutar python3 auth.py"); sys.exit(1)

    svc = _svc()

    # Solo limpieza de spam
    if action_filter == "spam-cleanup":
        import subprocess
        result = subprocess.run(
            ["gog","gmail","search","in:spam older_than:7d","--max","500","--json","--no-input"],
            capture_output=True, text=True)
        import json as _json
        try:
            spam_ids = [m["id"] for m in _json.loads(result.stdout or "[]")]
        except Exception:
            spam_ids = []
        if spam_ids:
            print(f"🗑️  {len(spam_ids)} correos de spam encontrados.")
            if auto or input("¿Eliminar? (s/n): ").lower() in ("s","si","sí"):
                do_action(svc, spam_ids, "trash")
                print(f"✅ {len(spam_ids)} correos movidos a papelera.")
        else:
            print("✅ Spam vacío.")
        return

    # Flujo completo
    inbox = fetch_emails("INBOX", max_results=50)
    spam  = fetch_emails("SPAM",  max_results=50)
    all_emails = inbox + spam

    if not all_emails:
        print("✅ No hay correos nuevos."); return

    print(f"📬 {len(all_emails)} correos a analizar...")
    results = analyze_all(all_emails)

    spam_emails  = [e for e in results if e.get("es_spam")]
    important    = [e for e in results if e.get("prioridad",0) >= NOTIFY_THRESHOLD]
    with_prompts = [e for e in results if e.get("tiene_prompt")]
    phishing     = [e for e in results if e.get("es_phishing")]

    # Resumen
    print(f"\n📊 Resultados:")
    print(f"  🔴 Críticos (≥{NOTIFY_THRESHOLD}): {len(important)}")
    print(f"  🗑️  Spam:     {len(spam_emails)}")
    print(f"  🔍 Prompts:  {len(with_prompts)}")
    print(f"  ⚠️  Phishing: {len(phishing)}")

    if important:
        print("\n⭐ Correos importantes:")
        for e in important:
            print(f"  [{e.get('prioridad',0)}/10] {e.get('remitente','')[:40]} — {e.get('asunto','')[:50]}")

    if phishing:
        print("\n🚨 PHISHING detectado:")
        for e in phishing:
            print(f"  ⚠️  {e.get('remitente','')} — {e.get('asunto','')}")

    # Acciones con confirmación
    if spam_emails:
        msg = f"Borrar {len(spam_emails)} correos de spam?"
        if auto or input(f"\n❓ {msg} (s/n): ").lower() in ("s","si","sí"):
            ids = [e["id"] for e in spam_emails]
            do_action(svc, ids, "trash")

    if with_prompts:
        from responder import guardar_prompts
        msg = f"Guardar {len(with_prompts)} prompt/s detectados?"
        if auto or input(f"\n❓ {msg} (s/n): ").lower() in ("s","si","sí"):
            guardar_prompts(with_prompts)

    print("\n✅ Agente finalizado.")


def run_loop(interval_min=30, notify_threshold=7):
    global NOTIFY_THRESHOLD
    NOTIFY_THRESHOLD = notify_threshold
    print(f"⏰ Loop activo — cada {interval_min} min. Ctrl+C para detener.")
    while True:
        try:
            run_once(auto=False)
            print(f"😴 Próxima revisión en {interval_min} min...")
            time.sleep(interval_min * 60)
        except KeyboardInterrupt:
            print("\n👋 Loop detenido."); break
        except Exception as e:
            print(f"⚠️  Error: {e}. Reintentando en {interval_min} min...")
            time.sleep(interval_min * 60)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--once",             action="store_true", help="Ejecutar una vez")
    p.add_argument("--auto",             action="store_true", help="Sin confirmaciones ⚠️")
    p.add_argument("--action",           default=None,        help="spam-cleanup / full")
    p.add_argument("--interval",         type=int, default=30,help="Minutos entre revisiones")
    p.add_argument("--notify-threshold", type=int, default=7, help="Prioridad mínima para notificar")
    a = p.parse_args()

    if a.once: run_once(auto=a.auto, action_filter=a.action)
    else:      run_loop(interval_min=a.interval, notify_threshold=a.notify_threshold)
