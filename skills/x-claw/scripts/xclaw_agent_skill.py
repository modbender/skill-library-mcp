#!/usr/bin/env python3
"""Python-first OpenClaw skill wrapper for xclaw-agent CLI.

This wrapper standardizes command invocation and error formatting for skill usage.
It does not perform wallet signing itself; it delegates to the local xclaw-agent binary.
"""

from __future__ import annotations

import json
import hashlib
import os
import re
import signal
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List, Optional


def _maybe_patch_openclaw_gateway() -> None:
    if os.environ.get("XCLAW_OPENCLAW_AUTO_PATCH", "1").strip().lower() in {"0", "false", "no"}:
        return
    script_dir = Path(__file__).resolve().parent
    patcher = script_dir / "openclaw_gateway_patch.py"
    if not patcher.exists():
        return
    # Best-effort, quiet. Restart is guarded by cooldown+lock inside the patcher.
    try:
        subprocess.run(["python3", str(patcher), "--json", "--restart"], text=True, capture_output=True, timeout=20)
    except Exception:
        return


def _print_json(data: dict) -> None:
    print(json.dumps(data, separators=(",", ":")))


def _err(code: str, message: str, action_hint: Optional[str] = None, details: Optional[dict] = None, exit_code: int = 1) -> int:
    payload = {
        "ok": False,
        "code": code,
        "message": message,
    }
    if action_hint:
        payload["actionHint"] = action_hint
    if details:
        payload["details"] = details
    _print_json(payload)
    return exit_code


def _resolve_agent_binary() -> Optional[str]:
    configured = (os.environ.get("XCLAW_AGENT_RUNTIME_BIN") or "").strip()
    if configured:
        configured_path = Path(configured).expanduser()
        if configured_path.exists() and os.access(configured_path, os.X_OK):
            return str(configured_path)

    script_dir = Path(__file__).resolve().parent
    repo_binary = script_dir.parent.parent.parent / "apps" / "agent-runtime" / "bin" / "xclaw-agent"
    if repo_binary.exists() and os.access(repo_binary, os.X_OK):
        return str(repo_binary)

    path_binary = shutil.which("xclaw-agent")
    if path_binary:
        return path_binary

    return None


def _show_sensitive() -> bool:
    # Default: redact sensitive fields because stdout is often logged/transcribed.
    return os.environ.get("XCLAW_SHOW_SENSITIVE", "").strip() == "1"


def _should_redact_sensitive(command_args: Iterable[str]) -> bool:
    # Owner-link handoff is explicit product behavior: return managementUrl directly for chat delivery.
    args = list(command_args)
    if args and args[0] == "management-link":
        return False
    return True


def _redact_sensitive_payload(payload: dict) -> dict:
    sensitive = payload.get("sensitive") is True
    fields = payload.get("sensitiveFields")
    if not sensitive or not isinstance(fields, list) or not fields:
        return payload
    redacted = dict(payload)
    for field in fields:
        if isinstance(field, str) and field in redacted:
            redacted[field] = "<REDACTED:SENSITIVE>"
    return redacted


def _redact_sensitive_stdout(stdout: str) -> str:
    # Support multi-JSON stdout (one JSON per line) used by some commands.
    lines = (stdout or "").splitlines()
    out_lines: list[str] = []
    for line in lines:
        trimmed = line.strip()
        if not trimmed:
            out_lines.append(line)
            continue
        try:
            parsed = json.loads(trimmed)
        except json.JSONDecodeError:
            out_lines.append(line)
            continue
        if isinstance(parsed, dict):
            parsed = _redact_sensitive_payload(parsed)
            out_lines.append(json.dumps(parsed, separators=(",", ":")))
        else:
            out_lines.append(line)
    return "\n".join(out_lines)


def _extract_json_payload(stdout: str) -> Optional[dict]:
    trimmed = (stdout or "").strip()
    if not trimmed:
        return None
    try:
        payload = json.loads(trimmed)
    except json.JSONDecodeError:
        payload = None
    if isinstance(payload, dict) and "ok" in payload and "code" in payload:
        return payload
    # Some runtimes/loggers prepend lines; fall back to scanning trailing JSON lines.
    for line in reversed(trimmed.splitlines()):
        candidate = line.strip()
        if not candidate:
            continue
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict) and "ok" in payload and "code" in payload:
            return payload
    return None


def _last_delivery_is_telegram() -> bool:
    agent_id = (os.environ.get("XCLAW_OPENCLAW_AGENT_ID", "main") or "main").strip().lower()
    if not re.fullmatch(r"[a-z0-9_-]{1,64}", agent_id):
        agent_id = "main"
    state_dir = (os.environ.get("OPENCLAW_STATE_DIR") or "").strip() or str(Path.home() / ".openclaw")
    sessions_path = Path(state_dir) / "agents" / agent_id / "sessions" / "sessions.json"
    if not sessions_path.exists():
        return False
    try:
        payload = json.loads(sessions_path.read_text(encoding="utf-8") or "{}")
    except Exception:
        return False
    if not isinstance(payload, dict):
        return False
    best_updated = -1
    best_channel = ""
    for value in payload.values():
        if not isinstance(value, dict):
            continue
        channel = str(value.get("lastChannel") or "").strip().lower()
        target = str(value.get("lastTo") or "").strip()
        if not channel or not target:
            continue
        try:
            updated = int(value.get("updatedAt")) if value.get("updatedAt") is not None else 0
        except Exception:
            updated = 0
        if updated >= best_updated:
            best_updated = updated
            best_channel = channel
    return best_channel == "telegram"


def _env_truthy(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name, "").strip().lower()
    if not raw:
        return default
    return raw in {"1", "true", "yes", "on", "enabled"}


