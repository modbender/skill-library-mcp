#!/usr/bin/env python3
"""
🚨 ORef Alerts - OpenClaw Native
מערכת התרעות פיקוד העורף - ניהול מלא דרך OpenClaw בלבד

ללא תלות ב-Home Assistant, ללא wacli נפרד.
הכל דרך OpenClaw CLI:
  - openclaw message → WhatsApp
  - openclaw tts     → הכרזה קולית
"""

import requests
import subprocess
import time
import logging
import os
import json
from datetime import datetime
import zoneinfo

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# הגדרות
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OREF_API        = os.getenv("OREF_API_URL", "http://localhost:49000/current")
POLL_INTERVAL   = int(os.getenv("OREF_POLL_INTERVAL", "5"))
COOLDOWN_SEC    = int(os.getenv("OREF_COOLDOWN", "60"))
OPENCLAW_BIN    = os.getenv("OPENCLAW_BIN", "openclaw")

# Home Assistant - לרמקול בלבד
HA_URL          = os.getenv("HASS_SERVER", "https://ha.right-api.com")
HA_TOKEN        = os.getenv("HASS_TOKEN", "")
HA_TTS_SPEAKER  = os.getenv("HA_TTS_SPEAKER", "media_player.home_assistant_voice_09a069_media_player")

# 3CX - חיוג טלפוני
CX3_API         = os.getenv("CX3_API", "http://localhost:3000/api/outbound-call")
CX3_EXTENSION   = os.getenv("CX3_EXTENSION", "12610")
CX3_ENABLED     = os.getenv("CX3_ENABLED", "true").lower() == "true"

# פילטר אזורים
MONITORED_AREAS = [a.strip() for a in os.getenv("MONITORED_AREAS", "הרצליה,הרצליה - גליל ים ומרכז").split(",") if a.strip()]

