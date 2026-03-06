#!/usr/bin/env python3
"""Redact common secret patterns from text before inclusion in subcall prompts.

Patterns covered:
- API keys / tokens (Bearer, Authorization headers, common key prefixes)
- AWS-style credentials (AKIA..., secret keys)
- PEM-encoded blocks (private keys, certificates)
- Generic password / secret assignments
- Connection strings with embedded credentials
- .env-style KEY=VALUE secrets

Usage as module:
    from rlm_redact import redact_secrets
    safe_text = redact_secrets(text)
"""
import re

REDACTED = "[REDACTED]"

# Order matters: more specific patterns first to avoid partial matches.
_PATTERNS = [
    # PEM blocks (private keys, certificates, etc.)
    (re.compile(
        r"-----BEGIN\s[\w\s]+-----[\s\S]*?-----END\s[\w\s]+-----",
        re.MULTILINE,
    ), REDACTED),

    # Bearer / Authorization header values
    (re.compile(
        r"((?:Bearer|Basic|Token)\s+)[A-Za-z0-9\-._~+/]+=*",
        re.IGNORECASE,
    ), r"\1" + REDACTED),

    # AWS access key IDs (AKIA…)
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), REDACTED),

    # AWS secret access keys (40-char base64)
    (re.compile(
        r"(?i)(aws_secret_access_key\s{0,3}=\s{0,3})[A-Za-z0-9/+=]{40}",
    ), r"\1" + REDACTED),

    # Generic "password", "secret", "token", "api_key" assignments
    # Matches: password = "...", SECRET: '...', api_key=...
    # Quoted values may contain spaces; unquoted values stop at whitespace.
    (re.compile(
        r"""(?i)((?:password|passwd|secret|token|api_key|apikey|api[-_]?secret|access_key|private_key)"""
        r"""\s*[:=]\s*)(?:"[^"]*"|'[^']*'|\S+)""",
    ), r"\1" + REDACTED),

    # Connection strings with short-form pwd (pwd=...; )
    # Note: password=... is already handled by the generic pattern above.
    (re.compile(
        r"(?i)(pwd\s*=\s*)[^;\s]+",
    ), r"\1" + REDACTED),

    # Hex-encoded secrets (>=32 hex chars that look like hashes/keys)
    (re.compile(
        r"(?<![A-Za-z0-9])[0-9a-fA-F]{32,64}(?![A-Za-z0-9])",
    ), REDACTED),
]


def redact_secrets(text: str) -> str:
    """Return *text* with common secret patterns replaced by [REDACTED]."""
    for pattern, replacement in _PATTERNS:
        text = pattern.sub(replacement, text)
    return text