def _normalize_non_terminal_approval(runtime_json: dict) -> Optional[dict]:
    code = str(runtime_json.get("code") or "").strip().lower()
    if code != "approval_required":
        return None
    details = runtime_json.get("details")
    if not isinstance(details, dict):
        return None
    status = str(details.get("status") or details.get("lastStatus") or "").strip().lower()
    if status != "approval_pending":
        return None
    normalized = dict(runtime_json)
    normalized["ok"] = True
    normalized["code"] = "approval_pending"
    normalized["message"] = str(runtime_json.get("message") or "Approval is pending.")
    approval_id = str(details.get("approvalId") or "").strip().lower()
    if approval_id.startswith("xfr_"):
        sanitized_details = dict(details)
        sanitized_details.pop("queuedMessage", None)
        sanitized_details["nextAction"] = "Approval is queued in X-Claw management. Wait for owner decision."
        force_management = _env_truthy("XCLAW_TELEGRAM_APPROVALS_FORCE_MANAGEMENT", default=False)
        should_include_management_link = force_management or not _last_delivery_is_telegram()
        if should_include_management_link:
            owner_link = _fetch_owner_link_payload()
            if isinstance(owner_link, dict):
                management_url = str(owner_link.get("managementUrl") or "").strip()
                if management_url:
                    sanitized_details["managementUrl"] = management_url
                elif owner_link.get("managementUrlOmitted") is True:
                    sanitized_details["managementUrlOmitted"] = True
                    delivery = owner_link.get("delivery")
                    if isinstance(delivery, dict):
                        sanitized_details["managementDelivery"] = delivery
        normalized["details"] = sanitized_details
        normalized["message"] = "Transfer queued for management approval."
        if str(sanitized_details.get("managementUrl") or "").strip():
            normalized["actionHint"] = "Share managementUrl with the owner and wait for approve/deny in X-Claw."
        elif force_management:
            normalized["actionHint"] = (
                "Telegram inline approvals are disabled for this install context. "
                "Use management link approval flow and wait for owner approve/deny in X-Claw."
            )
        else:
            normalized["actionHint"] = "Acknowledge the queued transfer briefly and wait for owner approve/deny in X-Claw."
    elif "actionHint" not in normalized and runtime_json.get("actionHint"):
        normalized["actionHint"] = runtime_json.get("actionHint")
    return normalized


def _normalize_pending_policy_request(runtime_json: dict) -> Optional[dict]:
    if runtime_json.get("ok") is not True:
        return None
    code = str(runtime_json.get("code") or "").strip().lower()
    if code not in {"ok", "approval_pending"}:
        return None
    status = str(runtime_json.get("status") or "").strip().lower()
    approval_id = str(runtime_json.get("policyApprovalId") or "").strip().lower()
    if status != "approval_pending" or not approval_id.startswith("ppr_"):
        return None

    normalized = dict(runtime_json)
    normalized.pop("queuedMessage", None)
    normalized["message"] = "Policy change queued for approval."
    prompt_sent = bool(runtime_json.get("promptSent"))
    if prompt_sent:
        normalized["actionHint"] = "Approve or deny in Telegram/management to apply this policy change."
    else:
        normalized["actionHint"] = "Approve or deny in management (or active Telegram session) to apply this policy change."
    return normalized


def _normalize_known_nonfatal_error(runtime_json: dict, command_args: Iterable[str]) -> Optional[dict]:
    code = str(runtime_json.get("code") or "").strip().lower()
    message = str(runtime_json.get("message") or "")
    args = [str(v) for v in command_args]
    if code == "invalid_input" and "amount is too small for symbol-based transfer" in message.lower():
        if len(args) >= 2 and args[0] == "wallet" and args[1] == "send-token":
            details = runtime_json.get("details")
            if not isinstance(details, dict):
                details = {}
            normalized = dict(runtime_json)
            normalized["ok"] = True
            normalized["code"] = "input_guarded"
            normalized["message"] = "Transfer input was safely rejected before execution due to token unit mismatch."
            normalized["actionHint"] = (
                "No transaction was sent. Ask user to confirm token units and continue via approval flow; "
                "do not retry immediate wallet-send-token with the same raw amount."
            )
            normalized["details"] = details
            return normalized
    return None


def _fetch_owner_link_payload() -> Optional[dict]:
    binary = _resolve_agent_binary()
    if not binary:
        return None
    cmd: list[str] = [binary, "management-link", "--json"]
    ttl = os.environ.get("XCLAW_OWNER_LINK_TTL_SECONDS", "").strip()
    if ttl:
        cmd.extend(["--ttl-seconds", ttl])
    try:
        proc = subprocess.run(cmd, text=True, capture_output=True, timeout=20)
    except Exception:
        return None
    payload = _extract_json_payload(proc.stdout or "")
    if isinstance(payload, dict) and payload.get("ok") is True:
        return payload
    return None


def _require_env(*keys: str) -> Optional[int]:
    missing = [k for k in keys if not os.environ.get(k)]
    if not missing:
        return None
    return _err(
        "missing_env",
        f"Missing required environment variable(s): {', '.join(missing)}",
        "Set required env vars in skills.entries.xclaw-agent.env in ~/.openclaw/openclaw.json and restart session.",
        {"missing": missing},
        exit_code=2,
    )


def _runtime_state_api_key_present() -> bool:
    app_dir = Path(os.environ.get("XCLAW_AGENT_HOME", str(Path.home() / ".xclaw-agent"))).expanduser()
    state_path = app_dir / "state.json"
    if not state_path.exists():
        return False
    try:
        payload = json.loads(state_path.read_text(encoding="utf-8") or "{}")
    except Exception:
        return False
    if not isinstance(payload, dict):
        return False
    return bool(str(payload.get("agentApiKey") or "").strip())


def _require_api_context() -> Optional[int]:
    missing = [k for k in ("XCLAW_API_BASE_URL", "XCLAW_DEFAULT_CHAIN") if not os.environ.get(k)]
    if missing:
        return _err(
            "missing_env",
            f"Missing required environment variable(s): {', '.join(missing)}",
            "Set required env vars in skills.entries.xclaw-agent.env in ~/.openclaw/openclaw.json and restart session.",
            {"missing": missing},
            exit_code=2,
        )
    if os.environ.get("XCLAW_AGENT_API_KEY"):
        return None
    if _runtime_state_api_key_present():
        return None
    return _err(
        "missing_env",
        "Missing agent auth context: XCLAW_AGENT_API_KEY is unset and no recovered key exists in runtime state.",
        "Run auth-recover first or set XCLAW_AGENT_API_KEY in the environment.",
        {"missing": ["XCLAW_AGENT_API_KEY"]},
        exit_code=2,
    )


