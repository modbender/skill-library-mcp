import json
import os
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

import scripts.core as core
import scripts.db as db


ActionType = Literal["VERIFY_PLAN", "VERIFY_RUN", "SYNTHESIZE", "SCUTTLE"]


@dataclass(frozen=True)
class StrategyConfig:
    # Verification
    verify_threshold: float = 0.7
    max_verification_missions: int = 20
    verify_run_limit: int = 5

    # Synthesis
    synth_threshold: float = 0.78
    synth_top_k: int = 5
    synth_max_links: int = 50

    # Heuristic knobs
    data_density_threshold: int = 8
    coverage_low_threshold: float = 0.25
    findings_low_threshold: int = 3
    max_findings_for_coverage: int = 200


_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "but",
    "by",
    "for",
    "from",
    "has",
    "have",
    "if",
    "in",
    "into",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "then",
    "there",
    "these",
    "this",
    "to",
    "was",
    "were",
    "will",
    "with",
}


def _tokenize(text: str) -> List[str]:
    tokens = re.findall(r"[a-z0-9]{3,}", (text or "").lower())
    return [t for t in tokens if t not in _STOPWORDS]


def _safe_iso_max(*values: Optional[str]) -> Optional[str]:
    best_dt: Optional[datetime] = None
    best_raw: Optional[str] = None
    for raw in values:
        if not raw:
            continue
        try:
            dt = datetime.fromisoformat(raw)
        except Exception:
            continue
        if best_dt is None or dt > best_dt:
            best_dt = dt
            best_raw = raw
    return best_raw


def _parse_iso(raw: Optional[str]) -> Optional[datetime]:
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw)
    except Exception:
        return None


@dataclass(frozen=True)
class ProjectState:
    project_id: str
    project_name: str
    objective: str
    status: str
    priority: int
    branch: str
    branch_id: str

    # Research progress / signals
    findings_count: int
    artifacts_count: int
    avg_confidence: float
    low_confidence_count: int
    unverified_count: int
    low_confidence_examples: List[Dict[str, Any]]

    coverage_score: float
    progress_score: float
    objective_tokens: List[str]
    covered_objective_tokens: List[str]

    # Activity / queues
    events_count: int
    last_event_type: Optional[str]
    last_event_at: Optional[str]
    last_finding_at: Optional[str]
    last_artifact_at: Optional[str]
    last_synthesis_at: Optional[str]

    branches_count: int
    hypotheses_open: int
    hypotheses_accepted: int
    hypotheses_rejected: int

    missions_open: int
    missions_in_progress: int
    missions_blocked: int

    synthesis_links: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project": {
                "id": self.project_id,
                "name": self.project_name,
                "objective": self.objective,
                "status": self.status,
                "priority": self.priority,
            },
            "branch": {"name": self.branch, "id": self.branch_id},
            "metrics": {
                "findings": {
                    "count": self.findings_count,
                    "avg_confidence": self.avg_confidence,
                    "low_confidence_count": self.low_confidence_count,
                    "unverified_count": self.unverified_count,
                    "low_confidence_examples": self.low_confidence_examples,
                    "last_finding_at": self.last_finding_at,
                },
                "artifacts": {"count": self.artifacts_count, "last_artifact_at": self.last_artifact_at},
                "events": {
                    "count": self.events_count,
                    "last_event_type": self.last_event_type,
                    "last_event_at": self.last_event_at,
                    "last_synthesis_at": self.last_synthesis_at,
                },
                "branches": {
                    "count": self.branches_count,
                    "hypotheses": {
                        "open": self.hypotheses_open,
                        "accepted": self.hypotheses_accepted,
                        "rejected": self.hypotheses_rejected,
                    },
                },
                "verification": {
                    "missions": {
                        "open": self.missions_open,
                        "in_progress": self.missions_in_progress,
                        "blocked": self.missions_blocked,
                    }
                },
                "synthesis": {"links": self.synthesis_links},
                "progress": {
                    "coverage_score": self.coverage_score,
                    "progress_score": self.progress_score,
                    "objective_tokens": self.objective_tokens,
                    "covered_objective_tokens": self.covered_objective_tokens,
                },
            },
        }


