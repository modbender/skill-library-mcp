import importlib
import json

import pytest


def _reload_portal_secrets():
    import portal.backend.app.portal_secrets as portal_secrets

    return importlib.reload(portal_secrets)


def test_portal_secrets_env_only_no_file_created(tmp_path, monkeypatch):
    monkeypatch.setenv("RESEARCHVAULT_PORTAL_STATE_DIR", str(tmp_path))
    monkeypatch.setenv("BRAVE_API_KEY", "b" * 20)
    monkeypatch.setenv("SERPER_API_KEY", "s" * 20)
    monkeypatch.setenv("SEARXNG_BASE_URL", "https://searx.example")

    secrets = _reload_portal_secrets()
    status = secrets.secrets_status()

    assert status.brave_api_key_configured is True
    assert status.brave_api_key_source == "env"
    assert status.serper_api_key_configured is True
    assert status.serper_api_key_source == "env"
    assert status.searxng_base_url_configured is True
    assert status.searxng_base_url_source == "env"
    assert secrets.get_brave_api_key() == "b" * 20
    assert secrets.get_serper_api_key() == "s" * 20
    assert secrets.get_searxng_base_url() == "https://searx.example"
    assert not (tmp_path / "secrets.json").exists()


def test_portal_secret_write_apis_disabled(monkeypatch):
    monkeypatch.delenv("BRAVE_API_KEY", raising=False)
    monkeypatch.delenv("SERPER_API_KEY", raising=False)
    monkeypatch.delenv("SEARXNG_BASE_URL", raising=False)

    secrets = _reload_portal_secrets()

    with pytest.raises(RuntimeError, match="Portal secret writes are disabled"):
        secrets.set_brave_api_key("b" * 20)
    with pytest.raises(RuntimeError, match="Portal secret writes are disabled"):
        secrets.clear_brave_api_key()
    with pytest.raises(RuntimeError, match="Portal secret writes are disabled"):
        secrets.set_serper_api_key("s" * 20)
    with pytest.raises(RuntimeError, match="Portal secret writes are disabled"):
        secrets.clear_serper_api_key()
    with pytest.raises(RuntimeError, match="Portal secret writes are disabled"):
        secrets.set_searxng_base_url("https://searx.example")
    with pytest.raises(RuntimeError, match="Portal secret writes are disabled"):
        secrets.clear_searxng_base_url()


def test_state_json_never_persists_secrets_field(tmp_path, monkeypatch):
    monkeypatch.setenv("RESEARCHVAULT_PORTAL_STATE_DIR", str(tmp_path))

    from portal.backend.app.portal_state import set_selected_db_path

    set_selected_db_path(str(tmp_path / "vault.db"))
    payload = json.loads((tmp_path / "state.json").read_text(encoding="utf-8"))

    assert "selected_db_path" in payload
    assert "secrets" not in payload


def test_vault_subprocess_secret_injection_requires_opt_in(tmp_path, monkeypatch):
    monkeypatch.setenv("RESEARCHVAULT_PORTAL_STATE_DIR", str(tmp_path))
    monkeypatch.delenv("RESEARCHVAULT_PORTAL_INJECT_SECRETS", raising=False)
    monkeypatch.setenv("BRAVE_API_KEY", "b" * 20)

    import portal.backend.app.vault_exec as vault_exec

    captured_env = {}

    def fake_run(*args, **kwargs):
        captured_env.update(kwargs["env"])

        class Result:
            returncode = 0
            stdout = ""
            stderr = ""

        return Result()

    monkeypatch.setattr(vault_exec.subprocess, "run", fake_run)

    db_path = str(tmp_path / "vault.db")
    result = vault_exec.run_vault(["list"], timeout_s=1, db_path=db_path)

    assert result.exit_code == 0
    assert captured_env.get("RESEARCHVAULT_DB") == db_path
    assert "BRAVE_API_KEY" not in captured_env


def test_vault_subprocess_secret_injection_enabled_opt_in(tmp_path, monkeypatch):
    monkeypatch.setenv("RESEARCHVAULT_PORTAL_STATE_DIR", str(tmp_path))
    monkeypatch.setenv("RESEARCHVAULT_PORTAL_INJECT_SECRETS", "1")
    monkeypatch.setenv("BRAVE_API_KEY", "b" * 20)

    import portal.backend.app.vault_exec as vault_exec

    captured_env = {}

    def fake_run(*args, **kwargs):
        captured_env.update(kwargs["env"])

        class Result:
            returncode = 0
            stdout = ""
            stderr = ""

        return Result()

    monkeypatch.setattr(vault_exec.subprocess, "run", fake_run)

    db_path = str(tmp_path / "vault.db")
    result = vault_exec.run_vault(["list"], timeout_s=1, db_path=db_path)

    assert result.exit_code == 0
    assert captured_env.get("RESEARCHVAULT_DB") == db_path
    assert captured_env.get("BRAVE_API_KEY") == "b" * 20


def test_scrub_text_redacts_env_and_json_style_secrets():
    from portal.backend.app.vault_exec import scrub_text

    sample = 'BRAVE_API_KEY=abc123 {"api_key":"secret123","token":"tok456"} Authorization: Bearer xyz'
    redacted = scrub_text(sample)

    assert "abc123" not in redacted
    assert "secret123" not in redacted
    assert "tok456" not in redacted
    assert "xyz" not in redacted
