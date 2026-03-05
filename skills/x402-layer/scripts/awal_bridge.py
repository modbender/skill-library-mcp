#!/usr/bin/env python3
"""
Helpers for invoking Coinbase Agentic Wallet CLI (AWAL) from x402 scripts.
"""

import json
import os
import re
import shutil
import subprocess
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

DEFAULT_AWAL_PACKAGE = "awal@1.0.0"

# Shell metacharacters to reject for security
_SHELL_DANGEROUS_CHARS = set(';&|`$()<>!\n\r')


def _validate_safe_string(value: str) -> str:
    """Validate string doesn't contain shell metacharacters."""
    if not isinstance(value, str):
        return value
    for char in _SHELL_DANGEROUS_CHARS:
        if char in value:
            raise ValueError(f"Unsafe character detected in input")
    return value


def build_awal_command(args: List[str]) -> List[str]:
    explicit_bin = os.getenv("AWAL_BIN", "").strip()
    if explicit_bin:
        return [explicit_bin, *args]

    local_awal = shutil.which("awal")
    if local_awal and os.getenv("AWAL_FORCE_NPX", "").strip() != "1":
        return [local_awal, *args]

    package = os.getenv("AWAL_PACKAGE", DEFAULT_AWAL_PACKAGE).strip() or DEFAULT_AWAL_PACKAGE
    return ["npx", "-y", package, *args]


def run_awal(args: List[str], timeout: int = 180) -> Dict[str, Any]:
    # Validate all string arguments for security
    for arg in args:
        if isinstance(arg, str):
            _validate_safe_string(arg)

    cmd = build_awal_command(args)
    proc = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)
    return {
        "ok": proc.returncode == 0,
        "code": proc.returncode,
        "stdout": proc.stdout or "",
        "stderr": proc.stderr or "",
        "command": cmd,
    }


def _extract_json(text: str) -> Optional[Any]:
    raw = (text or "").strip()
    if not raw:
        return None

    try:
        return json.loads(raw)
    except Exception:
        pass

    lines = raw.splitlines()
    for i in range(len(lines) - 1, -1, -1):
        candidate = "\n".join(lines[i:]).strip()
        if not candidate:
            continue
        if candidate[0] not in "[{":
            continue
        try:
            return json.loads(candidate)
        except Exception:
            continue
    return None


def _split_url(url: str) -> Tuple[str, str]:
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError("URL must include scheme and host (e.g. https://api.x402layer.cc/e/gifu)")
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    path = parsed.path or "/"
    if parsed.query:
        path = f"{path}?{parsed.query}"
    return base_url, path


def get_awal_evm_address(required: bool = True) -> Optional[str]:
    result = run_awal(["address"])
    combined = f"{result['stdout']}\n{result['stderr']}"

    match = re.search(r"0x[a-fA-F0-9]{40}", combined)
    if match:
        return match.group(0)

    if required:
        if result["ok"]:
            raise ValueError("Could not parse wallet address from AWAL output")
        raise ValueError((result["stderr"] or result["stdout"] or "AWAL address failed").strip())
    return None


def awal_pay_url(
    url: str,
    method: str = "GET",
    data: Optional[Dict[str, Any]] = None,
    query: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, Any]] = None,
    max_amount: Optional[int] = None,
) -> Dict[str, Any]:
    # AWAL x402 pay expects the full URL, not split
    args: List[str] = ["x402", "pay", url]
    if method and method.upper() != "GET":
        args += ["-X", method.upper()]
    if data is not None:
        args += ["-d", json.dumps(data)]
    if query is not None:
        args += ["-q", json.dumps(query)]
    # NOTE: AWAL x402 pay supports --headers flag for custom headers
    if headers is not None:
        args += ["-h", json.dumps(headers)]
    if max_amount is not None:
        args += ["--max-amount", str(max_amount)]

    result = run_awal(args)
    parsed = _extract_json(result["stdout"])

    if result["ok"]:
        if isinstance(parsed, dict):
            return parsed
        if parsed is not None:
            return {"result": parsed}
        output = (result["stdout"] or "").strip()
        return {"success": True, "output": output}

    err = (result["stderr"] or result["stdout"] or f"AWAL command failed ({result['code']})").strip()
    return {"error": err, "output": (result["stdout"] or "").strip()}
