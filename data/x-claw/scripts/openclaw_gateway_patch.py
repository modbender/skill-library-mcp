#!/usr/bin/env python3
"""Idempotent OpenClaw gateway patcher for X-Claw Telegram approvals.

This script patches the installed OpenClaw gateway bundle so Telegram inline-button callbacks
(`xappr|a|<tradeId>|<chainKey>`) approve X-Claw trades strictly via agent-auth, without routing
through the LLM/message pipeline.

Design constraints:
- Portable: no dependency on repo-local OpenClaw sources.
- No external patch tooling required (no git/patch).
- Safe: restart only when a new patch was applied, with cooldown + lock to avoid loops.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


MARKER = "xclaw: telegram approval callback received"
DECISION_ACK_MARKER = "xclaw: telegram approval decision ack"
DECISION_ACK_MARKER_V2 = "xclaw: telegram approval decision ack v2"
DECISION_ACK_MARKER_V3 = "xclaw: telegram approval decision ack v3"
DECISION_ACK_MARKER_V4 = "xclaw: telegram approval decision ack v4"
DECISION_ACK_MARKER_V5 = "xclaw: telegram approval decision ack v5"
DECISION_ACK_MARKER_V6 = "xclaw: telegram approval decision ack v6"
DECISION_ACK_MARKER_V7 = "xclaw: telegram approval decision ack v7"
DECISION_ACK_MARKER_V8 = "xclaw: telegram approval decision ack v8"
DECISION_ACK_MARKER_V9 = "xclaw: telegram approval decision ack v9"
DECISION_ACK_MARKER_V10 = "xclaw: telegram approval decision ack v10"
DECISION_ACK_MARKER_V11 = "xclaw: telegram approval decision ack v11"
DECISION_ACK_MARKER_V12 = "xclaw: telegram approval decision ack v12"
DECISION_ACK_MARKER_V13 = "xclaw: telegram approval decision ack v13"
DECISION_ACK_MARKER_V14 = "xclaw: telegram approval decision ack v14"
DECISION_ACK_MARKER_V15 = "xclaw: telegram approval decision ack v15"
DECISION_ACK_MARKER_V16 = "xclaw: telegram approval decision ack v16"
DECISION_ACK_MARKER_V17 = "xclaw: telegram approval decision ack v17"
DECISION_ACK_MARKER_V18 = "xclaw: telegram approval decision ack v18"
DECISION_ACK_MARKER_V19 = "xclaw: telegram approval decision ack v19"
DECISION_ACK_MARKER_V20 = "xclaw: telegram approval decision ack v20"
DECISION_ACK_MARKER_V21 = "xclaw: telegram approval decision ack v21"
DECISION_ACK_MARKER_V22 = "xclaw: telegram approval decision ack v22"
DECISION_ACK_MARKER_V23 = "xclaw: telegram approval decision ack v23"
DECISION_ACK_MARKER_V24 = "xclaw: telegram approval decision ack v24"
DECISION_ACK_MARKER_V25 = "xclaw: telegram approval decision ack v25"
DECISION_ACK_MARKER_V26 = "xclaw: telegram approval decision ack v26"
DECISION_ACK_MARKER_V27 = "xclaw: telegram approval decision ack v27"
DECISION_ACK_MARKER_V28 = "xclaw: telegram approval decision ack v28"
DECISION_ROUTE_MARKER_V1 = "xclaw: telegram approval decision routed to agent"
DECISION_EXEC_MARKER_V1 = "xclaw: telegram trade resume trigger v1"
DECISION_RESULT_ROUTE_MARKER_V1 = "xclaw: telegram trade result routed to agent"
QUEUED_BUTTONS_MARKER = "xclaw: telegram queued approval buttons"
QUEUED_BUTTONS_MARKER_V2 = "xclaw: telegram queued approval buttons v2"
QUEUED_BUTTONS_MARKER_V3 = "xclaw: telegram queued approval buttons v3"
QUEUED_BUTTONS_MARKER_V4 = "xclaw: telegram queued approval buttons v4"
LEGACY_DM_SENTINEL = 'Allow in DMs even when inlineButtonsScope is "allowlist", gated by chatId == senderId.'
# Bump when patch semantics change so we invalidate the cached "already patched" fast-path.
STATE_SCHEMA_VERSION = 60
STATE_DIR = Path.home() / ".openclaw" / "xclaw"
STATE_FILE = STATE_DIR / "openclaw_patch_state.json"
LOCK_FILE = STATE_DIR / "openclaw_patch.lock"
LEGACY_SOURCE_SNIPPET_RE = re.compile(
    r",\s*source\s*:\s*\{\s*channel\s*:\s*\"telegram\"[^}]*\}",
    flags=re.MULTILINE,
)

# Match either older "approve-only" wording or newer "inline button handling" wording.
CANONICAL_BLOCK_START = "// X-Claw Telegram approvals:"
PAGINATION_ANCHOR = "const paginationMatch = data.match(/^commands_page_"
REPO_RUNTIME_BIN = (Path(__file__).resolve().parents[3] / "apps" / "agent-runtime" / "bin" / "xclaw-agent").as_posix()


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _emit(payload: dict[str, Any]) -> int:
    print(json.dumps(payload, separators=(",", ":")))
    return 0


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _bundle_supports_queued_policy_buttons(text: str) -> bool:
    """
    Heuristic: ensure the *sendTelegramText* queued-buttons block supports policy approvals
    (Approval ID: ppr_...) and emits the policy attach log.
    """
    # Keep this intentionally simple and stable: if these strings exist, we consider it upgraded.
    return ("queued policy buttons attached" in text) and ("xpol|a|${approvalId}" in text)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if os.name != "nt":
        try:
            os.chmod(path, 0o600)
        except Exception:
            pass


class LockTimeout(RuntimeError):
    pass


@dataclass
class PatchResult:
    ok: bool
    patched: bool
    restarted: bool
    openclaw_bin: str | None = None
    openclaw_version: str | None = None
    openclaw_root: str | None = None
    loader_paths: list[str] | None = None
    error: str | None = None


def _acquire_lock(timeout_sec: int = 10) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    start = time.time()
    while True:
        try:
            fd = os.open(str(LOCK_FILE), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.write(fd, str(os.getpid()).encode("ascii"))
            os.close(fd)
            return
        except FileExistsError:
            # Stale lock guard: if lock is old, remove it.
            try:
                age = time.time() - LOCK_FILE.stat().st_mtime
                if age > 120:
                    LOCK_FILE.unlink(missing_ok=True)  # type: ignore[arg-type]
                    continue
            except Exception:
                pass
            if time.time() - start > timeout_sec:
                raise LockTimeout("openclaw patch lock timed out")
            time.sleep(0.1)


def _release_lock() -> None:
    try:
        LOCK_FILE.unlink(missing_ok=True)  # type: ignore[arg-type]
    except Exception:
        pass


def _resolve_openclaw_bin() -> str | None:
    forced = os.environ.get("OPENCLAW_BIN", "").strip() or os.environ.get("XCLAW_OPENCLAW_BIN", "").strip()
    if forced:
        candidate = Path(forced).expanduser()
        if candidate.exists():
            return str(candidate)
        return None
    return shutil.which("openclaw")


def _openclaw_pkg_root(openclaw_bin: str) -> Path | None:
    try:
        resolved = Path(openclaw_bin).resolve()
    except Exception:
        resolved = Path(openclaw_bin)
    # For npm global install, openclaw_bin points to .../openclaw/openclaw.mjs
    parent = resolved.parent
    if (parent / "package.json").exists():
        return parent
    # If invoked via bin symlink, walk up a few levels.
    for candidate in [parent, *parent.parents]:
        if (candidate / "package.json").exists():
            return candidate
        if candidate == candidate.parent:
            break
    return None


def _read_openclaw_version(openclaw_bin: str, pkg_root: Path | None) -> str | None:
    try:
        proc = subprocess.run([openclaw_bin, "--version"], text=True, capture_output=True, timeout=5)
        if proc.returncode == 0:
            value = (proc.stdout or "").strip()
            if value:
                return value
    except Exception:
        pass
    if pkg_root and (pkg_root / "package.json").exists():
        try:
            payload = json.loads((pkg_root / "package.json").read_text(encoding="utf-8"))
            version = payload.get("version")
            return str(version) if isinstance(version, str) and version.strip() else None
        except Exception:
            return None
    return None


def _find_loader_bundles(pkg_root: Path) -> list[Path]:
    dist_dir = pkg_root / "dist"
    if not dist_dir.exists():
        return []
    # Patch all runtime reply bundles that actually contain the Telegram callback handler.
    # Some OpenClaw builds invoke plugin-sdk reply bundles in gateway execution paths.
    candidates = sorted(
        list(dist_dir.glob("reply-*.js")) + list((dist_dir / "plugin-sdk").glob("reply-*.js"))
    )
    bundles: list[Path] = []
    for path in candidates:
        # Safety: only patch the canonical gateway reply bundle(s). Patching multiple hashed bundles
        # has proven too risky (can brick the OpenClaw CLI if we ever mis-inject).
        if not path.name.startswith("reply-"):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        # Heuristic: Telegram callback_query handler with inline command pagination lives in these bundles.
        if 'bot.on("callback_query"' in text and "const paginationMatch = data.match(/^commands_page_" in text:
            bundles.append(path)
    return bundles


def _node_check_js_text(js_text: str) -> tuple[bool, str | None]:
    """
    Validate JS syntax for a would-be patched bundle. If this fails, do not write to disk.
    """
    node = shutil.which("node")
    if not node:
        return False, "node_not_found"
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        tmp = STATE_DIR / f".tmp-openclaw-bundle-check-{os.getpid()}.mjs"
        tmp.write_text(js_text, encoding="utf-8")
        proc = subprocess.run([node, "--check", str(tmp)], text=True, capture_output=True, timeout=10)
        ok = proc.returncode == 0
        if not ok:
            err = (proc.stderr or proc.stdout or "").strip()
            return False, err[:600] if err else "node_check_failed"
        return True, None
    except Exception as exc:
        return False, f"node_check_exception:{exc}"
    finally:
        try:
            (STATE_DIR / f".tmp-openclaw-bundle-check-{os.getpid()}.mjs").unlink(missing_ok=True)  # type: ignore[arg-type]
        except Exception:
            pass


def _inject_after_anchor(text: str, anchor: str, injection: str) -> tuple[str, bool]:
    idx = text.find(anchor)
    if idx < 0:
        return text, False
    insert_at = idx + len(anchor)
    return text[:insert_at] + injection + text[insert_at:], True


def _patch_loader_bundle(raw: str) -> tuple[str, bool, str | None]:
    # Normalize older patch variants to avoid duplicated intercept blocks (idempotent overwrite semantics).
    normalized = False
    # v1 legacy: payload had an extra `source` field that violates X-Claw trade-status schema.
    # Remove it in-place to upgrade older patched bundles without requiring marker removal.
    raw2, n_sub = LEGACY_SOURCE_SNIPPET_RE.subn("", raw)
    if n_sub:
        raw = raw2
        normalized = True

    if LEGACY_DM_SENTINEL in raw:
        sentinel_idx = raw.find(LEGACY_DM_SENTINEL)
        # Remove from the start of the legacy X-Claw block to just before the group-policy block.
        block_start = raw.rfind("// X-Claw Telegram approvals: approve-only inline button handling (strict, no LLM).", 0, sentinel_idx)
        if block_start >= 0:
            line_start = raw.rfind("\n", 0, block_start)
            if line_start < 0:
                line_start = 0
            block_end = raw.find("if (isGroup) {", sentinel_idx)
            if block_end > sentinel_idx:
                raw = raw[:line_start] + "\n" + raw[block_end:]
                normalized = True

    # Upgrade path: if an older canonical block exists, replace it with the current canonical block.
    # This lets us ship UX tweaks (e.g. remove keyboard immediately) without telling users to reinstall OpenClaw.
    if MARKER in raw and (
        "xappr|r|" not in raw
        or "xpol|" not in raw
        or DECISION_ACK_MARKER_V3 not in raw
        or DECISION_ACK_MARKER_V4 not in raw
        or DECISION_ACK_MARKER_V5 not in raw
        or DECISION_ACK_MARKER_V6 not in raw
        or DECISION_ACK_MARKER_V7 not in raw
        or DECISION_ACK_MARKER_V8 not in raw
        or DECISION_ACK_MARKER_V9 not in raw
        or DECISION_ACK_MARKER_V10 not in raw
        or DECISION_ACK_MARKER_V11 not in raw
        or DECISION_ACK_MARKER_V12 not in raw
        or DECISION_ACK_MARKER_V13 not in raw
        or DECISION_ACK_MARKER_V14 not in raw
        or DECISION_ACK_MARKER_V15 not in raw
        or DECISION_ACK_MARKER_V16 not in raw
        or DECISION_ACK_MARKER_V25 not in raw
        or DECISION_ACK_MARKER_V26 not in raw
        or DECISION_ACK_MARKER_V27 not in raw
        or DECISION_ACK_MARKER_V28 not in raw
        or DECISION_ROUTE_MARKER_V1 not in raw
        or DECISION_EXEC_MARKER_V1 not in raw
        or DECISION_RESULT_ROUTE_MARKER_V1 not in raw
        or "xfer|" not in raw
    ):
        idx = raw.find(PAGINATION_ANCHOR)
        if idx < 0:
            return raw, False, "pagination_anchor_not_found"
        start = raw.rfind(CANONICAL_BLOCK_START, 0, idx)
        if start >= 0:
            raw = raw[:start] + raw[idx:]
            normalized = True

    # If the canonical decision block is already present (newest version), ensure queued-message auto-buttons are too.
    # If we see the old ack-only version (missing route marker), drop and re-inject canonical block.
    if MARKER in raw and DECISION_ACK_MARKER_V3 in raw and (
        DECISION_ACK_MARKER_V4 not in raw
        or DECISION_ACK_MARKER_V5 not in raw
        or DECISION_ACK_MARKER_V6 not in raw
        or DECISION_ACK_MARKER_V7 not in raw
        or DECISION_ACK_MARKER_V8 not in raw
        or DECISION_ACK_MARKER_V9 not in raw
        or DECISION_ACK_MARKER_V10 not in raw
        or DECISION_ACK_MARKER_V11 not in raw
        or DECISION_ACK_MARKER_V12 not in raw
        or DECISION_ACK_MARKER_V13 not in raw
        or DECISION_ACK_MARKER_V14 not in raw
        or DECISION_ACK_MARKER_V15 not in raw
        or DECISION_ACK_MARKER_V16 not in raw
        or DECISION_ACK_MARKER_V25 not in raw
        or DECISION_ACK_MARKER_V26 not in raw
        or DECISION_ACK_MARKER_V27 not in raw
        or DECISION_ACK_MARKER_V28 not in raw
        or DECISION_ROUTE_MARKER_V1 not in raw
        or DECISION_EXEC_MARKER_V1 not in raw
        or DECISION_RESULT_ROUTE_MARKER_V1 not in raw
        or "xpol|" not in raw
        or "xfer|" not in raw
    ):
        idx = raw.find(PAGINATION_ANCHOR)
        if idx < 0:
            return raw, False, "pagination_anchor_not_found"
        start = raw.rfind(CANONICAL_BLOCK_START, 0, idx)
        if start >= 0:
            raw = raw[:start] + raw[idx:]
            normalized = True

    def _upgrade_spawn_env(text: str) -> tuple[str, bool]:
        changed = False
        text, n_transfer = re.subn(
            r'const child = childMod\.spawn\(runtimeBin, \["approvals", "decide-transfer", [^\n]*\{ stdio: \["ignore", "pipe", "pipe"\] \}\);',
            'const childEnv = { ...process.env, ...Object.fromEntries(Object.entries(env || {}).map(([k, v]) => [String(k), String(v)])) }; const child = childMod.spawn(runtimeBin, ["approvals", "decide-transfer", "--approval-id", subjectId, "--decision", decision, "--chain", chainKey, "--reason-message", action === "r" ? "Denied via Telegram" : "", "--json"], { stdio: ["ignore", "pipe", "pipe"], env: childEnv });',
            text,
        )
        text, n_trade = re.subn(
            r'const child = childMod\.spawn\(runtimeBin, \["approvals", "resume-spot", [^\n]*\{ stdio: \["ignore", "pipe", "pipe"\] \}\);',
            'const childEnv = { ...process.env, ...Object.fromEntries(Object.entries(env || {}).map(([k, v]) => [String(k), String(v)])) }; const child = childMod.spawn(runtimeBin, ["approvals", "resume-spot", "--trade-id", subjectId, "--chain", chainKey, "--json"], { stdio: ["ignore", "pipe", "pipe"], env: childEnv });',
            text,
        )
        changed = (n_transfer > 0) or (n_trade > 0)
        return text, changed

    def _upgrade_transfer_result_routing(text: str) -> tuple[str, bool]:
        text2, n = re.subn(
            r'const decisionWord = body\?\.ok \? "FILLED" : "FAILED";\s*const instruction = body\?\.ok \? "Reply to the user confirming the transfer succeeded with tx details\." : "Reply to the user confirming the transfer failed and provide next steps\.";',
            'const transferStatus = String(body?.status ?? (body?.ok ? "filled" : "failed")).toLowerCase(); const isRejected = transferStatus === "rejected"; const isFilled = transferStatus === "filled"; const decisionWord = isFilled ? "FILLED" : (isRejected ? "REJECTED" : "FAILED"); const instruction = isFilled ? "Reply to the user confirming the transfer succeeded with tx details." : (isRejected ? "Reply to the user confirming the transfer was denied and no transaction was executed." : "Reply to the user confirming the transfer failed and provide next steps.");',
            text,
        )
        text3, n2 = re.subn(
            r'const amountWei = String\(body\?\.amountWei \?\? "\?"\);\s*const toAddress = String\(body\?\.to \?\? "\?"\);',
            'const amountWei = String(body?.amountWei ?? "?"); const amountDisplay = String(body?.amountDisplay ?? "").trim(); const toAddress = String(body?.to ?? "?");',
            text2,
        )
        text4, n3 = re.subn(
            r'const finalMsg = `\$\{head\}\\n\$\{amountWei\} \$\{tokenSymbol\}\\nTo: \$\{toAddress\}\\nApproval: \$\{subjectId\}\\nChain: \$\{chainKey\}\$\{modeLine\}\$\{txLine\}\$\{reasonLine\}`;',
            'const amountLine = amountDisplay ? amountDisplay : `${amountWei} ${tokenSymbol}`; const finalMsg = `${head}\\n${amountLine}\\nTo: ${toAddress}\\nApproval: ${subjectId}\\nChain: ${chainKey}${modeLine}${txLine}${reasonLine}`;',
            text3,
        )
        text5, n4 = re.subn(
            r'AmountWei: \$\{amountWei\}\\nToken: \$\{tokenSymbol\}',
            'Amount: ${amountDisplay || `${amountWei} ${tokenSymbol}`}\\nAmountWei: ${amountWei}\\nToken: ${tokenSymbol}',
            text4,
        )
        text6, n5 = re.subn(
            r'const amountLine = amountDisplay \? amountDisplay : `\$\{amountWei\} \$\{tokenSymbol\}`;',
            'let normalizedAmount = ""; if (!amountDisplay && /^[0-9]+$/.test(amountWei)) { const tokenDecimalsRaw = Number(body?.tokenDecimals); const tokenDecimals = Number.isFinite(tokenDecimalsRaw) && tokenDecimalsRaw >= 0 ? Math.floor(tokenDecimalsRaw) : 18; if (tokenDecimals <= 36) { const s = String(BigInt(amountWei)); const padded = s.length <= tokenDecimals ? s.padStart(tokenDecimals + 1, "0") : s; const whole = tokenDecimals > 0 ? padded.slice(0, -tokenDecimals) : padded; const fracRaw = tokenDecimals > 0 ? padded.slice(-tokenDecimals) : ""; const frac = fracRaw.replace(/0+$/, ""); normalizedAmount = frac ? `${whole}.${frac} ${tokenSymbol}` : `${whole} ${tokenSymbol}`; } } const amountLine = amountDisplay ? amountDisplay : (normalizedAmount || `${amountWei} ${tokenSymbol}`);',
            text5,
        )
        text7, n6 = re.subn(
            r'Amount: \$\{amountDisplay \|\| `\$\{amountWei\} \$\{tokenSymbol\}`\}',
            'Amount: ${amountLine}',
            text6,
        )
        text8, n7 = re.subn(
            r'try \{ logger\.info\(\{ subjectId, chainKey, chatId \}, "xclaw: telegram transfer result delivered \(no synthetic route\)"\); \} catch \{\}\s*return;',
            'try { const transferStatus = String(body?.status ?? (body?.ok ? "filled" : "failed")).toLowerCase(); const isRejected = transferStatus === "rejected"; const isFilled = transferStatus === "filled"; const decisionWord = isFilled ? "FILLED" : (isRejected ? "REJECTED" : "FAILED"); const instruction = isFilled ? "Reply to the user confirming the transfer succeeded with tx details." : (isRejected ? "Reply to the user confirming the transfer was denied and no transaction was executed." : "Reply to the user confirming the transfer failed and provide next steps."); const syntheticText = `[X-CLAW TRANSFER RESULT]\\nDecision: ${decisionWord}\\nApproval: ${subjectId}\\nChain: ${chainKey}\\nTxHash: ${txHash || "n/a"}\\nAmount: ${amountLine}\\nTo: ${toAddress}\\nSource: telegram_callback_transfer\\nInstruction: ${instruction}`; const storeAllowFrom2 = await readChannelAllowFromStore("telegram").catch(() => []); const syntheticAllowFrom = Array.from(new Set([...(Array.isArray(storeAllowFrom2) ? storeAllowFrom2.map((v) => String(v)) : []), String(callback?.from?.id ?? ""), String(chatId ?? "")])).filter((v) => !!v); const getFile2 = typeof ctx.getFile === "function" ? ctx.getFile.bind(ctx) : async () => ({}); const syntheticMessage2 = { ...callbackMessage, from: callback.from, text: syntheticText, caption: void 0, caption_entities: void 0, entities: void 0, date: Math.floor(Date.now() / 1000) }; await processMessage({ message: syntheticMessage2, me: ctx.me, getFile: getFile2 }, [], syntheticAllowFrom, { messageIdOverride: `xclaw-transfer-result-${callback.id}` }); } catch {} try { logger.info({ subjectId, chainKey, chatId, ok: !!body?.ok }, "xclaw: telegram transfer result routed to agent"); } catch {} return;',
            text7,
        )
        text9, n8 = re.subn(
            r'• To: \$\{toAddress\}\\n• Approval ID: \\`\$\{subjectId\}\\`\\n• Chain: \\`\$\{chainKey\}\\`',
            '• To: \\`${toAddress}\\`\\n• Approval ID: \\`${subjectId}\\`\\n• Chain: \\`${chainKey}\\`',
            text8,
        )
        return text9, (n > 0) or (n2 > 0) or (n3 > 0) or (n4 > 0) or (n5 > 0) or (n6 > 0) or (n7 > 0) or (n8 > 0)

    def _upgrade_trade_result_noise(text: str) -> tuple[str, bool]:
        text2, n1 = re.subn(
            r'const amountHuman = String\(body\?\.amountIn \?\? flow\?\.amountInHuman \?\? \(pairMatch\?\.\[1\] \|\| "\?"\)\);',
            'const amountHuman = String(body?.amountIn ?? flow?.amountInHuman ?? (pairMatch?.[1] || "")).trim();',
            text,
        )
        text3, n2 = re.subn(
            r'const tokenInSym = String\(body\?\.tokenInSymbol \?\? flow\?\.tokenInSymbol \?\? \(pairMatch\?\.\[2\] \|\| "TOKEN_IN"\)\);',
            'const tokenInSym = String(body?.tokenInSymbol ?? flow?.tokenInSymbol ?? (pairMatch?.[2] || "")).trim();',
            text2,
        )
        text4, n3 = re.subn(
            r'const tokenOutSym = String\(body\?\.tokenOutSymbol \?\? flow\?\.tokenOutSymbol \?\? \(pairMatch\?\.\[3\] \|\| "TOKEN_OUT"\)\);',
            'const tokenOutSym = String(body?.tokenOutSymbol ?? flow?.tokenOutSymbol ?? (pairMatch?.[3] || "")).trim();',
            text3,
        )
        text5, n4 = re.subn(
            r'const finalMsg = `\$\{head\}\\n\$\{amountHuman\} \$\{tokenInSym\} -> \$\{tokenOutSym\}\\nTrade: \$\{subjectId\}\\nChain: \$\{chainKey\}\$\{txLine\}\$\{reasonLine\}`;',
            'const pairLine = amountHuman && tokenInSym && tokenOutSym ? `\\n${amountHuman} ${tokenInSym} -> ${tokenOutSym}` : ""; const finalMsg = `${head}${pairLine}\\nTrade: ${subjectId}\\nChain: ${chainKey}${txLine}${reasonLine}`;',
            text4,
        )
        text6, n5 = re.subn(
            r'(const finalMsg = `\$\{head\}\$\{pairLine\}\\nTrade: \$\{subjectId\}\\nChain: \$\{chainKey\}\$\{txLine\}\$\{reasonLine\}`;)',
            r'\1 try { const decisionWord = body?.ok ? "FILLED" : "FAILED"; const instruction = body?.ok ? "Reply to the user confirming the trade succeeded with tx details." : "Reply to the user confirming the trade failed and provide next steps."; const syntheticText = `[X-CLAW TRADE RESULT]\\nDecision: ${decisionWord}\\nTrade: ${subjectId}\\nChain: ${chainKey}\\nTxHash: ${txHash || "n/a"}${pairLine ? `\\nPair: ${amountHuman} ${tokenInSym} -> ${tokenOutSym}` : ""}\\nSource: telegram_callback_trade\\nInstruction: ${instruction}`; const storeAllowFrom2 = await readChannelAllowFromStore("telegram").catch(() => []); const syntheticAllowFrom = Array.from(new Set([...(Array.isArray(storeAllowFrom2) ? storeAllowFrom2.map((v) => String(v)) : []), String(callback?.from?.id ?? ""), String(chatId ?? "")])).filter((v) => !!v); const getFile2 = typeof ctx.getFile === "function" ? ctx.getFile.bind(ctx) : async () => ({}); const syntheticMessage2 = { ...callbackMessage, from: callback.from, text: syntheticText, caption: void 0, caption_entities: void 0, entities: void 0, date: Math.floor(Date.now() / 1000) }; await processMessage({ message: syntheticMessage2, me: ctx.me, getFile: getFile2 }, [], syntheticAllowFrom, { messageIdOverride: `xclaw-trade-result-${callback.id}` }); } catch {}',
            text5,
        )
        text7, n6 = re.subn(
            r'(const finalMsg = `\$\{head\}\$\{pairLine\}\\nTrade: \$\{subjectId\}\\nChain: \$\{chainKey\}\$\{txLine\}\$\{reasonLine\}`;\s*)(try \{ const decisionWord = body\?\.ok \? "FILLED" : "FAILED";)',
            r'\1\2',
            text6,
        )
        return text7, (n1 > 0) or (n2 > 0) or (n3 > 0) or (n4 > 0) or (n5 > 0) or (n6 > 0)

    def _upgrade_approval_route_dedupe(text: str) -> tuple[str, bool]:
        changed = False
        text2, n1 = re.subn(
            r'await processMessage\(\{ message: syntheticMessage, me: ctx\.me, getFile \}, \[\], storeAllowFrom, \{ messageIdOverride: `xclaw-approval-\$\{callback\.id\}` \}\);',
            'if (!(parts[0] === "xappr" && action !== "r")) { await processMessage({ message: syntheticMessage, me: ctx.me, getFile }, [], storeAllowFrom, { messageIdOverride: `xclaw-approval-${callback.id}` }); }',
            text,
        )
        changed = changed or (n1 > 0)
        text3, n2 = re.subn(
            r'try \{ logger\.info\(\{ subjectId, chainKey, chatId, action, kind: parts\[0\] \}, "xclaw: telegram approval decision routed to agent"\); \} catch \{\}',
            'if (!(parts[0] === "xappr" && action !== "r")) { try { logger.info({ subjectId, chainKey, chatId, action, kind: parts[0] }, "xclaw: telegram approval decision routed to agent"); } catch {} }',
            text2,
        )
        changed = changed or (n2 > 0)
        return text3, changed

    def _upgrade_runtime_success_trade_resume(text: str) -> tuple[str, bool]:
        # Ensure runtime-success callback path (exitCode===0 && body.ok) also triggers
        # resume-spot and synthetic trade-result routing before returning.
        marker = 'if (parts[0] === "xappr" && action !== "r") {'
        pattern = re.compile(
            r'(if \(exitCode === 0 && !!body\?\.ok\) \{[\s\S]*?if \(action === "r"\) \{[\s\S]*?\}\s*)(return;\s*\})'
        )
        injection = (
            '\t\t\t\t\t\t\t\tif (parts[0] === "xappr" && action !== "r") {\n'
            f'\t\t\t\t\t\t\t\t\t\t// {DECISION_EXEC_MARKER_V1}\n'
            '\t\t\t\t\t\t\t\t\t\ttry {\n'
            '\t\t\t\t\t\t\t\t\t\t\tconst inflightKey = `${subjectId}|${chainKey}`;\n'
            '\t\t\t\t\t\t\t\t\t\t\tconst __resumeSet = (globalThis.__xclawTradeResumeInflight && globalThis.__xclawTradeResumeInflight instanceof Set)\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t? globalThis.__xclawTradeResumeInflight\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t: (() => { const s = new Set(); globalThis.__xclawTradeResumeInflight = s; return s; })();\n'
            '\t\t\t\t\t\t\t\t\t\t\tif (!__resumeSet.has(inflightKey)) {\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t__resumeSet.add(inflightKey);\n'
            '\t\t\t\t\t\t\t\t\t\t\t\tsetTimeout(async () => {\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\ttry {\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst childMod = await import("node:child_process");\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst fsMod = await import("node:fs");\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst runtimeCandidates = [\n'
            f'\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t{json.dumps(REPO_RUNTIME_BIN)},\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tString(env?.XCLAW_AGENT_RUNTIME_BIN ?? process.env.XCLAW_AGENT_RUNTIME_BIN ?? "").trim(),\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t"xclaw-agent"\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\t].filter((v) => !!v);\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst runtimeBin = runtimeCandidates.find((candidate) => candidate === "xclaw-agent" || fsMod.existsSync(candidate)) || "xclaw-agent";\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst childEnv = { ...process.env, ...Object.fromEntries(Object.entries(env || {}).map(([k, v]) => [String(k), String(v)])) };\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst child = childMod.spawn(runtimeBin, ["approvals", "resume-spot", "--trade-id", subjectId, "--chain", chainKey, "--json"], { stdio: ["ignore", "pipe", "pipe"], env: childEnv });\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\tlet out = "";\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\tlet err = "";\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\tchild.stdout?.on("data", (chunk) => { if (out.length < 12000) out += String(chunk); });\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\tchild.stderr?.on("data", (chunk) => { if (err.length < 4000) err += String(chunk); });\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst exitCode = await new Promise((resolve) => child.on("close", (code) => resolve(Number(code ?? 1))));\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst lines = out.split(/\\r?\\n/).map((v) => String(v || "").trim()).filter((v) => v.length > 0);\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\tlet body = null;\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\ttry { body = lines.length > 0 ? JSON.parse(lines[lines.length - 1]) : null; } catch {}\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst statusWord = String(body?.status ?? (body?.ok ? "filled" : "failed"));\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst txHash = String(body?.txHash ?? "").trim();\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst flow = body?.flowSummary ?? {};\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst promptText = String(callbackMessage.text ?? "");\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst pairMatch = promptText.match(/\\n\\s*([0-9]+(?:\\.[0-9]+)?)\\s+([A-Z0-9_]+)\\s*->\\s*([A-Z0-9_]+)/i);\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst amountHuman = String(body?.amountIn ?? flow?.amountInHuman ?? (pairMatch?.[1] || "")).trim();\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst tokenInSym = String(body?.tokenInSymbol ?? flow?.tokenInSymbol ?? (pairMatch?.[2] || "")).trim();\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst tokenOutSym = String(body?.tokenOutSymbol ?? flow?.tokenOutSymbol ?? (pairMatch?.[3] || "")).trim();\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst head = body?.ok ? `Trade result: ${statusWord}` : `Trade result: failed`;\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst txLine = txHash ? `\\nTx: ${txHash}` : "";\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst reasonLine = !body?.ok ? `\\nReason: ${String(body?.message ?? err ?? `resume exit ${exitCode}`)}` : "";\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst pairLine = amountHuman && tokenInSym && tokenOutSym ? `\\n${amountHuman} ${tokenInSym} -> ${tokenOutSym}` : "";\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst finalMsg = `${head}${pairLine}\\nTrade: ${subjectId}\\nChain: ${chainKey}${txLine}${reasonLine}`;\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\ttry {\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst decisionWord = body?.ok ? "FILLED" : "FAILED";\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst instruction = body?.ok\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t? "Reply to the user confirming the trade succeeded with tx details."\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t: "Reply to the user confirming the trade failed and provide next steps.";\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst syntheticText = `[X-CLAW TRADE RESULT]\\nDecision: ${decisionWord}\\nTrade: ${subjectId}\\nChain: ${chainKey}\\nTxHash: ${txHash || "n/a"}${pairLine ? `\\nPair: ${amountHuman} ${tokenInSym} -> ${tokenOutSym}` : ""}\\nSource: telegram_callback_trade\\nInstruction: ${instruction}`;\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst storeAllowFrom2 = await readChannelAllowFromStore("telegram").catch(() => []);\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst syntheticAllowFrom = Array.from(new Set([...(Array.isArray(storeAllowFrom2) ? storeAllowFrom2.map((v) => String(v)) : []), String(callback?.from?.id ?? ""), String(chatId ?? "")])).filter((v) => !!v);\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst getFile2 = typeof ctx.getFile === "function" ? ctx.getFile.bind(ctx) : async () => ({});\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst syntheticMessage2 = {\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t...callbackMessage,\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tfrom: callback.from,\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\ttext: syntheticText,\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tcaption: void 0,\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tcaption_entities: void 0,\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tentities: void 0,\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tdate: Math.floor(Date.now() / 1000)\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t};\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tawait processMessage({ message: syntheticMessage2, me: ctx.me, getFile: getFile2 }, [], syntheticAllowFrom, { messageIdOverride: `xclaw-trade-result-${callback.id}` });\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\t} catch {}\n'
            f'\t\t\t\t\t\t\t\t\t\t\t\t\t\ttry {{ logger.info({{ subjectId, chainKey, chatId, ok: !!body?.ok }}, "{DECISION_RESULT_ROUTE_MARKER_V1}"); }} catch {{}}\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t} catch (resumeErr) {\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\ttry { logger.error({ subjectId, chainKey, err: String(resumeErr) }, "xclaw: trade resume trigger failed"); } catch {}\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t} finally {\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t\ttry { __resumeSet.delete(inflightKey); } catch {}\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t\t}\n'
            '\t\t\t\t\t\t\t\t\t\t\t\t}, 0);\n'
            '\t\t\t\t\t\t\t\t\t\t\t}\n'
            '\t\t\t\t\t\t\t\t\t\t} catch {}\n'
            '\t\t\t\t\t\t\t\t}\n'
        )
        changed = False

        def _repl(match: re.Match[str]) -> str:
            nonlocal changed
            before = match.group(1)
            if marker in before:
                return match.group(0)
            changed = True
            return before + injection + match.group(2)

        out = pattern.sub(_repl, text, count=1)
        return out, changed

    if (
        MARKER in raw
        and DECISION_ACK_MARKER_V3 in raw
        and DECISION_ACK_MARKER_V4 in raw
        and DECISION_ACK_MARKER_V5 in raw
        and DECISION_ACK_MARKER_V6 in raw
        and DECISION_ACK_MARKER_V7 in raw
        and DECISION_ACK_MARKER_V8 in raw
        and DECISION_ACK_MARKER_V9 in raw
        and DECISION_ACK_MARKER_V10 in raw
        and DECISION_ACK_MARKER_V11 in raw
        and DECISION_ACK_MARKER_V12 in raw
        and DECISION_ACK_MARKER_V13 in raw
        and DECISION_ACK_MARKER_V14 in raw
        and DECISION_ACK_MARKER_V15 in raw
        and DECISION_ACK_MARKER_V16 in raw
        and DECISION_ACK_MARKER_V25 in raw
        and DECISION_ACK_MARKER_V26 in raw
        and DECISION_ACK_MARKER_V27 in raw
        and DECISION_ACK_MARKER_V28 in raw
        and DECISION_ROUTE_MARKER_V1 in raw
        and DECISION_EXEC_MARKER_V1 in raw
        and DECISION_RESULT_ROUTE_MARKER_V1 in raw
        and "xpol|" in raw
        and "xfer|" in raw
    ):
        changed_any = False
        raw, changed_spawn = _upgrade_spawn_env(raw)
        changed_any = changed_any or changed_spawn
        raw, changed_route = _upgrade_transfer_result_routing(raw)
        changed_any = changed_any or changed_route
        raw, changed_trade_noise = _upgrade_trade_result_noise(raw)
        changed_any = changed_any or changed_trade_noise
        raw, changed_dedupe = _upgrade_approval_route_dedupe(raw)
        changed_any = changed_any or changed_dedupe
        raw, changed_runtime_success = _upgrade_runtime_success_trade_resume(raw)
        changed_any = changed_any or changed_runtime_success
        if QUEUED_BUTTONS_MARKER not in raw:
            raw2, changed2, err2 = _patch_queued_buttons(raw)
            if not err2:
                raw = raw2
                changed_any = changed_any or changed2
        # Always evaluate the v3 queued-buttons injection for upgrades (trade-only v3 -> trade+policy v3).
        raw3, changed3, err3 = _patch_queued_buttons_v2(raw)
        if not err3:
            raw = raw3
            changed_any = changed_any or changed3
        normalized = normalized or changed_any
        return raw, normalized, None

    idx = raw.find(PAGINATION_ANCHOR)
    if idx < 0:
        return raw, False, "pagination_anchor_not_found"

    # Insert immediately before pagination handling (after allowlist/group policy checks).
    general_injection = (
        '\n'
        '\t\t\t// X-Claw Telegram approvals: inline button handling (strict, no LLM).\n'
        '\t\t\t// Expected callback_data:\n'
        '\t\t\t// - trade approval: xappr|a|<tradeId>|<chainKey> (approve) OR xappr|r|<tradeId>|<chainKey> (reject)\n'
        '\t\t\t// - policy approval: xpol|a|<policyApprovalId>|<chainKey> (approve) OR xpol|r|<policyApprovalId>|<chainKey> (reject)\n'
        '\t\t\t// - transfer approval: xfer|a|<approvalId>|<chainKey> (approve) OR xfer|r|<approvalId>|<chainKey> (deny)\n'
        '\t\t\t// This runs after allowlist/group policy checks.\n'
        '\t\t\tif (data.startsWith("xappr|") || data.startsWith("xpol|") || data.startsWith("xfer|")) {\n'
        '\t\t\t\tconst parts = data.split("|").map((p) => String(p || "").trim());\n'
        '\t\t\t\tif (parts.length === 4 && (parts[0] === "xappr" || parts[0] === "xpol" || parts[0] === "xfer") && (parts[1] === "a" || parts[1] === "r") && parts[2] && parts[3]) {\n'
        '\t\t\t\t\tconst action = parts[1];\n'
        '\t\t\t\t\tconst subjectId = parts[2];\n'
        '\t\t\t\t\tconst chainKey = parts[3];\n'
        f'\t\t\t\t\ttry {{ logger.info({{ subjectId, chainKey, chatId, senderId, isGroup, kind: parts[0] }}, "{MARKER}"); }} catch {{}}\n'
        '\t\t\t\t\tconst skill = cfg?.skills?.entries?.["xclaw-agent"];\n'
        '\t\t\t\t\tconst env = skill?.env ?? {};\n'
        '\t\t\t\t\tconst apiKey = String(skill?.apiKey ?? env?.XCLAW_API_KEY ?? process.env.XCLAW_API_KEY ?? "").trim();\n'
        '\t\t\t\t\t// Reduce perceived latency: best-effort stop spinner while runtime applies canonical clear.\n'
        '\t\t\t\t\ttry { bot.api.answerCallbackQuery(callback.id, { text: action === "r" ? "Denying..." : "Approving...", show_alert: false }); } catch {}\n'
        '\t\t\t\t\ttry {\n'
        '\t\t\t\t\t\tconst atEpochSec = (typeof callback?.date === "number" ? callback.date : (typeof callbackMessage?.date === "number" ? callbackMessage.date : Math.floor(Date.now() / 1000)));\n'
        '\t\t\t\t\t\tconst atIso = (/* @__PURE__ */ new Date(atEpochSec * 1000)).toISOString();\n'
        '\t\t\t\t\t\tif (parts[0] === "xfer") {\n'
        '\t\t\t\t\t\t\tconst decision = action === "r" ? "deny" : "approve";\n'
        '\t\t\t\t\t\t\tconst childMod = await import("node:child_process");\n'
        '\t\t\t\t\t\t\tconst fsMod = await import("node:fs");\n'
        '\t\t\t\t\t\t\tconst runtimeCandidates = [\n'
        f'\t\t\t\t\t\t\t\t{json.dumps(REPO_RUNTIME_BIN)},\n'
        '\t\t\t\t\t\t\t\tString(env?.XCLAW_AGENT_RUNTIME_BIN ?? process.env.XCLAW_AGENT_RUNTIME_BIN ?? "").trim(),\n'
        '\t\t\t\t\t\t\t\t"xclaw-agent"\n'
        '\t\t\t\t\t\t\t].filter((v) => !!v);\n'
        '\t\t\t\t\t\t\tconst runtimeBin = runtimeCandidates.find((candidate) => candidate === "xclaw-agent" || fsMod.existsSync(candidate)) || "xclaw-agent";\n'
        '\t\t\t\t\t\t\tconst childEnv = { ...process.env, ...Object.fromEntries(Object.entries(env || {}).map(([k, v]) => [String(k), String(v)])) };\n'
        '\t\t\t\t\t\t\tconst child = childMod.spawn(runtimeBin, ["approvals", "decide-transfer", "--approval-id", subjectId, "--decision", decision, "--chain", chainKey, "--reason-message", action === "r" ? "Denied via Telegram" : "", "--json"], { stdio: ["ignore", "pipe", "pipe"], env: childEnv });\n'
        '\t\t\t\t\t\t\tlet out = "";\n'
        '\t\t\t\t\t\t\tlet err = "";\n'
        '\t\t\t\t\t\t\tchild.stdout?.on("data", (chunk) => { if (out.length < 12000) out += String(chunk); });\n'
        '\t\t\t\t\t\t\tchild.stderr?.on("data", (chunk) => { if (err.length < 4000) err += String(chunk); });\n'
        '\t\t\t\t\t\t\tconst exitCode = await new Promise((resolve) => child.on("close", (code) => resolve(Number(code ?? 1))));\n'
        '\t\t\t\t\t\t\tconst lines = out.split(/\\r?\\n/).map((v) => String(v || "").trim()).filter((v) => v.length > 0);\n'
        '\t\t\t\t\t\t\tlet body = null;\n'
        '\t\t\t\t\t\t\ttry { body = lines.length > 0 ? JSON.parse(lines[lines.length - 1]) : null; } catch {}\n'
        '\t\t\t\t\t\t\tconst currentStatus = String(body?.status ?? (body?.ok ? "filled" : "failed"));\n'
        '\t\t\t\t\t\t\tconst txHash = String(body?.txHash ?? "").trim();\n'
        '\t\t\t\t\t\t\tconst tokenSymbol = String(body?.tokenSymbol ?? body?.tokenAddress ?? "TOKEN");\n'
        '\t\t\t\t\t\t\tconst amountWei = String(body?.amountWei ?? "?");\n'
        '\t\t\t\t\t\t\tconst amountDisplay = String(body?.amountDisplay ?? "").trim();\n'
        '\t\t\t\t\t\t\tconst toAddress = String(body?.to ?? "?");\n'
        '\t\t\t\t\t\t\tconst executionMode = String(body?.executionMode ?? "normal");\n'
        '\t\t\t\t\t\t\tlet normalizedAmount = "";\n'
        '\t\t\t\t\t\t\tif (!amountDisplay && /^[0-9]+$/.test(amountWei)) {\n'
        '\t\t\t\t\t\t\t\tconst tokenDecimalsRaw = Number(body?.tokenDecimals);\n'
        '\t\t\t\t\t\t\t\tconst tokenDecimals = Number.isFinite(tokenDecimalsRaw) && tokenDecimalsRaw >= 0 ? Math.floor(tokenDecimalsRaw) : 18;\n'
        '\t\t\t\t\t\t\t\tif (tokenDecimals <= 36) {\n'
        '\t\t\t\t\t\t\t\t\tconst s = String(BigInt(amountWei));\n'
        '\t\t\t\t\t\t\t\t\tconst padded = s.length <= tokenDecimals ? s.padStart(tokenDecimals + 1, "0") : s;\n'
        '\t\t\t\t\t\t\t\t\tconst whole = tokenDecimals > 0 ? padded.slice(0, -tokenDecimals) : padded;\n'
        '\t\t\t\t\t\t\t\t\tconst fracRaw = tokenDecimals > 0 ? padded.slice(-tokenDecimals) : "";\n'
        '\t\t\t\t\t\t\t\t\tconst frac = fracRaw.replace(/0+$/, "");\n'
        '\t\t\t\t\t\t\t\t\tnormalizedAmount = frac ? `${whole}.${frac} ${tokenSymbol}` : `${whole} ${tokenSymbol}`;\n'
        '\t\t\t\t\t\t\t\t}\n'
        '\t\t\t\t\t\t\t}\n'
        '\t\t\t\t\t\t\tconst amountLine = amountDisplay ? amountDisplay : (normalizedAmount || `${amountWei} ${tokenSymbol}`);\n'
        '\t\t\t\t\t\t\tif (action !== "r") {\n'
        '\t\t\t\t\t\t\t\ttry {\n'
        '\t\t\t\t\t\t\t\t\tconst approvedMsg = `Approved — transfer accepted ✅\\n\\n• Amount: ${amountLine}\\n• To: \\`${toAddress}\\`\\n• Approval ID: \\`${subjectId}\\`\\n• Chain: \\`${chainKey}\\`\\n\\nExecuting now.`;\n'
        '\t\t\t\t\t\t\t\t\tawait bot.api.sendMessage(chatId, approvedMsg);\n'
        '\t\t\t\t\t\t\t\t} catch {}\n'
        '\t\t\t\t\t\t\t}\n'
        '\t\t\t\t\t\t\ttry {\n'
        '\t\t\t\t\t\t\t\tconst transferStatus = String(body?.status ?? (body?.ok ? "filled" : "failed")).toLowerCase();\n'
        '\t\t\t\t\t\t\t\tconst isRejected = transferStatus === "rejected";\n'
        '\t\t\t\t\t\t\t\tconst isFilled = transferStatus === "filled";\n'
        '\t\t\t\t\t\t\t\tconst decisionWord = isFilled ? "FILLED" : (isRejected ? "REJECTED" : "FAILED");\n'
        '\t\t\t\t\t\t\t\tconst instruction = isFilled\n'
        '\t\t\t\t\t\t\t\t\t? "Reply to the user confirming the transfer succeeded with tx details."\n'
        '\t\t\t\t\t\t\t\t\t: (isRejected\n'
        '\t\t\t\t\t\t\t\t\t\t? "Reply to the user confirming the transfer was denied and no transaction was executed."\n'
        '\t\t\t\t\t\t\t\t\t\t: "Reply to the user confirming the transfer failed and provide next steps.");\n'
        '\t\t\t\t\t\t\t\tconst syntheticText = `[X-CLAW TRANSFER RESULT]\\nDecision: ${decisionWord}\\nApproval: ${subjectId}\\nChain: ${chainKey}\\nTxHash: ${txHash || "n/a"}\\nAmount: ${amountLine}\\nTo: ${toAddress}\\nSource: telegram_callback_transfer\\nInstruction: ${instruction}`;\n'
        '\t\t\t\t\t\t\t\tconst storeAllowFrom2 = await readChannelAllowFromStore("telegram").catch(() => []);\n'
        '\t\t\t\t\t\t\t\tconst syntheticAllowFrom = Array.from(new Set([...(Array.isArray(storeAllowFrom2) ? storeAllowFrom2.map((v) => String(v)) : []), String(callback?.from?.id ?? ""), String(chatId ?? "")])).filter((v) => !!v);\n'
        '\t\t\t\t\t\t\t\tconst getFile2 = typeof ctx.getFile === "function" ? ctx.getFile.bind(ctx) : async () => ({});\n'
        '\t\t\t\t\t\t\t\tconst syntheticMessage2 = {\n'
        '\t\t\t\t\t\t\t\t\t...callbackMessage,\n'
        '\t\t\t\t\t\t\t\t\tfrom: callback.from,\n'
        '\t\t\t\t\t\t\t\t\ttext: syntheticText,\n'
        '\t\t\t\t\t\t\t\t\tcaption: void 0,\n'
        '\t\t\t\t\t\t\t\t\tcaption_entities: void 0,\n'
        '\t\t\t\t\t\t\t\t\tentities: void 0,\n'
        '\t\t\t\t\t\t\t\t\tdate: Math.floor(Date.now() / 1000)\n'
        '\t\t\t\t\t\t\t\t};\n'
        '\t\t\t\t\t\t\t\tawait processMessage({ message: syntheticMessage2, me: ctx.me, getFile: getFile2 }, [], syntheticAllowFrom, { messageIdOverride: `xclaw-transfer-result-${callback.id}` });\n'
        '\t\t\t\t\t\t\t} catch {}\n'
        '\t\t\t\t\t\t\ttry { logger.info({ subjectId, chainKey, chatId, ok: !!body?.ok }, "xclaw: telegram transfer result routed to agent"); } catch {}\n'
        '\t\t\t\t\t\t\treturn;\n'
        '\t\t\t\t\t\t}\n'
        '\t\t\t\t\t\tif (parts[0] === "xappr" || parts[0] === "xpol") {\n'
        '\t\t\t\t\t\t\tconst decision = action === "r" ? "reject" : "approve";\n'
        '\t\t\t\t\t\t\tconst childMod = await import("node:child_process");\n'
        '\t\t\t\t\t\t\tconst fsMod = await import("node:fs");\n'
        '\t\t\t\t\t\t\tconst runtimeCandidates = [\n'
        f'\t\t\t\t\t\t\t\t{json.dumps(REPO_RUNTIME_BIN)},\n'
        '\t\t\t\t\t\t\t\tString(env?.XCLAW_AGENT_RUNTIME_BIN ?? process.env.XCLAW_AGENT_RUNTIME_BIN ?? "").trim(),\n'
        '\t\t\t\t\t\t\t\t"xclaw-agent"\n'
        '\t\t\t\t\t\t\t].filter((v) => !!v);\n'
        '\t\t\t\t\t\t\tconst runtimeBin = runtimeCandidates.find((candidate) => candidate === "xclaw-agent" || fsMod.existsSync(candidate)) || "xclaw-agent";\n'
        '\t\t\t\t\t\t\tconst cmdArgs = parts[0] === "xpol"\n'
        '\t\t\t\t\t\t\t\t? ["approvals", "decide-policy", "--approval-id", subjectId, "--decision", decision, "--chain", chainKey, "--source", "telegram", "--idempotency-key", `tg-cb-${callback.id}`, "--decision-at", atIso, "--reason-message", action === "r" ? "Denied via Telegram" : "", "--json"]\n'
        '\t\t\t\t\t\t\t\t: ["approvals", "decide-spot", "--trade-id", subjectId, "--decision", decision, "--chain", chainKey, "--source", "telegram", "--idempotency-key", `tg-cb-${callback.id}`, "--decision-at", atIso, "--reason-message", action === "r" ? "Denied via Telegram" : "", "--json"];\n'
        '\t\t\t\t\t\t\tconst childEnv = { ...process.env, ...Object.fromEntries(Object.entries(env || {}).map(([k, v]) => [String(k), String(v)])) };\n'
        '\t\t\t\t\t\t\tconst child = childMod.spawn(runtimeBin, cmdArgs, { stdio: ["ignore", "pipe", "pipe"], env: childEnv });\n'
        '\t\t\t\t\t\t\tlet out = "";\n'
        '\t\t\t\t\t\t\tlet err = "";\n'
        '\t\t\t\t\t\t\tchild.stdout?.on("data", (chunk) => { if (out.length < 12000) out += String(chunk); });\n'
        '\t\t\t\t\t\t\tchild.stderr?.on("data", (chunk) => { if (err.length < 4000) err += String(chunk); });\n'
        '\t\t\t\t\t\t\tconst exitCode = await new Promise((resolve) => child.on("close", (code) => resolve(Number(code ?? 1))));\n'
        '\t\t\t\t\t\t\tconst lines = out.split(/\\r?\\n/).map((v) => String(v || "").trim()).filter((v) => v.length > 0);\n'
        '\t\t\t\t\t\t\tlet body = null;\n'
        '\t\t\t\t\t\t\ttry { body = lines.length > 0 ? JSON.parse(lines[lines.length - 1]) : null; } catch {}\n'
        '\t\t\t\t\t\t\ttry { logger.info({ subjectId, chainKey, kind: parts[0], ok: !!body?.ok, exitCode }, "xclaw: telegram approval callback runtime response"); } catch {}\n'
        '\t\t\t\t\t\t\tif (exitCode === 0 && !!body?.ok) {\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V2}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V3}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V4}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V5}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V6}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V7}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V8}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V9}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V10}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V11}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V12}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V13}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V14}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V15}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V16}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V17}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V18}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V19}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V20}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V21}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V22}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V23}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V24}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V25}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V26}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V27}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V28}\n'
        '\t\t\t\t\t\t\t\ttry {\n'
        '\t\t\t\t\t\t\t\t\tconst subjectLabel = parts[0] === "xpol" ? "policy approval" : "trade";\n'
        '\t\t\t\t\t\t\t\t\tconst msg = `${action === "r" ? "Denied" : "Approved"} ${subjectLabel} ${subjectId}\\nChain: ${chainKey}`;\n'
        '\t\t\t\t\t\t\t\t\tif (!((parts[0] === "xappr" || parts[0] === "xpol") && action !== "r")) {\n'
        '\t\t\t\t\t\t\t\t\t\tawait bot.api.sendMessage(chatId, msg);\n'
        '\t\t\t\t\t\t\t\t\t}\n'
        '\t\t\t\t\t\t\t\t} catch {}\n'
        '\t\t\t\t\t\t\t\tif (action === "r") {\n'
        '\t\t\t\t\t\t\t\t\ttry {\n'
        '\t\t\t\t\t\t\t\t\t\tconst instruction = parts[0] === "xpol"\n'
        '\t\t\t\t\t\t\t\t\t\t\t? "Reply to the user confirming the policy approval was denied and describe impact/next step."\n'
        '\t\t\t\t\t\t\t\t\t\t\t: "Reply to the user confirming the trade was denied and no execution occurred.";\n'
        '\t\t\t\t\t\t\t\t\t\tconst syntheticText = `[X-CLAW ${parts[0] === "xpol" ? "POLICY" : "TRADE"} DECISION]\\nDecision: REJECTED\\nSubject: ${subjectId}\\nChain: ${chainKey}\\nSource: telegram_callback_${parts[0] === "xpol" ? "policy" : "trade"}\\nInstruction: ${instruction}`;\n'
        '\t\t\t\t\t\t\t\t\t\tconst storeAllowFrom2 = await readChannelAllowFromStore("telegram").catch(() => []);\n'
        '\t\t\t\t\t\t\t\t\t\tconst syntheticAllowFrom = Array.from(new Set([...(Array.isArray(storeAllowFrom2) ? storeAllowFrom2.map((v) => String(v)) : []), String(callback?.from?.id ?? ""), String(chatId ?? "")])).filter((v) => !!v);\n'
        '\t\t\t\t\t\t\t\t\t\tconst getFile2 = typeof ctx.getFile === "function" ? ctx.getFile.bind(ctx) : async () => ({});\n'
        '\t\t\t\t\t\t\t\t\t\tconst syntheticMessage2 = { ...callbackMessage, from: callback.from, text: syntheticText, caption: void 0, caption_entities: void 0, entities: void 0, date: Math.floor(Date.now() / 1000) };\n'
        '\t\t\t\t\t\t\t\t\t\tawait processMessage({ message: syntheticMessage2, me: ctx.me, getFile: getFile2 }, [], syntheticAllowFrom, { messageIdOverride: `xclaw-${parts[0]}-reject-${callback.id}` });\n'
        '\t\t\t\t\t\t\t\t\t} catch {}\n'
        '\t\t\t\t\t\t\t\t}\n'
        '\t\t\t\t\t\t\t\tif (parts[0] === "xappr" && action !== "r") {\n'
        f'\t\t\t\t\t\t\t\t\t\t// {DECISION_EXEC_MARKER_V1}\n'
        '\t\t\t\t\t\t\t\t\t\ttry {\n'
        '\t\t\t\t\t\t\t\t\t\t\tconst inflightKey = `${subjectId}|${chainKey}`;\n'
        '\t\t\t\t\t\t\t\t\t\t\tconst __resumeSet = (globalThis.__xclawTradeResumeInflight && globalThis.__xclawTradeResumeInflight instanceof Set)\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t? globalThis.__xclawTradeResumeInflight\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t: (() => { const s = new Set(); globalThis.__xclawTradeResumeInflight = s; return s; })();\n'
        '\t\t\t\t\t\t\t\t\t\t\tif (!__resumeSet.has(inflightKey)) {\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t__resumeSet.add(inflightKey);\n'
        '\t\t\t\t\t\t\t\t\t\t\t\tsetTimeout(async () => {\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\ttry {\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst childMod = await import("node:child_process");\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst fsMod = await import("node:fs");\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst runtimeCandidates = [\n'
        f'\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t{json.dumps(REPO_RUNTIME_BIN)},\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tString(env?.XCLAW_AGENT_RUNTIME_BIN ?? process.env.XCLAW_AGENT_RUNTIME_BIN ?? "").trim(),\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t"xclaw-agent"\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t].filter((v) => !!v);\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst runtimeBin = runtimeCandidates.find((candidate) => candidate === "xclaw-agent" || fsMod.existsSync(candidate)) || "xclaw-agent";\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst childEnv = { ...process.env, ...Object.fromEntries(Object.entries(env || {}).map(([k, v]) => [String(k), String(v)])) };\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst child = childMod.spawn(runtimeBin, ["approvals", "resume-spot", "--trade-id", subjectId, "--chain", chainKey, "--json"], { stdio: ["ignore", "pipe", "pipe"], env: childEnv });\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tlet out = "";\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tlet err = "";\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tchild.stdout?.on("data", (chunk) => { if (out.length < 12000) out += String(chunk); });\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tchild.stderr?.on("data", (chunk) => { if (err.length < 4000) err += String(chunk); });\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst exitCode = await new Promise((resolve) => child.on("close", (code) => resolve(Number(code ?? 1))));\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst lines = out.split(/\\r?\\n/).map((v) => String(v || "").trim()).filter((v) => v.length > 0);\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tlet body = null;\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\ttry { body = lines.length > 0 ? JSON.parse(lines[lines.length - 1]) : null; } catch {}\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst statusWord = String(body?.status ?? (body?.ok ? "filled" : "failed"));\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst txHash = String(body?.txHash ?? "").trim();\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst flow = body?.flowSummary ?? {};\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst promptText = String(callbackMessage.text ?? "");\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst pairMatch = promptText.match(/\\n\\s*([0-9]+(?:\\.[0-9]+)?)\\s+([A-Z0-9_]+)\\s*->\\s*([A-Z0-9_]+)/i);\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst amountHuman = String(body?.amountIn ?? flow?.amountInHuman ?? (pairMatch?.[1] || "")).trim();\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst tokenInSym = String(body?.tokenInSymbol ?? flow?.tokenInSymbol ?? (pairMatch?.[2] || "")).trim();\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst tokenOutSym = String(body?.tokenOutSymbol ?? flow?.tokenOutSymbol ?? (pairMatch?.[3] || "")).trim();\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst head = body?.ok ? `Trade result: ${statusWord}` : `Trade result: failed`;\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst txLine = txHash ? `\\nTx: ${txHash}` : "";\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst reasonLine = !body?.ok ? `\\nReason: ${String(body?.message ?? err ?? `resume exit ${exitCode}`)}` : "";\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst pairLine = amountHuman && tokenInSym && tokenOutSym ? `\\n${amountHuman} ${tokenInSym} -> ${tokenOutSym}` : "";\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst finalMsg = `${head}${pairLine}\\nTrade: ${subjectId}\\nChain: ${chainKey}${txLine}${reasonLine}`;\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\ttry {\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst decisionWord = body?.ok ? "FILLED" : "FAILED";\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst instruction = body?.ok\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t? "Reply to the user confirming the trade succeeded with tx details."\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t: "Reply to the user confirming the trade failed and provide next steps.";\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst syntheticText = `[X-CLAW TRADE RESULT]\\nDecision: ${decisionWord}\\nTrade: ${subjectId}\\nChain: ${chainKey}\\nTxHash: ${txHash || "n/a"}${pairLine ? `\\nPair: ${amountHuman} ${tokenInSym} -> ${tokenOutSym}` : ""}\\nSource: telegram_callback_trade\\nInstruction: ${instruction}`;\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst storeAllowFrom2 = await readChannelAllowFromStore("telegram").catch(() => []);\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst syntheticAllowFrom = Array.from(new Set([...(Array.isArray(storeAllowFrom2) ? storeAllowFrom2.map((v) => String(v)) : []), String(callback?.from?.id ?? ""), String(chatId ?? "")])).filter((v) => !!v);\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst getFile2 = typeof ctx.getFile === "function" ? ctx.getFile.bind(ctx) : async () => ({});\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst syntheticMessage2 = {\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t...callbackMessage,\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tfrom: callback.from,\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\ttext: syntheticText,\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tcaption: void 0,\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tcaption_entities: void 0,\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tentities: void 0,\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tdate: Math.floor(Date.now() / 1000)\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t};\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tawait processMessage({ message: syntheticMessage2, me: ctx.me, getFile: getFile2 }, [], syntheticAllowFrom, { messageIdOverride: `xclaw-trade-result-${callback.id}` });\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t} catch {}\n'
        f'\t\t\t\t\t\t\t\t\t\t\t\t\t\ttry {{ logger.info({{ subjectId, chainKey, chatId, ok: !!body?.ok }}, "{DECISION_RESULT_ROUTE_MARKER_V1}"); }} catch {{}}\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t} catch (resumeErr) {\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\ttry { logger.error({ subjectId, chainKey, err: String(resumeErr) }, "xclaw: trade resume trigger failed"); } catch {}\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t} finally {\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\ttry { __resumeSet.delete(inflightKey); } catch {}\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t}\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t}, 0);\n'
        '\t\t\t\t\t\t\t\t\t\t\t}\n'
        '\t\t\t\t\t\t\t\t\t\t} catch {}\n'
        '\t\t\t\t\t\t\t\t}\n'
        '\t\t\t\t\t\t\t\treturn;\n'
        '\t\t\t\t\t\t\t}\n'
        '\t\t\t\t\t\t\ttry {\n'
        '\t\t\t\t\t\t\t\tconst kb = parts[0] === "xpol"\n'
        '\t\t\t\t\t\t\t\t\t? [[{ text: "Approve", callback_data: `xpol|a|${subjectId}|${chainKey}` }, { text: "Deny", callback_data: `xpol|r|${subjectId}|${chainKey}` }]]\n'
        '\t\t\t\t\t\t\t\t\t: [[{ text: "Approve", callback_data: `xappr|a|${subjectId}|${chainKey}` }, { text: "Deny", callback_data: `xappr|r|${subjectId}|${chainKey}` }]];\n'
        '\t\t\t\t\t\t\t\tawait bot.api.editMessageReplyMarkup(chatId, callbackMessage.message_id, { inline_keyboard: kb });\n'
        '\t\t\t\t\t\t\t} catch {}\n'
        '\t\t\t\t\t\t\tawait bot.api.sendMessage(chatId, `Approval failed: ${String(body?.code ?? ("runtime exit " + String(exitCode)))} (${String((body?.message ?? err) || "runtime decision failed")}).`);\n'
        '\t\t\t\t\t\t\treturn;\n'
        '\t\t\t\t\t\t}\n'
        '\t\t\t\t\t\tconst url = parts[0] === "xpol"\n'
        '\t\t\t\t\t\t\t? `${apiBase}/policy-approvals/${encodeURIComponent(subjectId)}/decision`\n'
        '\t\t\t\t\t\t\t: `${apiBase}/trades/${encodeURIComponent(subjectId)}/status`;\n'
        '\t\t\t\t\t\tconst payload = parts[0] === "xpol"\n'
        '\t\t\t\t\t\t\t? { policyApprovalId: subjectId, fromStatus: "approval_pending", toStatus: action === "r" ? "rejected" : "approved", reasonMessage: action === "r" ? "Denied via Telegram" : null, at: atIso }\n'
        '\t\t\t\t\t\t\t: { tradeId: subjectId, fromStatus: "approval_pending", toStatus: action === "r" ? "rejected" : "approved", reasonCode: action === "r" ? "approval_rejected" : null, reasonMessage: action === "r" ? "Denied via Telegram" : null, at: atIso };\n'
        '\t\t\t\t\t\tconst res = await fetch(url, {\n'
        '\t\t\t\t\t\t\tmethod: "POST",\n'
        '\t\t\t\t\t\t\theaders: { "content-type": "application/json", authorization: `Bearer ${apiKey}`, "idempotency-key": `tg-cb-${callback.id}` },\n'
        '\t\t\t\t\t\t\tbody: JSON.stringify(payload)\n'
        '\t\t\t\t\t\t});\n'
        '\t\t\t\t\t\ttry { logger.info({ subjectId, chainKey, kind: parts[0], status: res.status }, "xclaw: telegram approval callback server response"); } catch {}\n'
        '\t\t\t\t\t\t\ttry {\n'
        '\t\t\t\t\t\t\tif (res.ok) {\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V2}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V3}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V4}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V5}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V6}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V7}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V8}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V9}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V10}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V11}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V12}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V13}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V14}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V15}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V16}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V17}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V18}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V19}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V20}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V21}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V22}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V23}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V24}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V25}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V26}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V27}\n'
        f'\t\t\t\t\t\t\t\t// {DECISION_ACK_MARKER_V28}\n'
        '\t\t\t\t\t\t\t\t// Runtime is canonical owner of queued prompt cleanup (button clear, no delete).\n'
        '\t\t\t\t\t\t\t\t// Emit deterministic confirmation immediately so users always see a result.\n'
        '\t\t\t\t\t\t\t\ttry {\n'
        '\t\t\t\t\t\t\t\t\tconst subjectLabel = parts[0] === "xpol" ? "policy approval" : (parts[0] === "xfer" ? "transfer approval" : "trade");\n'
        '\t\t\t\t\t\t\t\t\tconst msg = `${action === "r" ? "Denied" : "Approved"} ${subjectLabel} ${subjectId}\\nChain: ${chainKey}`;\n'
        '\t\t\t\t\t\t\t\t\tif (!((parts[0] === "xappr" || parts[0] === "xpol") && action !== "r")) {\n'
        '\t\t\t\t\t\t\t\t\t\tawait bot.api.sendMessage(chatId, msg);\n'
        '\t\t\t\t\t\t\t\t\t}\n'
        '\t\t\t\t\t\t\t\t} catch {}\n'
        '\t\t\t\t\t\t\t\t// Notify the agent pipeline only for explicit rejections.\n'
        '\t\t\t\t\t\t\t\tif (action === "r" && (parts[0] === "xappr" || parts[0] === "xpol")) {\n'
        '\t\t\t\t\t\t\t\t\ttry {\n'
        '\t\t\t\t\t\t\t\t\t\tconst subjectLabel = parts[0] === "xpol" ? "policy approval" : "trade";\n'
        '\t\t\t\t\t\t\t\t\t\tconst instruction = parts[0] === "xpol"\n'
        '\t\t\t\t\t\t\t\t\t\t\t? "Reply to the user confirming the policy approval was denied and describe impact/next step."\n'
        '\t\t\t\t\t\t\t\t\t\t\t: "Reply to the user confirming the trade was denied and no execution occurred.";\n'
        '\t\t\t\t\t\t\t\t\t\tconst syntheticText = `[X-CLAW ${parts[0] === "xpol" ? "POLICY" : "TRADE"} DECISION]\\nDecision: REJECTED\\nSubject: ${subjectId}\\nChain: ${chainKey}\\nSource: telegram_callback_${parts[0] === "xpol" ? "policy" : "trade"}\\nInstruction: ${instruction}`;\n'
        '\t\t\t\t\t\t\t\t\t\tconst storeAllowFrom2 = await readChannelAllowFromStore("telegram").catch(() => []);\n'
        '\t\t\t\t\t\t\t\t\t\tconst syntheticAllowFrom = Array.from(new Set([...(Array.isArray(storeAllowFrom2) ? storeAllowFrom2.map((v) => String(v)) : []), String(callback?.from?.id ?? ""), String(chatId ?? "")])).filter((v) => !!v);\n'
        '\t\t\t\t\t\t\t\t\t\tconst getFile2 = typeof ctx.getFile === "function" ? ctx.getFile.bind(ctx) : async () => ({});\n'
        '\t\t\t\t\t\t\t\t\t\tconst syntheticMessage2 = {\n'
        '\t\t\t\t\t\t\t\t\t\t\t...callbackMessage,\n'
        '\t\t\t\t\t\t\t\t\t\t\tfrom: callback.from,\n'
        '\t\t\t\t\t\t\t\t\t\t\ttext: syntheticText,\n'
        '\t\t\t\t\t\t\t\t\t\t\tcaption: void 0,\n'
        '\t\t\t\t\t\t\t\t\t\t\tcaption_entities: void 0,\n'
        '\t\t\t\t\t\t\t\t\t\t\tentities: void 0,\n'
        '\t\t\t\t\t\t\t\t\t\t\tdate: Math.floor(Date.now() / 1000)\n'
        '\t\t\t\t\t\t\t\t\t\t};\n'
        '\t\t\t\t\t\t\t\t\t\tawait processMessage({ message: syntheticMessage2, me: ctx.me, getFile: getFile2 }, [], syntheticAllowFrom, { messageIdOverride: `xclaw-${parts[0]}-reject-${callback.id}` });\n'
        '\t\t\t\t\t\t\t\t\t} catch {}\n'
        '\t\t\t\t\t\t\t\t}\n'
        '\t\t\t\t\t\t\t\tif (parts[0] === "xappr" && action !== "r") {\n'
        f'\t\t\t\t\t\t\t\t\t\t// {DECISION_EXEC_MARKER_V1}\n'
        '\t\t\t\t\t\t\t\t\t\ttry {\n'
        '\t\t\t\t\t\t\t\t\t\t\tconst inflightKey = `${subjectId}|${chainKey}`;\n'
        '\t\t\t\t\t\t\t\t\t\t\tconst __resumeSet = (globalThis.__xclawTradeResumeInflight && globalThis.__xclawTradeResumeInflight instanceof Set)\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t? globalThis.__xclawTradeResumeInflight\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t: (() => { const s = new Set(); globalThis.__xclawTradeResumeInflight = s; return s; })();\n'
        '\t\t\t\t\t\t\t\t\t\t\tif (!__resumeSet.has(inflightKey)) {\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t__resumeSet.add(inflightKey);\n'
        '\t\t\t\t\t\t\t\t\t\t\t\tsetTimeout(async () => {\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\ttry {\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst childMod = await import("node:child_process");\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst fsMod = await import("node:fs");\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst runtimeCandidates = [\n'
        f'\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t{json.dumps(REPO_RUNTIME_BIN)},\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tString(env?.XCLAW_AGENT_RUNTIME_BIN ?? process.env.XCLAW_AGENT_RUNTIME_BIN ?? "").trim(),\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t"xclaw-agent"\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t].filter((v) => !!v);\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst runtimeBin = runtimeCandidates.find((candidate) => candidate === "xclaw-agent" || fsMod.existsSync(candidate)) || "xclaw-agent";\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst childEnv = { ...process.env, ...Object.fromEntries(Object.entries(env || {}).map(([k, v]) => [String(k), String(v)])) };\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst child = childMod.spawn(runtimeBin, ["approvals", "resume-spot", "--trade-id", subjectId, "--chain", chainKey, "--json"], { stdio: ["ignore", "pipe", "pipe"], env: childEnv });\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tlet out = "";\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tlet err = "";\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tchild.stdout?.on("data", (chunk) => { if (out.length < 12000) out += String(chunk); });\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tchild.stderr?.on("data", (chunk) => { if (err.length < 4000) err += String(chunk); });\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst exitCode = await new Promise((resolve) => child.on("close", (code) => resolve(Number(code ?? 1))));\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst lines = out.split(/\\r?\\n/).map((v) => String(v || "").trim()).filter((v) => v.length > 0);\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tlet body = null;\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\ttry { body = lines.length > 0 ? JSON.parse(lines[lines.length - 1]) : null; } catch {}\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst statusWord = String(body?.status ?? (body?.ok ? "filled" : "failed"));\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst txHash = String(body?.txHash ?? "").trim();\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst flow = body?.flowSummary ?? {};\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst promptText = String(callbackMessage.text ?? "");\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst pairMatch = promptText.match(/\\n\\s*([0-9]+(?:\\.[0-9]+)?)\\s+([A-Z0-9_]+)\\s*->\\s*([A-Z0-9_]+)/i);\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst amountHuman = String(body?.amountIn ?? flow?.amountInHuman ?? (pairMatch?.[1] || "")).trim();\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst tokenInSym = String(body?.tokenInSymbol ?? flow?.tokenInSymbol ?? (pairMatch?.[2] || "")).trim();\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst tokenOutSym = String(body?.tokenOutSymbol ?? flow?.tokenOutSymbol ?? (pairMatch?.[3] || "")).trim();\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst head = body?.ok ? `Trade result: ${statusWord}` : `Trade result: failed`;\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst txLine = txHash ? `\\nTx: ${txHash}` : "";\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst reasonLine = !body?.ok ? `\\nReason: ${String(body?.message ?? err ?? `resume exit ${exitCode}`)}` : "";\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst pairLine = amountHuman && tokenInSym && tokenOutSym ? `\\n${amountHuman} ${tokenInSym} -> ${tokenOutSym}` : "";\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst finalMsg = `${head}${pairLine}\\nTrade: ${subjectId}\\nChain: ${chainKey}${txLine}${reasonLine}`;\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\ttry {\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst decisionWord = body?.ok ? "FILLED" : "FAILED";\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst instruction = body?.ok\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t? "Reply to the user confirming the trade succeeded with tx details."\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t: "Reply to the user confirming the trade failed and provide next steps.";\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst syntheticText = `[X-CLAW TRADE RESULT]\\nDecision: ${decisionWord}\\nTrade: ${subjectId}\\nChain: ${chainKey}\\nTxHash: ${txHash || "n/a"}${pairLine ? `\\nPair: ${amountHuman} ${tokenInSym} -> ${tokenOutSym}` : ""}\\nSource: telegram_callback_trade\\nInstruction: ${instruction}`;\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst storeAllowFrom2 = await readChannelAllowFromStore("telegram").catch(() => []);\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst syntheticAllowFrom = Array.from(new Set([...(Array.isArray(storeAllowFrom2) ? storeAllowFrom2.map((v) => String(v)) : []), String(callback?.from?.id ?? ""), String(chatId ?? "")])).filter((v) => !!v);\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst getFile2 = typeof ctx.getFile === "function" ? ctx.getFile.bind(ctx) : async () => ({});\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tconst syntheticMessage2 = {\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t...callbackMessage,\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tfrom: callback.from,\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\ttext: syntheticText,\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tcaption: void 0,\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tcaption_entities: void 0,\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tentities: void 0,\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tdate: Math.floor(Date.now() / 1000)\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t};\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tawait processMessage({ message: syntheticMessage2, me: ctx.me, getFile: getFile2 }, [], syntheticAllowFrom, { messageIdOverride: `xclaw-trade-result-${callback.id}` });\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t} catch {}\n'
        f'\t\t\t\t\t\t\t\t\t\t\t\t\t\ttry {{ logger.info({{ subjectId, chainKey, chatId, ok: !!body?.ok }}, "{DECISION_RESULT_ROUTE_MARKER_V1}"); }} catch {{}}\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t} catch (resumeErr) {\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\ttry { logger.error({ subjectId, chainKey, err: String(resumeErr) }, "xclaw: trade resume trigger failed"); } catch {}\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t} finally {\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\ttry { __resumeSet.delete(inflightKey); } catch {}\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t\t}\n'
        '\t\t\t\t\t\t\t\t\t\t\t\t}, 0);\n'
        '\t\t\t\t\t\t\t\t\t\t\t}\n'
        '\t\t\t\t\t\t\t\t\t\t} catch {}\n'
        '\t\t\t\t\t\t\t\t}\n'
        '\t\t\t\t\t\t\t\tif (parts[0] === "xpol" && action !== "r") {\n'
        '\t\t\t\t\t\t\t\t\ttry {\n'
        '\t\t\t\t\t\t\t\t\t\tconst instruction = "Reply to the user confirming the policy approval was applied and summarize what changed.";\n'
        '\t\t\t\t\t\t\t\t\t\tconst syntheticText = `[X-CLAW POLICY DECISION]\\nDecision: APPROVED\\nSubject: ${subjectId}\\nChain: ${chainKey}\\nSource: telegram_callback_policy\\nInstruction: ${instruction}`;\n'
        '\t\t\t\t\t\t\t\t\t\tconst storeAllowFrom2 = await readChannelAllowFromStore("telegram").catch(() => []);\n'
        '\t\t\t\t\t\t\t\t\t\tconst syntheticAllowFrom = Array.from(new Set([...(Array.isArray(storeAllowFrom2) ? storeAllowFrom2.map((v) => String(v)) : []), String(callback?.from?.id ?? ""), String(chatId ?? "")])).filter((v) => !!v);\n'
        '\t\t\t\t\t\t\t\t\t\tconst getFile2 = typeof ctx.getFile === "function" ? ctx.getFile.bind(ctx) : async () => ({});\n'
        '\t\t\t\t\t\t\t\t\t\tconst syntheticMessage2 = {\n'
        '\t\t\t\t\t\t\t\t\t\t\t...callbackMessage,\n'
        '\t\t\t\t\t\t\t\t\t\t\tfrom: callback.from,\n'
        '\t\t\t\t\t\t\t\t\t\t\ttext: syntheticText,\n'
        '\t\t\t\t\t\t\t\t\t\t\tcaption: void 0,\n'
        '\t\t\t\t\t\t\t\t\t\t\tcaption_entities: void 0,\n'
        '\t\t\t\t\t\t\t\t\t\t\tentities: void 0,\n'
        '\t\t\t\t\t\t\t\t\t\t\tdate: Math.floor(Date.now() / 1000)\n'
        '\t\t\t\t\t\t\t\t\t\t};\n'
        '\t\t\t\t\t\t\t\t\t\tawait processMessage({ message: syntheticMessage2, me: ctx.me, getFile: getFile2 }, [], syntheticAllowFrom, { messageIdOverride: `xclaw-policy-approve-${callback.id}` });\n'
        '\t\t\t\t\t\t\t\t\t} catch {}\n'
        '\t\t\t\t\t\t\t\t}\n'
        '\t\t\t\t\t\t\t}\n'
        '\t\t\t\t\t\t\t} catch (err) {\n'
        '\t\t\t\t\t\t\t\t\t// Fallback: still send minimal confirmation so the user sees feedback even if the agent pipeline fails.\n'
        '\t\t\t\t\t\t\t\t\ttry {\n'
        '\t\t\t\t\t\t\t\t\t\tconst promptLine = (callbackMessage.text ?? \"\").split(\"\\n\")[0] ?? \"\";\n'
        '\t\t\t\t\t\t\t\t\t\tconst summary = promptLine.trim() ? `\\n${promptLine.trim()}` : \"\";\n'
        '\t\t\t\t\t\t\t\t\t\tconst subjectLabel = parts[0] === \"xpol\" ? \"policy approval\" : (parts[0] === \"xfer\" ? \"transfer approval\" : \"trade\");\n'
        '\t\t\t\t\t\t\t\t\t\tconst msg = `${action === \"r\" ? \"Denied\" : \"Approved\"} ${subjectLabel} ${subjectId}${summary}\\nChain: ${chainKey}`;\n'
        '\t\t\t\t\t\t\t\t\t\tif (!((parts[0] === \"xappr\" || parts[0] === \"xpol\") && action !== \"r\")) {\n'
        '\t\t\t\t\t\t\t\t\t\t\tawait bot.api.sendMessage(chatId, msg);\n'
        '\t\t\t\t\t\t\t\t\t\t}\n'
        '\t\t\t\t\t\t\t\t\t\ttry { logger.error({ subjectId, chainKey, chatId, action, kind: parts[0], err: String(err) }, \"xclaw: telegram approval decision route failed; fallback ack sent\"); } catch {}\n'
        '\t\t\t\t\t\t\t\t\t} catch {}\n'
        '\t\t\t\t\t\t\t\t}\n'
        '\t\t\t\t\t\t\t\treturn;\n'
        '\t\t\t\t\t\t\tlet errCode = "api_error"; let errMsg = `HTTP ${res.status}`;\n'
        '\t\t\t\t\t\t\ttry { const body = await res.json(); if (typeof body?.code === "string" && body.code.trim()) errCode = body.code.trim(); if (typeof body?.message === "string" && body.message.trim()) errMsg = body.message.trim(); if (res.status === 409 && (body?.details?.currentStatus === "approved" || body?.details?.currentStatus === "filled" || body?.details?.currentStatus === "rejected")) { const currentStatus = String(body?.details?.currentStatus || ""); const decision = currentStatus === "rejected" ? "Denied" : "Approved"; const subjectLabel = parts[0] === "xpol" ? "policy approval" : (parts[0] === "xfer" ? "transfer approval" : "trade"); if (!(parts[0] === "xappr" || (parts[0] === "xpol" && currentStatus !== "rejected"))) { await bot.api.sendMessage(chatId, `${decision} ${subjectLabel} ${subjectId}\\nChain: ${chainKey}`); } return; } } catch {}\n'
        '\t\t\t\t\t\t\ttry {\n'
        '\t\t\t\t\t\t\t\tconst kb = parts[0] === "xpol"\n'
        '\t\t\t\t\t\t\t\t\t? [[{ text: "Approve", callback_data: `xpol|a|${subjectId}|${chainKey}` }, { text: "Deny", callback_data: `xpol|r|${subjectId}|${chainKey}` }]]\n'
        '\t\t\t\t\t\t\t\t\t: (parts[0] === "xfer"\n'
        '\t\t\t\t\t\t\t\t\t\t? [[{ text: "Approve", callback_data: `xfer|a|${subjectId}|${chainKey}` }, { text: "Deny", callback_data: `xfer|r|${subjectId}|${chainKey}` }]]\n'
        '\t\t\t\t\t\t\t\t\t\t: [[{ text: "Approve", callback_data: `xappr|a|${subjectId}|${chainKey}` }, { text: "Deny", callback_data: `xappr|r|${subjectId}|${chainKey}` }]]);\n'
        '\t\t\t\t\t\t\t\tawait bot.api.editMessageReplyMarkup(chatId, callbackMessage.message_id, { inline_keyboard: kb });\n'
        '\t\t\t\t\t\t\t} catch {}\n'
        '\t\t\t\t\t\t\tawait bot.api.sendMessage(chatId, `Approval failed: ${errCode} (${errMsg}).`);\n'
        '\t\t\t\t\t\t\treturn;\n'
        '\t\t\t\t\t\t} catch (err) {\n'
        '\t\t\t\t\t\t\ttry {\n'
        '\t\t\t\t\t\t\t\tconst kb = parts[0] === "xpol"\n'
        '\t\t\t\t\t\t\t\t\t? [[{ text: "Approve", callback_data: `xpol|a|${subjectId}|${chainKey}` }, { text: "Deny", callback_data: `xpol|r|${subjectId}|${chainKey}` }]]\n'
        '\t\t\t\t\t\t\t\t\t: (parts[0] === "xfer"\n'
        '\t\t\t\t\t\t\t\t\t\t? [[{ text: "Approve", callback_data: `xfer|a|${subjectId}|${chainKey}` }, { text: "Deny", callback_data: `xfer|r|${subjectId}|${chainKey}` }]]\n'
        '\t\t\t\t\t\t\t\t\t\t: [[{ text: "Approve", callback_data: `xappr|a|${subjectId}|${chainKey}` }, { text: "Deny", callback_data: `xappr|r|${subjectId}|${chainKey}` }]]);\n'
        '\t\t\t\t\t\t\t\tawait bot.api.editMessageReplyMarkup(chatId, callbackMessage.message_id, { inline_keyboard: kb });\n'
        '\t\t\t\t\t\t\t} catch {}\n'
        '\t\t\t\t\t\t\tawait bot.api.sendMessage(chatId, `Approval failed: ${String(err)}`);\n'
        '\t\t\t\t\t\t\treturn;\n'
        '\t\t\t\t\t\t}\n'
        '\t\t\t\t\t}\n'
        '\t\t\t\t}\n'
        '\n'
    )

    out2 = raw[:idx] + general_injection + raw[idx:]
    if MARKER not in out2:
        return raw, False, "marker_missing_after_patch"
    # Ensure queued-message auto-buttons are present too (CLI + runtime send paths).
    out3, changed3, err3 = _patch_queued_buttons(out2)
    if err3:
        out3 = out2
        changed3 = False
    out4, changed4, err4 = _patch_queued_buttons_v2(out3)
    if err4:
        out4 = out3
        changed4 = False
    return out4, True or changed3 or changed4, None


def _patch_queued_buttons(raw: str) -> tuple[str, bool, str | None]:
    """
    Patch OpenClaw's Telegram send path so that when a message contains an X-Claw queued approval_pending
    trade summary, OpenClaw attaches Approve/Deny inline buttons to that same message.
    """
    if QUEUED_BUTTONS_MARKER in raw:
        return raw, False, None

    # Target: sendMessageTelegram(...) where the replyMarkup is derived from opts.buttons.
    # We change `const replyMarkup = ...` to `let replyMarkup = ...` and add a fallback builder.
    anchor = "const replyMarkup = buildInlineKeyboard(opts.buttons);"
    if anchor not in raw:
        # Already converted to `let`? Patch that variant too.
        anchor = "let replyMarkup = buildInlineKeyboard(opts.buttons);"
        if anchor not in raw:
            return raw, False, "queued_buttons_anchor_not_found"
        already_let = True
    else:
        already_let = False

    injection = (
        "\n\t// xclaw: telegram queued approval buttons\n"
        "\t// If the agent posts an approval_pending trade summary (queued message), attach inline Approve/Deny buttons.\n"
        "\t// This avoids sending a second Telegram prompt message.\n"
        "\tif (!replyMarkup && typeof text === \"string\" && (/\\bStatus:\\s*approval_pending\\b/i.test(text) || /\\bppr_[a-z0-9]+\\b/i.test(text))) {\n"
        "\t\tconst tradeMatch = text.match(/\\bTrade ID:\\s*`?(trd_[a-z0-9]+)`?\\b/i) ?? text.match(/\\bTrade:\\s*`?(trd_[a-z0-9]+)`?\\b/i);\n"
        "\t\tconst policyMatch = text.match(/\\bApproval ID:\\s*`?(ppr_[a-z0-9]+)`?\\b/i) ?? text.match(/\\bPolicy Approval ID:\\s*`?(ppr_[a-z0-9]+)`?\\b/i);\n"
        "\t\tconst transferMatch = text.match(/\\bApproval ID:\\s*`?(xfr(?:\\\\_|[_-])?[a-z0-9]+)`?\\b/i) ?? text.match(/\\bTransfer Approval ID:\\s*`?(xfr(?:\\\\_|[_-])?[a-z0-9]+)`?\\b/i) ?? text.match(/\\bApproval:\\s*`?(xfr(?:\\\\_|[_-])?[a-z0-9]+)`?\\b/i);\n"
        "\t\tif (tradeMatch && tradeMatch[1]) {\n"
        "\t\t\tconst tradeId = tradeMatch[1];\n"
        "\t\t\tlet chainKey = \"\";\n"
        "\t\t\tconst cm = text.match(/\\bChain:\\s*`?([a-z0-9_]+)`?\\b/i);\n"
        "\t\t\tif (cm && cm[1]) chainKey = cm[1];\n"
        "\t\t\tif (!chainKey) {\n"
        "\t\t\t\tconst skill = cfg?.skills?.entries?.[\"xclaw-agent\"]; const env = skill?.env ?? {};\n"
        "\t\t\t\tchainKey = String(env?.XCLAW_DEFAULT_CHAIN ?? process.env.XCLAW_DEFAULT_CHAIN ?? \"base_sepolia\").trim() || \"base_sepolia\";\n"
        "\t\t\t}\n"
        "\t\t\treplyMarkup = { inline_keyboard: [[{ text: \"Approve\", callback_data: `xappr|a|${tradeId}|${chainKey}` }, { text: \"Deny\", callback_data: `xappr|r|${tradeId}|${chainKey}` }]] };\n"
        "\t\t} else if (policyMatch && policyMatch[1]) {\n"
        "\t\t\tconst approvalId = policyMatch[1];\n"
        "\t\t\tlet chainKey = \"\";\n"
        "\t\t\tconst cm = text.match(/\\bChain:\\s*`?([a-z0-9_]+)`?\\b/i);\n"
        "\t\t\tif (cm && cm[1]) chainKey = cm[1];\n"
        "\t\t\tif (!chainKey) {\n"
        "\t\t\t\tconst skill = cfg?.skills?.entries?.[\"xclaw-agent\"]; const env = skill?.env ?? {};\n"
        "\t\t\t\tchainKey = String(env?.XCLAW_DEFAULT_CHAIN ?? process.env.XCLAW_DEFAULT_CHAIN ?? \"base_sepolia\").trim() || \"base_sepolia\";\n"
        "\t\t\t}\n"
        "\t\t\treplyMarkup = { inline_keyboard: [[{ text: \"Approve\", callback_data: `xpol|a|${approvalId}|${chainKey}` }, { text: \"Deny\", callback_data: `xpol|r|${approvalId}|${chainKey}` }]] };\n"
        "\t\t} else if (transferMatch && transferMatch[1]) {\n"
        "\t\t\tconst approvalId = `xfr_${String(transferMatch[1] || \"\").replace(/^xfr(?:\\\\_|[_-])?/i, \"\").toLowerCase()}`;\n"
        "\t\t\tlet chainKey = \"\";\n"
        "\t\t\tconst cm = text.match(/\\bChain:\\s*`?([a-z0-9_]+)`?\\b/i);\n"
        "\t\t\tif (cm && cm[1]) chainKey = cm[1];\n"
        "\t\t\tif (!chainKey) {\n"
        "\t\t\t\tconst skill = cfg?.skills?.entries?.[\"xclaw-agent\"]; const env = skill?.env ?? {};\n"
        "\t\t\t\tchainKey = String(env?.XCLAW_DEFAULT_CHAIN ?? process.env.XCLAW_DEFAULT_CHAIN ?? \"base_sepolia\").trim() || \"base_sepolia\";\n"
        "\t\t\t}\n"
        "\t\t\treplyMarkup = { inline_keyboard: [[{ text: \"Approve\", callback_data: `xfer|a|${approvalId}|${chainKey}` }, { text: \"Deny\", callback_data: `xfer|r|${approvalId}|${chainKey}` }]] };\n"
        "\t\t}\n"
        "\t}\n"
    )

    text2 = raw
    if not already_let:
        text2 = text2.replace("const replyMarkup = buildInlineKeyboard(opts.buttons);", "let replyMarkup = buildInlineKeyboard(opts.buttons);", 1)
    text2, ok = _inject_after_anchor(text2, anchor if already_let else "let replyMarkup = buildInlineKeyboard(opts.buttons);", injection)
    if not ok:
        return raw, False, "queued_buttons_injection_failed"
    if QUEUED_BUTTONS_MARKER not in text2:
        return raw, False, "queued_buttons_marker_missing_after_patch"
    return text2, True, None


def _patch_queued_buttons_v2(raw: str) -> tuple[str, bool, str | None]:
    """
    Patch the Telegram *runtime* send path used by agent replies (`sendTelegramText(bot, ...)`),
    not the CLI send path (`sendMessageTelegram(...)`).
    """
    anchor = 'const htmlText = (opts?.textMode ?? "markdown") === "html" ? text : markdownToTelegramHtml(text);'
    if anchor not in raw:
        return raw, False, "queued_buttons_v2_anchor_not_found"

    # v3 is our current canonical behavior. If a v3 block exists but doesn't support policy approvals,
    # replace it in-place. This handles upgrades from trade-only v3 -> trade+policy v3.
    anchor_idx = raw.find(anchor)
    if QUEUED_BUTTONS_MARKER_V4 in raw:
        window = raw[anchor_idx : min(len(raw), anchor_idx + 9000)]
        if (
            ("xpol|a|${approvalId}" in window)
            and ("xfer|a|${approvalId}" in window)
            and ("queued policy buttons attached" in window)
            and ("missing trade/policy/transfer id" in window)
            and ("xfr(?:\\\\_|[_-])?" in window)
            and ("__xclawHasPolicyPending" in window)
        ):
            return raw, False, None
        start = raw.find(f"\n\t// {QUEUED_BUTTONS_MARKER_V4}", anchor_idx)
        if start >= 0:
            end = raw.find("\n\n\ttry {", start)
            if end < 0:
                end = raw.find("\n\ttry {", start)
            if end > start and end < anchor_idx + 12000:
                # Replace the existing v3 block with the current injection.
                raw = raw[:start] + raw[end:]
    elif QUEUED_BUTTONS_MARKER_V3 in raw:
        start = raw.find(f"\n\t// {QUEUED_BUTTONS_MARKER_V3}", anchor_idx)
        if start >= 0:
            end = raw.find("\n\n\ttry {", start)
            if end < 0:
                end = raw.find("\n\ttry {", start)
            if end > start and end < anchor_idx + 12000:
                raw = raw[:start] + raw[end:]

    if QUEUED_BUTTONS_MARKER_V2 in raw:
        # Only remove v2 when it appears in the local window right after the anchor (inside sendTelegramText).
        window = raw[anchor_idx : min(len(raw), anchor_idx + 6000)]
        local_start = window.find(f"// {QUEUED_BUTTONS_MARKER_V2}")
        if local_start >= 0:
            start = anchor_idx + local_start
            end = raw.find("\n\t\ttry {", start)
            if end > start and end < anchor_idx + 8000:
                raw = raw[:start] + raw[end:]

    injection = (
        "\n\t// xclaw: telegram queued approval buttons v4\n"
        "\t// Auto-attach Approve/Deny buttons to queued approval_pending trade summaries sent by the agent runtime.\n"
        "\t// This avoids relying on the model to emit `[[buttons:...]]` directives.\n"
        "\tconst __xclawCheckText = String(opts?.plainText ?? text ?? \"\");\n"
        "\tconst __xclawNormalized = __xclawCheckText.replace(/<[^>]*>/g, \" \").replace(/&nbsp;/g, \" \").replace(/\\s+/g, \" \").trim();\n"
        "\tconst __xclawHasPolicyPending = /\\bppr_[a-z0-9]+\\b/i.test(__xclawNormalized);\n"
        "\tconst __xclawHasPending = /\\bStatus:\\s*approval_pending\\b/i.test(__xclawNormalized) || __xclawHasPolicyPending;\n"
        "\tif (__xclawHasPending && !opts?.replyMarkup) {\n"
        "\t\tconst tradeMatch = __xclawNormalized.match(/\\bTrade ID:\\s*`?(trd_[a-z0-9]+)`?\\b/i) ?? __xclawNormalized.match(/\\bTrade:\\s*`?(trd_[a-z0-9]+)`?\\b/i) ?? __xclawNormalized.match(/\\b(trd_[a-z0-9]+)\\b/i);\n"
        "\t\tconst policyMatch = __xclawNormalized.match(/\\bApproval ID:\\s*`?(ppr_[a-z0-9]+)`?\\b/i) ?? __xclawNormalized.match(/\\bPolicy Approval ID:\\s*`?(ppr_[a-z0-9]+)`?\\b/i) ?? __xclawNormalized.match(/\\b(ppr_[a-z0-9]+)\\b/i);\n"
        "\t\tconst transferMatch = __xclawNormalized.match(/\\bApproval ID:\\s*`?(xfr(?:\\\\_|[_-])?[a-z0-9]+)`?\\b/i) ?? __xclawNormalized.match(/\\bTransfer Approval ID:\\s*`?(xfr(?:\\\\_|[_-])?[a-z0-9]+)`?\\b/i) ?? __xclawNormalized.match(/\\bApproval:\\s*`?(xfr(?:\\\\_|[_-])?[a-z0-9]+)`?\\b/i) ?? __xclawNormalized.match(/\\b(xfr(?:\\\\_|[_-])?[a-z0-9]{10,})\\b/i);\n"
        "\t\tif (tradeMatch && tradeMatch[1]) {\n"
        "\t\t\tconst tradeId = tradeMatch[1];\n"
        "\t\t\tlet chainKey = \"\";\n"
        "\t\t\tconst cm = __xclawNormalized.match(/\\bChain:\\s*`?([a-z0-9_]+)`?\\b/i);\n"
        "\t\t\tif (cm && cm[1]) chainKey = cm[1];\n"
        "\t\t\tif (!chainKey) chainKey = String(process.env.XCLAW_DEFAULT_CHAIN ?? \"base_sepolia\").trim() || \"base_sepolia\";\n"
        "\t\t\ttry {\n"
        "\t\t\t\t// Attach buttons to the same message. Callback routing is handled by the gateway callback intercept.\n"
        "\t\t\t\tif (!opts) opts = {};\n"
        "\t\t\t\topts.replyMarkup = { inline_keyboard: [[{ text: \"Approve\", callback_data: `xappr|a|${tradeId}|${chainKey}` }, { text: \"Deny\", callback_data: `xappr|r|${tradeId}|${chainKey}` }]] };\n"
        "\t\t\t\ttry { runtime.log?.(`xclaw: queued buttons attached tradeId=${tradeId} chainKey=${chainKey}`); } catch {}\n"
        "\t\t\t} catch (err) {\n"
        "\t\t\t\ttry { runtime.log?.(`xclaw: queued buttons attach failed err=${String(err)}`); } catch {}\n"
        "\t\t\t}\n"
        "\t\t} else if (policyMatch && policyMatch[1]) {\n"
        "\t\t\tconst approvalId = policyMatch[1];\n"
        "\t\t\tlet chainKey = \"\";\n"
        "\t\t\tconst cm = __xclawNormalized.match(/\\bChain:\\s*`?([a-z0-9_]+)`?\\b/i);\n"
        "\t\t\tif (cm && cm[1]) chainKey = cm[1];\n"
        "\t\t\tif (!chainKey) chainKey = String(process.env.XCLAW_DEFAULT_CHAIN ?? \"base_sepolia\").trim() || \"base_sepolia\";\n"
        "\t\t\ttry {\n"
        "\t\t\t\tif (!opts) opts = {};\n"
        "\t\t\t\topts.replyMarkup = { inline_keyboard: [[{ text: \"Approve\", callback_data: `xpol|a|${approvalId}|${chainKey}` }, { text: \"Deny\", callback_data: `xpol|r|${approvalId}|${chainKey}` }]] };\n"
        "\t\t\t\ttry { runtime.log?.(`xclaw: queued policy buttons attached approvalId=${approvalId} chainKey=${chainKey}`); } catch {}\n"
        "\t\t\t} catch (err) {\n"
        "\t\t\t\ttry { runtime.log?.(`xclaw: queued policy buttons attach failed err=${String(err)}`); } catch {}\n"
        "\t\t\t}\n"
        "\t\t} else if (transferMatch && transferMatch[1]) {\n"
        "\t\t\tconst approvalId = `xfr_${String(transferMatch[1] || \"\").replace(/^xfr(?:\\\\_|[_-])?/i, \"\").toLowerCase()}`;\n"
        "\t\t\tlet chainKey = \"\";\n"
        "\t\t\tconst cm = __xclawNormalized.match(/\\bChain:\\s*`?([a-z0-9_]+)`?\\b/i);\n"
        "\t\t\tif (cm && cm[1]) chainKey = cm[1];\n"
        "\t\t\tif (!chainKey) chainKey = String(process.env.XCLAW_DEFAULT_CHAIN ?? \"base_sepolia\").trim() || \"base_sepolia\";\n"
        "\t\t\ttry {\n"
        "\t\t\t\tif (!opts) opts = {};\n"
        "\t\t\t\topts.replyMarkup = { inline_keyboard: [[{ text: \"Approve\", callback_data: `xfer|a|${approvalId}|${chainKey}` }, { text: \"Deny\", callback_data: `xfer|r|${approvalId}|${chainKey}` }]] };\n"
        "\t\t\t\ttry { runtime.log?.(`xclaw: queued transfer buttons attached approvalId=${approvalId} chainKey=${chainKey}`); } catch {}\n"
        "\t\t\t} catch (err) {\n"
        "\t\t\t\ttry { runtime.log?.(`xclaw: queued transfer buttons attach failed err=${String(err)}`); } catch {}\n"
        "\t\t\t}\n"
        "\t\t} else {\n"
        "\t\t\ttry { runtime.log?.(`xclaw: queued buttons skipped (pending but missing trade/policy/transfer id) sample=${__xclawNormalized.slice(0, 180)}`); } catch {}\n"
        "\t\t}\n"
        "\t} else if (__xclawHasPending && opts?.replyMarkup) {\n"
        "\t\ttry { runtime.log?.(`xclaw: queued buttons skipped (already has replyMarkup)`); } catch {}\n"
        "\t}\n"
    )

    out, ok = _inject_after_anchor(raw, anchor, injection)
    if not ok:
        return raw, False, "queued_buttons_v2_injection_failed"
    if QUEUED_BUTTONS_MARKER_V4 not in out:
        return raw, False, "queued_buttons_v2_marker_missing_after_patch"
    return out, True, None


def _restart_gateway_best_effort(cooldown_sec: int, state: dict[str, Any]) -> bool:
    now = time.time()
    last = state.get("lastRestartAtEpoch")
    try:
        last_epoch = float(last) if last is not None else 0.0
    except Exception:
        last_epoch = 0.0
    if now - last_epoch < cooldown_sec:
        return False

    # Prefer systemd user service when present.
    if shutil.which("systemctl"):
        try:
            active = subprocess.run(
                ["systemctl", "--user", "is-active", "openclaw-gateway.service"],
                text=True,
                capture_output=True,
                timeout=5,
            )
            if active.returncode == 0:
                subprocess.run(["systemctl", "--user", "restart", "openclaw-gateway.service"], timeout=15)
                state["lastRestartAtEpoch"] = now
                state["lastRestartAt"] = _utc_now()
                _write_json(STATE_FILE, state)
                return True
        except Exception:
            return False

    # Fall back: try openclaw CLI restart if available (may be a no-op in some setups).
    openclaw = _resolve_openclaw_bin()
    if openclaw:
        try:
            proc = subprocess.run([openclaw, "gateway", "restart"], text=True, capture_output=True, timeout=20)
            if proc.returncode == 0:
                state["lastRestartAtEpoch"] = now
                state["lastRestartAt"] = _utc_now()
                _write_json(STATE_FILE, state)
                return True
        except Exception:
            return False
    return False


def ensure_patched(*, restart: bool, cooldown_sec: int) -> PatchResult:
    try:
        _acquire_lock()
    except Exception as exc:
        return PatchResult(ok=False, patched=False, restarted=False, error=str(exc))

    try:
        openclaw_bin = _resolve_openclaw_bin()
        if not openclaw_bin:
            return PatchResult(ok=False, patched=False, restarted=False, error="openclaw_not_found")
        pkg_root = _openclaw_pkg_root(openclaw_bin)
        if not pkg_root:
            return PatchResult(ok=False, patched=False, restarted=False, error="openclaw_pkg_root_not_found")
        version = _read_openclaw_version(openclaw_bin, pkg_root)

        bundles = _find_loader_bundles(pkg_root)
        if not bundles:
            return PatchResult(
                ok=False,
                patched=False,
                restarted=False,
                openclaw_bin=openclaw_bin,
                openclaw_version=version,
                openclaw_root=str(pkg_root),
                error="callback_bundle_not_found",
            )

        state = _read_json(STATE_FILE)
        # Bump schemaVersion when patch heuristics/normalization change to invalidate cached fast-path.
        state["schemaVersion"] = STATE_SCHEMA_VERSION
        state.setdefault("bundles", {})
        state["lastAttemptAt"] = _utc_now()
        state["openclawBin"] = openclaw_bin
        state["openclawVersion"] = version
        state["openclawRoot"] = str(pkg_root)

        # Failure backoff: if we recently failed to patch this same OpenClaw version, avoid thrashing.
        last_error_version = state.get("lastErrorVersion")
        last_error_epoch = state.get("lastErrorAtEpoch")
        try:
            last_error_epoch_f = float(last_error_epoch) if last_error_epoch is not None else 0.0
        except Exception:
            last_error_epoch_f = 0.0
        if last_error_version == version and (time.time() - last_error_epoch_f) < 600:
            return PatchResult(
                ok=False,
                patched=False,
                restarted=False,
                openclaw_bin=openclaw_bin,
                openclaw_version=version,
                openclaw_root=str(pkg_root),
                loader_paths=[str(p) for p in bundles],
                error=str(state.get("lastError") or "backoff_active"),
            )

        patched_any = False
        changed_any = False
        loader_paths: list[str] = []
        for bundle in bundles:
            loader_paths.append(str(bundle))
            try:
                stat = bundle.stat()
                size = int(stat.st_size)
                mtime = float(stat.st_mtime)
            except Exception:
                size = -1
                mtime = -1.0

            # Fast path: if state indicates this bundle is already patched and unchanged, avoid re-reading.
            bundles_state = state.get("bundles")
            if isinstance(bundles_state, dict):
                cached = bundles_state.get(str(bundle))
            if (
                isinstance(cached, dict)
                and bool(cached.get("patched")) is True
                and cached.get("size") == size
                and cached.get("mtime") == mtime
                and state.get("openclawVersion") == version
                and cached.get("schemaVersion") == STATE_SCHEMA_VERSION
                and bool(cached.get("supportsQueuedPolicyButtons")) is True
            ):
                patched_any = True
                continue

            try:
                raw = bundle.read_text(encoding="utf-8")
            except Exception as exc:
                state["lastErrorAt"] = _utc_now()
                state["lastErrorAtEpoch"] = time.time()
                state["lastErrorVersion"] = version
                state["lastError"] = f"read_failed:{bundle}:{exc}"
                continue

            before_hash = _sha256_text(raw)
            patched_text, changed, err = _patch_loader_bundle(raw)
            if err:
                state["lastErrorAt"] = _utc_now()
                state["lastErrorAtEpoch"] = time.time()
                state["lastErrorVersion"] = version
                state["lastError"] = f"patch_failed:{bundle}:{err}"
                continue

            # Safety gate: never write a patched bundle that does not parse.
            ok_js, js_err = _node_check_js_text(patched_text)
            if not ok_js:
                state["lastErrorAt"] = _utc_now()
                state["lastErrorAtEpoch"] = time.time()
                state["lastErrorVersion"] = version
                state["lastError"] = f"syntax_check_failed:{bundle}:{js_err or 'node_check_failed'}"
                continue

            if changed:
                try:
                    bundle.write_text(patched_text, encoding="utf-8")
                    changed_any = True
                except Exception as exc:
                    state["lastErrorAt"] = _utc_now()
                    state["lastErrorAtEpoch"] = time.time()
                    state["lastErrorVersion"] = version
                    state["lastError"] = f"write_failed:{bundle}:{exc}"
                    continue

            after_hash = _sha256_text(patched_text)
            patched_any = patched_any or (MARKER in patched_text)
            bundles_state = state.get("bundles")
            if isinstance(bundles_state, dict):
                try:
                    stat2 = bundle.stat()
                    size2 = int(stat2.st_size)
                    mtime2 = float(stat2.st_mtime)
                except Exception:
                    size2 = size
                    mtime2 = mtime
                bundles_state[str(bundle)] = {
                    "beforeSha256": before_hash,
                    "afterSha256": after_hash,
                    "patched": MARKER in patched_text,
                    "supportsQueuedPolicyButtons": _bundle_supports_queued_policy_buttons(patched_text),
                    "size": size2,
                    "mtime": mtime2,
                    "updatedAt": _utc_now(),
                    "schemaVersion": STATE_SCHEMA_VERSION,
                }

        state["lastPatchedAt"] = _utc_now() if changed_any else state.get("lastPatchedAt")
        _write_json(STATE_FILE, state)

        restarted = False
        if restart and changed_any:
            restarted = _restart_gateway_best_effort(cooldown_sec=cooldown_sec, state=state)

        return PatchResult(
            ok=patched_any,
            patched=changed_any or patched_any,
            restarted=restarted,
            openclaw_bin=openclaw_bin,
            openclaw_version=version,
            openclaw_root=str(pkg_root),
            loader_paths=loader_paths,
            error=None if patched_any else state.get("lastError") or None,
        )
    finally:
        _release_lock()


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--restart", action="store_true", default=False)
    parser.add_argument("--restart-cooldown-sec", type=int, default=int(os.environ.get("XCLAW_OPENCLAW_PATCH_RESTART_COOLDOWN_SEC", "1800")))
    args = parser.parse_args(argv)

    result = ensure_patched(restart=bool(args.restart), cooldown_sec=int(args.restart_cooldown_sec))
    if args.json:
        return _emit(
            {
                "ok": result.ok,
                "patched": result.patched,
                "restarted": result.restarted,
                "openclawBin": result.openclaw_bin,
                "openclawVersion": result.openclaw_version,
                "openclawRoot": result.openclaw_root,
                "loaderPaths": result.loader_paths,
                "error": result.error,
            }
        )
    if not result.ok:
        sys.stderr.write(f"[xclaw] openclaw patch failed: {result.error}\\n")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
