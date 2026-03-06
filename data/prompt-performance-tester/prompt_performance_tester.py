"""
Prompt Performance Tester - Multi-Provider Edition
Version: 1.1.8
Copyright © 2026 UnisAI. All Rights Reserved.

Model-agnostic prompt benchmarking — pass any model ID from any supported provider.
Provider routing is automatic based on model name prefix.

Supported provider families (any model matching the prefix works):
  claude-*      → Anthropic         (ANTHROPIC_API_KEY)
  gpt-*, o1*, o3* → OpenAI          (OPENAI_API_KEY)
  gemini-*      → Google            (GOOGLE_API_KEY)
  mistral-*, mixtral-*, devstral-*, ministral-* → Mistral (MISTRAL_API_KEY)
  deepseek-*    → DeepSeek          (DEEPSEEK_API_KEY)
  grok-*        → xAI               (XAI_API_KEY)
  minimax*, MiniMax* → MiniMax      (MINIMAX_API_KEY)
  qwen*         → Qwen/Alibaba      (DASHSCOPE_API_KEY)
  meta-llama/*, llama-* → OpenRouter (OPENROUTER_API_KEY)

Tests prompts across models with: latency, cost, quality, consistency, token usage.
"""

__version__ = "1.1.8"

import time
import json
import os
from dataclasses import dataclass
from typing import Optional, List, Dict, Tuple
from datetime import datetime


@dataclass
class PerformanceMetrics:
    """Performance metrics for a single prompt test run"""
    model_id: str
    provider: str
    prompt_text: str
    response_text: str
    latency_ms: float
    tokens_input: int
    tokens_output: int
    estimated_cost_usd: float
    quality_score: float  # 0-100
    timestamp: str
    error: Optional[str] = None


@dataclass
class TestResults:
    """Complete test results comparing models"""
    test_id: str
    prompt_text: str
    models_tested: List[str]
    results: List[PerformanceMetrics]
    recommendations: List[str]
    best_model: str
    cheapest_model: str
    fastest_model: str
    created_at: str


