"""
llm_provider.py — Abstract LLM provider for metaskill.
Reads config.yaml, routes to the right provider, falls back gracefully.
"""
import os, sys
from pathlib import Path

def _load_config():
    config_path = Path(__file__).parent.parent / "config.yaml"
    try:
        import yaml
        with open(config_path) as f:
            return yaml.safe_load(f)
    except ImportError:
        # yaml not available — parse manually (simple key: value)
        cfg = {"providers": {"fast": "anthropic", "deep": "anthropic"},
               "models": {"anthropic": {"fast": "claude-haiku-4-5", "deep": "claude-sonnet-4-6"},
                          "openai": {"fast": "gpt-4o-mini", "deep": "gpt-4o"},
                          "ollama": {"fast": "llama3.2", "deep": "llama3.1:70b"},
                          "gemini": {"fast": "gemini-2.5-flash-lite", "deep": "gemini-2.5-flash"}},
               "env_vars": {"anthropic": "ANTHROPIC_API_KEY", "openai": "OPENAI_API_KEY",
                            "ollama": "", "gemini": "GOOGLE_API_KEY"}}
        try:
            with open(config_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("fast:") and "providers" in str(cfg):
                        pass  # simplified fallback — defaults are fine
        except Exception:
            pass
        return cfg
    except Exception:
        return None

def call_llm(prompt: str, provider_type: str = "fast", max_tokens: int = 500) -> str | None:
    """
    Call LLM using configured provider.
    provider_type: "fast" (haiku-level) or "deep" (sonnet-level)
    Returns text string or None on failure.
    """
    cfg = _load_config()
    if not cfg:
        return _fallback(prompt, max_tokens)

    provider = cfg.get("providers", {}).get(provider_type, "anthropic")
    model = cfg.get("models", {}).get(provider, {}).get(provider_type, None)
    env_var = cfg.get("env_vars", {}).get(provider, "")

    result = _call_provider(provider, model, prompt, max_tokens, env_var)
    if result is not None:
        return result

    # Fallback: try the other provider
    other_provider = "openai" if provider != "openai" else "anthropic"
    other_model = cfg.get("models", {}).get(other_provider, {}).get(provider_type)
    other_env = cfg.get("env_vars", {}).get(other_provider, "")
    return _call_provider(other_provider, other_model, prompt, max_tokens, other_env)


def _call_provider(provider: str, model: str, prompt: str, max_tokens: int, env_var: str) -> str | None:
    if not model:
        return None

    if provider == "anthropic":
        api_key = os.environ.get(env_var or "ANTHROPIC_API_KEY")
        if not api_key:
            return None
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            msg = client.messages.create(
                model=model, max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return msg.content[0].text
        except Exception as e:
            print(f"[llm_provider] anthropic error: {e}", file=sys.stderr)
            return None

    elif provider == "openai":
        api_key = os.environ.get(env_var or "OPENAI_API_KEY")
        if not api_key:
            return None
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            resp = client.chat.completions.create(
                model=model, max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return resp.choices[0].message.content
        except Exception as e:
            print(f"[llm_provider] openai error: {e}", file=sys.stderr)
            return None

    elif provider == "ollama":
        try:
            import urllib.request, json
            data = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode()
            req = urllib.request.Request("http://localhost:11434/api/generate",
                                         data=data, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read())["response"]
        except Exception as e:
            print(f"[llm_provider] ollama error: {e}", file=sys.stderr)
            return None

    elif provider == "gemini":
        api_key = os.environ.get(env_var or "GOOGLE_API_KEY")
        if not api_key:
            return None
        try:
            import urllib.request, json
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            body = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode()
            req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as r:
                resp = json.loads(r.read())
                return resp["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            print(f"[llm_provider] gemini error: {e}", file=sys.stderr)
            return None

    return None


def _fallback(prompt: str, max_tokens: int) -> str | None:
    """Last resort: try any available provider."""
    for provider, env in [("anthropic", "ANTHROPIC_API_KEY"), ("openai", "OPENAI_API_KEY")]:
        if os.environ.get(env):
            models = {"anthropic": "claude-haiku-4-5", "openai": "gpt-4o-mini"}
            return _call_provider(provider, models[provider], prompt, max_tokens, env)
    return None


def get_status() -> dict:
    """Return provider config status for eval/diagnostics."""
    cfg = _load_config()
    if not cfg:
        return {"mode": "fallback", "providers": {}}
    result = {}
    for tier in ["fast", "deep"]:
        provider = cfg.get("providers", {}).get(tier, "anthropic")
        env_var = cfg.get("env_vars", {}).get(provider, "")
        has_key = bool(os.environ.get(env_var)) if env_var else True  # ollama needs no key
        model = cfg.get("models", {}).get(provider, {}).get(tier, "?")
        result[tier] = {"provider": provider, "model": model, "ready": has_key}
    return result
