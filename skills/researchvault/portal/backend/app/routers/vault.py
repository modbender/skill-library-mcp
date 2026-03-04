from __future__ import annotations

import json
from typing import Optional, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from portal.backend.app.auth import require_session
from portal.backend.app.db_resolver import resolve_effective_db
from portal.backend.app.vault_exec import run_vault


router = APIRouter(prefix="/vault", dependencies=[Depends(require_session)])


def _run(args: list[str], *, timeout_s: int = 60):
    resolved = resolve_effective_db()
    res = run_vault(args, timeout_s=timeout_s, db_path=resolved.path)
    return {
        "argv": res.argv,
        "exit_code": res.exit_code,
        "stdout": res.stdout,
        "stderr": res.stderr,
        "truncated": res.truncated,
        "ok": res.exit_code == 0,
        "db_path": resolved.path,
        "db_source": resolved.source,
        "db_note": resolved.note,
    }


class InitRequest(BaseModel):
    id: Optional[str] = None
    objective: str = Field(min_length=1, max_length=5000)
    name: Optional[str] = Field(default=None, max_length=500)
    priority: int = Field(default=0, ge=0, le=100)


@router.post("/init")
def vault_init(req: InitRequest):
    # Handle empty string from frontend
    project_id = req.id if req.id and req.id.strip() else None
    
    args = ["init", "--objective", req.objective, "--priority", str(req.priority)]
    if project_id:
        args += ["--id", project_id]
    if req.name:
        args += ["--name", req.name]
    return _run(args)


@router.get("/list")
def vault_list():
    # Portal needs structured data for the Entry Screen project table.
    # The CLI remains the single source of truth; we request JSON output.
    return _run(["list", "--format", "json"], timeout_s=30)


class UpdateRequest(BaseModel):
    id: str
    status: Optional[Literal["active", "paused", "completed", "failed"]] = None
    priority: Optional[int] = Field(default=None, ge=0, le=100)


@router.post("/update")
def vault_update(req: UpdateRequest):
    args = ["update", "--id", req.id]
    if req.status:
        args += ["--status", req.status]
    if req.priority is not None:
        args += ["--priority", str(req.priority)]
    return _run(args)


class StatusRequest(BaseModel):
    id: str
    filter_tag: Optional[str] = None
    branch: Optional[str] = None
    format: Literal["rich", "json"] = "rich"
    insights_limit: int = Field(default=50, ge=1, le=500)


@router.post("/status")
def vault_status(req: StatusRequest):
    args = ["status", "--id", req.id]
    if req.filter_tag:
        args += ["--filter-tag", req.filter_tag]
    if req.branch:
        args += ["--branch", req.branch]
    args += ["--insights-limit", str(req.insights_limit)]
    # Ensure format is always passed
    fmt = req.format if req.format else "json"
    args += ["--format", fmt]
    return _run(args)


class SummaryRequest(BaseModel):
    id: str
    branch: Optional[str] = None
    format: Literal["rich", "json"] = "rich"


@router.post("/summary")
def vault_summary(req: SummaryRequest):
    args = ["summary", "--id", req.id]
    if req.branch:
        args += ["--branch", req.branch]
    args += ["--format", req.format]
    return _run(args)


class LogRequest(BaseModel):
    id: str
    type: str
    step: int = 0
    payload: dict = Field(default_factory=dict)
    conf: float = Field(default=1.0, ge=0.0, le=1.0)
    source: str = "portal"
    tags: str = ""
    branch: Optional[str] = None


@router.post("/log")
def vault_log(req: LogRequest):
    args = [
        "log",
        "--id",
        req.id,
        "--type",
        req.type,
        "--step",
        str(req.step),
        "--payload",
        json.dumps(req.payload),
        "--conf",
        str(req.conf),
        "--source",
        req.source,
        "--tags",
        req.tags,
    ]
    if req.branch:
        args += ["--branch", req.branch]
    return _run(args)


class SearchRequest(BaseModel):
    query: str
    set_result: Optional[dict | str] = None
    format: Literal["rich", "json"] = "json"


@router.post("/search")
def vault_search(req: SearchRequest):
    args = ["search", "--query", req.query]
    if req.set_result is not None:
        if isinstance(req.set_result, str):
            args += ["--set-result", req.set_result]
        else:
            args += ["--set-result", json.dumps(req.set_result)]
    args += ["--format", req.format]
    return _run(args, timeout_s=60)


class ScuttleRequest(BaseModel):
    id: str
    url: str
    tags: str = ""
    branch: Optional[str] = None
    allow_private_networks: bool = False


@router.post("/scuttle")
def vault_scuttle(req: ScuttleRequest):
    args = ["scuttle", req.url, "--id", req.id]
    if req.tags:
        args += ["--tags", req.tags]
    if req.branch:
        args += ["--branch", req.branch]
    if req.allow_private_networks:
        args.append("--allow-private-networks")
    return _run(args, timeout_s=120)


