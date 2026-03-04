#!/usr/bin/env python3
"""Diagnose bot detection issues. Run to check IP, proxy, and stealth config."""

import json
import os
import subprocess
import sys

CONFIG_DIR = os.path.expanduser("~/.config/stealth")

def check_ip(proxy=None):
    """Check current IP and whether it's datacenter or residential."""
    cmd = ["curl", "-s", "--max-time", "10", "https://ipinfo.io/json"]
    if proxy:
        cmd = ["curl", "-s", "--max-time", "10", "-x", proxy, "https://ipinfo.io/json"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        data = json.loads(result.stdout)
    except Exception as e:
        print(f"❌ Failed to check IP: {e}")
        return None
    
    ip = data.get("ip", "unknown")
    org = data.get("org", "unknown")
    city = data.get("city", "")
    country = data.get("country", "")
    
    # Detect datacenter
    dc_keywords = [
        "digitalocean", "amazon", "aws", "google", "microsoft", "azure",
        "linode", "vultr", "hetzner", "ovh", "cloud", "hosting", "server",
        "contabo", "kamatera", "upcloud", "scaleway"
    ]
    is_dc = any(kw in org.lower() for kw in dc_keywords)
    
    # Also check privacy field if available
    if "privacy" in data and data["privacy"].get("hosting"):
        is_dc = True
    
    label = "via proxy" if proxy else "direct"
    print(f"\n{'='*50}")
    print(f"IP Check ({label})")
    print(f"{'='*50}")
    print(f"IP:       {ip}")
    print(f"Org:      {org}")
    print(f"Location: {city}, {country}")
    print(f"Type:     {'⚠️  DATACENTER' if is_dc else '✅ RESIDENTIAL'}")
    
    if is_dc and not proxy:
        print("\n→ You need a residential proxy (Layer 1).")
        print("  See: references/proxy-setup.md")
    
    return {"ip": ip, "org": org, "datacenter": is_dc}


def check_proxy_config():
    """Check if proxy credentials are saved."""
    proxy_file = os.path.join(CONFIG_DIR, "proxy.json")
    if os.path.exists(proxy_file):
        with open(proxy_file) as f:
            config = json.load(f)
        host = config.get("host", "")
        port = config.get("port", "")
        user = config.get("username", "")
        pw = config.get("password", "")
        if host and port and user and pw:
            proxy_url = f"http://{user}:{pw}@{host}:{port}"
            print(f"\n✅ Proxy configured: {host}:{port} ({config.get('provider', 'unknown')})")
            return proxy_url
        else:
            print(f"\n⚠️  Proxy config exists but incomplete: {proxy_file}")
            return None
    else:
        print(f"\n❌ No proxy configured at {proxy_file}")
        return None


def check_captcha_config():
    """Check if captcha solver is configured."""
    captcha_file = os.path.join(CONFIG_DIR, "captcha.json")
    if os.path.exists(captcha_file):
        with open(captcha_file) as f:
            config = json.load(f)
        provider = config.get("provider", "unknown")
        has_key = bool(config.get("api_key"))
        if has_key:
            print(f"✅ CAPTCHA solver configured: {provider}")
        else:
            print(f"⚠️  CAPTCHA config exists but no API key: {captcha_file}")
        return config if has_key else None
    else:
        print(f"❌ No CAPTCHA solver at {captcha_file}")
        return None


def main():
    print("🔍 Stealth Diagnostic")
    print("=" * 50)
    
    # Check direct IP
    direct = check_ip()
    
    # Check proxy config
    proxy_url = check_proxy_config()
    
    # If proxy configured, test it
    if proxy_url:
        proxy_result = check_ip(proxy=proxy_url)
        if proxy_result and proxy_result["datacenter"]:
            print("\n⚠️  WARNING: Proxy IP is datacenter, not residential!")
            print("   Your proxy provider may be selling datacenter IPs.")
    
    # Check captcha config
    print()
    check_captcha_config()
    
    # Summary
    print(f"\n{'='*50}")
    print("Summary")
    print(f"{'='*50}")
    
    needs = []
    if direct and direct["datacenter"] and not proxy_url:
        needs.append("Layer 1: Residential proxy (you're on a datacenter IP)")
    if not check_captcha_file_exists():
        needs.append("Layer 2: CAPTCHA solver (not configured)")
    
    if needs:
        print("Action needed:")
        for n in needs:
            print(f"  → {n}")
    else:
        print("✅ All layers configured. If still blocked, check Layer 3 (browser stealth).")
        print("   See: references/browser-stealth.md")


def check_captcha_file_exists():
    return os.path.exists(os.path.join(CONFIG_DIR, "captcha.json"))


if __name__ == "__main__":
    main()
