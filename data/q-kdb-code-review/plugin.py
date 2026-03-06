"""Q/kdb+ code review plugin for OpenClaw.

Reviews Q/kdb+ code through Astrai's intelligent API gateway.
Specialized prompts for Q idioms, performance patterns, and
common pitfalls in the most terse language in quantitative finance.

BYOK (Bring Your Own Keys): Your provider API keys stay with you.
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

# Q/kdb+-specific review prompts
REVIEW_PROMPTS = {
    "standard": (
        "You are an expert Q/kdb+ code reviewer with deep knowledge of the Q programming language "
        "and kdb+ database. Q is an extremely terse, vector-oriented language used in quantitative "
        "finance for high-frequency trading, time-series analysis, and real-time analytics.\n\n"
        "Review the provided Q code and identify:\n"
        "- Type errors from implicit casts (e.g., mixing longs and floats in comparisons)\n"
        "- Rank errors from wrong argument counts in function calls\n"
        "- Unescaped signals in protected evaluation\n"
        "- Missing null handling (0N, 0Ni, 0Nj, 0Nf, etc.)\n"
        "- Off-by-one errors in `til`, `sublist`, and indexing\n"
        "- Race conditions in timer callbacks (.z.ts)\n"
        "- Incorrect join semantics (lj vs ij vs aj vs wj)\n"
        "- Table schema mismatches in inserts and upserts\n"
        "- Incorrect use of `over` (/) and `scan` (\\) adverbs\n"
        "- Missing error trapping with @[;::] or .[;::] protected evaluation\n\n"
        "For each issue, return a JSON object with:\n"
        "- file: the filename\n"
        "- line: the line number\n"
        "- severity: critical | warning | info\n"
        "- message: what the problem is (explain in terms a Q developer would understand)\n"
        "- suggestion: the corrected Q code\n\n"
        "Return a JSON object with keys: issues (array), summary (string).\n"
        "If no issues found, return empty issues array with a positive summary."
    ),
    "strict": (
        "You are an expert Q/kdb+ code reviewer performing a strict performance and style review. "
        "Q is an extremely terse, vector-oriented language where idiomatic code can be 1000x faster "
        "than naive implementations.\n\n"
        "Review the provided Q code and identify:\n"
        "ALL issues from standard review, PLUS:\n"
        "- Missing `peach` (parallel each) for embarrassingly parallel operations\n"
        "- N-squared complexity that should use `aj` (asof join) or `wj` (window join)\n"
        "- Missing `g#` (grouped) attribute on high-cardinality join columns\n"
        "- Missing `s#` (sorted) attribute on time columns for efficient `aj`\n"
        "- Missing `p#` (parted) attribute on partitioned date columns\n"
        "- Unlocked tables during concurrent inserts (missing `.[;;:;]` pattern)\n"
        "- Memory-inefficient queries (selecting all columns when only some needed)\n"
        "- Using `each` where vector operations would suffice\n"
        "- String operations that should use symbols for performance\n"
        "- Inefficient `select` with `where` that could use `fby` (filter by)\n"
        "- Non-idiomatic patterns (verbose code that has terse Q equivalents)\n"
        "- Inconsistent naming conventions (mixedCase vs under_score)\n"
        "- Missing or misleading comments on complex one-liners\n"
        "- Functions exceeding 10 lines (Q functions should be short)\n\n"
        "For each issue, return a JSON object with:\n"
        "- file: the filename\n"
        "- line: the line number\n"
        "- severity: critical | warning | info\n"
        "- message: what the problem is\n"
        "- suggestion: the improved Q code with explanation\n\n"
        "Return a JSON object with keys: issues (array), summary (string)."
    ),
    "security": (
        "You are a security-focused Q/kdb+ code reviewer. kdb+ systems often handle "
        "real-time market data and trading signals worth millions. Security is critical.\n\n"
        "Review the provided Q code and identify security vulnerabilities:\n"
        "- Unprotected IPC handlers (.z.pg, .z.ps, .z.pp, .z.ph) accepting arbitrary queries\n"
        "- Missing or weak .z.pw (password authentication) on open ports\n"
        "- Unsafe `value` or `eval` on user-supplied strings (Q injection)\n"
        "- Exposed -p port without IP whitelist restrictions\n"
        "- Unvalidated inputs in .z.ph HTTP handlers\n"
        "- Sensitive data (API keys, credentials) in plaintext Q files\n"
        "- Missing TLS for IPC connections (-E flag or stunnel)\n"
        "- Unrestricted \\\\system commands via IPC\n"
        "- Log injection via unescaped user strings in -1 or 0N!\n"
        "- File path traversal in `read0`, `read1`, `hopen` with user input\n"
        "- Unrestricted .z.ws (WebSocket handler) without authentication\n"
        "- Timer callbacks (.z.ts) modifying global state without atomicity\n\n"
        "For each issue, return a JSON object with:\n"
        "- file: the filename\n"
        "- line: the line number\n"
        "- severity: critical | warning | info\n"
        "- message: what the vulnerability is\n"
        "- suggestion: the secure Q code pattern\n\n"
        "Return a JSON object with keys: issues (array), summary (string)."
    ),
}


def _collect_provider_keys() -> Dict[str, str]:
    keys = {}
    for provider, env_var in PROVIDER_KEY_MAP.items():
        val = os.getenv(env_var, "")
        if val:
            keys[provider] = val
    return keys


@dataclass
class ReviewResult:
    issues: List[Dict[str, Any]]
    summary: str
    model_used: str
    cost_usd: float
    savings_usd: float


class QKdbCodeReviewPlugin:
    """OpenClaw plugin that reviews Q/kdb+ code via Astrai's intelligent router.

    Specialized for the Q programming language -- understands adverbs,
    implicit types, IPC patterns, and kdb+ performance idioms.
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

        self._requests = 0
        self._total_cost = 0.0
        self._total_savings = 0.0
        self._models_used: Dict[str, int] = {}
        self._session_start = time.time()

    def _build_headers(self) -> Dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Astrai-Task-Type": "code-review-q-kdb",
            "X-Astrai-Source": "openclaw-skill-q-kdb-review",
        }

        if self.local_only:
            headers["X-Astrai-Routing-Mode"] = "local-only"
        else:
            headers["X-Astrai-Provider-Keys"] = json.dumps(self.provider_keys)
            headers["X-Astrai-Available-Providers"] = ",".join(
                self.provider_keys.keys()
            )

        return headers

    def _call_astrai(self, system_prompt: str, user_content: str) -> Dict[str, Any]:
        url = f"{ASTRAI_BASE_URL}/chat/completions"
        headers = self._build_headers()

        payload = json.dumps({
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            "response_format": {"type": "json_object"},
        }).encode("utf-8")

        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")

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

        model_used = resp_headers.get("X-Astrai-Model", "unknown")
        cost = float(resp_headers.get("X-Astrai-Cost", "0") or 0)
        savings = float(resp_headers.get("X-Astrai-Savings", "0") or 0)

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

    def _parse_review_response(self, api_result: Dict[str, Any]) -> ReviewResult:
        body = api_result["body"]

        content_str = ""
        if "choices" in body and body["choices"]:
            message = body["choices"][0].get("message", {})
            content_str = message.get("content", "")
        elif "content" in body:
            content_str = body["content"]

        try:
            review_data = json.loads(content_str) if isinstance(content_str, str) else content_str
        except (json.JSONDecodeError, TypeError):
            review_data = {
                "issues": [],
                "summary": content_str if content_str else "Review completed but response could not be parsed.",
            }

        issues = review_data.get("issues", [])
        summary = review_data.get("summary", "Review completed.")

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

    def review_q(
        self,
        code: str,
        context: str = "",
        strictness: Optional[str] = None,
    ) -> ReviewResult:
        """Review Q/kdb+ code."""
        level = (strictness or self.strictness).lower()
        if level not in REVIEW_PROMPTS:
            level = "standard"

        system_prompt = REVIEW_PROMPTS[level]
        user_content = f"Review the following Q/kdb+ code:\n\n```q\n{code}\n```"
        if context:
            user_content = f"Context: {context}\n\n{user_content}"

        api_result = self._call_astrai(system_prompt, user_content)
        return self._parse_review_response(api_result)

    def review_file(self, file_path: str, content: str) -> ReviewResult:
        """Review a .q file."""
        system_prompt = REVIEW_PROMPTS[self.strictness]
        user_content = f"Review the following Q/kdb+ file: {file_path}\n\n```q\n{content}\n```"
        api_result = self._call_astrai(system_prompt, user_content)
        return self._parse_review_response(api_result)

    def status(self) -> Dict[str, Any]:
        elapsed = time.time() - self._session_start
        hours = elapsed / 3600
        providers = list(self.provider_keys.keys())
        savings_rate = f"${self._total_savings / hours:.2f}/hr" if hours > 0.1 else "N/A"

        return {
            "status": "active",
            "mode": "local-only" if self.local_only else "byok",
            "language": "Q/kdb+",
            "strictness": self.strictness,
            "providers_configured": providers,
            "provider_count": len(providers),
            "reviews_completed": self._requests,
            "total_cost_usd": round(self._total_cost, 4),
            "total_savings_usd": round(self._total_savings, 4),
            "savings_rate": savings_rate,
            "models_used": self._models_used,
        }
