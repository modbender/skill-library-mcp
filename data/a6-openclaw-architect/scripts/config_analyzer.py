#!/usr/bin/env python3
"""Analyze openclaw.json and suggest improvements. Stdlib only."""
import json, os, sys

CONFIG_PATHS = [
    os.path.expanduser("~/.openclaw/openclaw.json"),
    os.path.join(os.environ.get("OPENCLAW_WORKSPACE", ""), "..", "openclaw.json"),
]

def load_config():
    for p in CONFIG_PATHS:
        if os.path.exists(p):
            with open(p) as f:
                return json.load(f), p
    print("ERROR: openclaw.json not found", file=sys.stderr)
    sys.exit(1)

def analyze(config):
    issues = []
    suggestions = []
    good = []

    # Model config
    agents = config.get("agents", {}).get("defaults", {})
    model = agents.get("model", {})
    if model.get("primary"):
        good.append(f"✅ Primary model: {model['primary']}")
    else:
        issues.append("❌ No primary model configured")
    
    fallbacks = model.get("fallbacks", [])
    if len(fallbacks) >= 2:
        good.append(f"✅ {len(fallbacks)} fallback models configured")
    elif len(fallbacks) == 1:
        suggestions.append("⚠️  Only 1 fallback model — recommend at least 2 from different providers")
    else:
        issues.append("❌ No fallback models — if primary fails, agent is dead")

    # Memory search
    ms = agents.get("memorySearch", {})
    if ms.get("enabled"):
        good.append("✅ Memory search enabled")
    else:
        suggestions.append("⚠️  Memory search disabled — agent can't search memory/*.md files")

    # Compaction
    comp = agents.get("compaction", {})
    flush = comp.get("memoryFlush", {})
    if flush.get("enabled"):
        good.append("✅ Memory flush before compaction enabled")
    else:
        issues.append("❌ Memory flush disabled — info will be lost during compaction")

    # Heartbeat
    hb = agents.get("heartbeat", {})
    if hb.get("every"):
        good.append(f"✅ Heartbeat: {hb['every']}")

    # Concurrency
    mc = agents.get("maxConcurrent", 0)
    smc = agents.get("subagents", {}).get("maxConcurrent", 0)
    if mc:
        good.append(f"✅ Max concurrent sessions: {mc}")
    if smc:
        good.append(f"✅ Max concurrent subagents: {smc}")
    if smc > 10:
        suggestions.append(f"⚠️  {smc} max subagents is high — watch credit usage")

    # Channels
    channels = config.get("channels", {})
    for name, ch in channels.items():
        if ch.get("botToken") or ch.get("token"):
            good.append(f"✅ Channel {name} configured")
        policy = ch.get("dmPolicy", "")
        if policy == "open":
            issues.append(f"❌ Channel {name} has open DM policy — anyone can message your bot")
        elif policy == "allowlist":
            allowed = ch.get("allowFrom", [])
            good.append(f"✅ Channel {name} restricted to {len(allowed)} user(s)")

    # Gateway auth
    gw = config.get("gateway", {})
    auth = gw.get("auth", {})
    if auth.get("token"):
        good.append("✅ Gateway auth token set")
    else:
        issues.append("❌ No gateway auth token — anyone can connect")
    if auth.get("allowTailscale"):
        good.append("✅ Tailscale auth enabled")

    # Diagnostics
    diag = config.get("diagnostics", {})
    otel = diag.get("otel", {})
    if otel.get("enabled"):
        good.append(f"✅ OTEL tracing enabled → {otel.get('endpoint', 'unknown')}")
        if otel.get("sampleRate", 1) == 1:
            suggestions.append("⚠️  OTEL sample rate is 1.0 (100%) — consider 0.1 for production to reduce overhead")

    # Browser
    br = config.get("browser", {})
    if br.get("enabled"):
        good.append("✅ Browser automation enabled")
    if br.get("noSandbox"):
        suggestions.append("⚠️  Browser running with --no-sandbox (required in Docker, but note security implications)")

    # Context pruning
    cp = agents.get("contextPruning", {})
    if cp.get("mode") == "cache-ttl":
        good.append(f"✅ Context pruning: cache-ttl ({cp.get('ttl', 'default')})")
    else:
        suggestions.append("⚠️  No context pruning — consider cache-ttl mode to save context window")

    # Skills
    skills = config.get("skills", {}).get("entries", {})
    enabled = [k for k, v in skills.items() if v.get("enabled")]
    if enabled:
        good.append(f"✅ {len(enabled)} skill(s) with config: {', '.join(enabled)}")

    # API key exposure check
    def check_keys(obj, path=""):
        exposed = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                full = f"{path}.{k}" if path else k
                if isinstance(v, str) and any(prefix in v for prefix in ["sk-", "pplx-", "am_"]):
                    if len(v) > 20:
                        exposed.append(full)
                else:
                    exposed.extend(check_keys(v, full))
        return exposed
    
    exposed = check_keys(config)
    if exposed:
        suggestions.append(f"⚠️  {len(exposed)} API key(s) in config — consider using env vars instead")

    return good, suggestions, issues

def main():
    config, path = load_config()
    print(f"📋 Analyzing: {path}\n")
    
    good, suggestions, issues = analyze(config)
    
    if good:
        print("=== Working Well ===")
        for g in good:
            print(f"  {g}")
        print()
    
    if suggestions:
        print("=== Suggestions ===")
        for s in suggestions:
            print(f"  {s}")
        print()
    
    if issues:
        print("=== Issues ===")
        for i in issues:
            print(f"  {i}")
        print()
    
    total = len(issues)
    print(f"Summary: {len(good)} good, {len(suggestions)} suggestions, {total} issues")
    if total == 0:
        print("🎉 Config looks healthy!")
    else:
        print(f"🔧 {total} issue(s) need attention")

if __name__ == "__main__":
    main()
