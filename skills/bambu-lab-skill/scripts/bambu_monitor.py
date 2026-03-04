#!/usr/bin/env python3
"""
Bambu Lab Drucker Überwachung mit Telegram-Benachrichtigungen
Wird vom Cron alle 2 Minuten aufgerufen
"""

import json
import sys
import os
import ssl
from datetime import datetime

# Pfade
STATE_FILE = "/home/node/.openclaw/workspace/.bambu_state.json"

try:
    import paho.mqtt.client as mqtt
except ImportError:
    print("paho-mqtt nicht installiert")
    sys.exit(1)

# Konfiguration
HOST = "192.168.30.103"
PORT = 8883
SERIAL = "03919A3A2200009"
ACCESS_CODE = "33576961"
REPORT_TOPIC = f"device/{SERIAL}/report"

# Telegram Bot Config (aus ENV oder default)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = "428605191"

class BambuMonitor:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.username_pw_set(SERIAL, ACCESS_CODE)
        self.client.tls_set(cert_reqs=ssl.CERT_NONE)
        self.client.tls_insecure_set(True)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.connected = False
        self.last_status = {}
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            client.subscribe(REPORT_TOPIC)
            
    def on_message(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())
            self.last_status = data
        except:
            pass
    
    def get_status(self, timeout=3):
        try:
            self.client.connect(HOST, PORT, 60)
            self.client.loop_start()
            
            start = datetime.now()
            while not self.connected and (datetime.now() - start).seconds < timeout:
                pass
                
            # Warte auf Nachricht
            start = datetime.now()
            while not self.last_status and (datetime.now() - start).seconds < timeout:
                pass
            
            self.client.loop_stop()
            self.client.disconnect()
            return self.last_status
        except Exception as e:
            return None


def load_state():
    """Letzten Status laden"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"state": "UNKNOWN", "percent": 0, "notified_finish": False}


def save_state(state):
    """Status speichern"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)


def send_telegram(message):
    """Nachricht über Telegram senden"""
    import urllib.request
    import urllib.parse
    
    # Versuche OpenClaw's message tool zu nutzen
    try:
        # Prüfe ob wir im OpenClaw Kontext sind
        if os.path.exists("/home/node/.openclaw"):
            # Schreibe Nachricht in eine Datei die OpenClaw lesen kann
            msg_file = "/tmp/bambu_notification.txt"
            with open(msg_file, 'w') as f:
                f.write(message)
            print(f"NOTIFICATION: {message}")
            return True
    except:
        pass
    
    return False


def main():
    monitor = BambuMonitor()
    status = monitor.get_status()
    
    if not status:
        print(f"[{datetime.now()}] Keine Verbindung zum Drucker")
        return
    
    p = status.get("print", {})
    current_state = p.get("gcode_state", "UNKNOWN")
    current_percent = p.get("mc_percent", 0)
    error = p.get("print_error", 0)
    filename = p.get("filename", "Unbekannt")
    
    saved = load_state()
    
    # Prüfe auf Status-Änderungen
    notifications = []
    
    # Druck fertig
    if current_state == "FINISH" and saved.get("state") != "FINISH" and not saved.get("notified_finish"):
        notifications.append(f"✅ DRUCK FERTIG!\n🖨️ {filename}")
        saved["notified_finish"] = True
    
    # Druck gestartet
    if current_state == "RUNNING" and saved.get("state") != "RUNNING":
        notifications.append(f"🟢 Druck gestartet\n🖨️ {filename}")
        saved["notified_finish"] = False
    
    # Fehler
    if error and error != 0 and saved.get("error") != error:
        notifications.append(f"❌ FEHLER beim Drucken!\nCode: {error}\n🖨️ {filename}")
    
    # Fortschritt alle 25%
    last_percent = saved.get("percent", 0)
    if current_state == "RUNNING":
        for milestone in [25, 50, 75]:
            if last_percent < milestone and current_percent >= milestone:
                notifications.append(f"📊 Fortschritt: {current_percent}%\n🖨️ {filename}")
                break
    
    # Sende Benachrichtigungen
    for msg in notifications:
        send_telegram(msg)
        print(f"[{datetime.now()}] {msg}")
    
    # Status aktualisieren
    saved["state"] = current_state
    saved["percent"] = current_percent
    saved["error"] = error
    saved["filename"] = filename
    saved["last_check"] = datetime.now().isoformat()
    save_state(saved)
    
    # Debug-Output
    print(f"[{datetime.now()}] State: {current_state}, {current_percent}%, Error: {error}")


if __name__ == "__main__":
    main()
