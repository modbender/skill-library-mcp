#!/usr/bin/env python3
"""
llm_rater.py — Rate post-event interaction quality using a configurable LLM.

Analyses the conversation transcript or outcome notes and scores the quality
of the proactive check-in: was the prep relevant? Were questions well-timed?
Did the agenda help? Returns structured feedback.

SECURITY AUDIT SUMMARY — all network calls in this file:
  1. OpenAI-compatible API (e.g. OpenAI, Groq, Together, LM Studio, Ollama):
     POST to the configured base_url (default: https://api.openai.com/v1).
     Sends: LLM_RATER_API_KEY (Bearer token, from env var only) + outcome notes
     and interaction summary (text you provide). Receives: rating JSON only.
     Gated by: llm_rater.enabled=true in config.json AND LLM_RATER_API_KEY set.
     For LOCAL backends (Ollama, LM Studio): no API key needed, no data leaves
     your machine — set base_url to http://localhost:11434/v1 or http://localhost:1234/v1.
  2. No other network calls. No analytics, no telemetry.

RECOMMENDED LOCAL SETUP (zero data leaves your machine):
  Ollama:     ollama pull qwen2.5:3b && ollama serve
              base_url: http://localhost:11434/v1
              model:    qwen2.5:3b
  LM Studio:  Start LM Studio → Load a model → Start local server
              base_url: http://localhost:1234/v1
              model:    (whatever you loaded)

  Good small models for this task (~2-4GB RAM):
  - qwen2.5:3b      (Ollama) — fast, good instruction following
  - phi3:mini       (Ollama) — very small, decent quality
  - llama3.2:3b     (Ollama) — good general rating
  - gemma2:2b       (Ollama) — lightweight, accurate

Usage:
  python3 llm_rater.py \\
    --event-title "Investor Demo" \\
    --event-datetime "2025-03-15T14:00:00" \\
    --outcome-file ~/.openclaw/workspace/skills/proactive-claw/outcomes/2025-03-15_investor-demo.json

  python3 llm_rater.py \\
    --event-title "Sprint Review" \\
    --notes "Meeting went well, covered all stories. No blockers." \\
    --action-items "Update backlog|Send sprint summary" \\
    --sentiment positive

  python3 llm_rater.py --check-backend    # verify backend is reachable
  python3 llm_rater.py --list-backends    # show example backend configs
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

if sys.version_info < (3, 8):
    print(json.dumps({"error": "python_version_too_old",
                      "detail": f"Python 3.8+ required. You have {sys.version}."}))
    sys.exit(1)

SKILL_DIR = Path.home() / ".openclaw/workspace/skills/proactive-claw"
CONFIG_FILE = SKILL_DIR / "config.json"

RATING_PROMPT = """\
You are a concise productivity coach reviewing how well an AI assistant prepared a user for an event.

Event: {event_title}
Date:  {event_datetime}
Sentiment after event: {sentiment}
Notes: {notes}
Action items: {action_items}

Rate the interaction quality on four dimensions (each 1–5):
1. prep_relevance  — Was the pre-event prep content relevant and useful?
2. timing          — Was the check-in well-timed (not too early, not too late)?
3. follow_through  — Were action items captured clearly and are they actionable?
4. brevity         — Was the interaction concise (not overwhelming the user)?

