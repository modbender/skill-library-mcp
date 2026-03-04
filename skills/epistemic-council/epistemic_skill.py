"""
epistemic_skill.py — OpenClaw skill entry point for Epistemic Council v2.0

OpenClaw invokes this file when a trigger phrase is matched.
All skill entrypoints are routed through dispatch().

Workspace access: READ_WRITE (set in skill.json + workspace.json)
Shell access: enabled (runs run.py, substrate_health.py, etc.)

Available triggers and what they do:
  "run council" / "run pipeline"    → full pipeline run (run.py)
  "substrate status" / "council status" → health check
  "analyze cross-domain"            → detection only (no new claims)
  "find analogies"                  → same as analyze
  "validate claims"                 → validate_claim.py
  "check boundaries"                → boundary_audit.py
  "find gaps"                       → evidence_search.py
  "rechallenge"                     → adversarial_rechallenge.py
"""

import os
import sys
import json
import subprocess
import logging
from pathlib import Path
from datetime import datetime

# ── Path setup ─────────────────────────────────────────────────────────────
SKILL_DIR   = Path(__file__).parent.resolve()          # epistemic_council/
WORKSPACE   = SKILL_DIR.parent.resolve()               # workspace root
MEMORY_DIR  = SKILL_DIR / "memory"
STATE_FILE  = MEMORY_DIR / "heartbeat-state.json"
DB_PATH     = SKILL_DIR / "epistemic.db"

if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))

from substrate import Substrate, EventType

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("epistemic_skill")


# ── Helpers ─────────────────────────────────────────────────────────────────

def _substrate() -> Substrate:
    return Substrate(str(DB_PATH))


def _load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {}


def _save_state(state: dict):
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def _run_script(script_name: str, extra_args: list = None) -> tuple[int, str]:
    """Run a task script in the epistemic_council directory. Returns (returncode, output)."""
    cmd = [sys.executable, str(SKILL_DIR / script_name)] + (extra_args or [])
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(SKILL_DIR),
            timeout=300,
        )
        output = result.stdout + (("\n[stderr] " + result.stderr) if result.stderr.strip() else "")
        return result.returncode, output.strip()
    except subprocess.TimeoutExpired:
        return 1, f"[timeout] {script_name} exceeded 300s"
    except Exception as e:
        return 1, f"[error] {script_name}: {e}"


def _query_for_index(index: int) -> str:
    queries = [
        "optimization_under_constraints",
        "emergent_collective_behavior",
        "adaptation_to_changing_environment",
    ]
    return queries[index % len(queries)]


# ── Skill handlers ───────────────────────────────────────────────────────────

def handle_run_pipeline(message: str) -> str:
    """Run the full epistemic council pipeline (run.py)."""
    state = _load_state()

    if state.get("pipeline_running"):
        return "⚠️  Pipeline is already running. Check memory/heartbeat-state.json."

    idx   = state.get("query_rotation_index", 0)
    query = _query_for_index(idx)

    state["pipeline_running"] = True
    state["last_pipeline_start"] = datetime.utcnow().isoformat()
    _save_state(state)

    log.info(f"Starting pipeline with query: {query}")
    rc, output = _run_script("run.py", ["--query", query, "--db", str(DB_PATH)])

    summary = {"query": query, "raw_exit": rc}
    for line in output.splitlines():
        for key in ("Validated:", "Challenged:", "Rejected:", "Total events:"):
            if key in line:
                try:
                    summary[key.rstrip(":")] = int(line.split(":")[-1].strip())
                except ValueError:
                    pass

    state["pipeline_running"]       = False
    state["last_pipeline_run"]      = datetime.utcnow().isoformat()
    state["last_query"]             = query
    state["query_rotation_index"]   = idx + 1
    state["last_run_summary"]       = summary
    _save_state(state)

    if rc != 0:
        return f"❌ Pipeline exited with code {rc}.\n\n{output[-1000:]}"

    validated  = summary.get("Validated",  "?")
    challenged = summary.get("Challenged", "?")
    rejected   = summary.get("Rejected",   "?")
    return (
        f"✅ Pipeline complete — query: {query}\n"
        f"   Validated: {validated}  |  Challenged: {challenged}  |  Rejected: {rejected}\n"
        f"   Results in epistemic.db. Run 'substrate status' for detail."
    )