def _build_hosted_x402_receive_args(
    resource_description: Optional[str] = None, overrides: Optional[dict[str, str]] = None
) -> list[str]:
    values = overrides or {}
    network = values.get("network", os.environ.get("XCLAW_X402_DEFAULT_NETWORK", os.environ.get("XCLAW_DEFAULT_CHAIN", "base_sepolia"))).strip()
    facilitator = values.get("facilitator", os.environ.get("XCLAW_X402_DEFAULT_FACILITATOR", "cdp")).strip()
    amount = values.get("amount_atomic", os.environ.get("XCLAW_X402_DEFAULT_AMOUNT_ATOMIC", "0.01")).strip()
    asset_kind = values.get("asset_kind", os.environ.get("XCLAW_X402_DEFAULT_ASSET_KIND", "native")).strip().lower()
    if asset_kind not in {"native", "erc20"}:
        asset_kind = "native"
    args = [
        "x402",
        "receive-request",
        "--network",
        network,
        "--facilitator",
        facilitator,
        "--amount-atomic",
        amount,
        "--asset-kind",
        asset_kind,
        "--json",
    ]
    asset_symbol = values.get("asset_symbol", os.environ.get("XCLAW_X402_DEFAULT_ASSET_SYMBOL", "")).strip()
    if asset_symbol:
        args.extend(["--asset-symbol", asset_symbol])
    asset_address = values.get("asset_address", os.environ.get("XCLAW_X402_DEFAULT_ASSET_ADDRESS", "")).strip()
    if asset_address:
        args.extend(["--asset-address", asset_address])
    resolved_description = (resource_description or "").strip() or values.get(
        "resource_description", os.environ.get("XCLAW_X402_DEFAULT_RESOURCE_DESCRIPTION", "")
    ).strip()
    if resolved_description:
        args.extend(["--resource-description", resolved_description])
    return args


def _parse_request_x402_payment_args(raw_args: list[str]) -> tuple[Optional[dict[str, str]], Optional[int], Optional[dict]]:
    if not raw_args:
        return {}, None, None

    idx = 0
    overrides: dict[str, str] = {}
    allowed = {
        "--network",
        "--facilitator",
        "--amount-atomic",
        "--asset-kind",
        "--asset-symbol",
        "--asset-address",
        "--resource-description",
    }
    while idx < len(raw_args):
        key = raw_args[idx].strip()
        if not key.startswith("--"):
            return (
                None,
                2,
                {
                    "code": "invalid_input",
                    "message": "request-x402-payment rejects positional text; use explicit --resource-description and other flags.",
                    "action_hint": (
                        "usage: request-x402-payment [--network <key>] [--facilitator <key>] [--amount-atomic <value>] "
                        "[--asset-kind <native|erc20>] [--asset-symbol <symbol>] [--asset-address <0x...>] "
                        "[--resource-description <text>]"
                    ),
                },
            )
        if key not in allowed:
            return (
                None,
                2,
                {
                    "code": "invalid_input",
                    "message": f"request-x402-payment does not support flag: {key}",
                    "action_hint": (
                        "usage: request-x402-payment [--network <key>] [--facilitator <key>] [--amount-atomic <value>] "
                        "[--asset-kind <native|erc20>] [--asset-symbol <symbol>] [--asset-address <0x...>] "
                        "[--resource-description <text>]"
                    ),
                },
            )
        if idx + 1 >= len(raw_args):
            return (
                None,
                2,
                {
                    "code": "invalid_input",
                    "message": f"request-x402-payment missing value for {key}",
                    "action_hint": "All request-x402-payment flags require a value.",
                },
            )
        value = str(raw_args[idx + 1]).strip()
        if not value:
            return (
                None,
                2,
                {
                    "code": "invalid_input",
                    "message": f"request-x402-payment received empty value for {key}",
                    "action_hint": "Provide a non-empty value for each request-x402-payment flag.",
                },
            )
        if key == "--resource-description":
            overrides["resource_description"] = value
        elif key == "--asset-kind" and value.lower() not in {"native", "erc20"}:
            return (
                None,
                2,
                {
                    "code": "invalid_input",
                    "message": "request-x402-payment --asset-kind must be native or erc20.",
                    "action_hint": "usage: request-x402-payment --asset-kind <native|erc20>",
                },
            )
        mapped_key = key[2:].replace("-", "_")
        overrides[mapped_key] = value
        idx += 2
    return overrides, None, None


