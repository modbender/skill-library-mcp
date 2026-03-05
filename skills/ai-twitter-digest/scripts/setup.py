#!/usr/bin/env python3
"""
AI Twitter Digest — Setup Wizard
Run this once after installing the skill to configure your local environment.

Usage:
    python3 scripts/setup.py
"""

import os
import json
import sys
import subprocess
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
ENV_FILE = Path(__file__).parent / ".env"

def banner(text):
    print(f"\n{'─' * 50}")
    print(f"  {text}")
    print('─' * 50)

def ok(text):   print(f"  ✅ {text}")
def warn(text): print(f"  ⚠️  {text}")
def info(text): print(f"  ℹ️  {text}")
def ask(prompt, default=None):
    suffix = f" [{default}]" if default else ""
    val = input(f"  → {prompt}{suffix}: ").strip()
    return val or default or ""

# ── 1. Detect OpenClaw installation ──────────────────────────────────────────

def find_openclaw_auth():
    """Try to read API keys from OpenClaw's auth.json (if installed)."""
    found = {}

    # Common OpenClaw auth file locations
    candidates = [
        Path.home() / ".openclaw" / "agents" / "main" / "agent" / "auth.json",
        Path(os.environ.get("OPENCLAW_STATE_DIR", "~/.openclaw")).expanduser()
            / "agents" / "main" / "agent" / "auth.json",
    ]

    for path in candidates:
        if path.exists():
            try:
                data = json.loads(path.read_text())
                # Google/Gemini
                g = data.get("google", {})
                if g.get("key"):
                    found["GEMINI_API_KEY"] = g["key"]
                    ok(f"Found Google/Gemini key in OpenClaw config ({path})")
                # Minimax (uses Anthropic-compatible API)
                mm = data.get("minimax", {})
                if mm.get("key"):
                    found["_MINIMAX_KEY"] = mm["key"]
                # Note: Anthropic token in OpenClaw is OAuth and can't be used directly
            except Exception as e:
                warn(f"Could not read {path}: {e}")
            break

    return found

def find_env_keys():
    """Collect API keys already set in the environment."""
    found = {}
    for key in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY", "AISA_API_KEY"):
        val = os.environ.get(key, "").strip()
        if val:
            found[key] = val
            ok(f"Found {key} in environment")
    return found

# ── 2. Detect available channels ─────────────────────────────────────────────

SUPPORTED_CHANNELS = {
    "discord":  {
        "label": "Discord",
        "target_hint": "channel:<channel_id>  e.g. channel:1234567890",
        "cards": True,
    },
    "whatsapp": {
        "label": "WhatsApp",
        "target_hint": "E.164 phone number  e.g. +1234567890  (or group:<group_id>)",
        "cards": False,
    },
    "telegram": {
        "label": "Telegram",
        "target_hint": "@username or chat_id  (or group:<group_id>)",
        "cards": False,
    },
    "slack": {
        "label": "Slack",
        "target_hint": "#channel-name or channel:<channel_id>",
        "cards": False,
    },
    "signal": {
        "label": "Signal",
        "target_hint": "E.164 phone number  e.g. +1234567890",
        "cards": False,
    },
}

