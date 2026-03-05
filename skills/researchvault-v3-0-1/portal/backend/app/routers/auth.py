from __future__ import annotations

import os
from fastapi import APIRouter, Response, Depends, Cookie
from pydantic import BaseModel

from portal.backend.app.auth import (
    SESSION_COOKIE_NAME,
    create_session,
    revoke_session,
    require_session,
)

router = APIRouter()


class LoginRequest(BaseModel):
    token: str


@router.post("/auth/login")
def login(req: LoginRequest, response: Response):
    sid = create_session(req.token)

    secure_cookie = os.getenv("RESEARCHVAULT_PORTAL_COOKIE_SECURE", "false").lower() == "true"

    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=sid,
        httponly=True,
        secure=secure_cookie,
        samesite="lax",
        max_age=12 * 60 * 60,
        path="/",
    )
    return {"ok": True}


@router.post("/auth/logout", dependencies=[Depends(require_session)])
def logout(
    response: Response,
    rv_session: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
):
    # Best-effort; cookie will be cleared regardless.
    if rv_session:
        revoke_session(rv_session)
    response.delete_cookie(key=SESSION_COOKIE_NAME, path="/")
    return {"ok": True}


@router.get("/auth/status")
def status_check(authed: None = Depends(require_session)):
    return {"ok": True}
