import os
from contextlib import asynccontextmanager
from importlib.metadata import PackageNotFoundError, version as pkg_version

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from portal.backend.app.routers import auth as auth_router
from portal.backend.app.routers import system as system_router
from portal.backend.app.routers import vault as vault_router
from portal.backend.app.vault_exec import run_vault


def _cors_origins_from_env() -> list[str]:
    raw = os.getenv(
        "RESEARCHVAULT_PORTAL_CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    )
    origins = [o.strip() for o in raw.split(",") if o.strip()]
    return origins


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure DB exists/migrated via the CLI (single source of truth).
    try:
        run_vault(["list"], timeout_s=30)
    except Exception as e:
        # Keep startup resilient; portal can still start even if vault init fails.
        print(f"Vault initialization via CLI failed: {e}")
    yield


app = FastAPI(title="ResearchVault Portal", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins_from_env(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(auth_router.router, prefix="/api", tags=["auth"])
app.include_router(system_router.router, prefix="/api", tags=["system"])
app.include_router(vault_router.router, prefix="/api", tags=["vault"])


def _app_version() -> str:
    try:
        return str(pkg_version("researchvault"))
    except PackageNotFoundError:
        return "unknown"


@app.get("/health")
def health_check():
    return {"status": "ok", "version": _app_version()}
