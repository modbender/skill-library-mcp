from __future__ import annotations

from pathlib import Path

import pytest

from workcrm.profile import resolve_db_path


def test_resolve_db_path_default_work(tmp_path: Path) -> None:
    p = resolve_db_path(None, data_dir=tmp_path)
    assert p.endswith("workcrm_work.sqlite")


def test_resolve_db_path_family(tmp_path: Path) -> None:
    p = resolve_db_path("family", data_dir=tmp_path)
    assert p.endswith("workcrm_family.sqlite")


def test_resolve_db_path_unknown_profile_raises(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        resolve_db_path("nope", data_dir=tmp_path)