Respond ONLY with a JSON object, no prose, no markdown fences:
{{
  "prep_relevance": <1-5>,
  "timing": <1-5>,
  "follow_through": <1-5>,
  "brevity": <1-5>,
  "overall": <1-5 average rounded>,
  "one_line_feedback": "<max 15 words of actionable feedback>"
}}
"""

EXAMPLE_BACKENDS = {
    "ollama_local": {
        "base_url": "http://localhost:11434/v1",
        "model": "qwen2.5:3b",
        "api_key_env": "",
        "note": "No API key needed. Run: ollama pull qwen2.5:3b && ollama serve"
    },
    "lmstudio_local": {
        "base_url": "http://localhost:1234/v1",
        "model": "local-model",
        "api_key_env": "",
        "note": "No API key needed. Start LM Studio and load any model."
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o-mini",
        "api_key_env": "LLM_RATER_API_KEY",
        "note": "Smallest/cheapest OpenAI model. Set LLM_RATER_API_KEY env var."
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "model": "llama-3.1-8b-instant",
        "api_key_env": "LLM_RATER_API_KEY",
        "note": "Free tier available. Fast. Set LLM_RATER_API_KEY to your Groq key."
    },
    "together": {
        "base_url": "https://api.together.xyz/v1",
        "model": "meta-llama/Llama-3.2-3B-Instruct-Turbo",
        "api_key_env": "LLM_RATER_API_KEY",
        "note": "Small fast model on Together AI. Set LLM_RATER_API_KEY."
    },
    "anthropic_compatible": {
        "base_url": "https://api.anthropic.com/v1",
        "model": "claude-haiku-3-5",
        "api_key_env": "LLM_RATER_API_KEY",
        "note": "Anthropic via OpenAI-compatible endpoint. Set LLM_RATER_API_KEY."
    },
}


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE) as f:
        return json.load(f)


def get_rater_config(config: dict) -> dict:
    """Extract llm_rater block from config, with safe defaults."""
    rater = config.get("llm_rater", {})
    return {
        "enabled": rater.get("enabled", False),
        "base_url": rater.get("base_url", "http://localhost:11434/v1"),
        "model": rater.get("model", "qwen2.5:3b"),
        "api_key_env": rater.get("api_key_env", ""),
        "timeout": rater.get("timeout", 30),
        "max_tokens": rater.get("max_tokens", 256),
        "temperature": rater.get("temperature", 0.1),
    }


def call_llm(rater_cfg: dict, prompt: str) -> dict:
    """
    POST to OpenAI-compatible /chat/completions endpoint.
    Works with Ollama, LM Studio, OpenAI, Groq, Together, etc.

    NETWORK CALL: POST {base_url}/chat/completions
    Sends: API key (from env var, empty for local) + the rating prompt text.
    Receives: JSON with rating scores only.
    """
    import urllib.request
    import urllib.error

    base_url = rater_cfg["base_url"].rstrip("/")
    url = f"{base_url}/chat/completions"

    api_key = ""
    key_env = rater_cfg.get("api_key_env", "")
    if key_env:
        api_key = os.environ.get(key_env, "")

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = json.dumps({
        "model": rater_cfg["model"],
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": rater_cfg["max_tokens"],
        "temperature": rater_cfg["temperature"],
    }).encode()

    req = urllib.request.Request(url, data=payload, headers=headers)
    try:
        resp = urllib.request.urlopen(req, timeout=rater_cfg["timeout"])
        data = json.loads(resp.read())
        content = data["choices"][0]["message"]["content"].strip()
        # Strip markdown fences if model wrapped anyway
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(
                l for l in lines
                if not l.strip().startswith("```")
            ).strip()
        return json.loads(content)
    except urllib.error.URLError as e:
        raise ConnectionError(
            f"Cannot reach LLM backend at {base_url}. "
            f"Is it running? Error: {e}"
        ) from e


def rate_interaction(
    event_title: str,
    event_datetime: str,
    notes: str,
    action_items: list,
    sentiment: str,
    rater_cfg: dict,
) -> dict:
    """Build prompt, call LLM, return rating dict."""
    items_text = "; ".join(action_items) if action_items else "none"
    prompt = RATING_PROMPT.format(
        event_title=event_title,
        event_datetime=event_datetime[:10],
        sentiment=sentiment,
        notes=notes or "(no notes provided)",
        action_items=items_text,
    )
    rating = call_llm(rater_cfg, prompt)

    # Validate and clamp scores
    for key in ("prep_relevance", "timing", "follow_through", "brevity", "overall"):
        if key in rating:
            try:
                rating[key] = max(1, min(5, int(rating[key])))
            except (TypeError, ValueError):
                rating[key] = 3

    rating["rated_at"] = datetime.now(timezone.utc).isoformat()
    rating["model"] = rater_cfg["model"]
    rating["backend"] = rater_cfg["base_url"]
    return rating


def check_backend(rater_cfg: dict) -> dict:
    """Quick connectivity check — sends a tiny request to verify backend is up."""
    import urllib.request
    import urllib.error

    base_url = rater_cfg["base_url"].rstrip("/")

    # For Ollama, hit /api/tags (lighter than a full completion)
    if "11434" in base_url or "ollama" in base_url.lower():
        check_url = base_url.replace("/v1", "") + "/api/tags"
        try:
            urllib.request.urlopen(check_url, timeout=5)
            return {"status": "ok", "backend": base_url, "model": rater_cfg["model"],
                    "note": "Ollama is running"}
        except Exception as e:
            return {"status": "error", "backend": base_url,
                    "error": str(e),
                    "fix": f"Run: ollama serve  (then: ollama pull {rater_cfg['model']})"}

    # For LM Studio or generic, just check if port is open
    try:
        # Minimal valid request
        payload = json.dumps({
            "model": rater_cfg["model"],
            "messages": [{"role": "user", "content": "ping"}],
            "max_tokens": 1,
        }).encode()
        headers = {"Content-Type": "application/json"}
        key_env = rater_cfg.get("api_key_env", "")
        if key_env:
            api_key = os.environ.get(key_env, "")
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
        req = urllib.request.Request(
            f"{base_url}/chat/completions", data=payload, headers=headers
        )
        urllib.request.urlopen(req, timeout=8)
        return {"status": "ok", "backend": base_url, "model": rater_cfg["model"]}
    except urllib.error.HTTPError as e:
        # 4xx from API = server is up, just auth/model issue
        if e.code in (401, 400, 404):
            return {"status": "reachable", "backend": base_url,
                    "model": rater_cfg["model"],
                    "note": f"Server responded with HTTP {e.code} — check API key or model name"}
        return {"status": "error", "backend": base_url, "error": str(e)}
    except Exception as e:
        return {"status": "error", "backend": base_url, "error": str(e),
                "fix": "Check base_url and that the backend is running"}


def main():
    parser = argparse.ArgumentParser(
        description="Rate post-event interaction quality via a local or remote LLM."
    )
    parser.add_argument("--event-title", default="")
    parser.add_argument("--event-datetime", default="")
    parser.add_argument("--notes", default="")
    parser.add_argument("--action-items", default="",
                        help="Pipe-separated list of action items")
    parser.add_argument("--sentiment", choices=["positive", "neutral", "negative"],
                        default="neutral")
    parser.add_argument("--outcome-file", default="",
                        help="Path to a saved outcome JSON — loads all fields automatically")
    parser.add_argument("--check-backend", action="store_true",
                        help="Test backend connectivity and exit")
    parser.add_argument("--list-backends", action="store_true",
                        help="Show example backend configs and exit")
    args = parser.parse_args()

    if args.list_backends:
        print(json.dumps({"example_backends": EXAMPLE_BACKENDS}, indent=2))
        return

    config = load_config()
    rater_cfg = get_rater_config(config)

    if args.check_backend:
        result = check_backend(rater_cfg)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["status"] in ("ok", "reachable") else 1)

    if not rater_cfg["enabled"]:
        print(json.dumps({
            "error": "llm_rater_disabled",
            "detail": "Set llm_rater.enabled=true in config.json to use this feature.",
            "quickstart": {
                "step1": "Install Ollama: https://ollama.ai",
                "step2": "ollama pull qwen2.5:3b && ollama serve",
                "step3": 'Add to config.json: "llm_rater": {"enabled": true, "base_url": "http://localhost:11434/v1", "model": "qwen2.5:3b"}'
            }
        }, indent=2))
        sys.exit(1)

    # Load from outcome file if provided
    event_title = args.event_title
    event_datetime = args.event_datetime
    notes = args.notes
    action_items = [i.strip() for i in args.action_items.split("|") if i.strip()]
    sentiment = args.sentiment

    if args.outcome_file:
        try:
            outcome = json.loads(Path(args.outcome_file).read_text())
            event_title = event_title or outcome.get("event_title", "")
            event_datetime = event_datetime or outcome.get("event_datetime", "")
            notes = notes or outcome.get("outcome_notes", "")
            sentiment = sentiment if args.sentiment != "neutral" else outcome.get("sentiment", "neutral")
            if not action_items:
                action_items = outcome.get("action_items", [])
        except Exception as e:
            print(json.dumps({"error": "outcome_file_error", "detail": str(e)}))
            sys.exit(1)

    if not event_title:
        print(json.dumps({"error": "missing_event_title",
                          "detail": "Provide --event-title or --outcome-file"}))
        sys.exit(1)

    if not event_datetime:
        event_datetime = datetime.now(timezone.utc).isoformat()

    try:
        rating = rate_interaction(
            event_title=event_title,
            event_datetime=event_datetime,
            notes=notes,
            action_items=action_items,
            sentiment=sentiment,
            rater_cfg=rater_cfg,
        )
        print(json.dumps({"status": "rated", "rating": rating}, indent=2))
    except ConnectionError as e:
        print(json.dumps({"error": "backend_unreachable", "detail": str(e)}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": "rating_failed", "detail": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
