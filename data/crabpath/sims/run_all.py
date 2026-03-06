"""Run all CrabPath simulations and print a compact summary."""

from __future__ import annotations

import json
import subprocess
import sys
import os
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SIMS = [
    ("deploy_pipeline.py", "deploy_pipeline_results.json"),
    ("negation.py", "negation_results.json"),
    ("context_reduction.py", "context_reduction_results.json"),
    ("pg_vs_heuristic.py", "pg_vs_heuristic_results.json"),
    ("merge_compression.py", "merge_compression_results.json"),
    ("prune_health.py", "prune_health_results.json"),
    ("structural_vs_edge_only.py", "structural_vs_edge_only_results.json"),
    ("noise_robustness.py", "noise_robustness_results.json"),
    ("static_vs_learning.py", "static_vs_learning_results.json"),
    ("scaling_analysis.py", "scaling_analysis_results.json"),
    ("forgetting.py", "forgetting_results.json"),
    ("edge_damping.py", "edge_damping_results.json"),
    ("domain_separation.py", "domain_separation_results.json"),
    ("brain_death.py", "brain_death_results.json"),
    ("individuation.py", "individuation_results.json"),
]


def _extract_claim(payload: Any) -> bool | None:
    claim = payload.get("claim")
    if claim is None:
        return None

    def _collect(node: Any, out: list[bool]) -> None:
        if isinstance(node, dict):
            if isinstance(node, dict) and isinstance(node.get("met"), bool):
                out.append(node["met"])
            if all(isinstance(v, bool) for v in node.values()):
                for value in node.values():
                    out.append(value)
            for value in node.values():
                _collect(value, out)
        elif isinstance(node, bool):
            out.append(node)
        elif isinstance(node, list):
            for value in node:
                _collect(value, out)

    values: list[bool] = []
    _collect(claim, values)
    if not values:
        return None
    return all(values)


def _load_result(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def _summary_value(payload: dict[str, Any]) -> str:
    if "final_health" in payload:
        return f"dormant={payload['final_health'].get('dormant_pct', 0):.3f}"
    if payload.get("simulation") == "edge_damping":
        return f"dr={payload['damped'].get('reached_D')} ur={payload['undamped'].get('reached_D')}"
    if payload.get("simulation") == "individuation":
        claim = payload["structural_distinctness"]
        return f"diff_edges={claim['edges_differ_by_gt_0_05']}"
    if payload.get("simulation") == "deploy_pipeline":
        return f"final={payload['claim']['edge_growth_to_reflex']['to_query_50']:.3f}"
    if payload.get("simulation") == "negation":
        return f"bad={payload['final_weights']['skip_tests_for_hotfix']:.3f}"
    if payload.get("simulation") == "context_reduction":
        first = payload["claim"]["reduction_to_few_nodes"]["from_query1"]
        last = payload["claim"]["reduction_to_few_nodes"]["to_last_10_avg"]
        return f"{first:.1f}->{last:.1f}"
    if payload.get("simulation") == "selective_forgetting":
        return f"dormant={payload['final_tier_distribution']['dormant_pct']:.3f}"
    if payload.get("simulation") == "domain_separation":
        return f"cross={payload['final_cross_file_edge_count']}"
    if payload.get("simulation") == "brain_death_recovery":
        return f"knobs={','.join(payload['recovery_signals'])}"
    return "-"


def _run_one(script: str, result_name: str) -> tuple[str, bool | None, str]:
    script_path = ROOT / script
    result_path = ROOT / result_name

    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT.parent)
    run = subprocess.run(
        [sys.executable, str(script_path)],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    if run.returncode != 0:
        raise RuntimeError(
            f"simulation failed: {script}\nstdout={run.stdout}\nstderr={run.stderr}"
        )

    payload = _load_result(result_path)
    claim_ok = _extract_claim(payload)
    return script.replace(".py", ""), claim_ok, _summary_value(payload)


def main() -> None:
    rows = []
    for script_name, result_name in SIMS:
        name, claim_ok, summary = _run_one(script_name, result_name)
        rows.append((name, claim_ok, summary))

    name_width = 26
    claim_width = 12
    print("simulation".ljust(name_width), "claim".ljust(claim_width), "summary")
    print("-" * (name_width + claim_width + 1 + 40))
    for name, claim_ok, summary in rows:
        claim = "PASS" if claim_ok is True else "FAIL" if claim_ok is False else "N/A"
        print(name.ljust(name_width), claim.ljust(claim_width), summary)


if __name__ == "__main__":
    main()