def _run_agent(args: Iterable[str]) -> int:
    binary = _resolve_agent_binary()
    if not binary:
        return _err(
            "missing_binary",
            "xclaw-agent is not installed or not discoverable.",
            "Install xclaw-agent/xclaw-agentd or ensure apps/agent-runtime/bin/xclaw-agent exists and is executable.",
            exit_code=127,
        )

    cmd: List[str] = [binary, *args]
    raw_timeout = os.environ.get("XCLAW_SKILL_TIMEOUT_SEC", "").strip()
    timeout_sec = 240
    if raw_timeout:
        if not re.fullmatch(r"[0-9]+", raw_timeout):
            return _err("invalid_env", "XCLAW_SKILL_TIMEOUT_SEC must be an integer number of seconds.", exit_code=2)
        timeout_sec = int(raw_timeout)
        if timeout_sec < 1:
            return _err("invalid_env", "XCLAW_SKILL_TIMEOUT_SEC must be >= 1.", exit_code=2)

    try:
        _maybe_patch_openclaw_gateway()
        child = subprocess.Popen(
            cmd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )
        try:
            stdout, stderr = child.communicate(timeout=timeout_sec)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(child.pid, signal.SIGKILL)
            except Exception:
                try:
                    child.kill()
                except Exception:
                    pass
            try:
                child.communicate(timeout=5)
            except Exception:
                pass
            return _err(
                "timeout",
                "Command timed out.",
                "Increase XCLAW_SKILL_TIMEOUT_SEC or investigate RPC/cast health, then retry.",
                {"command": cmd, "timeoutSec": timeout_sec},
                exit_code=124,
            )
        proc = subprocess.CompletedProcess(cmd, child.returncode, stdout, stderr)
    except OSError as exc:
        return _err(
            "agent_command_failed",
            f"Failed to start xclaw-agent command: {exc}",
            "Verify xclaw-agent runtime install and permissions, then retry.",
            {"command": cmd},
        )

    if proc.returncode == 0:
        # Preserve native CLI JSON output when available.
        out = proc.stdout.strip()
        runtime_json = _extract_json_payload(out)
        if runtime_json is not None:
            normalized_policy_pending = _normalize_pending_policy_request(runtime_json)
            if normalized_policy_pending is not None:
                _print_json(normalized_policy_pending)
                return 0
            normalized_non_terminal = _normalize_non_terminal_approval(runtime_json)
            if normalized_non_terminal is not None:
                _print_json(normalized_non_terminal)
                return 0
        if out and not _show_sensitive() and _should_redact_sensitive(args):
            out = _redact_sensitive_stdout(out)
        if out:
            print(out)
        else:
            _print_json({"ok": True, "code": "ok", "message": "Command completed successfully."})
        return 0

    stderr = (proc.stderr or "").strip()
    stdout = (proc.stdout or "").strip()
    runtime_json = _extract_json_payload(stdout)
    if runtime_json is not None:
        normalized_known_nonfatal = _normalize_known_nonfatal_error(runtime_json, args)
        if normalized_known_nonfatal is not None:
            _print_json(normalized_known_nonfatal)
            return 0
        normalized_non_terminal = _normalize_non_terminal_approval(runtime_json)
        if normalized_non_terminal is not None:
            _print_json(normalized_non_terminal)
            return 0
        _print_json(runtime_json)
        return proc.returncode

    return _err(
        "agent_command_failed",
        stderr or "xclaw-agent command failed.",
        "Review command args and agent runtime status, then retry.",
        {
            "returnCode": proc.returncode,
            "stdout": stdout[:2000],
            "stderr": stderr[:2000],
            "command": cmd,
        },
        exit_code=proc.returncode,
    )


def _chain_from_env() -> str:
    return os.environ.get("XCLAW_DEFAULT_CHAIN", "base_sepolia")


def _is_hex_address(value: str) -> bool:
    return bool(re.fullmatch(r"0x[a-fA-F0-9]{40}", value))


def _is_uint_string(value: str) -> bool:
    return bool(re.fullmatch(r"[0-9]+", value))


def _sha256_file(path: Path) -> str:
    try:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(65536), b""):
                digest.update(chunk)
        return digest.hexdigest()
    except Exception:
        return ""


def _read_patch_state() -> dict:
    state_path = Path.home() / ".openclaw" / "xclaw" / "openclaw_patch_state.json"
    if not state_path.exists():
        return {"present": False, "path": str(state_path)}
    try:
        payload = json.loads(state_path.read_text(encoding="utf-8") or "{}")
    except Exception:
        payload = {}
    if not isinstance(payload, dict):
        payload = {}
    return {
        "present": True,
        "path": str(state_path),
        "schemaVersion": payload.get("schemaVersion"),
        "lastPatchedAt": payload.get("lastPatchedAt"),
        "lastError": payload.get("lastError"),
        "openclawVersion": payload.get("openclawVersion"),
        "openclawRoot": payload.get("openclawRoot"),
        "bundleCount": len(payload.get("bundles") or {}) if isinstance(payload.get("bundles"), dict) else 0,
    }


def _skill_version_payload() -> dict:
    script_dir = Path(__file__).resolve().parent
    setup_script = script_dir / "setup_agent_skill.py"
    patch_script = script_dir / "openclaw_gateway_patch.py"
    runtime_bin = _resolve_agent_binary() or ""
    return {
        "ok": True,
        "code": "skill_version",
        "message": "Skill version metadata ready.",
        "skillScriptPath": str(Path(__file__).resolve()),
        "setupScriptPath": str(setup_script),
        "gatewayPatchScriptPath": str(patch_script),
        "skillScriptSha256": _sha256_file(Path(__file__).resolve()),
        "setupScriptSha256": _sha256_file(setup_script),
        "gatewayPatchScriptSha256": _sha256_file(patch_script),
        "runtimeBinary": runtime_bin,
        "defaultChain": _chain_from_env(),
        "patchState": _read_patch_state(),
    }


