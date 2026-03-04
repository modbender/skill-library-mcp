"""Astrai code review plugin for OpenClaw.

Routes code review requests through Astrai's intelligent API gateway.
Complex logic goes to powerful models. Simple formatting goes to cheap ones.
Saves 40%+ vs always using the most expensive model.

BYOK (Bring Your Own Keys): Users provide their own provider API keys.
Astrai routes to the best model using YOUR keys. You pay providers directly.
Astrai charges only for the routing intelligence.
"""

from __future__ import annotations

import json
import os
import time
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


ASTRAI_BASE_URL = os.getenv("ASTRAI_BASE_URL", "https://as-trai.com/v1")

# Supported providers and their env var names
PROVIDER_KEY_MAP = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "google": "GOOGLE_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
    "mistral": "MISTRAL_API_KEY",
    "groq": "GROQ_API_KEY",
    "together": "TOGETHER_API_KEY",
    "fireworks": "FIREWORKS_API_KEY",
    "cohere": "COHERE_API_KEY",
    "perplexity": "PERPLEXITY_API_KEY",
}

# System prompts by strictness level
REVIEW_PROMPTS = {
    "standard": (
        "You are an expert code reviewer. Analyze the provided diff and identify:\n"
        "- Bugs and logic errors\n"
        "- Potential runtime failures\n"
        "- Missing error handling\n"
        "- Off-by-one errors and edge cases\n\n"
        "For each issue found, return a JSON object with:\n"
        "- file: the filename\n"
        "- line: the line number (best estimate from diff context)\n"
        "- severity: critical | warning | info\n"
        "- message: what the problem is\n"
        "- suggestion: how to fix it\n\n"
        "Return a JSON object with keys: issues (array), summary (string).\n"
        "If no issues are found, return an empty issues array with a positive summary."
    ),
    "strict": (
        "You are an expert code reviewer performing a strict review. Analyze the "
        "provided diff and identify:\n"
        "- Bugs and logic errors\n"
        "- Potential runtime failures\n"
        "- Missing error handling and edge cases\n"
        "- Style violations and inconsistencies\n"
        "- Naming issues (unclear variable/function names)\n"
        "- Missing or incorrect type annotations\n"
        "- Violations of DRY, SOLID, or other best practices\n"
        "- Performance concerns\n"
        "- Missing tests or test coverage gaps\n\n"
        "For each issue found, return a JSON object with:\n"
        "- file: the filename\n"
        "- line: the line number (best estimate from diff context)\n"
        "- severity: critical | warning | info\n"
        "- message: what the problem is\n"
        "- suggestion: how to fix it\n\n"
        "Return a JSON object with keys: issues (array), summary (string).\n"
        "If no issues are found, return an empty issues array with a positive summary."
    ),
    "security": (
        "You are a security-focused code reviewer. Analyze the provided diff and "
        "identify security vulnerabilities:\n"
        "- SQL injection\n"
        "- Cross-site scripting (XSS)\n"
        "- Authentication and authorization bypass\n"
        "- Hardcoded secrets, API keys, or credentials\n"
        "- Insecure deserialization\n"
        "- Path traversal\n"
        "- Command injection\n"
        "- Improper input validation\n"
        "- Insecure cryptography or hashing\n"
        "- Information disclosure\n"
        "- Race conditions with security implications\n"
        "- Dependency vulnerabilities\n\n"
        "For each issue found, return a JSON object with:\n"
        "- file: the filename\n"
        "- line: the line number (best estimate from diff context)\n"
        "- severity: critical | warning | info\n"
        "- message: what the vulnerability is\n"
        "- suggestion: how to remediate it\n\n"
        "Return a JSON object with keys: issues (array), summary (string).\n"
        "If no issues are found, return an empty issues array with a positive summary."
    ),
}


def _collect_provider_keys() -> Dict[str, str]:
    """Collect all available provider API keys from environment."""
    keys = {}
    for provider, env_var in PROVIDER_KEY_MAP.items():
        val = os.getenv(env_var, "")
        if val:
            keys[provider] = val
    return keys


@dataclass
class ReviewResult:
    """Structured result from a code review."""

    issues: List[Dict[str, Any]]
    summary: str
    model_used: str
    cost_usd: float
    savings_usd: float


