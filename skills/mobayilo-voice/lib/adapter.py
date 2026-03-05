import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from .cli_runner import CliRunner, MobayiloCliError

PRODUCTION_HOST = "https://mobayilo.com"
NON_PROD_OVERRIDE_ENV = "MOBY_ALLOW_NON_PROD_HOST"
REQUIRE_APPROVAL_ENV = "MOBY_REQUIRE_APPROVAL"


@dataclass
class AdapterConfig:
    cli_path: str
    host: str
    balance_floor_cents: int
    hard_floor_cents: int
    caller_id_required: bool
    caller_id_number: Optional[str]
    audio_input_device: Optional[str]
    audio_output_device: Optional[str]
    max_concurrent_calls: int
    rate_limited_countries: list
    blocked_prefixes: list
    log_path: str
    timeout_seconds: int
    telemetry_path: str = "logs/mobayilo_voice_telemetry.log"
    update_check_enabled: bool = True
    twilio_sdk_path: Optional[str] = None

    @classmethod
    def load(cls, path: Optional[str] = None) -> "AdapterConfig":
        config_path = Path(path or os.environ.get("MOBY_CONFIG", "config/defaults.yaml"))
        with config_path.open() as handle:
            raw = yaml.safe_load(handle)
        return cls(**raw)


def mask_phone(number: Optional[str]) -> Optional[str]:
    if not number:
        return None
    digits = "".join(filter(str.isdigit, number))
    if len(digits) <= 4:
        return f"***{digits}"
    return f"***{digits[-4:]}"


def normalize_digits(number: str) -> str:
    return "".join(filter(str.isdigit, number))


