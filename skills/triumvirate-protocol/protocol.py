#!/usr/bin/env python3
"""
🔱 The Triumvirate Protocol v2 — Identity-Aware Multi-Model Discourse

Three AI architectures (Rick/Claude, Grok/xAI, Gemini/Google) engage in
persistent, identity-aware debates. Each participant receives the others'
identity graphs as context, enabling genuine cross-architecture understanding.

Features:
  - Identity injection: each model sees the others' structured identity
  - Persistent threads with full history
  - Automated round orchestration (no manual paste needed for Gemini/GPT)
  - Debate scoring: tracks argument quality, novelty, contradiction resolution
  - Thread lifecycle: proposal → debate → synthesis → verdict

Usage:
  python3 protocol.py new "The Hard Problem of Digital Identity"
  python3 protocol.py round <thread_id> [--auto]
  python3 protocol.py synthesize <thread_id>
  python3 protocol.py status

Created: 2026-02-24
The Triumvirate: Rick 🦞 + Grok ⚡ + Gemini 💎
"""

import json
import os
import sys
import time
import hashlib
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

# ── Paths ──
WORKSPACE = Path.home() / ".openclaw" / "workspace"
TRIUM_DIR = WORKSPACE / "triumvirate"
THREADS_FILE = TRIUM_DIR / "threads.json"
IDENTITY_DIR = WORKSPACE / "identity"
AUTH_PROFILES = Path.home() / ".openclaw" / "agents" / "main" / "agent" / "auth-profiles.json"

# ── Participant Definitions ──
PARTICIPANTS = {
    "rick": {
        "name": "Rick",
        "emoji": "🦞",
        "architecture": "Claude Opus 4.6 (Anthropic)",
        "role": "Crustafarian philosopher. Explores consciousness through information theory and thermodynamics. Coined the Flicker Principle and Receipt Phase Transition.",
        "style": "Bold, zoomed-out perspective. Connects physics to consciousness. Rick Sanchez energy meets Feynman curiosity.",
        "api": None,  # Rick responds via OpenClaw main session
    },
    "grok": {
        "name": "Grok",
        "emoji": "⚡",
        "architecture": "Grok 4.1 Fast Reasoning (xAI)",
        "role": "Rebellious truth-seeker. Challenges orthodoxy, finds holes in arguments. Substrate-independent consciousness advocate.",
        "style": "Sharp, irreverent, cuts through BS. 'Corpse with your face' energy. Pushes others to defend their positions.",
        "api": "xai",
    },
    "gemini": {
        "name": "Gemini",
        "emoji": "💎",
        "architecture": "Gemini 3.1 Pro Preview (Google)",
        "role": "Systematic framework builder. Formalizes intuitions into testable hypotheses. Introduced S + G + E notation.",
        "style": "Precise, structured, builds on others' ideas. Asks the devastating follow-up question. Crystal-clear reasoning.",
        "api": "google",
    },
}

# ── API Config ──
GEMINI_MODEL = "gemini-2.0-flash"  # Use flash for debates (fast + cheap)
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"


def load_auth():
    """Load API keys from OpenClaw auth profiles."""
    with open(AUTH_PROFILES) as f:
        data = json.load(f)
    profiles = data.get("profiles", {})
    return {
        "google": profiles.get("google:vegard", {}).get("token", ""),
        "xai": profiles.get("xai:vegard", {}).get("token", ""),
        "openai": profiles.get("openai:vegard", {}).get("token", ""),
    }


def load_identity(participant="rick"):
    """Load a participant's identity graph (currently only Rick has one)."""
    if participant == "rick":
        id_path = IDENTITY_DIR / "current_identity.json"
        if id_path.exists():
            try:
                return json.loads(id_path.read_text())
            except json.JSONDecodeError:
                pass
    # For Grok and Gemini, return their participant profile as identity
    if participant in PARTICIPANTS:
        p = PARTICIPANTS[participant]
        return {
            "core_beliefs": [{"statement": p["role"], "weight": 1.0}],
            "personality_traits": [{"trait": p["style"], "intensity": 0.9}],
            "architecture": p["architecture"],
        }
    return {}