class AstraiCodeReviewPlugin:
    """OpenClaw plugin that reviews code diffs via Astrai's intelligent router.

    Astrai analyzes the diff complexity and routes to the optimal model:
    - Complex logic/security -> expensive, powerful models (Opus, GPT-4o)
    - Simple formatting/style -> fast, cheap models (Haiku, GPT-4o-mini)

    BYOK mode: Your provider API keys stay with you. Astrai decides which
    model to use, then calls the provider using YOUR key.
    """

    def __init__(self) -> None:
        self.api_key = os.getenv("ASTRAI_API_KEY", "")
        self.provider_keys = _collect_provider_keys()
        self.strictness = os.getenv("REVIEW_STRICTNESS", "standard").lower()
        self.local_only = len(self.provider_keys) == 0

        if not self.api_key:
            raise ValueError(
                "ASTRAI_API_KEY is required. "
                "Get a free key at https://as-trai.com"
            )

        if self.strictness not in REVIEW_PROMPTS:
            raise ValueError(
                f"Invalid REVIEW_STRICTNESS: {self.strictness!r}. "
                f"Must be one of: standard, strict, security"
            )

        # Tracking stats
        self._requests = 0
        self._total_cost = 0.0
        self._total_savings = 0.0
        self._models_used: Dict[str, int] = {}
        self._session_start = time.time()

    def _build_headers(self) -> Dict[str, str]:
        """Build request headers for the Astrai API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Astrai-Task-Type": "code-review",
            "X-Astrai-Source": "openclaw-skill-code-review",
        }

        if self.local_only:
            headers["X-Astrai-Routing-Mode"] = "local-only"
        else:
            headers["X-Astrai-Provider-Keys"] = json.dumps(self.provider_keys)
            headers["X-Astrai-Available-Providers"] = ",".join(
                self.provider_keys.keys()
            )

        return headers

    def _call_astrai(
        self, system_prompt: str, user_content: str
    ) -> Dict[str, Any]:
        """Make a request to the Astrai chat completions API."""
        url = f"{ASTRAI_BASE_URL}/chat/completions"
        headers = self._build_headers()

        payload = json.dumps({
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            "response_format": {"type": "json_object"},
        }).encode("utf-8")

        req = urllib.request.Request(
            url, data=payload, headers=headers, method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                resp_headers = {k: v for k, v in resp.getheaders()}
                body = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"Astrai API returned HTTP {exc.code}: {error_body}"
            ) from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(
                f"Failed to connect to Astrai API at {url}: {exc.reason}"
            ) from exc

        # Extract routing metadata from response headers
        model_used = resp_headers.get("X-Astrai-Model", "unknown")
        cost = float(resp_headers.get("X-Astrai-Cost", "0") or 0)
        savings = float(resp_headers.get("X-Astrai-Savings", "0") or 0)

        # Update tracking
        self._requests += 1
        self._total_cost += cost
        self._total_savings += savings
        self._models_used[model_used] = self._models_used.get(model_used, 0) + 1

        return {
            "body": body,
            "model_used": model_used,
            "cost_usd": cost,
            "savings_usd": savings,
        }

    def _parse_review_response(
        self, api_result: Dict[str, Any]
    ) -> ReviewResult:
        """Parse the Astrai API response into a ReviewResult."""
        body = api_result["body"]

        # Extract the assistant message content
        content_str = ""
        if "choices" in body and body["choices"]:
            message = body["choices"][0].get("message", {})
            content_str = message.get("content", "")
        elif "content" in body:
            content_str = body["content"]

        # Parse the JSON content
        try:
            review_data = json.loads(content_str) if isinstance(content_str, str) else content_str
        except (json.JSONDecodeError, TypeError):
            # If the model didn't return valid JSON, wrap in a single-issue result
            review_data = {
                "issues": [],
                "summary": content_str if content_str else "Review completed but response could not be parsed.",
            }

        issues = review_data.get("issues", [])
        summary = review_data.get("summary", "Review completed.")

        # Validate issue structure
        validated_issues = []
        for issue in issues:
            validated_issues.append({
                "file": issue.get("file", "unknown"),
                "line": issue.get("line", 0),
                "severity": issue.get("severity", "info"),
                "message": issue.get("message", ""),
                "suggestion": issue.get("suggestion", ""),
            })

        return ReviewResult(
            issues=validated_issues,
            summary=summary,
            model_used=api_result["model_used"],
            cost_usd=api_result["cost_usd"],
            savings_usd=api_result["savings_usd"],
        )

    def review_diff(
        self,
        diff: str,
        context: str = "",
        strictness: Optional[str] = None,
    ) -> ReviewResult:
        """Review a code diff and return structured issues.

        Args:
            diff: The unified diff text to review.
            context: Optional additional context (e.g., PR description, file purpose).
            strictness: Override the default strictness level (standard/strict/security).

        Returns:
            ReviewResult with issues, summary, model used, cost, and savings.
        """
        level = (strictness or self.strictness).lower()
        if level not in REVIEW_PROMPTS:
            level = "standard"

        system_prompt = REVIEW_PROMPTS[level]

        user_content = f"Review the following diff:\n\n```diff\n{diff}\n```"
        if context:
            user_content = f"Context: {context}\n\n{user_content}"

        api_result = self._call_astrai(system_prompt, user_content)
        return self._parse_review_response(api_result)

    def review_file(
        self,
        file_path: str,
        content: str,
    ) -> ReviewResult:
        """Review a single file's content.

        Args:
            file_path: Path to the file being reviewed.
            content: The full file content.

        Returns:
            ReviewResult with issues, summary, model used, cost, and savings.
        """
        system_prompt = REVIEW_PROMPTS[self.strictness]

        # Detect language from file extension for better prompting
        ext = os.path.splitext(file_path)[1].lstrip(".")
        lang_hint = ext if ext else "text"

        user_content = (
            f"Review the following file: {file_path}\n\n"
            f"```{lang_hint}\n{content}\n```"
        )

        api_result = self._call_astrai(system_prompt, user_content)
        return self._parse_review_response(api_result)

    def status(self) -> Dict[str, Any]:
        """Return current routing and review stats."""
        elapsed = time.time() - self._session_start
        hours = elapsed / 3600

        providers = list(self.provider_keys.keys())
        savings_rate = (
            f"${self._total_savings / hours:.2f}/hr" if hours > 0.1 else "N/A"
        )

        return {
            "status": "active",
            "mode": "local-only" if self.local_only else "byok",
            "strictness": self.strictness,
            "providers_configured": providers,
            "provider_count": len(providers),
            "reviews_completed": self._requests,
            "total_cost_usd": round(self._total_cost, 4),
            "total_savings_usd": round(self._total_savings, 4),
            "savings_rate": savings_rate,
            "models_used": self._models_used,
            "session_uptime_seconds": round(elapsed, 1),
        }
