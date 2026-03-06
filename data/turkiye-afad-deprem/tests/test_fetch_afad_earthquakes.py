from __future__ import annotations

import importlib.util
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "fetch_afad_earthquakes.py"
FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "afad_sample_response.json"


def load_script_module():
    spec = importlib.util.spec_from_file_location("fetch_afad_earthquakes", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load script module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_normalize_event_converts_types_and_time():
    mod = load_script_module()
    raw = {
        "eventID": "abc-1",
        "date": "2026-02-28T12:00:00",
        "m": "4.5",
        "depth": "8.2",
        "lat": "38.10",
        "lon": "39.20",
        "location": "PULUMUR (TUNCELI)",
    }

    out = mod.normalize_event(raw)

    assert out["id"] == "abc-1"
    assert out["time_utc"] == "2026-02-28T09:00:00Z"
    assert out["magnitude"] == 4.5
    assert out["depth_km"] == 8.2
    assert out["latitude"] == 38.10
    assert out["longitude"] == 39.20
    assert out["province"] == "TUNCELI"
    assert out["district"] == "PULUMUR"


def test_run_with_fixture_and_magnitude_filter(capsys):
    mod = load_script_module()

    exit_code = mod.run(
        [
            "--fixture",
            str(FIXTURE_PATH),
            "--minMag",
            "3.5",
            "--query",
            "pul",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["source"] == "AFAD"
    assert payload["count"] == 1
    assert payload["items"][0]["id"] == "202602280001"


def test_resolve_time_window_raises_input_error_for_zero_window():
    mod = load_script_module()

    with pytest.raises(mod.AppError) as exc:
        mod.resolve_time_window(hours=0, days=0)

    assert exc.value.code == "INPUT_ERROR"


def test_normalize_events_applies_time_window_query_and_magnitude():
    mod = load_script_module()
    raw_events = [
        {
            "eventID": "1",
            "date": "2026-02-28T12:00:00",
            "m": "4.2",
            "location": "PULUMUR (TUNCELI)",
        },
        {
            "eventID": "2",
            "date": "2026-02-27T08:00:00",
            "m": "4.7",
            "location": "GOKSUN (KAHRAMANMARAS)",
        },
    ]

    now_utc = datetime(2026, 2, 28, 10, 0, 0, tzinfo=timezone.utc)
    items = mod.normalize_events(
        raw_events,
        window=timedelta(hours=30),
        min_magnitude=4.0,
        query="pul",
        now_utc=now_utc,
    )

    assert len(items) == 1
    assert items[0]["id"] == "1"
