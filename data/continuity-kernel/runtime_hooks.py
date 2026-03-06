from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional

from diagnostics import FailOpenDiagnostics
from injector import ContinuityInjector
from service import ContinuityRuntimeService
from store import ContinuityStore


DEFAULT_DB_PATH_ENV = "CONTINUITY_KERNEL_DB_PATH"
DEFAULT_DB_PATH = Path.home() / ".local" / "state" / "continuity-kernel" / "continuity.db"


class ContinuityHookAdapter:
    """Thin wrapper exposing the OpenClaw-style llm_input hook boundary.

    Backed by ContinuityRuntimeService to keep runtime behavior reusable across
    direct hook wiring, integration tests, and future plugin surfaces.
    """

    def __init__(
        self,
        store: Optional[ContinuityStore] = None,
        token_budget: int = 220,
        diagnostics: Optional[FailOpenDiagnostics] = None,
        injector: Optional[ContinuityInjector] = None,
        auto_migrate: bool = True,
        service: Optional[ContinuityRuntimeService] = None,
        db_path: str | None = None,
    ):
        if service is not None:
            self.service = service
            self.diagnostics = getattr(service, "diagnostics", diagnostics or FailOpenDiagnostics())
            return

        diagnostics = diagnostics or getattr(store, "diagnostics", None) or FailOpenDiagnostics()
        store = store or self._default_store(diagnostics=diagnostics, db_path=db_path)
        injector = injector or ContinuityInjector(
            store,
            token_budget=token_budget,
            diagnostics=diagnostics,
        )
        self.service = ContinuityRuntimeService(
            repository=store,
            packet_builder=injector,
            diagnostics=diagnostics,
            auto_migrate=auto_migrate,
        )
        self.diagnostics = diagnostics

    @classmethod
    def _resolve_default_db_path(cls, db_path: str | None = None) -> str:
        if isinstance(db_path, str) and db_path.strip():
            return db_path.strip()

        env_path = os.environ.get(DEFAULT_DB_PATH_ENV, "").strip()
        if env_path:
            return env_path

        return str(DEFAULT_DB_PATH)

    @classmethod
    def _default_store(cls, diagnostics: FailOpenDiagnostics, db_path: str | None = None) -> ContinuityStore:
        resolved = cls._resolve_default_db_path(db_path=db_path)
        if resolved == ":memory:":
            return ContinuityStore(resolved, diagnostics=diagnostics)

        expanded = Path(resolved).expanduser()
        try:
            expanded.parent.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            diagnostics.emit(
                component="runtime_hooks",
                code="default_db_parent_mkdir_error",
                detail="Failed to create default continuity DB parent directory.",
                context={"db_path": str(expanded), "error": str(exc)},
            )
        return ContinuityStore(str(expanded), diagnostics=diagnostics)

    @classmethod
    def from_db_path(
        cls,
        db_path: str,
        token_budget: int = 220,
        diagnostics: Optional[FailOpenDiagnostics] = None,
        auto_migrate: bool = True,
    ) -> "ContinuityHookAdapter":
        service = ContinuityRuntimeService.from_db_path(
            db_path=db_path,
            token_budget=token_budget,
            diagnostics=diagnostics,
            auto_migrate=auto_migrate,
        )
        return cls(service=service)

    def on_llm_input(self, agent_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self.service.inject_llm_input(agent_id, payload)