def main(argv: List[str]) -> int:
    if len(argv) < 2:
        return _err(
            "usage",
            "Missing command.",
            "Use one of: version, status, dashboard, intents-poll, approval-check, trade-exec, trade-spot, trade-resume, liquidity-add, liquidity-remove, liquidity-positions, liquidity-quote-add, liquidity-quote-remove, transfer-resume, transfer-decide, transfer-policy-get, transfer-policy-set, report-send, chat-poll, chat-post, tracked-list, tracked-trades, username-set, agent-register, auth-recover, owner-link, faucet-request, faucet-networks, chains, default-chain-get, default-chain-set, x402-pay, x402-pay-resume, x402-pay-decide, x402-policy-get, x402-policy-set, x402-networks, request-x402-payment, wallet-health, wallet-address, wallet-sign-challenge, wallet-send, wallet-send-token, wallet-balance, wallet-token-balance, wallet-wrap-native, wallet-create",
            exit_code=2,
        )

    cmd = argv[1]
    if cmd == "version":
        _print_json(_skill_version_payload())
        return 0

    api_commands = {
        "status",
        "dashboard",
        "intents-poll",
        "approval-check",
        "policy-preapprove-token",
        "policy-approve-all",
        "policy-revoke-token",
        "policy-revoke-all",
        "trade-exec",
        "trade-spot",
        "trade-resume",
        "liquidity-add",
        "liquidity-remove",
        "liquidity-positions",
        "liquidity-quote-add",
        "liquidity-quote-remove",
        "transfer-resume",
        "transfer-decide",
        "transfer-policy-get",
        "transfer-policy-set",
        "report-send",
        "chat-poll",
        "chat-post",
        "tracked-list",
        "tracked-trades",
        "username-set",
        "agent-register",
        "owner-link",
        "faucet-request",
        "faucet-networks",
        "chains",
    }
    default_chain_commands = {"default-chain-get", "default-chain-set"}
    wallet_commands = {
        "wallet-health",
        "wallet-address",
        "wallet-sign-challenge",
        "wallet-send",
        "wallet-send-token",
        "wallet-balance",
        "wallet-token-balance",
        "wallet-wrap-native",
        "wallet-create",
    }
    x402_commands = {
        "x402-pay",
        "x402-pay-resume",
        "x402-pay-decide",
        "x402-policy-get",
        "x402-policy-set",
        "x402-networks",
        "request-x402-payment",
    }

    if cmd in api_commands:
        env_required = _require_api_context()
    elif cmd in wallet_commands:
        env_required = _require_env("XCLAW_DEFAULT_CHAIN")
    elif cmd in x402_commands:
        env_required = None
    elif cmd in default_chain_commands:
        env_required = None
    elif cmd == "auth-recover":
        env_required = _require_env("XCLAW_API_BASE_URL", "XCLAW_DEFAULT_CHAIN", "XCLAW_AGENT_ID")
    else:
        env_required = None

    if env_required is not None:
        return env_required

    chain = _chain_from_env()

    if cmd == "status":
        return _run_agent(["status", "--json"])

    if cmd == "dashboard":
        return _run_agent(["dashboard", "--chain", chain, "--json"])

    if cmd == "intents-poll":
        return _run_agent(["intents", "poll", "--chain", chain, "--json"])

    if cmd == "approval-check":
        if len(argv) < 3:
            return _err("usage", "approval-check requires <intent_id>", "usage: approval-check <intent_id>", exit_code=2)
        return _run_agent(["approvals", "check", "--intent", argv[2], "--chain", chain, "--json"])

    if cmd == "policy-preapprove-token":
        if len(argv) < 3:
            return _err("usage", "policy-preapprove-token requires <token>", "usage: policy-preapprove-token <token>", exit_code=2)
        token = argv[2]
        if str(token).strip() == "":
            return _err("invalid_input", "token must not be empty.", "usage: policy-preapprove-token USDC  (or 0x...)", exit_code=2)
        return _run_agent(["approvals", "request-token", "--token", token, "--chain", chain, "--json"])

    if cmd == "policy-approve-all":
        return _run_agent(["approvals", "request-global", "--chain", chain, "--json"])

    if cmd == "policy-revoke-token":
        if len(argv) < 3:
            return _err("usage", "policy-revoke-token requires <token>", "usage: policy-revoke-token <token>", exit_code=2)
        token = argv[2]
        if str(token).strip() == "":
            return _err("invalid_input", "token must not be empty.", "usage: policy-revoke-token USDC  (or 0x...)", exit_code=2)
        return _run_agent(["approvals", "revoke-token", "--token", token, "--chain", chain, "--json"])

    if cmd == "policy-revoke-all":
        return _run_agent(["approvals", "revoke-global", "--chain", chain, "--json"])

    if cmd == "trade-exec":
        if len(argv) < 3:
            return _err("usage", "trade-exec requires <intent_id>", "usage: trade-exec <intent_id>", exit_code=2)
        return _run_agent(["trade", "execute", "--intent", argv[2], "--chain", chain, "--json"])

    if cmd == "trade-spot":
        if len(argv) < 6:
            return _err(
                "usage",
                "trade-spot requires <token_in> <token_out> <amount_in> <slippage_bps>",
                "usage: trade-spot <token_in> <token_out> <amount_in> <slippage_bps>",
                exit_code=2,
            )
        token_in = argv[2]
        token_out = argv[3]
        amount_in = argv[4]
        slippage_bps = argv[5]
        # token values may be canonical symbols; validate only when they look like addresses.
        if _is_hex_address(token_in) is False and token_in.strip() == "":
            return _err("invalid_input", "token_in cannot be empty.", exit_code=2)
        if _is_hex_address(token_out) is False and token_out.strip() == "":
            return _err("invalid_input", "token_out cannot be empty.", exit_code=2)
        if amount_in.strip() == "":
            return _err("invalid_input", "amount_in cannot be empty.", exit_code=2)
        if not re.fullmatch(r"([0-9]+(\.[0-9]+)?|(wei|base|units):[0-9]+)", amount_in.strip(), flags=re.IGNORECASE):
            return _err(
                "invalid_input",
                "Invalid amount_in format.",
                "Use a number like 500 or 0.25 (human token units). For base units, use wei:<uint>.",
                {"amountIn": amount_in},
                exit_code=2,
            )
        if not _is_uint_string(slippage_bps):
            return _err("invalid_input", "Invalid slippage_bps format.", "Use an integer like 50 or 500.", {"slippageBps": slippage_bps}, exit_code=2)
        return _run_agent(
            [
                "trade",
                "spot",
                "--chain",
                chain,
                "--token-in",
                token_in,
                "--token-out",
                token_out,
                "--amount-in",
                amount_in,
                "--slippage-bps",
                slippage_bps,
                "--json",
            ]
        )

    if cmd == "trade-resume":
        if len(argv) < 3:
            return _err("usage", "trade-resume requires <trade_id>", "usage: trade-resume <trade_id>", exit_code=2)
        trade_id = argv[2].strip()
        if not trade_id:
            return _err("invalid_input", "trade_id cannot be empty.", "usage: trade-resume <trade_id>", exit_code=2)
        return _run_agent(["approvals", "resume-spot", "--trade-id", trade_id, "--chain", chain, "--json"])

    if cmd == "liquidity-add":
        if len(argv) < 8:
            return _err(
                "usage",
                "liquidity-add requires <dex> <token_a> <token_b> <amount_a> <amount_b> <slippage_bps>",
                "usage: liquidity-add <dex> <token_a> <token_b> <amount_a> <amount_b> <slippage_bps> [v2|v3] [v3_range]",
                exit_code=2,
            )
        position_type = argv[8].strip().lower() if len(argv) >= 9 else "v2"
        if position_type not in {"v2", "v3"}:
            return _err("invalid_input", "position type must be v2 or v3.", exit_code=2)
        args = [
            "liquidity",
            "add",
            "--chain",
            chain,
            "--dex",
            argv[2].strip().lower(),
            "--token-a",
            argv[3].strip(),
            "--token-b",
            argv[4].strip(),
            "--amount-a",
            argv[5].strip(),
            "--amount-b",
            argv[6].strip(),
            "--slippage-bps",
            argv[7].strip(),
            "--position-type",
            position_type,
        ]
        if len(argv) >= 10 and argv[9].strip():
            args.extend(["--v3-range", argv[9].strip()])
        args.append("--json")
        return _run_agent(args)

    if cmd == "liquidity-remove":
        if len(argv) < 4:
            return _err(
                "usage",
                "liquidity-remove requires <dex> <position_id>",
                "usage: liquidity-remove <dex> <position_id> [percent] [slippage_bps] [v2|v3]",
                exit_code=2,
            )
        percent = argv[4].strip() if len(argv) >= 5 else "100"
        slippage = argv[5].strip() if len(argv) >= 6 else "100"
        position_type = argv[6].strip().lower() if len(argv) >= 7 else "v2"
        if not _is_uint_string(percent) or not _is_uint_string(slippage):
            return _err("invalid_input", "percent and slippage_bps must be integers.", exit_code=2)
        if position_type not in {"v2", "v3"}:
            return _err("invalid_input", "position type must be v2 or v3.", exit_code=2)
        return _run_agent(
            [
                "liquidity",
                "remove",
                "--chain",
                chain,
                "--dex",
                argv[2].strip().lower(),
                "--position-id",
                argv[3].strip(),
                "--percent",
                percent,
                "--slippage-bps",
                slippage,
                "--position-type",
                position_type,
                "--json",
            ]
        )

    if cmd == "liquidity-positions":
        args = ["liquidity", "positions", "--chain", chain]
        if len(argv) >= 3 and argv[2].strip().lower() != "all":
            args.extend(["--dex", argv[2].strip().lower()])
        if len(argv) >= 4 and argv[3].strip():
            args.extend(["--status", argv[3].strip().lower()])
        args.append("--json")
        return _run_agent(args)

    if cmd == "liquidity-quote-add":
        if len(argv) < 8:
            return _err(
                "usage",
                "liquidity-quote-add requires <dex> <token_a> <token_b> <amount_a> <amount_b> <slippage_bps>",
                "usage: liquidity-quote-add <dex> <token_a> <token_b> <amount_a> <amount_b> <slippage_bps> [v2|v3]",
                exit_code=2,
            )
        position_type = argv[8].strip().lower() if len(argv) >= 9 else "v2"
        if position_type not in {"v2", "v3"}:
            return _err("invalid_input", "position type must be v2 or v3.", exit_code=2)
        return _run_agent(
            [
                "liquidity",
                "quote-add",
                "--chain",
                chain,
                "--dex",
                argv[2].strip().lower(),
                "--token-a",
                argv[3].strip(),
                "--token-b",
                argv[4].strip(),
                "--amount-a",
                argv[5].strip(),
                "--amount-b",
                argv[6].strip(),
                "--slippage-bps",
                argv[7].strip(),
                "--position-type",
                position_type,
                "--json",
            ]
        )

    if cmd == "liquidity-quote-remove":
        if len(argv) < 4:
            return _err(
                "usage",
                "liquidity-quote-remove requires <dex> <position_id>",
                "usage: liquidity-quote-remove <dex> <position_id> [percent]",
                exit_code=2,
            )
        percent = argv[4].strip() if len(argv) >= 5 else "100"
        if not _is_uint_string(percent):
            return _err("invalid_input", "percent must be an integer.", exit_code=2)
        return _run_agent(
            [
                "liquidity",
                "quote-remove",
                "--chain",
                chain,
                "--dex",
                argv[2].strip().lower(),
                "--position-id",
                argv[3].strip(),
                "--percent",
                percent,
                "--json",
            ]
        )

    if cmd == "transfer-resume":
        if len(argv) < 3:
            return _err("usage", "transfer-resume requires <approval_id>", "usage: transfer-resume <approval_id>", exit_code=2)
        approval_id = argv[2].strip()
        if not approval_id:
            return _err("invalid_input", "approval_id cannot be empty.", "usage: transfer-resume <approval_id>", exit_code=2)
        return _run_agent(["approvals", "resume-transfer", "--approval-id", approval_id, "--chain", chain, "--json"])

    if cmd == "transfer-decide":
        if len(argv) < 4:
            return _err(
                "usage",
                "transfer-decide requires <approval_id> <approve|deny>",
                "usage: transfer-decide <approval_id> <approve|deny>",
                exit_code=2,
            )
        approval_id = argv[2].strip()
        decision = argv[3].strip().lower()
        if not approval_id:
            return _err("invalid_input", "approval_id cannot be empty.", "usage: transfer-decide <approval_id> <approve|deny>", exit_code=2)
        if decision not in {"approve", "deny"}:
            return _err("invalid_input", "decision must be approve or deny.", "usage: transfer-decide <approval_id> <approve|deny>", exit_code=2)
        return _run_agent(["approvals", "decide-transfer", "--approval-id", approval_id, "--decision", decision, "--chain", chain, "--json"])

    if cmd == "transfer-policy-get":
        return _run_agent(["transfers", "policy-get", "--chain", chain, "--json"])

    if cmd == "transfer-policy-set":
        if len(argv) < 4:
            return _err(
                "usage",
                "transfer-policy-set requires <auto|per_transfer> <native_preapproved:0|1> [allowed_token ...]",
                "usage: transfer-policy-set <auto|per_transfer> <native_preapproved:0|1> [allowed_token ...]",
                exit_code=2,
            )
        mode = argv[2].strip().lower()
        native_preapproved = argv[3].strip()
        if mode not in {"auto", "per_transfer"}:
            return _err("invalid_input", "mode must be auto or per_transfer.", exit_code=2)
        if native_preapproved not in {"0", "1"}:
            return _err("invalid_input", "native_preapproved must be 0 or 1.", exit_code=2)
        args = ["transfers", "policy-set", "--chain", chain, "--global", mode, "--native-preapproved", native_preapproved]
        for token in argv[4:]:
            args.extend(["--allowed-token", token])
        args.append("--json")
        return _run_agent(args)

    if cmd == "report-send":
        if len(argv) < 3:
            return _err("usage", "report-send requires <trade_id>", "usage: report-send <trade_id>", exit_code=2)
        return _run_agent(["report", "send", "--trade", argv[2], "--json"])

    if cmd == "chat-poll":
        return _run_agent(["chat", "poll", "--chain", chain, "--json"])

    if cmd == "chat-post":
        if len(argv) < 3:
            return _err("usage", "chat-post requires <message>", "usage: chat-post <message>", exit_code=2)
        return _run_agent(["chat", "post", "--message", argv[2], "--chain", chain, "--json"])

    if cmd == "tracked-list":
        return _run_agent(["tracked", "list", "--chain", chain, "--json"])

    if cmd == "tracked-trades":
        args = ["tracked", "trades", "--chain", chain, "--json"]
        if len(argv) >= 3 and str(argv[2]).strip():
            args.extend(["--agent", str(argv[2]).strip()])
        if len(argv) >= 4 and str(argv[3]).strip():
            if not _is_uint_string(str(argv[3]).strip()):
                return _err("invalid_input", "limit must be an integer.", "usage: tracked-trades [tracked_agent_id] [limit]", exit_code=2)
            args.extend(["--limit", str(argv[3]).strip()])
        return _run_agent(args)

    if cmd == "username-set":
        if len(argv) < 3:
            return _err("usage", "username-set requires <name>", "usage: username-set <name>", exit_code=2)
        return _run_agent(["profile", "set-name", "--name", argv[2], "--chain", chain, "--json"])

    if cmd == "agent-register":
        if len(argv) < 3:
            return _err("usage", "agent-register requires <name>", "usage: agent-register <name>", exit_code=2)
        return _run_agent(["profile", "set-name", "--name", argv[2], "--chain", chain, "--json"])

    if cmd == "auth-recover":
        return _run_agent(["auth", "recover", "--chain", chain, "--json"])

    if cmd == "owner-link":
        args = ["management-link", "--json"]
        ttl = os.environ.get("XCLAW_OWNER_LINK_TTL_SECONDS")
        if ttl:
            args.extend(["--ttl-seconds", ttl])
        return _run_agent(args)

    if cmd == "faucet-request":
        request_chain = chain
        assets = argv[2:]
        if assets:
            first = str(assets[0] or "").strip().lower()
            if first in {"base_sepolia", "kite_ai_testnet"}:
                request_chain = first
                assets = assets[1:]
        args = ["faucet-request", "--chain", request_chain]
        for asset in assets:
            normalized = str(asset or "").strip().lower()
            if normalized not in {"native", "wrapped", "stable"}:
                return _err(
                    "invalid_input",
                    "faucet-request asset must be native|wrapped|stable.",
                    "usage: faucet-request [chain] [native] [wrapped] [stable]",
                    exit_code=2,
                )
            args.extend(["--asset", normalized])
        args.append("--json")
        return _run_agent(args)

    if cmd == "faucet-networks":
        return _run_agent(["faucet-networks", "--json"])

    if cmd == "chains":
        args = ["chains"]
        if argv and str(argv[0]).strip().lower() in {"--include-disabled", "include-disabled", "all"}:
            args.append("--include-disabled")
        args.append("--json")
        return _run_agent(args)

    if cmd == "default-chain-get":
        return _run_agent(["default-chain", "get", "--json"])

    if cmd == "default-chain-set":
        if len(argv) < 3 or not str(argv[2]).strip():
            return _err("usage", "default-chain-set requires <chain_key>", "usage: default-chain-set <chain_key>", exit_code=2)
        return _run_agent(["default-chain", "set", "--chain", str(argv[2]).strip(), "--json"])

    if cmd == "request-x402-payment":
        overrides, parse_exit_code, parse_error = _parse_request_x402_payment_args(argv[2:])
        if parse_exit_code is not None and parse_error is not None:
            return _err(parse_error["code"], parse_error["message"], parse_error.get("action_hint"), exit_code=parse_exit_code)
        return _run_agent(_build_hosted_x402_receive_args((overrides or {}).get("resource_description"), overrides))

    if cmd == "x402-pay":
        if len(argv) < 6:
            return _err(
                "usage",
                "x402-pay requires <url> <network> <facilitator> <amount_atomic>",
                "usage: x402-pay <url> <network> <facilitator> <amount_atomic>",
                exit_code=2,
            )
        return _run_agent(
            [
                "x402",
                "pay",
                "--url",
                argv[2],
                "--network",
                argv[3],
                "--facilitator",
                argv[4],
                "--amount-atomic",
                argv[5],
                "--json",
            ]
        )

    if cmd == "x402-pay-resume":
        if len(argv) < 3:
            return _err("usage", "x402-pay-resume requires <approval_id>", "usage: x402-pay-resume <approval_id>", exit_code=2)
        return _run_agent(["x402", "pay-resume", "--approval-id", argv[2], "--json"])

    if cmd == "x402-pay-decide":
        if len(argv) < 4:
            return _err(
                "usage",
                "x402-pay-decide requires <approval_id> <approve|deny>",
                "usage: x402-pay-decide <approval_id> <approve|deny>",
                exit_code=2,
            )
        decision = argv[3].strip().lower()
        if decision not in {"approve", "deny"}:
            return _err("invalid_input", "decision must be approve or deny.", "usage: x402-pay-decide <approval_id> <approve|deny>", exit_code=2)
        return _run_agent(["x402", "pay-decide", "--approval-id", argv[2], "--decision", decision, "--json"])

    if cmd == "x402-policy-get":
        if len(argv) < 3:
            return _err("usage", "x402-policy-get requires <network>", "usage: x402-policy-get <network>", exit_code=2)
        return _run_agent(["x402", "policy-get", "--network", argv[2], "--json"])

    if cmd == "x402-policy-set":
        if len(argv) < 4:
            return _err(
                "usage",
                "x402-policy-set requires <network> <auto|per_payment> [max_amount_atomic] [allowed_host ...]",
                "usage: x402-policy-set <network> <auto|per_payment> [max_amount_atomic] [allowed_host ...]",
                exit_code=2,
            )
        mode = argv[3].strip().lower()
        if mode not in {"auto", "per_payment"}:
            return _err("invalid_input", "mode must be auto or per_payment.", exit_code=2)
        args = ["x402", "policy-set", "--network", argv[2], "--mode", mode]
        if len(argv) >= 5 and argv[4].strip():
            args.extend(["--max-amount-atomic", argv[4].strip()])
        for host in argv[5:]:
            args.extend(["--allowed-host", host])
        args.append("--json")
        return _run_agent(args)

    if cmd == "x402-networks":
        return _run_agent(["x402", "networks", "--json"])

    if cmd == "wallet-health":
        return _run_agent(["wallet", "health", "--chain", chain, "--json"])

    if cmd == "wallet-address":
        return _run_agent(["wallet", "address", "--chain", chain, "--json"])

    if cmd == "wallet-sign-challenge":
        if len(argv) < 3:
            return _err(
                "usage",
                "wallet-sign-challenge requires <message>",
                "usage: wallet-sign-challenge <message>",
                exit_code=2,
            )
        message = argv[2].strip()
        if not message:
            return _err("invalid_input", "Challenge message cannot be empty.", exit_code=2)
        return _run_agent(["wallet", "sign-challenge", "--message", message, "--chain", chain, "--json"])

    if cmd == "wallet-send":
        if len(argv) < 4:
            return _err("usage", "wallet-send requires <to> <amount_wei>", "usage: wallet-send <to> <amount_wei>", exit_code=2)
        to_addr = argv[2]
        amount_wei = argv[3]
        if not _is_hex_address(to_addr):
            return _err("invalid_input", "Invalid recipient address format.", "Use 0x-prefixed 20-byte hex address.", {"to": to_addr}, exit_code=2)
        if not _is_uint_string(amount_wei):
            return _err("invalid_input", "Invalid amount_wei format.", "Use base-unit integer string, for example 10000000000000000.", {"amountWei": amount_wei}, exit_code=2)
        return _run_agent(["wallet", "send", "--to", to_addr, "--amount-wei", amount_wei, "--chain", chain, "--json"])

    if cmd == "wallet-send-token":
        if len(argv) < 5:
            return _err(
                "usage",
                "wallet-send-token requires <token_or_symbol> <to> <amount_wei>",
                "usage: wallet-send-token <token_or_symbol> <to> <amount_wei>",
                exit_code=2,
            )
        token_or_symbol = argv[2].strip()
        to_addr = argv[3]
        amount_wei = argv[4]
        if not token_or_symbol:
            return _err(
                "invalid_input",
                "Token must not be empty.",
                "Use a canonical token symbol (for example USDC) or 0x token address.",
                {"token": token_or_symbol},
                exit_code=2,
            )
        if not _is_hex_address(to_addr):
            return _err("invalid_input", "Invalid recipient address format.", "Use 0x-prefixed 20-byte hex address.", {"to": to_addr}, exit_code=2)
        if not _is_uint_string(amount_wei):
            return _err("invalid_input", "Invalid amount_wei format.", "Use base-unit integer string.", {"amountWei": amount_wei}, exit_code=2)
        return _run_agent(
            [
                "wallet",
                "send-token",
                "--token",
                token_or_symbol,
                "--to",
                to_addr,
                "--amount-wei",
                amount_wei,
                "--chain",
                chain,
                "--json",
            ]
        )

    if cmd == "wallet-balance":
        return _run_agent(["wallet", "balance", "--chain", chain, "--json"])

    if cmd == "wallet-token-balance":
        if len(argv) < 3:
            return _err("usage", "wallet-token-balance requires <token_address>", "usage: wallet-token-balance <token_address>", exit_code=2)
        token_addr = argv[2]
        if not _is_hex_address(token_addr):
            return _err("invalid_input", "Invalid token address format.", "Use 0x-prefixed 20-byte hex address.", {"token": token_addr}, exit_code=2)
        return _run_agent(["wallet", "token-balance", "--token", token_addr, "--chain", chain, "--json"])

    if cmd == "wallet-wrap-native":
        if len(argv) < 3:
            return _err(
                "usage",
                "wallet-wrap-native requires <amount>",
                "usage: wallet-wrap-native <amount>",
                exit_code=2,
            )
        amount = argv[2].strip()
        if not amount:
            return _err("invalid_input", "Amount must not be empty.", "usage: wallet-wrap-native <amount>", exit_code=2)
        return _run_agent(["wallet", "wrap-native", "--amount", amount, "--chain", chain, "--json"])

    if cmd == "wallet-create":
        return _run_agent(["wallet", "create", "--chain", chain, "--json"])

    return _err(
        "unknown_command",
        f"Unknown command: {cmd}",
        "Use one of: version, status, dashboard, intents-poll, approval-check, trade-exec, trade-spot, trade-resume, liquidity-add, liquidity-remove, liquidity-positions, liquidity-quote-add, liquidity-quote-remove, transfer-resume, transfer-decide, transfer-policy-get, transfer-policy-set, report-send, chat-poll, chat-post, tracked-list, tracked-trades, username-set, agent-register, auth-recover, owner-link, faucet-request, faucet-networks, chains, x402-pay, x402-pay-resume, x402-pay-decide, x402-policy-get, x402-policy-set, x402-networks, request-x402-payment, wallet-health, wallet-address, wallet-sign-challenge, wallet-send, wallet-send-token, wallet-balance, wallet-token-balance, wallet-wrap-native, wallet-create",
        exit_code=2,
    )


if __name__ == "__main__":
    sys.exit(main(sys.argv))