def detect_configured_channels():
    """Ask openclaw which channels are configured."""
    configured = []
    try:
        result = subprocess.run(
            ["openclaw", "channels", "list"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            output = result.stdout.lower()
            for ch in SUPPORTED_CHANNELS:
                if ch in output:
                    configured.append(ch)
    except Exception:
        pass
    return configured

def list_channel_targets(channel):
    """Try to list available targets (e.g. Discord channels) via openclaw directory."""
    try:
        result = subprocess.run(
            ["openclaw", "directory", "list", "--channel", channel],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            info(f"Available {channel} targets:")
            print(result.stdout[:800])
    except Exception:
        pass

# ── 3. Test LLM connectivity ──────────────────────────────────────────────────

def test_llm(config):
    """Test which LLM provider works."""
    import requests

    if config.get("ANTHROPIC_API_KEY"):
        try:
            r = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={"x-api-key": config["ANTHROPIC_API_KEY"],
                         "anthropic-version": "2023-06-01",
                         "content-type": "application/json"},
                json={"model": "claude-haiku-4-5", "max_tokens": 10,
                      "messages": [{"role": "user", "content": "hi"}]},
                timeout=10,
            )
            if r.status_code == 200:
                ok("Anthropic Claude ✓ (will be used for summarization)")
                return "anthropic"
            else:
                warn(f"Anthropic key invalid ({r.status_code})")
        except Exception as e:
            warn(f"Anthropic unreachable: {e}")

    if config.get("OPENAI_API_KEY"):
        try:
            r = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {config['OPENAI_API_KEY']}",
                         "Content-Type": "application/json"},
                json={"model": "gpt-4o-mini", "max_tokens": 10,
                      "messages": [{"role": "user", "content": "hi"}]},
                timeout=10,
            )
            if r.status_code == 200:
                ok("OpenAI GPT-4o-mini ✓ (will be used for summarization)")
                return "openai"
            else:
                warn(f"OpenAI key invalid ({r.status_code})")
        except Exception as e:
            warn(f"OpenAI unreachable: {e}")

    if config.get("GEMINI_API_KEY"):
        try:
            r = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={config['GEMINI_API_KEY']}",
                headers={"Content-Type": "application/json"},
                json={"contents": [{"parts": [{"text": "hi"}]}]},
                timeout=10,
            )
            if r.status_code == 200:
                ok("Google Gemini 2.0 Flash ✓ (will be used for summarization)")
                return "gemini"
            else:
                warn(f"Gemini key invalid ({r.status_code})")
        except Exception as e:
            warn(f"Gemini unreachable: {e}")

    return None

# ── 4. Test AISA connectivity ─────────────────────────────────────────────────

def test_aisa(key):
    import requests
    try:
        r = requests.get(
            "https://api.aisa.one/apis/v1/twitter/tweet/advanced_search",
            params={"query": "from:sama AI", "queryType": "Latest"},
            headers={"Authorization": f"Bearer {key}"},
            timeout=10,
        )
        if r.status_code == 200 and r.json().get("tweets") is not None:
            ok("AISA API ✓")
            return True
        else:
            warn(f"AISA API responded with {r.status_code}")
    except Exception as e:
        warn(f"AISA unreachable: {e}")
    return False

# ── 5. Write .env ─────────────────────────────────────────────────────────────

