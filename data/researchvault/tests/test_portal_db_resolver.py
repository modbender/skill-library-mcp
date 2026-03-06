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


def _set_tmp_openclaw_deny_root(monkeypatch, workspace_root: Path) -> None:
    import portal.backend.app.db_roots as db_roots

    monkeypatch.setattr(db_roots, "_DENYLIST_ROOTS", (str(workspace_root.resolve()),))


def test_resolver_honors_selected_path_even_if_missing(tmp_path, monkeypatch):
    monkeypatch.setenv("RESEARCHVAULT_PORTAL_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("RESEARCHVAULT_PORTAL_ALLOWED_DB_ROOTS", str(tmp_path))

    from portal.backend.app.portal_state import set_selected_db_path
    from portal.backend.app.db_resolver import resolve_effective_db

    missing = tmp_path / "vaults" / "new.db"
    set_selected_db_path(str(missing))

    resolved = resolve_effective_db()
    assert resolved.source == "selected"
    assert Path(resolved.path) == missing.resolve()


def test_resolver_auto_uses_existing_default(tmp_path, monkeypatch):
    monkeypatch.setenv("RESEARCHVAULT_PORTAL_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("RESEARCHVAULT_PORTAL_ALLOWED_DB_ROOTS", str(tmp_path))
    monkeypatch.delenv("RESEARCHVAULT_DB", raising=False)

    default = tmp_path / "default.db"
    _make_min_db(default, projects=2, findings=5)

    import scripts.db as vault_db
    from portal.backend.app.portal_state import set_selected_db_path
    from portal.backend.app.db_resolver import resolve_effective_db

    monkeypatch.setattr(vault_db, "DEFAULT_DB_PATH", str(default))
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


def test_discover_candidates_only_allowed_roots(tmp_path, monkeypatch):
    allowed_root = tmp_path / "allowed"
    blocked_root = tmp_path / "blocked"

    monkeypatch.setenv("RESEARCHVAULT_PORTAL_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("RESEARCHVAULT_PORTAL_ALLOWED_DB_ROOTS", str(allowed_root))
    monkeypatch.delenv("RESEARCHVAULT_DB", raising=False)

    allowed_db = allowed_root / "research_vault.db"
    blocked_db = blocked_root / "research_vault.db"
    _make_min_db(allowed_db, projects=1, findings=1)
    _make_min_db(blocked_db, projects=10, findings=10)

    import scripts.db as vault_db
    from portal.backend.app.portal_state import set_selected_db_path
    from portal.backend.app.db_resolver import discover_candidate_paths

    monkeypatch.setattr(vault_db, "DEFAULT_DB_PATH", str(allowed_db))
    set_selected_db_path(str(blocked_db))

    candidates = discover_candidate_paths()
    assert str(allowed_db.resolve()) in candidates
    assert str(blocked_db.resolve()) not in candidates
    assert all(str(Path(p)).startswith(str(allowed_root.resolve())) for p in candidates)


def test_openclaw_workspace_path_is_never_discoverable(tmp_path, monkeypatch):
    monkeypatch.setenv("RESEARCHVAULT_PORTAL_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("RESEARCHVAULT_PORTAL_ALLOWED_DB_ROOTS", str(tmp_path))
    monkeypatch.setenv("RESEARCHVAULT_DB", str(tmp_path / ".openclaw" / "workspace" / "memory" / "research_vault.db"))

    openclaw_workspace = tmp_path / ".openclaw" / "workspace"
    openclaw_db = openclaw_workspace / "memory" / "research_vault.db"
    _make_min_db(openclaw_db, projects=3, findings=3)
    _set_tmp_openclaw_deny_root(monkeypatch, openclaw_workspace)

    import scripts.db as vault_db
    from portal.backend.app.portal_state import set_selected_db_path
    from portal.backend.app.db_resolver import discover_candidate_paths

    monkeypatch.setattr(vault_db, "DEFAULT_DB_PATH", str(tmp_path / ".researchvault" / "research_vault.db"))
    set_selected_db_path(str(openclaw_db))

    candidates = discover_candidate_paths()
    assert str(openclaw_db.resolve()) not in candidates


def test_system_rejects_openclaw_path_even_if_allowed_root_configured(tmp_path, monkeypatch):
    monkeypatch.setenv("RESEARCHVAULT_PORTAL_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("RESEARCHVAULT_PORTAL_ALLOWED_DB_ROOTS", str(tmp_path))

    openclaw_workspace = tmp_path / ".openclaw" / "workspace"
    _set_tmp_openclaw_deny_root(monkeypatch, openclaw_workspace)

    from portal.backend.app.routers.system import DbSelectRequest, system_select_db

    with pytest.raises(HTTPException) as e:
        system_select_db(DbSelectRequest(path=str(openclaw_workspace / "memory" / "blocked.db")))
    assert e.value.status_code == 400
    assert "outside allowed roots" in e.value.detail


def test_system_select_db_rejects_outside_allowed_roots(tmp_path, monkeypatch):
    monkeypatch.setenv("RESEARCHVAULT_PORTAL_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("RESEARCHVAULT_PORTAL_ALLOWED_DB_ROOTS", str(tmp_path / "allowed"))

    from portal.backend.app.routers.system import DbSelectRequest, system_select_db

    with pytest.raises(HTTPException) as e:
        system_select_db(DbSelectRequest(path=str(tmp_path / "blocked" / "x.db")))
    assert e.value.status_code == 400
    assert "outside allowed roots" in e.value.detail
