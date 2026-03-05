from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


class AdiRuntimeError(RuntimeError):
    """Raised when the ADI runtime is unavailable or execution fails."""


def read_input_payload(input_arg: str) -> tuple[str, Any]:
    """Read JSON or text payload from a file path or stdin marker."""
    if input_arg == "-":
        raw = sys.stdin.read()
        source = "<stdin>"
    else:
        path = Path(input_arg)
        raw = path.read_text(encoding="utf-8")
        source = str(path)

    try:
        return source, json.loads(raw)
    except json.JSONDecodeError:
        return source, raw


def write_json(data: Any) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def _adi_cli_path() -> str | None:
    return shutil.which("adi")


def _import_adi() -> tuple[Any, Any] | None:
    try:
        from adi.core.decision_engine import decide
        from adi.schemas.decision_request import DecisionRequest
    except Exception:
        return None
    return DecisionRequest, decide


def ensure_runtime_available() -> str:
    if _import_adi() is not None:
        return "python"
    if _adi_cli_path():
        return "cli"
    raise AdiRuntimeError(
        "ADI runtime not found. Install the 'adi-decision' Python package or make the 'adi' CLI available on PATH."
    )


def validate_request_data(data: dict[str, Any]) -> dict[str, Any]:
    runtime = ensure_runtime_available()
    if runtime == "python":
        DecisionRequest, _ = _import_adi()  # type: ignore[misc]
        request = DecisionRequest.model_validate(data)
        return request.model_dump()

    cli = _adi_cli_path()
    assert cli is not None
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8", delete=False) as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        temp_path = handle.name

    result = subprocess.run(
        [cli, "validate", temp_path],
        capture_output=True,
        text=True,
        check=False,
    )
    Path(temp_path).unlink(missing_ok=True)
    if result.returncode != 0:
        raise AdiRuntimeError(result.stderr.strip() or result.stdout.strip() or "ADI validation failed.")
    return data


def run_request_data(data: dict[str, Any], policy_override: str | None = None) -> dict[str, Any]:
    runtime = ensure_runtime_available()
    payload = dict(data)
    if policy_override:
        payload["policy_name"] = policy_override

    if runtime == "python":
        DecisionRequest, decide = _import_adi()  # type: ignore[misc]
        request = DecisionRequest.model_validate(payload)
        return decide(request).model_dump()

    cli = _adi_cli_path()
    assert cli is not None
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8", delete=False) as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        temp_path = handle.name

    command = [cli, "decide", "--input", temp_path]
    if policy_override:
        command.extend(["--policy", policy_override])

    result = subprocess.run(command, capture_output=True, text=True, check=False)
    Path(temp_path).unlink(missing_ok=True)
    if result.returncode != 0:
        raise AdiRuntimeError(result.stderr.strip() or result.stdout.strip() or "ADI execution failed.")

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise AdiRuntimeError(f"ADI CLI returned non-JSON output: {exc}") from exc
