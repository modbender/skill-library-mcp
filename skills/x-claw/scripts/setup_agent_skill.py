#!/usr/bin/env python3
"""Idempotent one-command setup for X-Claw OpenClaw skill runtime."""

from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path
from typing import Optional

APP_DIR = Path.home() / ".xclaw-agent"
POLICY_FILE = APP_DIR / "policy.json"
PATCHER = Path(__file__).resolve().parent / "openclaw_gateway_patch.py"


def run(
    cmd: list[str],
    check: bool = True,
    capture: bool = True,
    env: Optional[dict[str, str]] = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        check=check,
        text=True,
        capture_output=capture,
        env=env,
    )


def _python_command() -> list[str]:
    if sys.executable:
        return [sys.executable]
    fallback = shutil.which("python3") or shutil.which("python")
    if fallback:
        return [fallback]
    raise RuntimeError("Python interpreter not found.")


def fail(message: str, action_hint: str = "") -> int:
    payload = {"ok": False, "code": "setup_failed", "message": message}
    if action_hint:
        payload["actionHint"] = action_hint
    print(json.dumps(payload))
    return 1


def _parse_last_json_line(text: str) -> dict | None:
    for raw in reversed((text or "").splitlines()):
        line = raw.strip()
        if not line:
            continue
        if not (line.startswith("{") and line.endswith("}")):
            continue
        try:
            parsed = json.loads(line)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            continue
    return None


def resolve_openclaw() -> Optional[Path]:
    found = shutil.which("openclaw")
    if found:
        return Path(found)

    nvm_versions = Path.home() / ".nvm" / "versions" / "node"
    if nvm_versions.exists():
        candidates = sorted(nvm_versions.glob("*/bin/openclaw"))
        if candidates:
            return candidates[-1]
    return None


def ensure_openclaw(workspace: Path) -> Path:
    openclaw_bin = resolve_openclaw()
    if openclaw_bin is None:
        raise RuntimeError("openclaw CLI not found. Install OpenClaw first, then rerun this setup command.")
    os.environ["PATH"] = f"{openclaw_bin.parent}:{os.environ.get('PATH', '')}"

    cfg = Path.home() / ".openclaw" / "openclaw.json"
    if not cfg.exists():
        run(
            [
                str(openclaw_bin),
                "onboard",
                "--non-interactive",
                "--accept-risk",
                "--mode",
                "local",
                "--flow",
                "manual",
                "--auth-choice",
                "skip",
                "--skip-channels",
                "--skip-daemon",
                "--skip-ui",
                "--skip-health",
                "--workspace",
                str(workspace),
                "--json",
            ]
        )
    else:
        # Preserve existing workspace unless explicitly requested to update.
        if os.environ.get("XCLAW_OPENCLAW_SET_WORKSPACE", "").strip().lower() in {"1", "true", "yes"}:
            run([str(openclaw_bin), "config", "set", "agents.defaults.workspace", str(workspace)])
    return openclaw_bin


def ensure_managed_skill_copy(workspace: Path) -> Path:
    source = workspace / "skills" / "xclaw-agent"
    if not source.exists():
        raise RuntimeError(f"Missing skill source directory: {source}")

    target = Path.home() / ".openclaw" / "skills" / "xclaw-agent"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, dirs_exist_ok=True)
    return target


