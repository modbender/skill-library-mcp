import importlib


def _reload_portal_main(monkeypatch, cors_env: str | None = None):
    # Keep startup deterministic and local for tests.
    if cors_env is None:
        monkeypatch.delenv("RESEARCHVAULT_PORTAL_CORS_ORIGINS", raising=False)
    else:
        monkeypatch.setenv("RESEARCHVAULT_PORTAL_CORS_ORIGINS", cors_env)
    import portal.backend.app.main as main_mod

    return importlib.reload(main_mod)


def test_cors_defaults_include_localhost_and_127(monkeypatch):
    main_mod = _reload_portal_main(monkeypatch)
    origins = set(main_mod._cors_origins_from_env())
    assert "http://localhost:5173" in origins
    assert "http://127.0.0.1:5173" in origins


def test_cors_middleware_allows_credentials_for_local_origins(monkeypatch):
    main_mod = _reload_portal_main(monkeypatch)
    cors_layer = next(m for m in main_mod.app.user_middleware if m.cls.__name__ == "CORSMiddleware")
    origins = set(cors_layer.kwargs.get("allow_origins", []))
    assert "http://localhost:5173" in origins
    assert "http://127.0.0.1:5173" in origins
    assert cors_layer.kwargs.get("allow_credentials") is True