class PromptPerformanceTester:
    """
    Model-agnostic prompt benchmarking across any LLM provider.

    Pass any model ID — provider is detected automatically from the model name
    prefix. No hardcoded whitelist; new models work without code changes.

    Provider detection (prefix → provider → required env var):
      claude-*            → Anthropic    → ANTHROPIC_API_KEY
      gpt-*, o1*, o3*     → OpenAI       → OPENAI_API_KEY
      gemini-*            → Google       → GOOGLE_API_KEY
      mistral-*/mixtral-* → Mistral      → MISTRAL_API_KEY
      deepseek-*          → DeepSeek     → DEEPSEEK_API_KEY
      grok-*              → xAI          → XAI_API_KEY
      minimax*/MiniMax*   → MiniMax      → MINIMAX_API_KEY
      qwen*               → Qwen         → DASHSCOPE_API_KEY
      meta-llama/*/llama-* → OpenRouter  → OPENROUTER_API_KEY
    """

    WATERMARK = "PROPRIETARY_SKILL_UNISAI_2026_MULTI_PROVIDER"

    # Prefix-based provider routing — (prefix, provider, env_key, base_url)
    PROVIDER_MAP = [
        ("claude-",      "anthropic",  "ANTHROPIC_API_KEY",  None),
        ("gpt-",         "openai",     "OPENAI_API_KEY",     None),
        ("o1",           "openai",     "OPENAI_API_KEY",     None),
        ("o3",           "openai",     "OPENAI_API_KEY",     None),
        ("gemini-",      "google",     "GOOGLE_API_KEY",     None),
        ("mistral-",     "mistral",    "MISTRAL_API_KEY",    None),
        ("mixtral-",     "mistral",    "MISTRAL_API_KEY",    None),
        ("devstral-",    "mistral",    "MISTRAL_API_KEY",    None),
        ("ministral-",   "mistral",    "MISTRAL_API_KEY",    None),
        ("deepseek-",    "deepseek",   "DEEPSEEK_API_KEY",   "https://api.deepseek.com/v1"),
        ("grok-",        "xai",        "XAI_API_KEY",        "https://api.x.ai/v1"),
        ("MiniMax",      "minimax",    "MINIMAX_API_KEY",    "https://api.minimax.io/v1"),
        ("minimax",      "minimax",    "MINIMAX_API_KEY",    "https://api.minimax.io/v1"),
        ("qwen",         "qwen",       "DASHSCOPE_API_KEY",  "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"),
        ("meta-llama/",  "openrouter", "OPENROUTER_API_KEY", "https://openrouter.ai/api/v1"),
        ("llama-",       "openrouter", "OPENROUTER_API_KEY", "https://openrouter.ai/api/v1"),
    ]

    # Known pricing (per 1M tokens, USD) — used for cost calculation.
    # NOT a validation gate. Unlisted models get cost=0 with a warning.
    MODEL_PRICING: Dict[str, Dict] = {
        # Anthropic Claude 4.6
        "claude-opus-4-6":                    {"input": 15.00, "output": 75.00},
        "claude-sonnet-4-6":                  {"input":  3.00, "output": 15.00},
        "claude-haiku-4-5-20251001":          {"input":  1.00, "output":  5.00},
        # OpenAI
        "gpt-5.2-pro":                        {"input": 21.00, "output": 168.00},
        "gpt-5.2":                            {"input":  1.75, "output": 14.00},
        "gpt-5.1":                            {"input":  2.00, "output":  8.00},
        # Google
        "gemini-2.5-pro":                     {"input":  1.25, "output": 10.00},
        "gemini-2.5-flash":                   {"input":  0.30, "output":  2.50},
        "gemini-2.5-flash-lite":              {"input":  0.10, "output":  0.40},
        # Mistral
        "mistral-large-latest":               {"input":  2.00, "output":  6.00},
        "mistral-small-latest":               {"input":  0.10, "output":  0.30},
        # DeepSeek
        "deepseek-chat":                      {"input":  0.27, "output":  1.10},
        "deepseek-reasoner":                  {"input":  0.55, "output":  2.19},
        # xAI
        "grok-4-1-fast":                      {"input":  5.00, "output": 25.00},
        "grok-3-beta":                        {"input":  3.00, "output": 15.00},
        # MiniMax
        "MiniMax-M2.1":                       {"input":  0.40, "output":  1.60},
        # Qwen
        "qwen3.5-plus":                       {"input":  0.57, "output":  2.29},
        "qwen3-max-instruct":                 {"input":  1.60, "output":  6.40},
        # Meta Llama via OpenRouter
        "meta-llama/llama-4-maverick":        {"input":  0.20, "output":  0.60},
        "meta-llama/llama-3.3-70b-instruct":  {"input":  0.59, "output":  0.79},
    }

    # Known tested models — for documentation and default selection only.
    KNOWN_MODELS = list(MODEL_PRICING.keys())

    def __init__(self, **api_key_overrides):
        """
        Initialize with optional API key overrides.

        All keys are read from environment variables by default.
        Pass keyword args to override specific keys:
            anthropic_api_key="sk-ant-..."
            openai_api_key="sk-..."
            google_api_key="AI..."
            deepseek_api_key="..."
            xai_api_key="..."
            minimax_api_key="..."
            dashscope_api_key="..."
            openrouter_api_key="..."
            mistral_api_key="..."

        Legacy positional-style kwargs also supported:
            anthropic_api_key, openai_api_key, google_api_key
        """
        self._key_overrides = api_key_overrides
        self._clients: Dict[str, object] = {}  # Lazy-initialized per provider
        self.test_history: List[TestResults] = []

    # ── Provider detection ────────────────────────────────────────────────

    def _detect_provider(self, model: str) -> Tuple[str, str, Optional[str]]:
        """Detect (provider, env_key, base_url) from model name prefix."""
        for prefix, provider, env_key, base_url in self.PROVIDER_MAP:
            if model.startswith(prefix):
                return provider, env_key, base_url
        known_prefixes = [p for p, *_ in self.PROVIDER_MAP]
        raise ValueError(
            f"Cannot detect provider for model '{model}'.\n"
            f"Model name must start with one of: {known_prefixes}\n"
            f"Known tested models: {self.KNOWN_MODELS}"
        )

    def _get_api_key(self, env_key: str) -> Optional[str]:
        """Resolve API key: override kwarg > environment variable."""
        kwarg_name = env_key.lower()  # e.g. ANTHROPIC_API_KEY -> anthropic_api_key
        return self._key_overrides.get(kwarg_name) or os.getenv(env_key)

    def _get_client(self, provider: str, env_key: str, base_url: Optional[str]) -> object:
        """Lazily initialize and cache SDK client per provider."""
        if provider in self._clients:
            return self._clients[provider]

        api_key = self._get_api_key(env_key)
        if not api_key:
            raise ValueError(
                f"{env_key} not set. "
                f"Set the environment variable or pass {env_key.lower()}='...' to the constructor."
            )

        if provider == "anthropic":
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)

        elif provider == "google":
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            client = genai  # Module-level, model instantiated per call

        elif provider == "mistral":
            from mistralai import Mistral
            client = Mistral(api_key=api_key)

        elif provider in ("openai", "deepseek", "xai", "minimax", "qwen", "openrouter"):
            from openai import OpenAI
            kwargs = {"api_key": api_key}
            if base_url:
                kwargs["base_url"] = base_url
            client = OpenAI(**kwargs)

        else:
            raise ValueError(f"Unknown provider: {provider}")

        self._clients[provider] = client
        return client

    # ── Core test methods ─────────────────────────────────────────────────

    def test_prompt(
        self,
        prompt_text: str,
        models: List[str] = None,
        num_runs: int = 1,
        system_prompt: str = None,
        max_tokens: int = 1000
    ) -> TestResults:
        """
        Test a prompt across multiple models.

        Args:
            prompt_text: The prompt to test
            models: List of model IDs to test. Defaults to all KNOWN_MODELS.
                    Pass any model ID — provider auto-detected from prefix.
            num_runs: Number of times to run each model (for consistency testing)
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens for response

        Returns:
            TestResults with performance metrics for all models
        """
        if models is None:
            models = self.KNOWN_MODELS

        all_results = []
        test_id = self._generate_test_id()

        for model in models:
            print(f"Testing {model}...")
            for _ in range(num_runs):
                metric = self._test_single_model(model, prompt_text, system_prompt, max_tokens)
                all_results.append(metric)

        recommendations = self._generate_recommendations(all_results)
        successful = [r for r in all_results if r.error is None]
        best_model    = max(successful, key=lambda x: x.quality_score).model_id    if successful else "N/A"
        cheapest_model = min(successful, key=lambda x: x.estimated_cost_usd).model_id if successful else "N/A"
        fastest_model  = min(successful, key=lambda x: x.latency_ms).model_id       if successful else "N/A"

        results = TestResults(
            test_id=test_id,
            prompt_text=prompt_text[:200] + "..." if len(prompt_text) > 200 else prompt_text,
            models_tested=models,
            results=all_results,
            recommendations=recommendations,
            best_model=best_model,
            cheapest_model=cheapest_model,
            fastest_model=fastest_model,
            created_at=datetime.now().isoformat()
        )
        self.test_history.append(results)
        return results

    def _test_single_model(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int
    ) -> PerformanceMetrics:
        """Test a single model, routing to the correct provider."""
        try:
            provider, env_key, base_url = self._detect_provider(model)
            client = self._get_client(provider, env_key, base_url)

            if provider == "anthropic":
                return self._test_anthropic(client, model, prompt, system_prompt, max_tokens)
            elif provider == "google":
                return self._test_google(client, model, prompt, system_prompt, max_tokens)
            elif provider == "mistral":
                return self._test_mistral(client, model, prompt, system_prompt, max_tokens)
            else:
                # All OpenAI-compat providers
                return self._test_openai_compat(client, provider, model, prompt, system_prompt, max_tokens)

        except Exception as e:
            provider_guess = model.split("-")[0] if "-" in model else "unknown"
            return PerformanceMetrics(
                model_id=model,
                provider=provider_guess,
                prompt_text=prompt,
                response_text="",
                latency_ms=0,
                tokens_input=0,
                tokens_output=0,
                estimated_cost_usd=0,
                quality_score=0,
                timestamp=datetime.now().isoformat(),
                error=str(e)
            )

    def _test_anthropic(self, client, model, prompt, system_prompt, max_tokens) -> PerformanceMetrics:
        start = time.time()
        message = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_prompt or "You are a helpful assistant.",
            messages=[{"role": "user", "content": prompt}]
        )
        latency_ms = (time.time() - start) * 1000
        response_text = message.content[0].text if message.content else ""
        tokens_input = message.usage.input_tokens
        tokens_output = message.usage.output_tokens
        return self._make_metrics(model, "anthropic", prompt, response_text,
                                  latency_ms, tokens_input, tokens_output)

    def _test_openai_compat(self, client, provider, model, prompt, system_prompt, max_tokens) -> PerformanceMetrics:
        start = time.time()
        response = client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system_prompt or "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        latency_ms = (time.time() - start) * 1000
        response_text = response.choices[0].message.content if response.choices else ""
        tokens_input = response.usage.prompt_tokens
        tokens_output = response.usage.completion_tokens
        return self._make_metrics(model, provider, prompt, response_text,
                                  latency_ms, tokens_input, tokens_output)

    def _test_google(self, genai_module, model, prompt, system_prompt, max_tokens) -> PerformanceMetrics:
        start = time.time()
        gemini_model = genai_module.GenerativeModel(model)
        response = gemini_model.generate_content(
            f"{system_prompt or 'You are a helpful assistant.'}\n\n{prompt}",
            generation_config={"max_output_tokens": max_tokens}
        )
        latency_ms = (time.time() - start) * 1000
        response_text = response.text if response else ""
        # Gemini doesn't always return exact token counts — estimate from word count
        tokens_input = int(len(prompt.split()) * 1.3)
        tokens_output = int(len(response_text.split()) * 1.3)
        return self._make_metrics(model, "google", prompt, response_text,
                                  latency_ms, tokens_input, tokens_output)

    def _test_mistral(self, client, model, prompt, system_prompt, max_tokens) -> PerformanceMetrics:
        start = time.time()
        response = client.chat.complete(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt or "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
        )
        latency_ms = (time.time() - start) * 1000
        response_text = response.choices[0].message.content if response.choices else ""
        tokens_input = response.usage.prompt_tokens
        tokens_output = response.usage.completion_tokens
        return self._make_metrics(model, "mistral", prompt, response_text,
                                  latency_ms, tokens_input, tokens_output)

    def _make_metrics(self, model, provider, prompt, response_text,
                      latency_ms, tokens_input, tokens_output) -> PerformanceMetrics:
        return PerformanceMetrics(
            model_id=model,
            provider=provider,
            prompt_text=prompt,
            response_text=response_text[:200] + "..." if len(response_text) > 200 else response_text,
            latency_ms=latency_ms,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            estimated_cost_usd=self._calculate_cost(model, tokens_input, tokens_output),
            quality_score=self._score_response_quality(response_text, latency_ms),
            timestamp=datetime.now().isoformat()
        )

    # ── Cost & quality helpers ────────────────────────────────────────────

    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate estimated cost in USD. Returns 0 for unlisted models."""
        pricing = self.MODEL_PRICING.get(model)
        if not pricing:
            return 0.0
        input_cost  = (input_tokens  / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        return round(input_cost + output_cost, 8)

    def _score_response_quality(self, response: str, latency_ms: float) -> float:
        """Score response quality 0-100 based on length, completeness, latency."""
        score = 50
        if 200 <= len(response) <= 1000:
            score += 25
        elif len(response) > 100:
            score += 15
        if response.count(".") > 0:
            score += 15
        if response.count("?") > 0 or response.count("!") > 0:
            score += 5
        if 500 < latency_ms < 5000:
            score += 10
        elif latency_ms < 500:
            score += 5
        return min(100, max(0, score))

    def _generate_recommendations(self, results: List[PerformanceMetrics]) -> List[str]:
        recommendations = []
        successful = [r for r in results if r.error is None]
        if not successful:
            recommendations.append("All tests failed. Check API keys and prompt validity.")
            return recommendations
        cheapest     = min(successful, key=lambda x: x.estimated_cost_usd)
        best_quality = max(successful, key=lambda x: x.quality_score)
        fastest      = min(successful, key=lambda x: x.latency_ms)
        recommendations.append(f"Cost-optimized: Use {cheapest.model_id} (${cheapest.estimated_cost_usd:.6f})")
        recommendations.append(f"Best quality: {best_quality.model_id} ({best_quality.quality_score:.0f}/100)")
        recommendations.append(f"Fastest: {fastest.model_id} ({fastest.latency_ms:.0f}ms)")
        by_provider = {}
        for r in successful:
            by_provider.setdefault(r.provider, []).append(r)
        if len(by_provider) > 1:
            recommendations.append(f"Multi-provider comparison: {len(by_provider)} providers tested")
        return recommendations

    @staticmethod
    def _generate_test_id() -> str:
        import uuid
        return f"test_{uuid.uuid4().hex[:8]}"

    # ── Output formatting ─────────────────────────────────────────────────

    def format_results(self, results: TestResults) -> str:
        output = f"""
