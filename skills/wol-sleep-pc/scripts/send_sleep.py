#!/usr/bin/env python3
"""
Send Sleep-on-LAN (SOL) magic packet using inverted MAC.
Defaults are zeroed; can be overridden via config file (~/.config/wol-sleep-pc/config.json) or command-line flags.
Usage: python3 send_sleep.py [--mac MAC] [--broadcast ADDR] [--port PORT]
"""
import argparse
import json
import os
import socket

DEFAULT_MAC = "00:00:00:00:00:00"
DEFAULT_BROADCAST = "0.0.0.0"
DEFAULT_PORT = 9

CONFIG_PATH = os.path.expanduser('~/.config/wol-sleep-pc/config.json')


def load_config():
    try:
        with open(CONFIG_PATH,'r') as f:
            return json.load(f)
    except Exception:
        return {}


def send_sleep(mac=DEFAULT_MAC, broadcast=DEFAULT_BROADCAST, port=DEFAULT_PORT):
    mac_clean = mac.replace(":", "").replace("-", "")
    data = bytes.fromhex("ff" * 6 + mac_clean * 16)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    try:
        s.sendto(data, (broadcast, port))
        print(f"SOL packet sent to {mac} via {broadcast}:{port}")
    finally:
        s.close()


if __name__ == '__main__':
    cfg = load_config()
    p = argparse.ArgumentParser()
    p.add_argument('--mac', default=cfg.get('sleep_mac', DEFAULT_MAC), help='Target inverted MAC address')
    p.add_argument('--broadcast', default=cfg.get('broadcast', DEFAULT_BROADCAST), help='Broadcast address')
    p.add_argument('--port', type=int, default=cfg.get('port', DEFAULT_PORT), help='UDP port')
    args = p.parse_args()
    send_sleep(args.mac, args.broadcast, args.port)