def write_env(config):
    ch = config.get("DELIVERY_CHANNEL", "discord")
    cards_default = "true" if ch == "discord" else "false"
    lines = [
        "# AI Twitter Digest — auto-generated by setup.py",
        "# Edit manually if needed.\n",
        f"AISA_API_KEY={config.get('AISA_API_KEY', '')}",
        "",
        "# Delivery (channel + target)",
        f"DELIVERY_CHANNEL={ch}",
        f"DELIVERY_TARGET={config.get('DELIVERY_TARGET', '')}",
        f"# CARD_PREVIEWS={cards_default}  # Discord only — set false to disable link embeds",
        "",
        f"# Digest language",
        f"SUMMARY_LANGUAGE={config.get('SUMMARY_LANGUAGE', 'Chinese')}",
        "",
        "# LLM keys (script tries Anthropic → OpenAI → Gemini in order)",
        f"ANTHROPIC_API_KEY={config.get('ANTHROPIC_API_KEY', '')}",
        f"OPENAI_API_KEY={config.get('OPENAI_API_KEY', '')}",
        f"GEMINI_API_KEY={config.get('GEMINI_API_KEY', '')}",
        "",
        "# Optional",
        f"STATE_FILE={config.get('STATE_FILE', str(Path.home() / '.ai-twitter-sent.json'))}",
        "MAX_STORED_IDS=500",
    ]
    ENV_FILE.write_text("\n".join(lines))
    ok(f".env written to {ENV_FILE}")

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("\n🤖 AI Twitter Digest — Setup Wizard")
    print("This will configure your local environment.\n")

    config = {}

    # Step 1: Auto-detect keys
    banner("Step 1: Detecting existing configuration")
    config.update(find_env_keys())
    config.update(find_openclaw_auth())  # OpenClaw config (non-destructive)

    # Step 2: AISA API key
    banner("Step 2: AISA API key (Twitter data)")
    if not config.get("AISA_API_KEY"):
        info("Get your key at https://aisa.one")
        config["AISA_API_KEY"] = ask("Paste your AISA_API_KEY")
    else:
        info(f"Using detected AISA key: {config['AISA_API_KEY'][:12]}...")
        override = ask("Press Enter to keep, or paste a different key")
        if override:
            config["AISA_API_KEY"] = override

    if config.get("AISA_API_KEY"):
        info("Testing AISA connectivity...")
        test_aisa(config["AISA_API_KEY"])
    else:
        warn("No AISA key — twitter fetching will not work")

    # Step 3: LLM key
    banner("Step 3: LLM API key (for summarization)")
    info("The script supports Anthropic, OpenAI, and Google Gemini.")
    info("It will use whichever key you provide (in that priority order).")

    for label, env_key, url in [
        ("Anthropic Claude", "ANTHROPIC_API_KEY", "console.anthropic.com"),
        ("OpenAI", "OPENAI_API_KEY", "platform.openai.com"),
        ("Google Gemini", "GEMINI_API_KEY", "aistudio.google.com"),
    ]:
        if not config.get(env_key):
            val = ask(f"{label} key (Enter to skip, get at {url})")
            if val:
                config[env_key] = val

    info("Testing LLM connectivity...")
    provider = test_llm(config)
    if not provider:
        warn("No working LLM found — summarization will fall back to raw tweet list")

    # Step 4: Delivery channel
    banner("Step 4: Delivery channel")
    configured = detect_configured_channels()
    if configured:
        ok(f"OpenClaw has configured channels: {', '.join(configured)}")
    else:
        info("Could not auto-detect configured channels.")

    print()
    print("  Supported channels:")
    for key, meta in SUPPORTED_CHANNELS.items():
        marker = "✅" if key in configured else "  "
        cards_note = " (supports card previews)" if meta["cards"] else ""
        print(f"  {marker} {key:10} — {meta['label']}{cards_note}")
    print()

    default_channel = configured[0] if configured else "discord"
    channel = ask("Which channel to deliver to?", default=default_channel).lower().strip()
    if channel not in SUPPORTED_CHANNELS:
        warn(f"'{channel}' is not in the supported list but will be used as-is.")
    config["DELIVERY_CHANNEL"] = channel

    ch_meta = SUPPORTED_CHANNELS.get(channel, {})
    hint = ch_meta.get("target_hint", "target identifier")
    info(f"Target format for {channel}: {hint}")
    list_channel_targets(channel)
    config["DELIVERY_TARGET"] = ask(f"Delivery target")

    # Step 5: Summary language
    banner("Step 5: Digest language")
    print("  The digest summary will be written in your chosen language.")
    print("  Examples: Chinese, English, Japanese, Korean, Spanish, French, German\n")
    lang = ask("Summary language", default="Chinese")
    config["SUMMARY_LANGUAGE"] = lang or "Chinese"
    ok(f"Digest will be delivered in: {config['SUMMARY_LANGUAGE']}")

    # Step 6: Optional config
    banner("Step 6: Optional settings")
    default_state = str(Path.home() / ".ai-twitter-sent.json")
    state = ask(f"State file path (for dedup tracking)", default=default_state)
    config["STATE_FILE"] = state or default_state

    # Step 7: Write .env
    banner("Step 7: Writing configuration")
    write_env(config)

    # Step 8: Summary
    banner("Setup complete!")
    print(f"""
  Run manually:
    python3 {SKILL_DIR}/scripts/monitor.py

  Schedule daily (OpenClaw cron):
    openclaw cron add "AI Twitter Digest" "30 15 * * *" \\
      "python3 {SKILL_DIR}/scripts/monitor.py" \\
      --timezone "America/New_York"

  Edit monitored accounts:
    {SKILL_DIR}/scripts/monitor.py  (ACCOUNTS list)
    See also: {SKILL_DIR}/references/accounts.md
""")

if __name__ == "__main__":
    main()