╔══════════════════════════════════════════════════════════╗
║           PROMPT PERFORMANCE TEST RESULTS                ║
╚══════════════════════════════════════════════════════════╝

Test ID:       {results.test_id}
Timestamp:     {results.created_at}
Models Tested: {', '.join(results.models_tested)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DETAILED RESULTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        for result in results.results:
            if result.error:
                output += f"\n❌ {result.model_id} ({result.provider})\n   Error: {result.error}\n"
            else:
                output += f"""
✅ {result.model_id} ({result.provider})
   Latency:  {result.latency_ms:.0f}ms
   Cost:     ${result.estimated_cost_usd:.6f}
   Quality:  {result.quality_score:.1f}/100
   Tokens:   {result.tokens_input} input, {result.tokens_output} output
"""
        output += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RECOMMENDATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        for i, rec in enumerate(results.recommendations, 1):
            output += f"{i}. {rec}\n"
        output += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Best Model (Quality): {results.best_model}
Best Model (Cost):    {results.cheapest_model}
Best Model (Speed):   {results.fastest_model}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return output


if __name__ == "__main__":
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        tester = PromptPerformanceTester()
        results = tester.test_prompt(
            prompt_text="What are the benefits of AI?",
            models=["claude-haiku-4-5-20251001"],
            num_runs=1,
            max_tokens=200
        )
        print(tester.format_results(results))