class InsightAddRequest(BaseModel):
    id: str
    title: str
    content: str
    url: str = ""
    tags: str = ""
    conf: float = Field(default=1.0, ge=0.0, le=1.0)
    branch: Optional[str] = None


@router.post("/insight/add")
def vault_insight_add(req: InsightAddRequest):
    args = [
        "insight",
        "--id",
        req.id,
        "--add",
        "--title",
        req.title,
        "--content",
        req.content,
        "--url",
        req.url,
        "--tags",
        req.tags,
        "--conf",
        str(req.conf),
    ]
    if req.branch:
        args += ["--branch", req.branch]
    return _run(args)


class InsightListRequest(BaseModel):
    id: str
    filter_tag: Optional[str] = None
    branch: Optional[str] = None
    format: Literal["rich", "json"] = "rich"
    limit: int = Field(default=200, ge=1, le=1000)


@router.post("/insight/list")
def vault_insight_list(req: InsightListRequest):
    args = ["insight", "--id", req.id]
    if req.filter_tag:
        args += ["--filter-tag", req.filter_tag]
    if req.branch:
        args += ["--branch", req.branch]
    args += ["--limit", str(req.limit)]
    args += ["--format", req.format]
    return _run(args)


class ExportRequest(BaseModel):
    id: str
    format: Literal["json", "markdown"] = "json"
    branch: Optional[str] = None


@router.post("/export")
def vault_export(req: ExportRequest):
    # Portal does not write files; it returns stdout.
    args = ["export", "--id", req.id, "--format", req.format]
    if req.branch:
        args += ["--branch", req.branch]
    return _run(args, timeout_s=60)


class VerifyPlanRequest(BaseModel):
    id: str
    branch: Optional[str] = None
    threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    max: int = Field(default=20, ge=1, le=200)
    format: Literal["rich", "json"] = "rich"


@router.post("/verify/plan")
def vault_verify_plan(req: VerifyPlanRequest):
    args = ["verify", "plan", "--id", req.id, "--threshold", str(req.threshold), "--max", str(req.max)]
    if req.branch:
        args += ["--branch", req.branch]
    args += ["--format", req.format]
    return _run(args)


class VerifyListRequest(BaseModel):
    id: str
    branch: Optional[str] = None
    status: Optional[Literal["open", "in_progress", "done", "blocked", "cancelled"]] = None
    limit: int = Field(default=50, ge=1, le=200)
    format: Literal["rich", "json"] = "rich"


@router.post("/verify/list")
def vault_verify_list(req: VerifyListRequest):
    args = ["verify", "list", "--id", req.id, "--limit", str(req.limit)]
    if req.branch:
        args += ["--branch", req.branch]
    if req.status:
        args += ["--status", req.status]
    args += ["--format", req.format]
    return _run(args)


class VerifyRunRequest(BaseModel):
    id: str
    branch: Optional[str] = None
    status: Literal["open", "blocked"] = "open"
    limit: int = Field(default=5, ge=1, le=50)
    format: Literal["rich", "json"] = "rich"


@router.post("/verify/run")
def vault_verify_run(req: VerifyRunRequest):
    args = ["verify", "run", "--id", req.id, "--status", req.status, "--limit", str(req.limit)]
    if req.branch:
        args += ["--branch", req.branch]
    args += ["--format", req.format]
    return _run(args, timeout_s=120)


class VerifyCompleteRequest(BaseModel):
    mission: str
    status: Literal["done", "cancelled", "open"] = "done"
    note: str = ""


@router.post("/verify/complete")
def vault_verify_complete(req: VerifyCompleteRequest):
    args = ["verify", "complete", "--mission", req.mission, "--status", req.status, "--note", req.note]
    return _run(args)


class WatchAddRequest(BaseModel):
    id: str
    type: Literal["url", "query"]
    target: str
    interval: int = Field(default=3600, ge=60, le=7 * 24 * 3600)
    tags: str = ""
    branch: Optional[str] = None


@router.post("/watch/add")
def vault_watch_add(req: WatchAddRequest):
    args = [
        "watch",
        "add",
        "--id",
        req.id,
        "--type",
        req.type,
        "--target",
        req.target,
        "--interval",
        str(req.interval),
        "--tags",
        req.tags,
    ]
    if req.branch:
        args += ["--branch", req.branch]
    return _run(args)


class WatchListRequest(BaseModel):
    id: str
    branch: Optional[str] = None
    status: Literal["active", "disabled", "all"] = "active"


@router.post("/watch/list")
def vault_watch_list(req: WatchListRequest):
    args = ["watch", "list", "--id", req.id, "--status", req.status]
    if req.branch:
        args += ["--branch", req.branch]
    return _run(args)