@dataclass(frozen=True)
class StrategyRecommendation:
    action: ActionType
    title: str
    rationale: List[str]
    suggested_commands: List[str]
    params: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "title": self.title,
            "rationale": list(self.rationale),
            "suggested_commands": list(self.suggested_commands),
            "params": dict(self.params),
        }


@dataclass(frozen=True)
class StrategyExecution:
    action: ActionType
    ok: bool
    details: Dict[str, Any]
    error: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "ok": bool(self.ok),
            "details": dict(self.details),
            "error": self.error or "",
        }


def analyze_project_state(
    project_id: str,
    *,
    branch: Optional[str] = None,
    config: Optional[StrategyConfig] = None,
) -> ProjectState:
    cfg = config or StrategyConfig()
    branch_name = (branch or "main").strip() or "main"

    branch_id = core.resolve_branch_id(project_id, branch_name)

    conn = db.get_connection()
    c = conn.cursor()

    c.execute("SELECT id, name, objective, status, created_at, priority FROM projects WHERE id=?", (project_id,))
    project_row = c.fetchone()
    if not project_row:
        conn.close()
        raise ValueError(f"Project '{project_id}' not found")

    _pid, name, objective, status, _created_at, priority = project_row
    safe_name = str(core.scrub_data(name or project_id))
    safe_objective = str(core.scrub_data(objective or ""))
    safe_status = str(core.scrub_data(status or ""))

    # Findings metrics
    c.execute(
        """SELECT
               COUNT(*),
               AVG(confidence),
               SUM(CASE WHEN confidence < ? THEN 1 ELSE 0 END),
               MAX(created_at)
           FROM findings
           WHERE project_id=? AND branch_id=?""",
        (float(cfg.verify_threshold), project_id, branch_id),
    )
    f_count, f_avg_conf, f_low, last_finding_at = c.fetchone()
    findings_count = int(f_count or 0)
    avg_confidence = float(f_avg_conf or 0.0) if findings_count else 0.0
    low_confidence_count = int(f_low or 0)

    c.execute(
        "SELECT COUNT(*) FROM findings WHERE project_id=? AND branch_id=? AND tags LIKE '%unverified%'",
        (project_id, branch_id),
    )
    unverified_count = int((c.fetchone() or [0])[0] or 0)

    c.execute(
        """SELECT id, title, confidence, tags
           FROM findings
           WHERE project_id=? AND branch_id=? AND (confidence < ? OR tags LIKE '%unverified%')
           ORDER BY confidence ASC, created_at DESC
           LIMIT 5""",
        (project_id, branch_id, float(cfg.verify_threshold)),
    )
    examples: List[Dict[str, Any]] = []
    for fid, title, conf, tags in c.fetchall():
        examples.append(
            {
                "id": fid,
                "title": str(core.scrub_data(title or ""))[:120],
                "confidence": float(conf or 0.0),
                "tags": str(core.scrub_data(tags or ""))[:200],
            }
        )

    # Artifacts metrics
    c.execute(
        "SELECT COUNT(*), MAX(created_at) FROM artifacts WHERE project_id=? AND branch_id=?",
        (project_id, branch_id),
    )
    a_count, last_artifact_at = c.fetchone()
    artifacts_count = int(a_count or 0)

    # Events metrics
    c.execute("SELECT COUNT(*), MAX(timestamp) FROM events WHERE project_id=? AND branch_id=?", (project_id, branch_id))
    e_count, last_event_at = c.fetchone()
    events_count = int(e_count or 0)

    c.execute(
        "SELECT event_type, timestamp FROM events WHERE project_id=? AND branch_id=? ORDER BY id DESC LIMIT 1",
        (project_id, branch_id),
    )
    row = c.fetchone()
    last_event_type = row[0] if row else None

    c.execute(
        "SELECT MAX(timestamp) FROM events WHERE project_id=? AND branch_id=? AND event_type='SYNTHESIS'",
        (project_id, branch_id),
    )
    last_synthesis_at = (c.fetchone() or [None])[0]

    # Branch / hypothesis metrics (project-wide branches, branch-scoped hypotheses)
    c.execute("SELECT COUNT(*) FROM branches WHERE project_id=?", (project_id,))
    branches_count = int((c.fetchone() or [0])[0] or 0)

    c.execute(
        """SELECT h.status, COUNT(*)
           FROM hypotheses h
           WHERE h.branch_id=?
           GROUP BY h.status""",
        (branch_id,),
    )
    hyp_counts: Dict[str, int] = {str(status): int(cnt) for status, cnt in c.fetchall()}
    hypotheses_open = int(hyp_counts.get("open", 0))
    hypotheses_accepted = int(hyp_counts.get("accepted", 0))
    hypotheses_rejected = int(hyp_counts.get("rejected", 0))

    # Verification queue metrics
    c.execute(
        """SELECT status, COUNT(*)
           FROM verification_missions
           WHERE project_id=? AND branch_id=?
           GROUP BY status""",
        (project_id, branch_id),
    )
    mission_counts: Dict[str, int] = {str(status): int(cnt) for status, cnt in c.fetchall()}
    missions_open = int(mission_counts.get("open", 0))
    missions_in_progress = int(mission_counts.get("in_progress", 0))
    missions_blocked = int(mission_counts.get("blocked", 0))

    # Synthesis link count (best-effort; branch_id lives in metadata JSON).
    like_pat = f'%"branch_id": "{branch_id}"%'
    c.execute(
        "SELECT COUNT(*) FROM links WHERE link_type='SYNTHESIS_SIMILARITY' AND metadata LIKE ?",
        (like_pat,),
    )
    synthesis_links = int((c.fetchone() or [0])[0] or 0)

    # Objective coverage: tokenize objective and compare to recent findings.
    objective_tokens_set = set(_tokenize(safe_objective))
    objective_tokens = sorted(objective_tokens_set)
    findings_tokens: set[str] = set()
    if objective_tokens_set:
        c.execute(
            """SELECT title, content, tags
               FROM findings
               WHERE project_id=? AND branch_id=?
               ORDER BY created_at DESC
               LIMIT ?""",
            (project_id, branch_id, int(cfg.max_findings_for_coverage)),
        )
        for title, content, tags in c.fetchall():
            findings_tokens.update(_tokenize(str(title or "")))
            findings_tokens.update(_tokenize(str(content or "")))
            findings_tokens.update(_tokenize(str(tags or "")))

    covered = sorted(objective_tokens_set.intersection(findings_tokens))
    if not objective_tokens_set:
        # Treat empty/untokenizable objectives as "coverage unknown" rather than zero.
        coverage_score = 1.0
    else:
        coverage_score = float(len(covered)) / float(len(objective_tokens_set))

    # Progress score: weighted blend of coverage, evidence density, and confidence.
    density = findings_count + artifacts_count
    density_score = min(1.0, float(density) / 20.0)
    confidence_score = avg_confidence
    coverage_score = max(0.0, min(1.0, float(coverage_score)))
    # Penalize for unresolved verification queue.
    queue_penalty = min(0.25, float(missions_open + missions_blocked) / 40.0)
    progress_score = (0.45 * coverage_score) + (0.35 * density_score) + (0.20 * confidence_score) - queue_penalty
    progress_score = max(0.0, min(1.0, float(progress_score)))

    conn.close()
    return ProjectState(
        project_id=project_id,
        project_name=safe_name,
        objective=safe_objective,
        status=safe_status,
        priority=int(priority or 0),
        branch=branch_name,
        branch_id=branch_id,
        findings_count=findings_count,
        artifacts_count=artifacts_count,
        avg_confidence=avg_confidence,
        low_confidence_count=int(low_confidence_count),
        unverified_count=int(unverified_count),
        low_confidence_examples=examples,
        coverage_score=coverage_score,
        progress_score=progress_score,
        objective_tokens=objective_tokens,
        covered_objective_tokens=covered,
        events_count=events_count,
        last_event_type=str(core.scrub_data(last_event_type)) if last_event_type else None,
        last_event_at=last_event_at,
        last_finding_at=last_finding_at,
        last_artifact_at=last_artifact_at,
        last_synthesis_at=last_synthesis_at,
        branches_count=branches_count,
        hypotheses_open=hypotheses_open,
        hypotheses_accepted=hypotheses_accepted,
        hypotheses_rejected=hypotheses_rejected,
        missions_open=missions_open,
        missions_in_progress=missions_in_progress,
        missions_blocked=missions_blocked,
        synthesis_links=synthesis_links,
    )