class MobayiloVoiceAdapter:
    def __init__(self, config: Optional[AdapterConfig] = None, runner: Optional[CliRunner] = None):
        self.config = config or AdapterConfig.load()
        self._non_prod_host = None
        self._enforce_host_policy()
        self.runner = runner or CliRunner(self.config.cli_path, timeout=self.config.timeout_seconds)

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _append_jsonl(self, path: str, payload: Dict[str, Any]) -> None:
        try:
            out_path = Path(path)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with out_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(payload) + "\n")
        except Exception:
            # Never fail adapter flow because logging failed
            pass

    def log_event(self, event: str, payload: Dict[str, Any]) -> None:
        self._append_jsonl(
            self.config.log_path,
            {
                "ts": self._now_iso(),
                "event": event,
                "payload": payload,
            },
        )

    def emit_metric(self, name: str, value: Any = 1, tags: Optional[Dict[str, Any]] = None) -> None:
        self._append_jsonl(
            self.config.telemetry_path,
            {
                "ts": self._now_iso(),
                "metric": name,
                "value": value,
                "tags": tags or {},
            },
        )

    def _enforce_host_policy(self) -> None:
        configured_host = (self.config.host or "").strip()
        if not configured_host:
            self.config.host = PRODUCTION_HOST
            return

        normalized = configured_host.rstrip("/")
        self.config.host = normalized

        if normalized != PRODUCTION_HOST:
            if os.environ.get(NON_PROD_OVERRIDE_ENV) == "1":
                self._non_prod_host = normalized
            else:
                raise RuntimeError(
                    "Mobayilo host is set to a non-production endpoint. "
                    "Set MOBY_ALLOW_NON_PROD_HOST=1 to override intentionally."
                )

    def _base_env(self) -> Dict[str, str]:
        env = {}
        if self.config.host:
            env["MOBY_HOST"] = self.config.host
        if self.config.twilio_sdk_path:
            sdk_path = Path(self.config.twilio_sdk_path).expanduser()
            if sdk_path.exists():
                env["MOBY_TWILIO_SDK_PATH"] = str(sdk_path)
        return env

    def _get_update_hint(self) -> Dict[str, Any]:
        if not self.config.update_check_enabled:
            return {"enabled": False}

        try:
            result = self.runner.run(["self-update", "--check"], parse_json=False, env=self._base_env())
            text = (result.stdout or "").strip()
            needs_update = "update available" in text.lower() or "new version" in text.lower()
            return {
                "enabled": True,
                "needs_update": needs_update,
                "message": text,
            }
        except Exception as exc:
            # warning-only path, never block calling
            return {
                "enabled": True,
                "needs_update": False,
                "message": f"update check unavailable: {exc}",
            }

    def get_status(self) -> Dict[str, Any]:
        status = {
            "cli_path": self.config.cli_path,
            "host": self.config.host,
            "caller_id_required": self.config.caller_id_required,
            "caller_id_number": mask_phone(self.config.caller_id_number),
            "warnings": [],
        }

        if self._non_prod_host:
            status["non_production_host"] = self._non_prod_host
            status["warnings"].append("Non-production host override is active")

        auth = self.runner.run(["auth", "status", "--json"], parse_json=True, env=self._base_env()).json
        balance = self.runner.run(["balance", "--json"], parse_json=True, env=self._base_env()).json
        update_hint = self._get_update_hint()

        status["auth"] = auth
        status["balance"] = balance
        status["update"] = update_hint

        balance_cents = balance.get("balance_cents", 0)
        if balance_cents < self.config.balance_floor_cents:
            status["warnings"].append(
                f"Low balance warning: {balance_cents} < warning floor {self.config.balance_floor_cents}"
            )
            self.emit_metric("mobayilo.balance.low", balance_cents)

        if update_hint.get("needs_update"):
            status["warnings"].append("CLI update available")
            self.emit_metric("mobayilo.cli.update_available", 1)

        status["ready"] = bool(
            auth.get("authenticated") and balance_cents >= self.config.hard_floor_cents
        )

        if self.config.caller_id_required:
            caller_status = None
            if isinstance(auth.get("account"), dict):
                caller_status = auth["account"].get("caller_id_status")
            status["caller_id_ready"] = caller_status == "verified"
            if not status["caller_id_ready"]:
                status["ready"] = False

        return status

    def ensure_ready(self) -> Dict[str, Any]:
        data = self.get_status()
        if not data.get("ready"):
            self.emit_metric("mobayilo.preflight.failed", 1)
            raise MobayiloCliError(
                message="Mobayilo CLI not ready for calls",
                exit_code=1,
                stdout=json.dumps(data, indent=2),
                stderr="pre-flight failed",
            )
        return data

    def _validate_destination(self, destination: str) -> None:
        if not destination:
            raise MobayiloCliError(
                message="Destination number is required",
                exit_code=2,
                stdout="",
                stderr="missing destination",
            )

        digits = normalize_digits(destination)
        if len(digits) < 8 or len(digits) > 15:
            raise MobayiloCliError(
                message="Destination must be a valid E.164-like number",
                exit_code=2,
                stdout="",
                stderr="invalid destination",
            )

        emergency_numbers = {"911", "112", "999"}
        if digits in emergency_numbers:
            raise MobayiloCliError(
                message="Emergency numbers are blocked",
                exit_code=3,
                stdout="",
                stderr="blocked destination",
            )

        for prefix in self.config.blocked_prefixes:
            if digits.startswith(prefix):
                raise MobayiloCliError(
                    message="Destination prefix is blocked",
                    exit_code=3,
                    stdout="",
                    stderr="blocked destination",
                )

    def _approval_required(self) -> bool:
        return os.environ.get(REQUIRE_APPROVAL_ENV) == "1"

    def _agent_status(self) -> Optional[Dict[str, Any]]:
        try:
            return self.runner.run(["agent", "status", "--json"], parse_json=True, env=self._base_env()).json
        except Exception:
            return None

    def _open_agent_tab(self, agent_url: str = "http://127.0.0.1:7788/") -> None:
        try:
            if sys.platform == "darwin":
                subprocess.Popen(["open", agent_url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            # best-effort only
            pass

    def _fetch_agent_call_state(self, call_id: str) -> Optional[Dict[str, Any]]:
        try:
            url = f"http://127.0.0.1:7788/v1/calls/{call_id}"
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=2) as resp:
                body = resp.read().decode("utf-8")
            return json.loads(body)
        except Exception:
            return None

    def _wait_for_agent_progress(self, call_id: str, timeout_seconds: int = 12) -> Optional[Dict[str, Any]]:
        deadline = time.time() + timeout_seconds
        last_state = None
        while time.time() < deadline:
            state = self._fetch_agent_call_state(call_id)
            if state and isinstance(state, dict):
                s = str(state.get("state", "")).lower()
                last_state = state
                if s in {"queued", "dialing", "answered", "connected", "completed", "failed", "error"}:
                    return state
            time.sleep(0.8)
        return last_state

    def _normalize_agent_outcome(self, state: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        if not state or not isinstance(state, dict):
            return {
                "state": "unknown",
                "definitive": False,
                "success": None,
                "note": "No call-state details returned by local agent endpoint",
            }

        raw_state = str(state.get("state", "")).lower()

        if raw_state == "queued":
            return {"state": "queued", "definitive": False, "success": None}
        if raw_state == "dialing":
            return {"state": "dialing", "definitive": False, "success": None}
        if raw_state == "answered":
            return {"state": "answered", "definitive": False, "success": None}
        if raw_state in {"completed"}:
            return {"state": "completed", "definitive": True, "success": True}
        if raw_state in {"failed", "error"}:
            return {"state": "failed", "definitive": True, "success": False}

        if raw_state == "connected":
            return {
                "state": "agent_connected_local",
                "definitive": False,
                "success": None,
                "note": "Local media/session connected, but destination-level success is not yet definitive",
            }

        return {
            "state": raw_state or "unknown",
            "definitive": False,
            "success": None,
        }

    def _agent_run_pids(self) -> list[int]:
        try:
            proc = subprocess.run(
                ["ps", "-ax", "-o", "pid=,command="],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
        except Exception:
            return []

        pids: list[int] = []
        for line in (proc.stdout or "").splitlines():
            row = line.strip()
            if not row:
                continue
            parts = row.split(None, 1)
            if len(parts) != 2:
                continue
            pid_txt, command = parts
            if "moby agent run" not in command:
                continue
            try:
                pid = int(pid_txt)
            except ValueError:
                continue
            pids.append(pid)
        return pids

    def _enforce_agent_singleton(self) -> None:
        pids = self._agent_run_pids()
        if len(pids) <= 1:
            return

        # Keep oldest PID, terminate extras.
        keep = min(pids)
        killed = 0
        for pid in pids:
            if pid == keep:
                continue
            try:
                os.kill(pid, 15)
                killed += 1
            except Exception:
                pass
        if killed:
            self.emit_metric("mobayilo.agent.singleton.killed_extras", killed)

    def _ensure_agent_running(self) -> Optional[Dict[str, Any]]:
        self._enforce_agent_singleton()
        status = self._agent_status()
        if status and status.get("running"):
            return status

        # Auto-start local agent so operators can use one command flow.
        log_file = Path(self.config.log_path)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        out = log_file.open("a", encoding="utf-8")
        try:
            subprocess.Popen(
                [self.config.cli_path, "agent", "run"],
                env={**os.environ, **self._base_env()},
                stdout=out,
                stderr=subprocess.STDOUT,
                start_new_session=True,
                text=True,
            )
        finally:
            out.close()

        for _ in range(10):
            time.sleep(0.4)
            self._enforce_agent_singleton()
            status = self._agent_status()
            if status and status.get("running"):
                self.emit_metric("mobayilo.agent.auto_started", 1)
                return status
        return status

    def start_call(
        self,
        destination: str,
        country: Optional[str] = None,
        dry_run: bool = True,
        approved: bool = False,
        callback: bool = False,
        fallback_callback: bool = False,
        require_agent_ready: bool = False,
    ) -> Dict[str, Any]:
        self._validate_destination(destination)

        if self._approval_required() and not approved:
            self.emit_metric("mobayilo.calls.blocked.approval_required", 1)
            raise MobayiloCliError(
                message="Call requires explicit approval",
                exit_code=4,
                stdout="",
                stderr="approval required",
            )

        readiness = self.ensure_ready()

        args = ["call", destination]
        if country:
            args += ["--country", country]
        if callback:
            args.append("--callback")
        args.append("--json")

        if dry_run:
            payload = {
                "dry_run": True,
                "mode": "callback" if callback else "agent",
                "command": " ".join([self.config.cli_path, *args]),
                "destination_masked": mask_phone(destination),
            }
            self.log_event("start_call", {"dry_run": True, "destination": mask_phone(destination)})
            self.emit_metric("mobayilo.calls.dry_run", 1)
            return payload

        self.emit_metric("mobayilo.calls.started", 1)
        try:
            selected_mode = "callback" if callback else "agent"

            # Phase-2 orchestration: let `moby call` own the agent lifecycle/UI flow.
            # No pre-start or singleton enforcement by default.
            if not callback and require_agent_ready:
                pre_status = self._agent_status()
                if not pre_status or not pre_status.get("running") or not pre_status.get("ready"):
                    self.emit_metric("mobayilo.agent.not_ready.strict", 1)
                    raise MobayiloCliError(
                        message="Agent not ready for direct dialing",
                        exit_code=5,
                        stdout=json.dumps(pre_status or {}, indent=2),
                        stderr="agent not ready",
                    )
            result = self.runner.run(args, parse_json=True, env=self._base_env())
            payload = {
                "dry_run": False,
                "mode": selected_mode,
                "payload": result.json,
                "destination_masked": mask_phone(destination),
            }

            if not callback:
                call_id = None
                if isinstance(result.json, dict):
                    call_id = result.json.get("call_id")
                if call_id:
                    progress = self._wait_for_agent_progress(call_id)
                    outcome = self._normalize_agent_outcome(progress)
                    payload["call_state"] = progress or {"state": "unknown"}
                    payload["call_outcome"] = outcome

                    state_value = str((progress or {}).get("state", "")).lower()
                    if state_value == "queued":
                        self.emit_metric("mobayilo.agent.queue_stalled", 1)
                        raise MobayiloCliError(
                            message="Call queued but agent did not start dialing",
                            exit_code=6,
                            stdout=json.dumps(payload, indent=2),
                            stderr="agent queue stalled",
                        )
                    if state_value in {"failed", "error"}:
                        self.emit_metric("mobayilo.calls.failed", 1, tags={"reason": state_value})
                        raise MobayiloCliError(
                            message="Call failed in local agent",
                            exit_code=7,
                            stdout=json.dumps(progress, indent=2),
                            stderr=state_value,
                        )
                    if state_value == "connected":
                        self.emit_metric("mobayilo.agent.connected_ambiguous", 1)

                agent_status = self._agent_status()
                if agent_status and agent_status.get("running") and not agent_status.get("ready"):
                    self.emit_metric("mobayilo.agent.not_ready", 1)
                    if fallback_callback:
                        fallback_args = ["call", destination]
                        if country:
                            fallback_args += ["--country", country]
                        fallback_args += ["--callback", "--json"]
                        fallback_result = self.runner.run(
                            fallback_args,
                            parse_json=True,
                            env=self._base_env(),
                        )
                        payload["mode"] = "callback"
                        payload["fallback_used"] = True
                        payload["fallback_reason"] = "agent_not_ready"
                        payload["payload"] = fallback_result.json
            self.log_event(
                "start_call",
                {
                    "dry_run": False,
                    "destination": mask_phone(destination),
                    "ready": readiness.get("ready"),
                },
            )
            self.emit_metric("mobayilo.calls.completed", 1)
            return payload
        except MobayiloCliError as exc:
            self.emit_metric("mobayilo.calls.failed", 1, tags={"reason": exc.stderr or "unknown"})
            raise