def handle_status(message: str) -> str:
    """Return substrate health + last run summary."""
    s = _substrate()
    total   = s.event_count()
    state   = _load_state()

    if total < 5:
        s.close()
        return (
            f"Substrate has {total} events — run 'run council' to populate it.\n"
            f"Last pipeline run: {state.get('last_pipeline_run', 'never')}"
        )

    insights   = s.get_insights()
    cs_claims  = s.get_claims_by_domain("computer_science")
    bio_claims = s.get_claims_by_domain("biology")
    integrity  = s.verify_all()
    s.close()

    summary  = state.get("last_run_summary") or {}
    last_run = state.get("last_pipeline_run", "never")

    return (
        f"📊 Epistemic Council — Substrate Status\n"
        f"{'─'*45}\n"
        f"  Total events     : {total}\n"
        f"  CS claims        : {len(cs_claims)}\n"
        f"  Biology claims   : {len(bio_claims)}\n"
        f"  Insights         : {len(insights)}\n"
        f"  Integrity        : {integrity['passed']}/{integrity['total']} passed\n"
        f"{'─'*45}\n"
        f"  Last pipeline run: {last_run}\n"
        f"  Last query       : {state.get('last_query', 'none')}\n"
        f"  Validated        : {summary.get('Validated', '–')}\n"
        f"  Challenged       : {summary.get('Challenged', '–')}\n"
        f"  Rejected         : {summary.get('Rejected', '–')}\n"
    )


def handle_health_check(message: str) -> str:
    """Run substrate_health.py and return the alert level."""
    rc, output = _run_script("substrate_health.py")
    try:
        report    = json.loads(output.split("\n[stderr]")[0].strip())
        alert     = report.get("alert", "UNKNOWN")
        total     = report.get("total_events", "?")
        hr_count  = report.get("high_risk_unverified", {}).get("count", 0)
        orphans   = report.get("orphan_claims", {}).get("count", 0)
        clusters  = report.get("divergence_clusters", {}).get("count", 0)
        prefix = "🔴" if alert == "CRITICAL" else "✅"
        return (
            f"{prefix} Substrate health: {alert}\n"
            f"   Total events          : {total}\n"
            f"   High-risk unverified  : {hr_count}\n"
            f"   Orphan claims         : {orphans}\n"
            f"   Divergence clusters   : {clusters}\n"
        )
    except Exception:
        return f"Health check output (exit {rc}):\n{output[-800:]}"


def handle_validate(message: str) -> str:
    """Run validate_claim.py on the challenged-zone claims."""
    rc, output = _run_script("validate_claim.py")
    try:
        data    = json.loads(output.split("\n[stderr]")[0].strip())
        count   = data.get("validated_count", 0)
        results = data.get("results", [])
        lines   = [f"Validated {count} claim(s) in confidence range 0.45–0.55:"]
        for r in results[:5]:
            adj  = r.get("suggested_magnitude", 0.0)
            sign = "+" if adj >= 0 else ""
            lines.append(
                f"  {r['claim_id'][:8]}... | {r['verdict']} | "
                f"conf {r['current_confidence']:.2f} → {r['suggested_new_confidence']:.2f} ({sign}{adj})"
            )
        return "\n".join(lines)
    except Exception:
        return f"Validate output (exit {rc}):\n{output[-800:]}"


def handle_boundary_audit(message: str) -> str:
    """Run boundary_audit.py."""
    rc, output = _run_script("boundary_audit.py", ["--recent", "20"])
    try:
        data       = json.loads(output.split("\n[stderr]")[0].strip())
        alert      = data.get("alert", "UNKNOWN")
        audited    = data.get("claims_audited", 0)
        violations = data.get("violation_count", 0)
        prefix = "⚠️ " if violations else "✅"
        return (
            f"{prefix} Boundary audit: {alert}\n"
            f"   Claims audited : {audited}\n"
            f"   Violations     : {violations}\n"
        )
    except Exception:
        return f"Boundary audit output (exit {rc}):\n{output[-800:]}"