# יעדי WhatsApp
WHATSAPP_GROUP  = os.getenv("WHATSAPP_GROUP_JID", "120363417492964228@g.us")
WHATSAPP_OWNER  = os.getenv("WHATSAPP_OWNER", "+972525173322")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# סוגי התרעות
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ALERT_TYPES = {
    "1":  {"emoji": "🚀", "level": "CRITICAL", "whatsapp": True,
           "action": "כנסו למרחב המוגן מיד! יש לכם 90 שניות!",
           "tts": "אזעקה! ירי רקטות וטילים! כנסו למרחב המוגן מיד!"},
    "2":  {"emoji": "✈️", "level": "CRITICAL", "whatsapp": True,
           "action": "כנסו למרחב המוגן מיד!",
           "tts": "אזעקה! חדירת כלי טיס עוין! כנסו למרחב המוגן מיד!"},
    "10": {"emoji": "🔴", "level": "CRITICAL", "whatsapp": True,
           "action": "חדירת מחבלים באזור!",
           "tts": "התרעה! חדירת מחבלים באזור!"},
    "13": {"emoji": "✅", "level": "ALL_CLEAR", "whatsapp": True,
           "action": "ניתן לצאת מהמרחב המוגן.",
           "tts": "האירוע הסתיים. ניתן לצאת מהמרחב המוגן."},
    "14": {"emoji": "⚠️",  "level": "WARNING",  "whatsapp": False,
           "action": "התכוננו! צפויות התרעות בקרוב!",
           "tts": "שימו לב! בדקות הקרובות צפויות התרעות באזורכם. התכוננו!"},
}
DEFAULT_TYPE = {"emoji": "🚨", "level": "UNKNOWN", "whatsapp": True,
                "action": "עיקבו אחר הוראות פיקוד העורף.",
                "tts": "התרעת פיקוד העורף. עיקבו אחר ההוראות."}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("/var/log/oref_native.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger("oref-native")

# State
last_alert_id  = None
alert_sent_at  = None
all_clear_sent = False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# OpenClaw - שליחת WhatsApp
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def openclaw_whatsapp(target: str, message: str):
    """שלח הודעת WhatsApp דרך OpenClaw CLI"""
    try:
        cmd = [OPENCLAW_BIN, "message", "send",
               "--channel", "whatsapp",
               "--target", target,
               "--message", message]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if r.returncode == 0:
            log.info(f"✅ WhatsApp → {target}")
        else:
            log.error(f"❌ WhatsApp failed: {r.stderr[:100]}")
    except Exception as e:
        log.error(f"❌ WhatsApp error: {e}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# OpenClaw - TTS הכרזה קולית
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def cx3_call(text: str):
    """חייג לשלוחה 3CX עם הודעת התרעה"""
    try:
        r = requests.post(CX3_API,
            json={"to": CX3_EXTENSION, "message": text, "language": "he"},
            timeout=10)
        if r.status_code == 200:
            log.info(f"✅ 3CX call → {CX3_EXTENSION}")
        else:
            log.warning(f"⚠️ 3CX {r.status_code}: {r.text[:80]}")
    except Exception as e:
        log.warning(f"⚠️ 3CX error: {e}")


def ha_tts(text: str):
    """הכרז קולית דרך רמקול Home Assistant"""
    try:
        r = requests.post(
            f"{HA_URL}/api/services/tts/google_translate_say",
            headers={"Authorization": f"Bearer {HA_TOKEN}", "Content-Type": "application/json"},
            json={"entity_id": HA_TTS_SPEAKER, "message": text, "language": "iw"},
            timeout=8
        )
        if r.status_code in (200, 201):
            log.info("✅ Speaker announced")
        else:
            log.warning(f"⚠️ Speaker {r.status_code}: {r.text[:80]}")
    except Exception as e:
        log.warning(f"⚠️ Speaker error: {e}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# בניית הודעה
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def build_message(data: dict, atype: dict) -> str:
    current = data.get("current", {})
    title   = current.get("title", "התרעה")
    areas   = current.get("data", []) or []
    desc    = current.get("desc", "")

    if MONITORED_AREAS and areas:
        matched = [a for a in areas if any(m in a for m in MONITORED_AREAS)]
        areas_to_show = matched if matched else areas[:5]
    else:
        areas_to_show = areas[:5]

    now = datetime.now(zoneinfo.ZoneInfo("Asia/Jerusalem")).strftime("%H:%M:%S")
    return (
        f"{atype['emoji']} *{title}* {atype['emoji']}\n\n"
        f"⏰ {now}\n"
        f"⚡ {atype['action']}"
        + (f"\n📍 {', '.join(areas_to_show)}" if areas_to_show else "")
        + (f"\n📋 {desc}" if desc else "")
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# שליחת התרעה
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def dispatch(data: dict):
    current = data.get("current", {})
    cat     = str(current.get("cat", "1"))
    atype   = ALERT_TYPES.get(cat, DEFAULT_TYPE)
    level   = atype["level"]

    log.info(f"🚨 [{level}] Dispatching alert")

    wa_msg   = build_message(data, atype)
    tts_text = atype["tts"]

    # 1️⃣ WhatsApp - קבוצת עדכונים בלבד
    if atype["whatsapp"]:
        openclaw_whatsapp(WHATSAPP_GROUP, wa_msg)

    # 3️⃣ רמקול HA - תמיד
    ha_tts(tts_text)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# לולאת ניטור
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def check_alert():
    global last_alert_id, alert_sent_at, all_clear_sent
    try:
        data = requests.get(OREF_API, timeout=5).json()
    except Exception as e:
        log.warning(f"⚠️ API: {e}")
        return

    if not data.get("alert"):
        if last_alert_id:
            log.info("✅ No active alert")
            last_alert_id  = None
            all_clear_sent = False
        return

    current  = data.get("current", {})
    cat      = str(current.get("cat", ""))
    alert_id = current.get("id", "")

    # פילטר אזורים (גם לסיום אירוע)
    if MONITORED_AREAS:
        areas   = current.get("data", []) or []
        matched = [a for a in areas if any(m in a for m in MONITORED_AREAS)]
        if not matched:
            log.debug(f"⏭️ Skipped (not in area): {areas}")
            return

    # סיום אירוע - שלח פעם אחת
    if cat == "13":
        if not all_clear_sent:
            all_clear_sent = True
            dispatch(data)
        return

    # מנע ספאם
    if alert_id == last_alert_id:
        return
    now = time.time()
    if alert_sent_at and (now - alert_sent_at) < COOLDOWN_SEC:
        return

    last_alert_id  = alert_id
    alert_sent_at  = now
    all_clear_sent = False
    dispatch(data)


def main():
    log.info("🚀 ORef Native Monitor started (OpenClaw-only mode)")
    log.info(f"📡 Polling: {OREF_API} every {POLL_INTERVAL}s")
    log.info(f"📍 Monitored: {MONITORED_AREAS}")
    log.info(f"📱 Group: {WHATSAPP_GROUP}")
    log.info("━" * 50)
    while True:
        try:
            check_alert()
        except Exception as e:
            log.error(f"❌ {e}")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
