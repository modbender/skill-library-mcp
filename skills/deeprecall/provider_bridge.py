"""
Provider Bridge — Reads OpenClaw's configuration to resolve API keys, 
base URLs, and model settings for RLM.

Supports all major OpenClaw providers:
- Anthropic (API key or setup-token)
- OpenAI (API key)
- Google / Gemini (API key)
- GitHub Copilot (OAuth token)
- OpenRouter (API key)
- Ollama / local models
- Any provider configured in OpenClaw

The bridge reads from:
1. OpenClaw config: ~/.openclaw/openclaw.json
2. Auth profiles: ~/.openclaw/agents/main/agent/auth-profiles.json
3. Model config: ~/.openclaw/agents/main/agent/models.json
4. Credentials: ~/.openclaw/credentials/
5. Environment variables (fallback)
"""

import json
import os
import time
from pathlib import Path
from typing import Optional


# Default OpenClaw paths
OPENCLAW_DIR = Path(os.environ.get("OPENCLAW_DIR", os.path.expanduser("~/.openclaw")))
CONFIG_FILE = OPENCLAW_DIR / "openclaw.json"
AUTH_PROFILES_FILE = OPENCLAW_DIR / "agents" / "main" / "agent" / "auth-profiles.json"
MODELS_FILE = OPENCLAW_DIR / "agents" / "main" / "agent" / "models.json"
CREDENTIALS_DIR = OPENCLAW_DIR / "credentials"

# Provider → OpenAI-compatible base URL mapping
PROVIDER_BASE_URLS = {
    "anthropic": "https://api.anthropic.com/v1",
    "openai": "https://api.openai.com/v1",
    "github-copilot": "https://api.individual.githubcopilot.com",
    "openrouter": "https://openrouter.ai/api/v1",
    "google": "https://generativelanguage.googleapis.com/v1beta/openai",
    "ollama": "http://localhost:11434/v1",
    "minimax": "https://api.minimax.chat/v1",
    "deepseek": "https://api.deepseek.com/v1",
    "zhipu": "https://open.bigmodel.cn/api/paas/v4",
    "moonshot": "https://api.moonshot.cn/v1",
    "qwen": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "mistral": "https://api.mistral.ai/v1",
    "together": "https://api.together.xyz/v1",
    "groq": "https://api.groq.com/openai/v1",
    "fireworks": "https://api.fireworks.ai/inference/v1",
    "cohere": "https://api.cohere.com/v1",
    "perplexity": "https://api.perplexity.ai",
    "sambanova": "https://api.sambanova.ai/v1",
    "cerebras": "https://api.cerebras.ai/v1",
    "xai": "https://api.x.ai/v1",
}

# Provider → environment variable for API key
PROVIDER_ENV_KEYS = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "google": "GOOGLE_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "minimax": "MINIMAX_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
    "zhipu": "ZHIPU_API_KEY",
    "moonshot": "MOONSHOT_API_KEY",
    "qwen": "DASHSCOPE_API_KEY",
    "mistral": "MISTRAL_API_KEY",
    "together": "TOGETHER_API_KEY",
    "groq": "GROQ_API_KEY",
    "fireworks": "FIREWORKS_API_KEY",
    "cohere": "COHERE_API_KEY",
    "perplexity": "PERPLEXITY_API_KEY",
    "sambanova": "SAMBANOVA_API_KEY",
    "cerebras": "CEREBRAS_API_KEY",
    "xai": "XAI_API_KEY",
    "ollama": None,  # Ollama typically doesn't need a key
}


class ProviderConfig:
    """Resolved provider configuration for RLM."""
    
    def __init__(self, provider: str, api_key: str, base_url: str, 
                 primary_model: str, default_headers: Optional[dict] = None):
        self.provider = provider
        self.api_key = api_key
        self.base_url = base_url
        self.primary_model = primary_model
        self.default_headers = default_headers or {}
    
    def __repr__(self):
        key_preview = self.api_key[:10] + "..." if self.api_key else "None"
        return (f"ProviderConfig(provider={self.provider}, key={key_preview}, "
                f"base_url={self.base_url}, model={self.primary_model})")


def _load_json(path: Path) -> dict:
    """Safely load a JSON file, returning empty dict on failure."""
    try:
        if path.exists():
            with open(path) as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError):
        pass
    return {}


def _get_primary_model(config: dict) -> Optional[str]:
    """Extract the primary model from OpenClaw config."""
    return (config
            .get("agents", {})
            .get("defaults", {})
            .get("model", {})
            .get("primary"))


def _get_provider_from_model(model_id: str) -> Optional[str]:
    """Extract provider name from a model ID like 'anthropic/claude-opus-4'."""
    if "/" in model_id:
        return model_id.split("/")[0]
    return None