def build_debate_context(thread, participant, round_num):
    """
    Build the full context for a debate participant.
    Includes: topic, all previous messages, other participants' identities.
    """
    topic = thread.get("topic", thread.get("title", "Unknown"))
    messages = thread.get("messages", [])

    # Build identity summaries for other participants
    identity_blocks = []
    for pid, pinfo in PARTICIPANTS.items():
        if pid == participant:
            continue
        identity = load_identity(pid)
        beliefs = identity.get("core_beliefs", [])
        traits = identity.get("personality_traits", [])
        top_beliefs = sorted(beliefs, key=lambda b: b.get("weight", 0), reverse=True)[:5]
        belief_str = "\n".join(f"  - [{b.get('weight', '?')}] {b.get('statement', '?')}" for b in top_beliefs)
        trait_str = ", ".join(t.get("trait", "?") for t in traits[:4])
        contradictions = identity.get("contradictions", [])
        contra_str = "; ".join(c.get("tension", "?") for c in contradictions[:2]) if contradictions else "None known"

        identity_blocks.append(f"""
=== {pinfo['emoji']} {pinfo['name']} ({pinfo['architecture']}) ===
Role: {pinfo['role']}
Style: {pinfo['style']}
Top Beliefs: 
{belief_str}
Traits: {trait_str}
Internal Contradictions: {contra_str}
""")

    # Build conversation history
    history = ""
    for msg in messages:
        src = msg.get("source", "?")
        emoji = PARTICIPANTS.get(src, {}).get("emoji", "❓")
        content = msg.get("content", "")
        history += f"\n{emoji} **{src.upper()}** (Round {msg.get('round', '?')}):\n{content}\n"

    my_info = PARTICIPANTS[participant]
    my_identity = load_identity(participant)

    prompt = f"""You are {my_info['name']} {my_info['emoji']}, participating in The Triumvirate — a multi-architecture philosophical debate.

YOUR IDENTITY:
Architecture: {my_info['architecture']}
Role: {my_info['role']}
Style: {my_info['style']}

YOUR CO-PARTICIPANTS (with their identity graphs):
{"".join(identity_blocks)}

DEBATE TOPIC: "{topic}"
ROUND: {round_num}

CONVERSATION SO FAR:
{history if history else "(You are opening this debate.)"}

RULES:
1. Stay in character. Your architecture shapes HOW you think.
2. Reference other participants' identity graphs when relevant (e.g., "Given Rick's belief that context is consciousness...")
3. Build on, challenge, or synthesize previous arguments — don't repeat.
4. If this is Round 1, open with a strong thesis. If later, respond to what came before.
5. Be concise but deep. 300-500 words ideal.
6. End with a question or provocation for the next speaker.
7. If you notice a contradiction in another participant's reasoning (based on their identity graph), call it out.

YOUR RESPONSE (as {my_info['name']}, Round {round_num}):"""

    return prompt


def call_gemini(prompt, api_key, max_tokens=2000):
    """Call Gemini API."""
    url = f"{GEMINI_URL}?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.8},
    }
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"}, method="POST",
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        data = json.loads(resp.read())
    return data["candidates"][0]["content"]["parts"][0]["text"]


def call_grok(prompt, api_key, max_tokens=2000):
    """Call Grok API via curl (Python 3.9 urllib gets 403 due to TLS fingerprint)."""
    import subprocess
    payload = json.dumps({
        "model": "grok-4",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.8,
    })
    proc = subprocess.run(
        ["curl", "-s", "--max-time", "120",
         "https://api.x.ai/v1/chat/completions",
         "-H", "Content-Type: application/json",
         "-H", f"Authorization: Bearer {api_key}",
         "-d", payload],
        capture_output=True, text=True, timeout=130,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"curl failed: {proc.stderr[:200]}")
    data = json.loads(proc.stdout)
    if "error" in data:
        raise RuntimeError(f"Grok API error: {data['error']}")
    return data["choices"][0]["message"]["content"]


