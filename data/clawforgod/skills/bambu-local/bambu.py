#!/usr/bin/env python3
"""
Bambu Lab Local Control - Contrôle local via MQTT
"""
import ssl
import json
import sys
import time
import argparse
import os
import paho.mqtt.client as mqtt

# Charge la config
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH) as f:
        config = json.load(f)
    PRINTER_IP = config.get("printer_ip", "")
    ACCESS_CODE = config.get("access_code", "")
    SERIAL = config.get("serial", "")
    PRINTER_NAME = config.get("printer_name", "Printer")
else:
    print("❌ config.json manquant. Crée-le avec tes infos imprimante.")
    sys.exit(1)

status_data = {}
seq_id = 0

def get_client():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set("bblp", ACCESS_CODE)
    client.tls_set(cert_reqs=ssl.CERT_NONE)
    client.tls_insecure_set(True)
    return client

def on_connect(client, userdata, flags, rc, properties=None):
    client.subscribe(f"device/{SERIAL}/report")

def on_message(client, userdata, msg):
    global status_data
    try:
        data = json.loads(msg.payload)
        if "print" in data:
            status_data.update(data["print"])
    except:
        pass

def send_command(cmd):
    global seq_id
    client = get_client()
    client.connect(PRINTER_IP, 8883, 60)
    client.loop_start()
    time.sleep(1)
    seq_id += 1
    cmd["sequence_id"] = str(seq_id)
    topic = f"device/{SERIAL}/request"
    client.publish(topic, json.dumps(cmd))
    time.sleep(1)
    client.loop_stop()
    client.disconnect()

def get_status():
    client = get_client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(PRINTER_IP, 8883, 60)
    client.loop_start()
    time.sleep(3)
    client.loop_stop()
    client.disconnect()
    
    print(f"🖨️  {PRINTER_NAME} (Bambu Lab)")
    print(f"   IP: {PRINTER_IP}")
    print(f"   Serial: {SERIAL}")
    print(f"   ─────────────────────────")
    print(f"   🌡️  Lit: {status_data.get('bed_temper', 'N/A')}°C / {status_data.get('bed_target_temper', 0)}°C")
    print(f"   🌡️  Buse: {status_data.get('nozzle_temper', 'N/A')}°C / {status_data.get('nozzle_target_temper', 0)}°C")
    print(f"   📶 WiFi: {status_data.get('wifi_signal', 'N/A')}")
    print(f"   ⚙️  État: {status_data.get('gcode_state', 'IDLE')}")
    
    if status_data.get('gcode_state') == 'RUNNING':
        print(f"   📊 Progression: {status_data.get('mc_percent', 0)}%")
        remaining = status_data.get('mc_remaining_time', 0)
        if remaining:
            print(f"   ⏱️  Restant: {remaining // 60}h{remaining % 60}m")
        print(f"   🎯 Couche: {status_data.get('layer_num', 0)}/{status_data.get('total_layer_num', 0)}")

def light_control(state):
    cmd = {"system": {"command": "ledctrl", "led_node": "chamber_light", "led_mode": "on" if state else "off"}}
    send_command(cmd)
    print(f"💡 Lumière {'allumée' if state else 'éteinte'}")

def print_control(action):
    cmd = {"print": {"command": action}}
    send_command(cmd)
    actions_fr = {"pause": "en pause", "resume": "reprise", "stop": "arrêtée"}
    print(f"🖨️  Impression {actions_fr.get(action, action)}")

def set_speed(level):
    cmd = {"print": {"command": "print_speed", "param": str(level)}}
    send_command(cmd)
    speeds = {1: "Silencieux", 2: "Standard", 3: "Sport", 4: "Ludicrous"}
    print(f"⚡ Vitesse: {speeds.get(level, level)}")

def set_temps(bed=None, nozzle=None):
    if bed is not None:
        send_command({"print": {"command": "gcode_line", "param": f"M140 S{bed}"}})
        print(f"🌡️  Lit: {bed}°C")
    if nozzle is not None:
        send_command({"print": {"command": "gcode_line", "param": f"M104 S{nozzle}"}})
        print(f"🌡️  Buse: {nozzle}°C")

def send_gcode(gcode):
    cmd = {"print": {"command": "gcode_line", "param": gcode}}
    send_command(cmd)
    print(f"📤 G-code: {gcode}")

def main():
    parser = argparse.ArgumentParser(description=f"Contrôle {PRINTER_NAME}")
    subparsers = parser.add_subparsers(dest="command")
    
    subparsers.add_parser("status")
    light_p = subparsers.add_parser("light")
    light_p.add_argument("state", choices=["on", "off"])
    print_p = subparsers.add_parser("print")
    print_p.add_argument("action", choices=["pause", "resume", "stop"])
    speed_p = subparsers.add_parser("speed")
    speed_p.add_argument("level", type=int, choices=[1, 2, 3, 4])
    temp_p = subparsers.add_parser("temp")
    temp_p.add_argument("--bed", type=int)
    temp_p.add_argument("--nozzle", type=int)
    gcode_p = subparsers.add_parser("gcode")
    gcode_p.add_argument("code")
    
    args = parser.parse_args()
    
    if args.command == "status" or args.command is None:
        get_status()
    elif args.command == "light":
        light_control(args.state == "on")
    elif args.command == "print":
        print_control(args.action)
    elif args.command == "speed":
        set_speed(args.level)
    elif args.command == "temp":
        set_temps(args.bed, args.nozzle)
    elif args.command == "gcode":
        send_gcode(args.code)

if __name__ == "__main__":
    main()
