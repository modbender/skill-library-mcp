#!/usr/bin/env python3
"""
Bambu Lab 3D-Drucker MQTT Control
Alternative zu mosquitto_sub/pub - nutzt paho-mqtt
"""

import json
import sys
import time
import ssl
import argparse
from datetime import datetime

try:
    import paho.mqtt.client as mqtt
except ImportError:
    print("Fehler: paho-mqtt nicht installiert")
    print("Installiere mit: pip3 install paho-mqtt")
    sys.exit(1)

# Konfiguration
HOST = "192.168.30.103"
PORT = 8883
SERIAL = "03919A3A2200009"
ACCESS_CODE = "33576961"
MODEL = "A1"

REPORT_TOPIC = f"device/{SERIAL}/report"
REQUEST_TOPIC = f"device/{SERIAL}/request"

class BambuPrinter:
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
        else:
            print(f"Verbindungsfehler: {rc}")
            
    def on_message(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())
            self.last_status = data
        except:
            pass
    
    def connect(self, timeout=5):
        try:
            self.client.connect(HOST, PORT, 60)
            self.client.loop_start()
            # Warte auf Verbindung
            start = time.time()
            while not self.connected and time.time() - start < timeout:
                time.sleep(0.1)
            return self.connected
        except Exception as e:
            print(f"Verbindungsfehler: {e}")
            return False
    
    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
    
    def get_status(self, timeout=3):
        """Status abfragen"""
        if not self.connect():
            return None
        
        # Warte auf erste Nachricht
        start = time.time()
        while not self.last_status and time.time() - start < timeout:
            time.sleep(0.1)
        
        status = self.last_status
        self.disconnect()
        return status
    
    def send_command(self, command):
        """Kommando senden"""
        if not self.connect():
            return False
        
        payload = json.dumps({"print": command})
        self.client.publish(REQUEST_TOPIC, payload)
        time.sleep(0.5)
        self.disconnect()
        return True
    
    def watch(self, callback=None):
        """Dauerhaft überwachen"""
        if not self.connect():
            print("❌ Keine Verbindung möglich")
            return
        
        print("🔴 Live-Überwachung gestartet (Strg+C zum Beenden)...")
        print("")
        
        try:
            while True:
                if self.last_status:
                    self._clear_screen()
                    self._print_status(self.last_status)
                    if callback:
                        callback(self.last_status)
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nÜberwachung beendet")
        finally:
            self.disconnect()
    
    def _clear_screen(self):
        print("\033[2J\033[H", end="")
    
    def _print_status(self, data):
        """Status formatiert ausgeben"""
        p = data.get("print", {})
        
        state = p.get("gcode_state", "UNKNOWN")
        state_icons = {
            "IDLE": "🟡 Bereit",
            "RUNNING": "🟢 Druckt",
            "PAUSE": "⏸️  Pausiert",
            "FINISH": "✅ Fertig",
            "FAILED": "❌ Fehlgeschlagen"
        }
        state_text = state_icons.get(state, state)
        
        percent = p.get("mc_percent", 0)
        remaining = p.get("mc_remaining_time", 0)
        hours = remaining // 3600
        mins = (remaining % 3600) // 60
        
        bed = p.get("bed_temper", 0)
        nozzle = p.get("nozzle_temper", 0)
        layer = p.get("layer_num", 0)
        total_layer = p.get("total_layer_num", 0)
        filename = p.get("filename", "-")
        error = p.get("print_error", 0)
        
        print("=" * 40)
        print(f"    🖨️  Bambu Lab {MODEL} Status")
        print("=" * 40)
        print(f"Status:    {state_text}")
        print(f"Datei:     {filename}")
        print(f"Fortschritt: {percent}%")
        print(f"Layer:     {layer} / {total_layer}")
        print(f"Restzeit:  {hours}h {mins}min")
        print("-" * 40)
        print("🌡️  Temperaturen:")
        print(f"   Nozzle: {nozzle}°C")
        print(f"   Bett:   {bed}°C")
        
        if error and error != 0:
            print("-" * 40)
            print(f"⚠️  Fehler-Code: {error}")
        print("=" * 40)
        print(f"Aktualisiert: {datetime.now().strftime('%H:%M:%S')}")


def cmd_status():
    printer = BambuPrinter()
    print(f"Verbinde mit {MODEL} @ {HOST}...")
    status = printer.get_status()
    
    if status:
        printer._print_status(status)
    else:
        print("❌ Keine Verbindung möglich")
        print("   Prüfe: Ist der Drucker im LAN-Mode?")