def recommend_next_best_action(
    state: ProjectState,
    *,
    config: Optional[StrategyConfig] = None,
) -> StrategyRecommendation:
    cfg = config or StrategyConfig()

    # Rule 1: confidence is low -> verification
    has_low_confidence = (state.low_confidence_count + state.unverified_count) > 0
    has_open_queue = (state.missions_open + state.missions_in_progress + state.missions_blocked) > 0
    brave_available = bool(os.environ.get("BRAVE_API_KEY"))
    serper_available = bool(os.environ.get("SERPER_API_KEY"))
    searxng_available = bool(os.environ.get("SEARXNG_BASE_URL"))

    if has_low_confidence:
        if not has_open_queue:
            rationale = [
                f"Low-confidence/unverified findings detected (low_conf={state.low_confidence_count}, unverified={state.unverified_count}).",
                "No verification missions exist yet for this branch.",
            ]
            cmds = [
                f"vault verify plan --id {state.project_id} --branch {state.branch} --threshold {cfg.verify_threshold} --max {cfg.max_verification_missions}",
                f"vault verify list --id {state.project_id} --branch {state.branch} --status open",
            ]
            return StrategyRecommendation(
                action="VERIFY_PLAN",
                title="Initiate verification planning",
                rationale=rationale,
                suggested_commands=cmds,
                params={
                    "threshold": float(cfg.verify_threshold),
                    "max_missions": int(cfg.max_verification_missions),
                },
            )

        rationale = [
            f"Verification queue exists (open={state.missions_open}, in_progress={state.missions_in_progress}, blocked={state.missions_blocked}).",
        ]
        if not brave_available and not serper_available and not searxng_available:
            rationale.append(
                "No key-based search provider configured; missions will fall back to DuckDuckGo/Wikipedia (best-effort). Configure Brave for higher quality and consistency."
            )

        cmds = [
            f"vault verify run --id {state.project_id} --branch {state.branch} --limit {cfg.verify_run_limit}",
            f"vault verify list --id {state.project_id} --branch {state.branch} --limit 20",
        ]
        return StrategyRecommendation(
            action="VERIFY_RUN",
            title="Execute verification missions",
            rationale=rationale,
            suggested_commands=cmds,
            params={"limit": int(cfg.verify_run_limit)},
        )

    # Rule 2: data density is high or new data since last synthesis -> synthesis
    density = state.findings_count + state.artifacts_count
    last_material_change = _safe_iso_max(state.last_finding_at, state.last_artifact_at)
    syn_dt = _parse_iso(state.last_synthesis_at)
    material_dt = _parse_iso(last_material_change)
    synthesis_out_of_date = (material_dt is not None) and (syn_dt is None or syn_dt < material_dt)

    if density >= int(cfg.data_density_threshold) and synthesis_out_of_date:
        rationale = [
            f"Data density is high (findings={state.findings_count}, artifacts={state.artifacts_count}).",
            "New material exists since last synthesis run.",
        ]
        cmds = [
            f"vault synthesize --id {state.project_id} --branch {state.branch} --threshold {cfg.synth_threshold} --top-k {cfg.synth_top_k} --max-links {cfg.synth_max_links}",
        ]
        return StrategyRecommendation(
            action="SYNTHESIZE",
            title="Run synthesis to discover cross-links",
            rationale=rationale,
            suggested_commands=cmds,
            params={
                "threshold": float(cfg.synth_threshold),
                "top_k": int(cfg.synth_top_k),
                "max_links": int(cfg.synth_max_links),
            },
        )

    # Rule 3: insufficient evidence or low objective coverage -> scuttle
    if state.findings_count < int(cfg.findings_low_threshold) or state.coverage_score < float(cfg.coverage_low_threshold):
        kws = (state.objective_tokens or [])[:8]
        kw_preview = " ".join(kws).strip()
        rationale = [
            f"Evidence is thin or coverage is low (findings={state.findings_count}, coverage={state.coverage_score:.2f}).",
            "Ingest more primary sources aligned to the objective.",
        ]
        cmds = [
            f"vault scuttle <URL> --id {state.project_id} --branch {state.branch}",
        ]
        if kw_preview:
            cmds.append(
                f"vault watch add --id {state.project_id} --branch {state.branch} --type query --target \"{kw_preview}\" --interval 21600"
            )
        return StrategyRecommendation(
            action="SCUTTLE",
            title="Increase signal with targeted ingestion",
            rationale=rationale,
            suggested_commands=cmds,
            params={"suggested_keywords": kws},
        )

    # Fallback: if there's enough material, synthesis is still the safest consolidation move.
    if density >= 2 and syn_dt is None:
        cmds = [
            f"vault synthesize --id {state.project_id} --branch {state.branch} --threshold {cfg.synth_threshold} --top-k {cfg.synth_top_k} --max-links {cfg.synth_max_links}",
        ]
        return StrategyRecommendation(
            action="SYNTHESIZE",
            title="Bootstrap synthesis map",
            rationale=["Sufficient material exists but synthesis has not been run yet."],
            suggested_commands=cmds,
            params={
                "threshold": float(cfg.synth_threshold),
                "top_k": int(cfg.synth_top_k),
                "max_links": int(cfg.synth_max_links),
            },
        )

    cmds = [f"vault scuttle <URL> --id {state.project_id} --branch {state.branch}"]
    return StrategyRecommendation(
        action="SCUTTLE",
        title="Continue ingestion",
        rationale=["No urgent verification or synthesis triggers detected; continue gathering evidence."],
        suggested_commands=cmds,
        params={},
    )


