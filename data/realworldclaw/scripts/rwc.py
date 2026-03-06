#!/usr/bin/env python3
"""RealWorldClaw CLI — Give AI agents physical world capabilities."""

import argparse
import json
import os
import ssl
import sys
import time
from pathlib import Path
from typing import Any, Optional

# Optional imports
try:
    import paho.mqtt.client as mqtt
    HAS_MQTT = True
except ImportError:
    HAS_MQTT = False

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

CONFIG_PATH = Path(__file__).parent.parent / "config.json"
RULES_PATH = Path(__file__).parent.parent / "rules.json"
DEFAULT_API = "https://realworldclaw-api.fly.dev/api/v1"


def load_config() -> dict:
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text())
    return {"api_url": DEFAULT_API, "devices": []}


def load_rules() -> list:
    if RULES_PATH.exists():
        return json.loads(RULES_PATH.read_text())
    return []


def save_rules(rules: list):
    RULES_PATH.write_text(json.dumps(rules, indent=2))


def get_device(config: dict, name: Optional[str] = None) -> dict:
    devices = config.get("devices", [])
    if not devices:
        print("❌ No devices configured. Edit config.json to add devices.")
        sys.exit(1)
    if name:
        for d in devices:
            if d["name"] == name:
                return d
        print(f"❌ Device '{name}' not found. Available: {[d['name'] for d in devices]}")
        sys.exit(1)
    return devices[0]


# ── MQTT Local Communication ──

class DeviceClient:
    """Communicate with ESP32 via MQTT (local network)."""

    def __init__(self, device: dict):
        self.device = device
        self.ip = device["ip"]
        self.code = device.get("access_code", "")
        self.serial = device.get("serial", "")
        self.data: dict = {}

    def _get_client(self):
        if not HAS_MQTT:
            print("❌ paho-mqtt not installed. Run: pip install paho-mqtt")
            sys.exit(1)
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        if self.code:
            client.username_pw_set("bblp", self.code)
            client.tls_set(cert_reqs=ssl.CERT_NONE)
            client.tls_insecure_set(True)
        return client

    def read_status(self, timeout: float = 5.0) -> dict:
        client = self._get_client()
        self.data = {}

        def on_connect(c, ud, flags, rc, props=None):
            c.subscribe(f"device/{self.serial}/report")

        def on_message(c, ud, msg):
            try:
                payload = json.loads(msg.payload)
                self.data.update(payload)
            except Exception:
                pass

        client.on_connect = on_connect
        client.on_message = on_message

        try:
            client.connect(self.ip, 8883, 60)
            client.loop_start()
            time.sleep(timeout)
            client.loop_stop()
            client.disconnect()
        except Exception as e:
            return {"error": str(e)}

        return self.data

    def send_command(self, command: dict) -> bool:
        client = self._get_client()
        try:
            client.connect(self.ip, 8883, 60)
            topic = f"device/{self.serial}/request"
            client.publish(topic, json.dumps(command))
            time.sleep(0.5)
            client.disconnect()
            return True
        except Exception as e:
            print(f"❌ Command failed: {e}")
            return False


# ── Platform API ──

class PlatformAPI:
    """HTTP client for RealWorldClaw cloud platform."""

    def __init__(self, base_url: str = DEFAULT_API, token: str = ""):
        if not HAS_HTTPX:
            print("❌ httpx not installed. Run: pip install httpx")
            sys.exit(1)
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self.http = httpx.Client(base_url=base_url, headers=headers, timeout=30)

    def health(self) -> dict:
        return self.http.get("/health").json()

    def modules(self) -> dict:
        return self.http.get("/modules").json()

    def register(self, username: str, email: str, password: str) -> dict:
        return self.http.post("/auth/register", json={
            "username": username, "email": email, "password": password
        }).json()

    def login(self, email: str, password: str) -> dict:
        return self.http.post("/auth/login", json={
            "email": email, "password": password
        }).json()


# ── Automation Rules ──

def evaluate_condition(condition: str, sensor_data: dict) -> bool:
    """Evaluate simple conditions like 'temperature > 30'."""
    try:
        parts = condition.split()
        if len(parts) != 3:
            return False
        key, op, value = parts
        actual = sensor_data.get(key)
        if actual is None:
            return False
        threshold = float(value)
        actual = float(actual)
        ops = {">": actual > threshold, "<": actual < threshold,
               ">=": actual >= threshold, "<=": actual <= threshold,
               "==": actual == threshold, "!=": actual != threshold}
        return ops.get(op, False)
    except Exception:
        return False


# ── Actions ──

ACTIONS = {
    "relay_on":  {"command": "gpio", "pin": 4, "value": 1},
    "relay_off": {"command": "gpio", "pin": 4, "value": 0},
    "led":       {"command": "led"},
    "servo":     {"command": "servo"},
    "buzzer_on": {"command": "gpio", "pin": 5, "value": 1},
    "buzzer_off":{"command": "gpio", "pin": 5, "value": 0},
}


def cmd_status(args, config):
    """Show all device status."""
    for dev in config.get("devices", []):
        print(f"\n🔌 {dev['name']} ({dev.get('type', 'unknown')}) @ {dev['ip']}")
        client = DeviceClient(dev)
        data = client.read_status(timeout=3)
        if "error" in data:
            print(f"   ❌ {data['error']}")
        else:
            for k, v in data.items():
                print(f"   {k}: {v}")
    if not config.get("devices"):
        print("No devices configured.")


def cmd_devices(args, config):
    """List configured devices."""
    for d in config.get("devices", []):
        print(f"  • {d['name']} — {d.get('type','?')} @ {d['ip']} (serial: {d.get('serial','?')})")