def cmd_progress():
    printer = BambuPrinter()
    status = printer.get_status()
    
    if status:
        p = status.get("print", {})
        print(f"Druckfortschritt: {p.get('mc_percent', 0)}% ({p.get('gcode_state', 'UNKNOWN')})")
    else:
        print("❌ Keine Verbindung")


def cmd_temps():
    printer = BambuPrinter()
    status = printer.get_status()
    
    if status:
        p = status.get("print", {})
        print("🌡️  Temperaturen:")
        print(f"   Nozzle: {p.get('nozzle_temper', 0)}°C / {p.get('nozzle_target_temper', 0)}°C")
        print(f"   Bett:   {p.get('bed_temper', 0)}°C / {p.get('bed_target_temper', 0)}°C")
    else:
        print("❌ Keine Verbindung")


def cmd_watch():
    printer = BambuPrinter()
    printer.watch()


def cmd_pause():
    printer = BambuPrinter()
    print("⏸️  Pausiere Druck...")
    if printer.send_command({"command": "pause"}):
        print("✅ Pausiert")


def cmd_resume():
    printer = BambuPrinter()
    print("▶️  Setze Druck fort...")
    if printer.send_command({"command": "resume"}):
        print("✅ Fortgesetzt")


def cmd_stop():
    printer = BambuPrinter()
    confirm = input("❌ Druck wirklich abbrechen? (j/N) ")
    if confirm.lower() == "j":
        print("Breche Druck ab...")
        if printer.send_command({"command": "stop"}):
            print("✅ Abgebrochen")
    else:
        print("Abbruch verworfen")


def cmd_light(mode):
    printer = BambuPrinter()
    modes = {"on": "on", "off": "off", "1": "on", "0": "off"}
    led_mode = modes.get(mode)
    
    if not led_mode:
        print("Fehler: on oder off angeben")
        return
    
    icon = "💡" if led_mode == "on" else "🌑"
    print(f"{icon} Schalte Licht {led_mode}...")
    
    if printer.send_command({"command": "ledctrl", "led_node": "chamber_light", "led_mode": led_mode}):
        print("✅ Fertig")


def cmd_notify():
    """Überwachung mit Benachrichtigungen"""
    printer = BambuPrinter()
    last_state = None
    last_percent = 0
    
    def check_notify(status):
        nonlocal last_state, last_percent
        p = status.get("print", {})
        state = p.get("gcode_state")
        percent = p.get("mc_percent", 0)
        error = p.get("print_error", 0)
        filename = p.get("filename", "Unbekannt")
        
        # Status-Änderung
        if state != last_state:
            if state == "FINISH":
                print(f"\n{'='*40}")
                print(f"✅ DRUCK FERTIG: {filename}")
                print(f"{'='*40}\n")
            elif state == "FAILED":
                print(f"\n{'='*40}")
                print(f"❌ DRUCK FEHLGESCHLAGEN: {filename}")
                print(f"{'='*40}\n")
            elif state == "PAUSE":
                print(f"⏸️  Druck pausiert: {filename}")
            elif state == "RUNNING" and last_state != "RUNNING":
                print(f"🟢 Druck läuft: {filename}")
            
            last_state = state
        
        # Fehler
        if error and error != 0:
            print(f"⚠️  FEHLER Code {error}!")
        
        # Fortschritt alle 10%
        if state == "RUNNING" and percent >= last_percent + 10:
            print(f"📊 Fortschritt: {percent}%")
            last_percent = percent
    
    printer.watch(callback=check_notify)


def main():
    parser = argparse.ArgumentParser(description="Bambu Lab 3D-Drucker Steuerung")
    parser.add_argument("command", choices=[
        "status", "progress", "temps", "watch", "pause", "resume", 
        "stop", "light", "notify"
    ], help="Befehl")
    parser.add_argument("arg", nargs="?", help="Zusätzliches Argument (z.B. on/off für light)")
    
    args = parser.parse_args()
    
    commands = {
        "status": cmd_status,
        "progress": cmd_progress,
        "temps": cmd_temps,
        "watch": cmd_watch,
        "pause": cmd_pause,
        "resume": cmd_resume,
        "stop": cmd_stop,
        "light": lambda: cmd_light(args.arg),
        "notify": cmd_notify,
    }
    
    if args.command == "light" and not args.arg:
        print("Fehler: light benötigt 'on' oder 'off'")
        sys.exit(1)
    
    commands[args.command]()


if __name__ == "__main__":
    main()