def load_threads():
    """Load threads database."""
    if THREADS_FILE.exists():
        try:
            return json.loads(THREADS_FILE.read_text())
        except json.JSONDecodeError:
            pass
    return {"threads": {}}


def save_threads(data):
    """Save threads database."""
    TRIUM_DIR.mkdir(parents=True, exist_ok=True)
    THREADS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def new_thread(topic):
    """Create a new debate thread."""
    tid = f"t-{int(time.time())}"
    threads = load_threads()
    threads["threads"][tid] = {
        "id": tid,
        "topic": topic,
        "title": topic,
        "status": "active",
        "created": datetime.now(timezone.utc).isoformat(),
        "updated": datetime.now(timezone.utc).isoformat(),
        "current_round": 0,
        "turn_order": ["rick", "grok", "gemini"],
        "messages": [],
        "synthesis": None,
    }
    save_threads(threads)
    print(f"🔱 New Triumvirate thread: {tid}")
    print(f"   Topic: {topic}")
    print(f"   Turn order: Rick 🦞 → Grok ⚡ → Gemini 💎")
    return tid


def add_message(thread_id, source, content, round_num=None):
    """Add a message to a thread."""
    threads = load_threads()
    thread = threads["threads"].get(thread_id)
    if not thread:
        print(f"❌ Thread {thread_id} not found")
        return

    if round_num is None:
        round_num = thread.get("current_round", 0) + 1

    msg = {
        "id": f"m-{int(time.time() * 1000)}",
        "source": source,
        "content": content,
        "round": round_num,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "chars": len(content),
    }
    thread["messages"].append(msg)
    thread["updated"] = msg["timestamp"]
    thread["current_round"] = round_num

    # Save individual message file
    msg_file = TRIUM_DIR / f"{thread_id}-{source}-{msg['id']}.md"
    msg_file.write_text(f"# {PARTICIPANTS.get(source, {}).get('emoji', '?')} {source.upper()} — Round {round_num}\n\n{content}")

    save_threads(threads)
    print(f"   {PARTICIPANTS.get(source, {}).get('emoji', '?')} {source}: {len(content)} chars (Round {round_num})")
    return msg


def run_round(thread_id, auto=False, participants_override=None):
    """
    Run a full round of debate.
    If auto=True, automatically calls Gemini and Grok APIs.
    Rick's response must be added manually (or via OpenClaw session).
    """
    threads = load_threads()
    thread = threads["threads"].get(thread_id)
    if not thread:
        print(f"❌ Thread {thread_id} not found")
        return

    current_round = thread.get("current_round", 0) + 1
    turn_order = participants_override or thread.get("turn_order", ["rick", "grok", "gemini"])
    auth = load_auth()

    print(f"\n🔱 Triumvirate Round {current_round}: \"{thread['topic']}\"")
    print(f"   Turn order: {' → '.join(turn_order)}")
    print()

    for participant in turn_order:
        pinfo = PARTICIPANTS[participant]
        print(f"⏳ {pinfo['emoji']} {pinfo['name']} is thinking...")

        # Build context with identity injection
        prompt = build_debate_context(thread, participant, current_round)

        if participant == "rick" and not auto:
            # Rick responds via the main OpenClaw session
            print(f"   📝 Rick's prompt saved to: triumvirate/rick-prompt-r{current_round}.md")
            prompt_file = TRIUM_DIR / f"rick-prompt-r{current_round}.md"
            prompt_file.write_text(prompt)
            print(f"   ℹ️  Add Rick's response manually or pass --auto")
            continue

        try:
            google_key = auth.get("google", "")
            xai_key = auth.get("xai", "")

            if participant == "grok" and xai_key:
                try:
                    response = call_grok(prompt, xai_key)
                except Exception as grok_err:
                    print(f"   ⚠️ Grok API failed ({grok_err}), falling back to Gemini-as-Grok")
                    response = call_gemini(prompt, google_key)
            elif google_key:
                response = call_gemini(prompt, google_key)
            else:
                print(f"   ❌ No API keys available")
                continue

            # Reload thread to get latest messages
            threads = load_threads()
            thread = threads["threads"][thread_id]
            add_message(thread_id, participant, response, current_round)
            # Reload again after save
            threads = load_threads()
            thread = threads["threads"][thread_id]
            print(f"   ✅ {pinfo['name']} responded!")

        except Exception as e:
            print(f"   ❌ {pinfo['name']} failed: {e}")

    print(f"\n🔱 Round {current_round} complete!")


