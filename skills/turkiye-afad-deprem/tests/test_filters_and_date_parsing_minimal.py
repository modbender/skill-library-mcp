from __future__ import annotations

import importlib.util
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "fetch_afad_earthquakes.py"
FIXTURE_NORMAL = (
    Path(__file__).resolve().parents[1] / "fixtures" / "afad_fixture_normal_10.json"
)


def load_script_module():
    spec = importlib.util.spec_from_file_location("fetch_afad_earthquakes", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load script module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_min_mag_filter_works():
    mod = load_script_module()
    raw_events = mod.load_fixture(str(FIXTURE_NORMAL))

    items = mod.normalize_events(
        raw_events,
        window=None,
        min_magnitude=4.0,
        query=None,
    )

    assert len(items) == 4
    assert all(item["magnitude"] >= 4.0 for item in items)


def test_query_filter_works():
    mod = load_script_module()
    raw_events = mod.load_fixture(str(FIXTURE_NORMAL))

    items = mod.normalize_events(
        raw_events,
        window=None,
        min_magnitude=None,
        query="izmir",
    )

    assert len(items) == 3
    assert all("izmir" in item["location"].casefold() for item in items)


def test_date_is_parsed():
    mod = load_script_module()

    dt = mod.parse_datetime("2026.02.28 12:00:00")

    assert dt is not None
    assert dt.isoformat() == "2026-02-28T09:00:00+00:00"