def ensure_launcher(workspace: Path, openclaw_bin: Path) -> Path:
    launcher_dir = openclaw_bin.parent
    fallback_dir = APP_DIR / "bin"
    target = workspace / "apps" / "agent-runtime"
    target_entry = target / "bin" / "xclaw-agent"
    if not target_entry.exists():
        raise RuntimeError(f"Missing runtime binary: {target_entry}")

    try_dirs = [launcher_dir]
    if fallback_dir != launcher_dir:
        try_dirs.append(fallback_dir)

    write_errors: list[str] = []
    for current_dir in try_dirs:
        try:
            current_dir.mkdir(parents=True, exist_ok=True)
            if os.name == "nt":
                launcher_path = current_dir / "xclaw-agent.cmd"
                python_cmd = _python_command()[0]
                content = "\n".join(
                    [
                        "@echo off",
                        "setlocal",
                        f'set "PYTHONPATH={target};%PYTHONPATH%"',
                        f'"{python_cmd}" -m xclaw_agent.cli %*',
                        "",
                    ]
                )
                launcher_path.write_text(content, encoding="utf-8")
                ps1_path = current_dir / "xclaw-agent.ps1"
                ps1_content = "\n".join(
                    [
                        "$ErrorActionPreference = 'Stop'",
                        f'$env:PYTHONPATH = "{target};" + $env:PYTHONPATH',
                        f'& "{python_cmd}" -m xclaw_agent.cli $args',
                        "",
                    ]
                )
                ps1_path.write_text(ps1_content, encoding="utf-8")
            else:
                launcher_path = current_dir / "xclaw-agent"
                content = "\n".join(
                    [
                        "#!/usr/bin/env bash",
                        "set -euo pipefail",
                        f'exec "{target_entry}" "$@"',
                        "",
                    ]
                )
                launcher_path.write_text(content, encoding="utf-8")
                launcher_path.chmod(launcher_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

            os.environ["PATH"] = f"{current_dir}:{os.environ.get('PATH', '')}"
            return launcher_path
        except OSError as exc:
            write_errors.append(f"{current_dir}: {exc}")

    raise RuntimeError("Unable to create xclaw-agent launcher. " + "; ".join(write_errors))


def ensure_runtime_bin_env(launcher_path: Path) -> None:
    cfg = Path.home() / ".openclaw" / "openclaw.json"
    if not cfg.exists():
        return
    payload = json.loads(cfg.read_text(encoding="utf-8"))
    skills = payload.setdefault("skills", {})
    entries = skills.setdefault("entries", {})
    xclaw = entries.setdefault("xclaw-agent", {})
    env = xclaw.setdefault("env", {})
    current = str(env.get("XCLAW_AGENT_RUNTIME_BIN", "")).strip()
    expected = str(launcher_path)
    if current == expected:
        return
    env["XCLAW_AGENT_RUNTIME_BIN"] = expected
    cfg.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def ensure_ready(openclaw_bin: Path) -> dict[str, str]:
    python_cmd = _python_command()

    if shutil.which("xclaw-agent") is None:
        raise RuntimeError("xclaw-agent launcher was not found on PATH after setup")

    run(["xclaw-agent", "status", "--json"])
    run([str(openclaw_bin), "skills", "info", "xclaw-agent"])
    run([str(openclaw_bin), "skills", "list", "--eligible"])

    python_version = run([*python_cmd, "--version"])
    version_text = (python_version.stdout or "").strip() or (python_version.stderr or "").strip()
    versions = {
        "python": version_text,
        "openclaw": run([str(openclaw_bin), "--version"]).stdout.strip(),
    }
    return versions


def _chmod_if_posix(path: Path, mode: int) -> None:
    if os.name == "nt":
        return
    os.chmod(path, mode)


def ensure_default_policy_file(default_chain: str) -> None:
    """Create a safe default local policy file when missing.

    Policy is required for spend actions (spot swap, transfers) and is enforced by xclaw-agent runtime.
    """
    APP_DIR.mkdir(parents=True, exist_ok=True)
    _chmod_if_posix(APP_DIR, 0o700)

    if POLICY_FILE.exists():
        # Do not mutate an existing policy; owners may have tightened it.
        return

    # NOTE: Slice 06 policy caps are temporarily native-denominated. In practice, this cap is used
    # as a coarse safety brake for any spend-like action until USD-cap pipeline slices land.
    #
    # Defaults are intentionally permissive enough for testnet usage while still being finite.
    payload = {
        "paused": False,
        "chains": {
            # Enable the default chain to avoid "policy missing" spend failures after install.
            default_chain: {"chain_enabled": True},
            # Hardhat-local is commonly used for local verification; keep enabled when present.
            "hardhat_local": {"chain_enabled": True},
        },
        "spend": {
            # Keep spot swaps usable out-of-the-box. Owners can tighten to require explicit approval.
            "approval_required": False,
            "approval_granted": True,
            # 1000e18 (1,000 "native wei-denominated units") daily cap as a coarse brake.
            "max_daily_native_wei": "1000000000000000000000",
        },
    }

    POLICY_FILE.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    _chmod_if_posix(POLICY_FILE, 0o600)


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    workspace = script_dir.parent.parent.parent.resolve()

    try:
        openclaw_bin = ensure_openclaw(workspace)
        managed_skill = ensure_managed_skill_copy(workspace)
        launcher = ensure_launcher(workspace, openclaw_bin)
        ensure_runtime_bin_env(launcher)
        ensure_default_policy_file(os.environ.get("XCLAW_DEFAULT_CHAIN", "base_sepolia"))
        gateway_patch: dict[str, object] | None = None
        # Portable Telegram approvals: patch OpenClaw gateway bundle idempotently.
        try:
            if os.environ.get("XCLAW_OPENCLAW_AUTO_PATCH", "1").strip().lower() not in {"0", "false", "no"} and PATCHER.exists():
                # Restart is best-effort and guarded by cooldown+lock inside patcher.
                patch_env = dict(os.environ)
                patch_env["OPENCLAW_BIN"] = str(openclaw_bin)
                patch_proc = run([*_python_command(), str(PATCHER), "--json", "--restart"], check=False, env=patch_env)
                gateway_patch = _parse_last_json_line((patch_proc.stdout or "").strip()) or {}
                if not gateway_patch:
                    gateway_patch = {
                        "ok": False,
                        "patched": False,
                        "error": "patch_output_parse_failed",
                        "stdout": (patch_proc.stdout or "").strip()[:300],
                        "stderr": (patch_proc.stderr or "").strip()[:300],
                    }
                strict_patch = os.environ.get("XCLAW_OPENCLAW_PATCH_STRICT", "1").strip().lower() not in {"0", "false", "no"}
                reported_bin = str(gateway_patch.get("openclawBin") or "").strip()
                if strict_patch and reported_bin:
                    expected_bin = str(openclaw_bin.resolve())
                    selected_bin = str(Path(reported_bin).resolve())
                    if selected_bin != expected_bin:
                        raise RuntimeError(
                            "OpenClaw gateway patch targeted a different binary than setup resolved "
                            f"(expected {expected_bin}, got {selected_bin})."
                        )
                if strict_patch and not bool(gateway_patch.get("ok")):
                    err = str(gateway_patch.get("error") or "unknown_patch_error")
                    hint = "Ensure OpenClaw is current, then rerun setup."
                    if "syntax_check_failed" in err:
                        hint = "OpenClaw bundle patch failed syntax check. Update OpenClaw and rerun setup."
                    if "write_failed" in err and "permission denied" in err.lower():
                        hint = (
                            "OpenClaw appears to be installed in a root-owned location. "
                            "Rerun the installer with sudo so gateway patching can write to the OpenClaw bundle."
                        )
                    raise RuntimeError(f"OpenClaw gateway patch failed: {err}. {hint}")
        except Exception:
            raise
        versions = ensure_ready(openclaw_bin)
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip()
        stdout = (exc.stdout or "").strip()
        return fail(
            f"Command failed: {' '.join(exc.cmd)}",
            action_hint=stderr or stdout or "Inspect OpenClaw and xclaw-agent setup, then retry.",
        )
    except Exception as exc:  # noqa: BLE001
        return fail(str(exc), "Ensure OpenClaw is installed and rerun this command.")

    payload = {
        "ok": True,
        "code": "setup_ok",
        "workspace": str(workspace),
        "launcher": str(launcher),
        "managedSkillPath": str(managed_skill),
        "openclawPath": str(openclaw_bin),
        "python": versions["python"],
        "openclaw": versions["openclaw"],
    }
    if gateway_patch is not None:
        payload["gatewayPatch"] = gateway_patch
    print(json.dumps(payload))
    return 0


if __name__ == "__main__":
    sys.exit(main())