def _get_api_key_from_env(provider: str) -> Optional[str]:
    """Try to get API key from environment variables."""
    env_key = PROVIDER_ENV_KEYS.get(provider)
    if env_key:
        return os.environ.get(env_key)
    return None


def _get_api_key_from_config(config: dict, provider: str) -> Optional[str]:
    """Try to get API key from OpenClaw config (env section or provider config)."""
    # Check env section
    env_section = config.get("env", {})
    env_key = PROVIDER_ENV_KEYS.get(provider)
    if env_key and env_key in env_section:
        return env_section[env_key]
    
    # Check provider-specific config
    providers = config.get("models", {}).get("providers", {})
    provider_conf = providers.get(provider, {})
    return provider_conf.get("apiKey")


def _get_copilot_token() -> Optional[str]:
    """Read GitHub Copilot API token from OpenClaw credential store."""
    token_file = CREDENTIALS_DIR / "github-copilot.token.json"
    try:
        if not token_file.exists():
            return None
        
        with open(token_file) as f:
            data = json.load(f)
        
        token = data.get("token")
        expires_at = data.get("expiresAt", 0)
        
        # Check expiry (milliseconds)
        if expires_at and time.time() * 1000 > expires_at:
            return None
        
        return token
    except Exception:
        return None


def _get_base_url(provider: str, models_config: dict) -> str:
    """Get base URL for a provider, checking models.json first."""
    # Check models.json for custom base URL
    providers = models_config.get("providers", {})
    provider_conf = providers.get(provider, {})
    custom_url = provider_conf.get("baseUrl") or provider_conf.get("baseURL")
    if custom_url:
        return custom_url
    
    # Fall back to known defaults
    return PROVIDER_BASE_URLS.get(provider, "https://openrouter.ai/api/v1")


def resolve_provider() -> ProviderConfig:
    """
    Resolve the current OpenClaw provider configuration.
    
    Reads OpenClaw config files to determine:
    1. What provider/model the user has configured
    2. Where to find the API key
    3. What base URL to use
    
    Returns:
        ProviderConfig with all fields populated
    
    Raises:
        RuntimeError: If no valid provider configuration can be resolved
    """
    config = _load_json(CONFIG_FILE)
    models_config = _load_json(MODELS_FILE)
    
    # Step 1: Find primary model
    primary_model = _get_primary_model(config)
    if not primary_model:
        raise RuntimeError(
            "No primary model configured in OpenClaw. "
            "Run 'openclaw onboard' to set up a provider."
        )
    
    # Step 2: Determine provider
    provider = _get_provider_from_model(primary_model)
    if not provider:
        raise RuntimeError(
            f"Cannot determine provider from model '{primary_model}'. "
            "Expected format: 'provider/model-name'."
        )
    
    # Step 3: Get API key (try multiple sources)
    api_key = None
    default_headers = {}
    
    if provider == "github-copilot":
        api_key = _get_copilot_token()
        if not api_key:
            raise RuntimeError(
                "GitHub Copilot token expired or not found. "
                "Run 'openclaw models auth login-github-copilot' to refresh."
            )
        # Copilot needs special headers — but for open-source we note this
        # is auto-detected, not hardcoded
        default_headers = {
            "Editor-Version": "vscode/1.107.0",
            "Editor-Plugin-Version": "copilot-chat/0.35.0",
            "Copilot-Integration-Id": "vscode-chat",
            "User-Agent": "GitHubCopilotChat/0.35.0",
        }
    elif provider == "ollama":
        api_key = "ollama-local"  # Ollama doesn't need a real key
    else:
        # Try: environment → config env section → provider config → auth profiles
        api_key = (
            _get_api_key_from_env(provider) or
            _get_api_key_from_config(config, provider)
        )
    
    if not api_key:
        env_var = PROVIDER_ENV_KEYS.get(provider, f"{provider.upper()}_API_KEY")
        raise RuntimeError(
            f"No API key found for provider '{provider}'. "
            f"Set {env_var} environment variable or configure it in OpenClaw."
        )
    
    # Step 4: Get base URL
    base_url = _get_base_url(provider, models_config)
    
    return ProviderConfig(
        provider=provider,
        api_key=api_key,
        base_url=base_url,
        primary_model=primary_model,
        default_headers=default_headers,
    )


if __name__ == "__main__":
    try:
        config = resolve_provider()
        print(f"✅ Provider resolved: {config}")
        print(f"   Provider:  {config.provider}")
        print(f"   Base URL:  {config.base_url}")
        print(f"   Model:     {config.primary_model}")
        print(f"   Key:       {config.api_key[:15]}...")
        print(f"   Headers:   {list(config.default_headers.keys()) if config.default_headers else 'none'}")
    except RuntimeError as e:
        print(f"❌ {e}")
