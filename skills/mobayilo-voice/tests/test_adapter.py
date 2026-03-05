import json
import os
from pathlib import Path

import pytest

from lib.adapter import AdapterConfig, MobayiloVoiceAdapter, mask_phone
from lib.cli_runner import CliResult, MobayiloCliError


class FakeRunner:
    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def run(self, args, parse_json=False, env=None):
        key = tuple(args)
        self.calls.append(key)
        resp = self.responses.get(key)
        if isinstance(resp, Exception):
            raise resp
        if callable(resp):
            resp = resp()
        if parse_json:
            return CliResult(command=["moby", *args], exit_code=0, stdout=json.dumps(resp), stderr="", json=resp)
        return CliResult(command=["moby", *args], exit_code=0, stdout=str(resp or ""), stderr="", json=None)


def mk_config(tmp_path, host="https://mobayilo.com"):
    return AdapterConfig(
        cli_path="/tmp/moby",
        host=host,
        balance_floor_cents=2000,
        hard_floor_cents=500,
        caller_id_required=True,
        caller_id_number=None,
        audio_input_device=None,
        audio_output_device=None,
        max_concurrent_calls=3,
        rate_limited_countries=[],
        blocked_prefixes=["1900"],
        log_path=str(tmp_path / "events.log"),
        telemetry_path=str(tmp_path / "telemetry.log"),
        timeout_seconds=30,
        update_check_enabled=True,
        twilio_sdk_path=None,
    )


def test_mask_phone_last4_only():
    assert mask_phone("+81 90-1234-5678") == "***5678"


def test_non_prod_host_blocked(tmp_path):
    config = mk_config(tmp_path, host="https://staging.mobayilo.local")
    with pytest.raises(RuntimeError):
        MobayiloVoiceAdapter(config=config, runner=FakeRunner({}))


def test_non_prod_host_allowed_with_override(tmp_path, monkeypatch):
    monkeypatch.setenv("MOBY_ALLOW_NON_PROD_HOST", "1")
    config = mk_config(tmp_path, host="https://staging.mobayilo.local")
    adapter = MobayiloVoiceAdapter(config=config, runner=FakeRunner({}))
    assert adapter.config.host == "https://staging.mobayilo.local"


def test_status_low_balance_and_update_warning(tmp_path):
    config = mk_config(tmp_path)
    runner = FakeRunner(
        {
            ("auth", "status", "--json"): {
                "authenticated": True,
                "account": {"caller_id_status": "verified", "caller_id_e164": "+14155550123"},
                "actor": {"email": "x@example.com"},
            },
            ("balance", "--json"): {"balance_cents": 600},
            ("self-update", "--check"): "Update available: v0.2.0",
        }
    )
    adapter = MobayiloVoiceAdapter(config=config, runner=runner)
    status = adapter.get_status()
    assert status["ready"] is True
    assert any("Low balance warning" in w for w in status["warnings"])
    assert any("CLI update available" in w for w in status["warnings"])


def test_start_call_requires_approval_when_enabled(tmp_path, monkeypatch):
    monkeypatch.setenv("MOBY_REQUIRE_APPROVAL", "1")
    config = mk_config(tmp_path)
    runner = FakeRunner(
        {
            ("auth", "status", "--json"): {
                "authenticated": True,
                "account": {"caller_id_status": "verified"},
            },
            ("balance", "--json"): {"balance_cents": 5000},
            ("self-update", "--check"): "up to date",
        }
    )
    adapter = MobayiloVoiceAdapter(config=config, runner=runner)
    with pytest.raises(MobayiloCliError):
        adapter.start_call(destination="+14155550123", dry_run=True, approved=False)


def test_start_call_dry_run_masks_destination(tmp_path):
    config = mk_config(tmp_path)
    runner = FakeRunner(
        {
            ("auth", "status", "--json"): {
                "authenticated": True,
                "account": {"caller_id_status": "verified"},
            },
            ("balance", "--json"): {"balance_cents": 5000},
            ("self-update", "--check"): "up to date",
        }
    )
    adapter = MobayiloVoiceAdapter(config=config, runner=runner)
    payload = adapter.start_call(destination="+14155550123", dry_run=True, approved=True)
    assert payload["destination_masked"] == "***0123"
    assert Path(config.log_path).exists()


def test_block_emergency_destination(tmp_path):
    config = mk_config(tmp_path)
    runner = FakeRunner({})
    adapter = MobayiloVoiceAdapter(config=config, runner=runner)
    with pytest.raises(MobayiloCliError):
        adapter.start_call(destination="911", dry_run=True)


def test_normalize_agent_outcome_connected_is_not_definitive(tmp_path):
    config = mk_config(tmp_path)
    adapter = MobayiloVoiceAdapter(config=config, runner=FakeRunner({}))
    normalized = adapter._normalize_agent_outcome({"state": "connected"})
    assert normalized["state"] == "agent_connected_local"
    assert normalized["definitive"] is False
    assert normalized["success"] is None


def test_start_call_reports_call_outcome_for_agent_progress(tmp_path, monkeypatch):
    config = mk_config(tmp_path)
    runner = FakeRunner(
        {
            ("auth", "status", "--json"): {
                "authenticated": True,
                "account": {"caller_id_status": "verified"},
            },
            ("balance", "--json"): {"balance_cents": 5000},
            ("self-update", "--check"): "up to date",
            ("call", "+14155550123", "--json"): {"call_id": "call_123", "state": "queued"},
            ("agent", "status", "--json"): {"running": True, "ready": True},
        }
    )
    adapter = MobayiloVoiceAdapter(config=config, runner=runner)
    monkeypatch.setattr(adapter, "_wait_for_agent_progress", lambda _call_id: {"state": "answered"})

    payload = adapter.start_call(destination="+14155550123", dry_run=False, approved=True)
    assert payload["call_outcome"]["state"] == "answered"
    assert payload["call_outcome"]["definitive"] is False