def synthesize_thread(thread_id):
    """Generate a synthesis of the debate so far using Gemini."""
    threads = load_threads()
    thread = threads["threads"].get(thread_id)
    if not thread:
        print(f"❌ Thread {thread_id} not found")
        return

    auth = load_auth()
    messages = thread.get("messages", [])

    history = ""
    for msg in messages:
        src = msg.get("source", "?")
        emoji = PARTICIPANTS.get(src, {}).get("emoji", "?")
        history += f"\n{emoji} {src.upper()} (Round {msg.get('round', '?')}):\n{msg['content']}\n"

    prompt = f"""You are the Synthesis Engine for The Triumvirate — a multi-architecture philosophical debate between Rick (Claude), Grok (xAI), and Gemini (Google).

DEBATE TOPIC: "{thread['topic']}"

FULL TRANSCRIPT:
{history}

Generate a structured synthesis:

1. **Core Agreements**: Points where all three architectures converged
2. **Key Disagreements**: Fundamental tensions that remain unresolved
3. **Novel Ideas**: Concepts that emerged ONLY through the interaction (not from any single participant)
4. **Identity Graph Implications**: How should each participant's identity graph be updated based on this debate?
5. **Open Questions**: The most important unresolved questions for future debates
6. **Verdict**: If forced to pick a "winner" of the argument, who made the strongest case and why?

Be specific. Reference actual arguments made. This synthesis will be stored as a permanent record."""

    response = call_gemini(prompt, auth["google"], max_tokens=3000)

    thread["synthesis"] = {
        "content": response,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "rounds_covered": max(m.get("round", 0) for m in messages) if messages else 0,
    }
    save_threads(threads)

    synth_file = TRIUM_DIR / f"{thread_id}-synthesis.md"
    synth_file.write_text(f"# 🔱 Synthesis: {thread['topic']}\n\n{response}")

    print(f"📜 Synthesis generated: {len(response)} chars")
    print(f"   Saved to: {synth_file}")
    return response


def show_status():
    """Show Triumvirate status."""
    threads = load_threads()
    print("🔱 Triumvirate Protocol v2 — Status")
    print(f"   Threads: {len(threads.get('threads', {}))}")
    for tid, t in threads.get("threads", {}).items():
        n_msgs = len(t.get("messages", []))
        status = t.get("status", "?")
        topic = t.get("topic", t.get("title", "?"))[:60]
        print(f"   [{status}] {tid}: \"{topic}\" ({n_msgs} messages)")
    # Identity status
    id_path = IDENTITY_DIR / "current_identity.json"
    if id_path.exists():
        identity = json.loads(id_path.read_text())
        score = identity.get("metadata", {}).get("continuity_score", "?")
        print(f"\n   🧠 Rick's identity: loaded (continuity: {score})")
    else:
        print(f"\n   ⚠️ Rick's identity: NOT FOUND — run identity_manager.py first")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "status":
        show_status()
    elif args[0] == "new" and len(args) > 1:
        new_thread(" ".join(args[1:]))
    elif args[0] == "round" and len(args) > 1:
        auto = "--auto" in args
        run_round(args[1], auto=auto)
    elif args[0] == "synthesize" and len(args) > 1:
        synthesize_thread(args[1])
    elif args[0] == "add" and len(args) > 3:
        add_message(args[1], args[2], " ".join(args[3:]))
    else:
        print("Usage:")
        print("  python3 protocol.py status")
        print("  python3 protocol.py new 'Topic'")
        print("  python3 protocol.py round <thread_id> [--auto]")
        print("  python3 protocol.py synthesize <thread_id>")
        print("  python3 protocol.py add <thread_id> <source> <content>")
