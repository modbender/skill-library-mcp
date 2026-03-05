import os
import sqlite3
from pathlib import Path

import pytest
from fastapi import HTTPException


def _make_min_db(path: Path, *, projects: int = 0, findings: int = 0) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS projects (id TEXT PRIMARY KEY)")
    c.execute("CREATE TABLE IF NOT EXISTS findings (id TEXT PRIMARY KEY)")
    for i in range(int(projects)):
        c.execute("INSERT OR IGNORE INTO projects (id) VALUES (?)", (f"p{i}",))
    for i in range(int(findings)):
        c.execute("INSERT OR IGNORE INTO findings (id) VALUES (?)", (f"f{i}",))
    conn.commit()
    conn.close()


def _patch_openclaw_workspace(monkeypatch, workspace_root: Path) -> None:
    import portal.backend.app.db_resolver as db_resolver

    workspace = workspace_root.resolve()
    monkeypatch.setattr(db_resolver, "OPENCLAW_WORKSPACE_ROOT", workspace)
    monkeypatch.setattr(db_resolver, "OPENCLAW_MEMORY_ROOT", workspace / "memory")


def test_resolver_honors_selected_path_even_if_missing(tmp_path, monkeypatch):
    # Redirect portal state to a temp dir so tests never touch the user's home.
    monkeypatch.setenv("RESEARCHVAULT_PORTAL_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("RESEARCHVAULT_PORTAL_ALLOWED_DB_ROOTS", str(tmp_path))

    from portal.backend.app.portal_state import set_selected_db_path
    from portal.backend.app.db_resolver import resolve_effective_db

    missing = tmp_path / "vaults" / "new.db"
    set_selected_db_path(str(missing))

    resolved = resolve_effective_db()
    assert resolved.source == "selected"
    assert Path(resolved.path) == missing.resolve()


def test_resolver_auto_prefers_populated_default_over_empty_legacy(tmp_path, monkeypatch):
    monkeypatch.setenv("RESEARCHVAULT_PORTAL_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("RESEARCHVAULT_PORTAL_ALLOWED_DB_ROOTS", str(tmp_path))
    monkeypatch.delenv("RESEARCHVAULT_DB", raising=False)

    legacy = tmp_path / "legacy.db"
    default = tmp_path / "default.db"

    _make_min_db(legacy, projects=0, findings=0)
    _make_min_db(default, projects=2, findings=5)

    import scripts.db as vault_db

    monkeypatch.setattr(vault_db, "LEGACY_DB_PATH", str(legacy))
    monkeypatch.setattr(vault_db, "DEFAULT_DB_PATH", str(default))

    from portal.backend.app.portal_state import set_selected_db_path
    from portal.backend.app.db_resolver import resolve_effective_db

    set_selected_db_path(None)
    resolved = resolve_effective_db()
    assert resolved.source == "auto"
    assert Path(resolved.path) == default.resolve()


def test_resolver_env_override_wins(tmp_path, monkeypatch):
    monkeypatch.setenv("RESEARCHVAULT_PORTAL_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("RESEARCHVAULT_PORTAL_ALLOWED_DB_ROOTS", str(tmp_path))
    monkeypatch.setenv("RESEARCHVAULT_DB", str(tmp_path / "env.db"))

    from portal.backend.app.portal_state import set_selected_db_path
    from portal.backend.app.db_resolver import resolve_effective_db

    set_selected_db_path(None)
    resolved = resolve_effective_db()
    assert resolved.source == "env"
    assert Path(resolved.path) == (tmp_path / "env.db").resolve()


def test_discover_candidates_default_excludes_legacy_openclaw(tmp_path, monkeypatch):
    monkeypatch.setenv("RESEARCHVAULT_PORTAL_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.delenv("RESEARCHVAULT_PORTAL_SCAN_OPENCLAW", raising=False)
    monkeypatch.delenv("RESEARCHVAULT_DB", raising=False)

    legacy = tmp_path / ".openclaw" / "workspace" / "memory" / "research_vault.db"
    default = tmp_path / ".researchvault" / "research_vault.db"
    _make_min_db(legacy, projects=3, findings=8)
    _make_min_db(default, projects=1, findings=1)

    import scripts.db as vault_db

    monkeypatch.setattr(vault_db, "LEGACY_DB_PATH", str(legacy))
    monkeypatch.setattr(vault_db, "DEFAULT_DB_PATH", str(default))

    from portal.backend.app.db_resolver import discover_candidate_paths
    from portal.backend.app.portal_state import set_selected_db_path

    set_selected_db_path(None)
    candidates = discover_candidate_paths()
    assert str(legacy.resolve()) not in candidates


def test_discover_candidates_opt_in_includes_legacy_openclaw(tmp_path, monkeypatch):
    monkeypatch.setenv("RESEARCHVAULT_PORTAL_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("RESEARCHVAULT_PORTAL_SCAN_OPENCLAW", "1")
    monkeypatch.delenv("RESEARCHVAULT_DB", raising=False)
    monkeypatch.setenv("RESEARCHVAULT_PORTAL_ALLOWED_DB_ROOTS", str(tmp_path))

    legacy = tmp_path / ".openclaw" / "workspace" / "memory" / "research_vault.db"
    default = tmp_path / ".researchvault" / "research_vault.db"
    _make_min_db(legacy, projects=3, findings=8)
    _make_min_db(default, projects=1, findings=1)

    import scripts.db as vault_db

    monkeypatch.setattr(vault_db, "LEGACY_DB_PATH", str(legacy))
    monkeypatch.setattr(vault_db, "DEFAULT_DB_PATH", str(default))
    _patch_openclaw_workspace(monkeypatch, tmp_path / ".openclaw" / "workspace")

    from portal.backend.app.db_resolver import discover_candidate_paths
    from portal.backend.app.portal_state import set_selected_db_path

    set_selected_db_path(None)
    candidates = discover_candidate_paths()
    assert str(legacy.resolve()) in candidates


def test_resolver_scan_disabled_ignores_legacy_even_if_present(tmp_path, monkeypatch):
    monkeypatch.setenv("RESEARCHVAULT_PORTAL_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("RESEARCHVAULT_PORTAL_ALLOWED_DB_ROOTS", str(tmp_path))
    monkeypatch.delenv("RESEARCHVAULT_DB", raising=False)
    monkeypatch.delenv("RESEARCHVAULT_PORTAL_SCAN_OPENCLAW", raising=False)

    legacy = tmp_path / ".openclaw" / "workspace" / "memory" / "research_vault.db"
    default = tmp_path / ".researchvault" / "research_vault.db"
    _make_min_db(legacy, projects=2, findings=4)

    import scripts.db as vault_db

    monkeypatch.setattr(vault_db, "LEGACY_DB_PATH", str(legacy))
    monkeypatch.setattr(vault_db, "DEFAULT_DB_PATH", str(default))

    from portal.backend.app.db_resolver import resolve_effective_db
    from portal.backend.app.portal_state import set_selected_db_path

    set_selected_db_path(None)
    resolved = resolve_effective_db()
    assert Path(resolved.path) == default.resolve()
    assert "No existing DB found" in resolved.note or "Only default DB exists" in resolved.note


def test_resolver_scan_enabled_can_use_legacy(tmp_path, monkeypatch):
    monkeypatch.setenv("RESEARCHVAULT_PORTAL_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.delenv("RESEARCHVAULT_DB", raising=False)
    monkeypatch.setenv("RESEARCHVAULT_PORTAL_SCAN_OPENCLAW", "1")
    monkeypatch.setenv("RESEARCHVAULT_PORTAL_ALLOWED_DB_ROOTS", str(tmp_path))

    legacy = tmp_path / ".openclaw" / "workspace" / "memory" / "research_vault.db"
    default = tmp_path / ".researchvault" / "research_vault.db"
    _make_min_db(legacy, projects=2, findings=4)

    import scripts.db as vault_db

    monkeypatch.setattr(vault_db, "LEGACY_DB_PATH", str(legacy))
    monkeypatch.setattr(vault_db, "DEFAULT_DB_PATH", str(default))
    _patch_openclaw_workspace(monkeypatch, tmp_path / ".openclaw" / "workspace")

    from portal.backend.app.db_resolver import resolve_effective_db
    from portal.backend.app.portal_state import set_selected_db_path

    set_selected_db_path(None)
    resolved = resolve_effective_db()
    assert Path(resolved.path) == legacy.resolve()


def test_system_rejects_openclaw_path_when_scan_disabled(monkeypatch):
    monkeypatch.delenv("RESEARCHVAULT_PORTAL_SCAN_OPENCLAW", raising=False)
    monkeypatch.delenv("RESEARCHVAULT_PORTAL_ALLOWED_DB_ROOTS", raising=False)

    from portal.backend.app.db_resolver import openclaw_workspace_root
    from portal.backend.app.routers.system import _allowed_db_path

    candidate = openclaw_workspace_root() / "memory" / "blocked.db"
    assert _allowed_db_path(candidate) is False


def test_system_allows_openclaw_path_when_scan_enabled(monkeypatch):
    monkeypatch.setenv("RESEARCHVAULT_PORTAL_SCAN_OPENCLAW", "1")
    from portal.backend.app.db_resolver import openclaw_workspace_root

    monkeypatch.setenv("RESEARCHVAULT_PORTAL_ALLOWED_DB_ROOTS", str(openclaw_workspace_root()))

    from portal.backend.app.routers.system import _allowed_db_path

    candidate = openclaw_workspace_root() / "memory" / "allowed.db"
    assert _allowed_db_path(candidate) is True


def test_scan_openclaw_requested_but_root_not_allowed(tmp_path, monkeypatch):
    monkeypatch.setenv("RESEARCHVAULT_PORTAL_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("RESEARCHVAULT_PORTAL_SCAN_OPENCLAW", "1")
    monkeypatch.setenv("RESEARCHVAULT_PORTAL_ALLOWED_DB_ROOTS", str(tmp_path / ".researchvault"))
    monkeypatch.delenv("RESEARCHVAULT_DB", raising=False)

    legacy = tmp_path / ".openclaw" / "workspace" / "memory" / "research_vault.db"
    default = tmp_path / ".researchvault" / "research_vault.db"
    _make_min_db(legacy, projects=3, findings=8)
    _make_min_db(default, projects=1, findings=1)

    import scripts.db as vault_db

    monkeypatch.setattr(vault_db, "LEGACY_DB_PATH", str(legacy))
    monkeypatch.setattr(vault_db, "DEFAULT_DB_PATH", str(default))
    _patch_openclaw_workspace(monkeypatch, tmp_path / ".openclaw" / "workspace")

    from portal.backend.app.db_resolver import discover_candidate_paths
    from portal.backend.app.portal_state import set_selected_db_path

    set_selected_db_path(None)
    candidates = discover_candidate_paths()
    assert str(legacy.resolve()) not in candidates


def test_system_select_db_rejects_outside_allowed_roots(tmp_path, monkeypatch):
    monkeypatch.setenv("RESEARCHVAULT_PORTAL_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("RESEARCHVAULT_PORTAL_ALLOWED_DB_ROOTS", str(tmp_path / "allowed"))

    from portal.backend.app.routers.system import DbSelectRequest, system_select_db

    with pytest.raises(HTTPException) as e:
        system_select_db(DbSelectRequest(path=str(tmp_path / "blocked" / "x.db")))
    assert e.value.status_code == 400
    assert "outside allowed roots" in e.value.detail