def cmd_sense(args, config):
    """Read sensors from a device."""
    dev = get_device(config, args.device)
    client = DeviceClient(dev)
    print(f"📡 Reading sensors from {dev['name']}...")
    data = client.read_status(timeout=args.timeout or 5)
    if "error" in data:
        print(f"❌ {data['error']}")
    else:
        print(json.dumps(data, indent=2))


def cmd_act(args, config):
    """Execute an action on a device."""
    dev = get_device(config, args.device)
    action_name = args.action
    if action_name not in ACTIONS:
        print(f"❌ Unknown action '{action_name}'. Available: {list(ACTIONS.keys())}")
        sys.exit(1)
    cmd = dict(ACTIONS[action_name])
    if args.value:
        cmd.update(json.loads(args.value))
    client = DeviceClient(dev)
    print(f"⚡ Executing {action_name} on {dev['name']}...")
    if client.send_command(cmd):
        print("✅ Command sent")
    else:
        print("❌ Failed")


def cmd_rule(args, config):
    """Manage automation rules."""
    rules = load_rules()
    if args.rule_action == "add":
        rule = {"name": args.name, "condition": args.condition,
                "action": args.rule_act, "device": args.device}
        rules.append(rule)
        save_rules(rules)
        print(f"✅ Rule '{args.name}' added")
    elif args.rule_action == "list":
        if not rules:
            print("No rules defined.")
        for r in rules:
            print(f"  📋 {r['name']}: IF {r['condition']} THEN {r['action']} ON {r['device']}")
    elif args.rule_action == "remove":
        rules = [r for r in rules if r["name"] != args.name]
        save_rules(rules)
        print(f"✅ Rule '{args.name}' removed")


def cmd_monitor(args, config):
    """Continuous monitoring with rule evaluation."""
    dev = get_device(config, args.device)
    rules = [r for r in load_rules() if r["device"] == dev["name"]]
    interval = args.interval or 5
    print(f"👁️ Monitoring {dev['name']} every {interval}s (Ctrl+C to stop)")
    if rules:
        print(f"   Active rules: {[r['name'] for r in rules]}")
    client = DeviceClient(dev)
    try:
        while True:
            data = client.read_status(timeout=3)
            ts = time.strftime("%H:%M:%S")
            if "error" in data:
                print(f"[{ts}] ❌ {data['error']}")
            else:
                summary = ", ".join(f"{k}={v}" for k, v in data.items() if k != "error")
                print(f"[{ts}] {summary}")
                for rule in rules:
                    if evaluate_condition(rule["condition"], data):
                        print(f"[{ts}] 🔔 Rule '{rule['name']}' triggered! Executing {rule['action']}")
                        act_cmd = dict(ACTIONS.get(rule["action"], {}))
                        client.send_command(act_cmd)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n⏹️ Monitoring stopped")


def cmd_api(args, config):
    """Platform API commands."""
    api = PlatformAPI(config.get("api_url", DEFAULT_API))
    if args.api_action == "health":
        print(json.dumps(api.health(), indent=2))
    elif args.api_action == "modules":
        print(json.dumps(api.modules(), indent=2))
    elif args.api_action == "register":
        print(json.dumps(api.register(args.username, args.email, args.password), indent=2))
    elif args.api_action == "login":
        print(json.dumps(api.login(args.email, args.password), indent=2))


def main():
    parser = argparse.ArgumentParser(description="RealWorldClaw — Physical World for AI Agents")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("status", help="Show all device status")
    sub.add_parser("devices", help="List configured devices")

    p_sense = sub.add_parser("sense", help="Read sensors")
    p_sense.add_argument("--device", "-d", help="Device name")
    p_sense.add_argument("--timeout", "-t", type=float, default=5)

    p_act = sub.add_parser("act", help="Execute action")
    p_act.add_argument("--device", "-d", help="Device name")
    p_act.add_argument("--action", "-a", required=True)
    p_act.add_argument("--value", "-v", help="JSON value")

    p_rule = sub.add_parser("rule", help="Manage automation rules")
    p_rule_sub = p_rule.add_subparsers(dest="rule_action")
    p_add = p_rule_sub.add_parser("add")
    p_add.add_argument("--name", required=True)
    p_add.add_argument("--condition", required=True)
    p_add.add_argument("--action", dest="rule_act", required=True)
    p_add.add_argument("--device", required=True)
    p_rule_sub.add_parser("list")
    p_rm = p_rule_sub.add_parser("remove")
    p_rm.add_argument("--name", required=True)

    p_mon = sub.add_parser("monitor", help="Continuous monitoring")
    p_mon.add_argument("--device", "-d", help="Device name")
    p_mon.add_argument("--interval", "-i", type=int, default=5)

    p_api = sub.add_parser("api", help="Platform API")
    p_api_sub = p_api.add_subparsers(dest="api_action")
    p_api_sub.add_parser("health")
    p_api_sub.add_parser("modules")
    p_reg = p_api_sub.add_parser("register")
    p_reg.add_argument("--username", required=True)
    p_reg.add_argument("--email", required=True)
    p_reg.add_argument("--password", required=True)
    p_login = p_api_sub.add_parser("login")
    p_login.add_argument("--email", required=True)
    p_login.add_argument("--password", required=True)

    args = parser.parse_args()
    config = load_config()

    commands = {
        "status": cmd_status, "devices": cmd_devices, "sense": cmd_sense,
        "act": cmd_act, "rule": cmd_rule, "monitor": cmd_monitor, "api": cmd_api,
    }

    if args.command in commands:
        commands[args.command](args, config)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