def handle_evidence_search(message: str) -> str:
    """Run evidence_search.py to find gaps."""
    rc, output = _run_script("evidence_search.py")
    try:
        data    = json.loads(output.split("\n[stderr]")[0].strip())
        summary = data.get("summary", {})
        return (
            f"🔍 Gap detection complete:\n"
            f"   Orphan claims        : {summary.get('orphan_count', 0)}\n"
            f"   Sparse domains       : {summary.get('sparse_domain_count', 0)}\n"
            f"   Unchallenged insights: {summary.get('unchallenged_insight_count', 0)}\n"
            f"   Report: memory/gaps-{datetime.utcnow().strftime('%Y-%m-%d')}.md"
        )
    except Exception:
        return f"Evidence search output (exit {rc}):\n{output[-800:]}"


def handle_rechallenge(message: str) -> str:
    """Run adversarial_rechallenge.py."""
    rc, output = _run_script("adversarial_rechallenge.py")
    try:
        data = json.loads(output.split("\n[stderr]")[0].strip())
        if data.get("status") == "rate_limited":
            return f"⏳ Re-challenge rate limited. Next eligible: {data.get('next_eligible', '?')}"
        if data.get("status") == "no_candidates":
            return "No high-confidence insights (>0.75) available for re-challenge."
        category   = data.get("verdict", {}).get("category", "?")
        insight_id = data.get("insight_id", "?")[:8]
        prior_conf = data.get("prior_confidence", 0)
        new_conf   = data.get("new_confidence_estimate", 0)
        return (
            f"🔬 Re-challenge complete:\n"
            f"   Insight   : {insight_id}...\n"
            f"   Category  : {category}\n"
            f"   Confidence: {prior_conf:.2f} → {new_conf:.2f}\n"
        )
    except Exception:
        return f"Re-challenge output (exit {rc}):\n{output[-800:]}"


# ── Dispatch table ───────────────────────────────────────────────────────────

TRIGGERS = {
    # Pipeline
    "run council":             handle_run_pipeline,
    "run pipeline":            handle_run_pipeline,
    "run the council":         handle_run_pipeline,
    "start pipeline":          handle_run_pipeline,
    # Status
    "substrate status":        handle_status,
    "council status":          handle_status,
    "epistemic status":        handle_status,
    "show status":             handle_status,
    # Health
    "health check":            handle_health_check,
    "check health":            handle_health_check,
    # Analysis
    "analyze cross-domain":    handle_evidence_search,
    "find analogies":          handle_evidence_search,
    "find gaps":               handle_evidence_search,
    "structural similarities": handle_evidence_search,
    "cross-domain patterns":   handle_evidence_search,
    "epistemic reasoning":     handle_run_pipeline,
    # Validation
    "validate claims":         handle_validate,
    "validate claim":          handle_validate,
    # Boundary
    "check boundaries":        handle_boundary_audit,
    "boundary audit":          handle_boundary_audit,
    # Re-challenge
    "rechallenge":             handle_rechallenge,
    "re-challenge":            handle_rechallenge,
    "adversarial rechallenge": handle_rechallenge,
}


def dispatch(message: str) -> str:
    """Entry point called by OpenClaw skill runner."""
    msg_lower = message.lower().strip()

    for trigger, handler in TRIGGERS.items():
        if trigger in msg_lower:
            try:
                return handler(message)
            except Exception as e:
                log.error(f"Handler error for '{trigger}': {e}", exc_info=True)
                return f"Skill error in '{trigger}': {e}"

    return (
        "🔬 Epistemic Council skill active.\n\n"
        "Commands:\n"
        "  'run council'        — full pipeline run (claims → insights → validation)\n"
        "  'substrate status'   — show event counts + last run summary\n"
        "  'health check'       — scan for high-risk claims and orphans\n"
        "  'validate claims'    — re-evaluate challenged-zone claims\n"
        "  'check boundaries'   — scan for domain boundary violations\n"
        "  'find gaps'          — detect orphan claims and sparse coverage\n"
        "  'rechallenge'        — re-challenge highest-confidence insight\n"
        "\nTo install new skills: use OpenClaw's native skill commands\n"
        "  'openclaw skill install <name>' or ask the agent to install a skill by name\n"
    )


if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "substrate status"
    print(dispatch(query))