class WatchDisableRequest(BaseModel):
    target_id: str


@router.post("/watch/disable")
def vault_watch_disable(req: WatchDisableRequest):
    args = ["watch", "disable", "--target-id", req.target_id]
    return _run(args)


class WatchdogOnceRequest(BaseModel):
    id: Optional[str] = None
    branch: Optional[str] = None
    limit: int = Field(default=10, ge=1, le=100)
    dry_run: bool = False


@router.post("/watchdog/once")
def vault_watchdog_once(req: WatchdogOnceRequest):
    args = ["watchdog", "--once", "--limit", str(req.limit)]
    if req.dry_run:
        args.append("--dry-run")
    if req.id:
        args += ["--id", req.id]
    if req.branch:
        args += ["--branch", req.branch]
    return _run(args, timeout_s=120)


class BranchCreateRequest(BaseModel):
    id: str
    name: str
    from_branch: Optional[str] = Field(default=None, alias="from")
    hypothesis: str = ""


@router.post("/branch/create")
def vault_branch_create(req: BranchCreateRequest):
    args = ["branch", "create", "--id", req.id, "--name", req.name]
    if req.from_branch:
        args += ["--from", req.from_branch]
    if req.hypothesis:
        args += ["--hypothesis", req.hypothesis]
    return _run(args)


class BranchListRequest(BaseModel):
    id: str
    format: Literal["rich", "json"] = "rich"


@router.post("/branch/list")
def vault_branch_list(req: BranchListRequest):
    args = ["branch", "list", "--id", req.id]
    args += ["--format", req.format]
    return _run(args)


class HypothesisAddRequest(BaseModel):
    id: str
    branch: str = "main"
    statement: str
    rationale: str = ""
    conf: float = Field(default=0.5, ge=0.0, le=1.0)
    status: Literal["open", "accepted", "rejected", "archived"] = "open"


@router.post("/hypothesis/add")
def vault_hypothesis_add(req: HypothesisAddRequest):
    args = [
        "hypothesis",
        "add",
        "--id",
        req.id,
        "--branch",
        req.branch,
        "--statement",
        req.statement,
        "--rationale",
        req.rationale,
        "--conf",
        str(req.conf),
        "--status",
        req.status,
    ]
    return _run(args)


class HypothesisListRequest(BaseModel):
    id: str
    branch: Optional[str] = None
    format: Literal["rich", "json"] = "rich"


@router.post("/hypothesis/list")
def vault_hypothesis_list(req: HypothesisListRequest):
    args = ["hypothesis", "list", "--id", req.id]
    if req.branch:
        args += ["--branch", req.branch]
    args += ["--format", req.format]
    return _run(args)


class ArtifactAddRequest(BaseModel):
    id: str
    path: str
    type: str = "FILE"
    metadata: dict = Field(default_factory=dict)
    branch: Optional[str] = None


@router.post("/artifact/add")
def vault_artifact_add(req: ArtifactAddRequest):
    args = [
        "artifact",
        "add",
        "--id",
        req.id,
        "--path",
        req.path,
        "--type",
        req.type,
        "--metadata",
        json.dumps(req.metadata),
    ]
    if req.branch:
        args += ["--branch", req.branch]
    return _run(args)


class ArtifactListRequest(BaseModel):
    id: str
    branch: Optional[str] = None
    format: Literal["rich", "json"] = "rich"


@router.post("/artifact/list")
def vault_artifact_list(req: ArtifactListRequest):
    args = ["artifact", "list", "--id", req.id]
    if req.branch:
        args += ["--branch", req.branch]
    args += ["--format", req.format]
    return _run(args)


class StrategyRequest(BaseModel):
    id: str
    branch: Optional[str] = None
    execute: bool = False
    format: Literal["rich", "json"] = "rich"


@router.post("/strategy")
def vault_strategy(req: StrategyRequest):
    args = ["strategy", "--id", req.id]
    if req.branch:
        args += ["--branch", req.branch]
    if req.execute:
        args.append("--execute")
    args += ["--format", req.format]
    return _run(args, timeout_s=120)


class SynthesizeRequest(BaseModel):
    id: str
    branch: Optional[str] = None
    threshold: float = Field(default=0.65, ge=0.0, le=1.0)
    top_k: int = Field(default=5, ge=1, le=50)
    max_links: int = Field(default=50, ge=1, le=500)
    format: Literal["rich", "json"] = "rich"


@router.post("/synthesize")
def vault_synthesize(req: SynthesizeRequest):
    args = [
        "synthesize",
        "--id",
        req.id,
        "--threshold",
        str(req.threshold),
        "--top-k",
        str(req.top_k),
        "--max-links",
        str(req.max_links),
        "--format",
        req.format,
    ]
    if req.branch:
        args += ["--branch", req.branch]
    return _run(args, timeout_s=120)