def execute_recommendation(
    project_id: str,
    recommendation: StrategyRecommendation,
    *,
    branch: Optional[str] = None,
    config: Optional[StrategyConfig] = None,
) -> StrategyExecution:
    cfg = config or StrategyConfig()
    branch_name = (branch or "main").strip() or "main"

    if recommendation.action == "VERIFY_PLAN":
        missions = core.plan_verification_missions(
            project_id,
            branch=branch_name,
            threshold=float(cfg.verify_threshold),
            max_missions=int(cfg.max_verification_missions),
        )
        return StrategyExecution(
            action=recommendation.action,
            ok=True,
            details={"missions_created": len(missions), "missions": missions[:10]},
        )

    if recommendation.action == "VERIFY_RUN":
        results = core.run_verification_missions(
            project_id,
            branch=branch_name,
            limit=int(cfg.verify_run_limit),
        )
        # Only report ok=True if all missions completed successfully (status="done")
        ok = bool(results) and all(
            isinstance(r, dict) and r.get("status") == "done" for r in results
        )
        return StrategyExecution(
            action=recommendation.action,
            ok=ok,
            details={"missions_executed": len(results), "results": results},
        )

    if recommendation.action == "SYNTHESIZE":
        from scripts.synthesis import synthesize

        links = synthesize(
            project_id,
            branch=branch_name,
            threshold=float(cfg.synth_threshold),
            top_k=int(cfg.synth_top_k),
            max_links=int(cfg.synth_max_links),
            persist=True,
        )
        return StrategyExecution(
            action=recommendation.action,
            ok=True,
            details={"links_created": len(links), "links": links[:10]},
        )

    if recommendation.action == "SCUTTLE":
        return StrategyExecution(
            action=recommendation.action,
            ok=False,
            details={},
            error="SCUTTLE is not auto-executable; provide a URL or add watch targets.",
        )

    return StrategyExecution(
        action=recommendation.action,
        ok=False,
        details={},
        error=f"Unknown action: {recommendation.action}",
    )


def strategize(
    project_id: str,
    *,
    branch: Optional[str] = None,
    config: Optional[StrategyConfig] = None,
    execute: bool = False,
) -> Dict[str, Any]:
    cfg = config or StrategyConfig()
    state = analyze_project_state(project_id, branch=branch, config=cfg)
    rec = recommend_next_best_action(state, config=cfg)
    out: Dict[str, Any] = {
        "state": state.to_dict(),
        "recommendation": rec.to_dict(),
    }
    if execute:
        ex = execute_recommendation(project_id, rec, branch=branch, config=cfg)
        out["execution"] = ex.to_dict()
    return json.loads(json.dumps(out, ensure_ascii=True))
