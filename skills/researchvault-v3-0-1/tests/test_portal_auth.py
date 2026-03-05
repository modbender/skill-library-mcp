import pytest

from fastapi import HTTPException
from fastapi import Response


def test_stateless_session_cookie_roundtrip(monkeypatch):
    import portal.backend.app.auth as auth

    monkeypatch.setenv("RESEARCHVAULT_PORTAL_TOKEN", "t0k3n")

    sid = auth.create_session("t0k3n")
    assert isinstance(sid, str) and "." in sid

    # Should not raise.
    auth.require_session(rv_session=sid)


def test_stateless_session_cookie_expires(monkeypatch):
    import portal.backend.app.auth as auth

    monkeypatch.setenv("RESEARCHVAULT_PORTAL_TOKEN", "t0k3n")

    now = 1_000_000
    monkeypatch.setattr(auth.time, "time", lambda: now)

    sid = auth.create_session("t0k3n")
    auth.require_session(rv_session=sid)

    now = now + auth.SESSION_TTL_S + 1
    monkeypatch.setattr(auth.time, "time", lambda: now)

    with pytest.raises(HTTPException) as e:
        auth.require_session(rv_session=sid)
    assert "expired" in str(e.value.detail).lower()


def test_login_cookie_is_host_only_and_lax(monkeypatch):
    from portal.backend.app.routers.auth import LoginRequest, login

    monkeypatch.setenv("RESEARCHVAULT_PORTAL_TOKEN", "t0k3n")

    response = Response()
    payload = LoginRequest(token="t0k3n")
    out = login(payload, response)
    assert out == {"ok": True}

    set_cookie = response.headers.get("set-cookie", "").lower()
    assert "domain=" not in set_cookie
    assert "samesite=lax" in set_cookie


def test_missing_portal_token_is_rejected(monkeypatch):
    import portal.backend.app.auth as auth

    monkeypatch.delenv("RESEARCHVAULT_PORTAL_TOKEN", raising=False)

    with pytest.raises(HTTPException) as e:
        auth.create_session("anything")

    assert "not configured" in str(e.value.detail).lower()
