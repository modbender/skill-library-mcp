#!/usr/bin/env python3
import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


VALID_STATUS = {"compliant", "partial", "violation", "not_assessed"}
VALID_RISK = {"low", "medium", "high", "critical"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def default_controls_path() -> Path:
    return Path(__file__).resolve().parent.parent / "references" / "compliance-controls-map.json"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
        f.write("\n")


def init_assessment(controls: List[Dict[str, object]], system_name: str) -> Dict[str, object]:
    checks = []
    for ctrl in controls:
        checks.append(
            {
                "check_id": ctrl["check_id"],
                "status": "not_assessed",
                "risk": ctrl.get("default_risk", "medium"),
                "observed_state": "",
                "evidence": "",
                "gap": "",
                "mitigation": "",
                "owner": "",
                "due_date": "",
            }
        )
    return {
        "metadata": {
            "system": system_name,
            "generated_at_utc": utc_now(),
            "frameworks": ["ISO/IEC 27001:2022", "NIST CSF"],
        },
        "checks": checks,
    }


def validate_assessment(assessment: Dict[str, object]) -> None:
    checks = assessment.get("checks", [])
    if not isinstance(checks, list):
        raise ValueError("Assessment must include 'checks' list.")
    for c in checks:
        status = c.get("status", "")
        risk = c.get("risk", "")
        if status not in VALID_STATUS:
            raise ValueError(f"Invalid status '{status}' for check {c.get('check_id')}")
        if risk not in VALID_RISK:
            raise ValueError(f"Invalid risk '{risk}' for check {c.get('check_id')}")


def merge_controls(controls: List[Dict[str, object]], assessment: Dict[str, object]) -> List[Dict[str, object]]:
    by_id = {c["check_id"]: c for c in assessment.get("checks", [])}
    merged = []
    for ctrl in controls:
        check = by_id.get(ctrl["check_id"], {})
        merged.append(
            {
                "check_id": ctrl["check_id"],
                "title": ctrl["title"],
                "iso27001": ctrl.get("iso27001", []),
                "nist": ctrl.get("nist", []),
                "expected_state": ctrl.get("expected_state", ""),
                "status": check.get("status", "not_assessed"),
                "risk": check.get("risk", ctrl.get("default_risk", "medium")),
                "observed_state": check.get("observed_state", ""),
                "evidence": check.get("evidence", ""),
                "gap": check.get("gap", ""),
                "mitigation": check.get("mitigation", ""),
                "owner": check.get("owner", ""),
                "due_date": check.get("due_date", ""),
            }
        )
    return merged


def summarize(merged: List[Dict[str, object]]) -> Dict[str, object]:
    status_counts = Counter(item["status"] for item in merged)
    risk_counts = Counter(item["risk"] for item in merged)
    violations = [m for m in merged if m["status"] in ("violation", "partial")]
    mitigations = [m for m in merged if m["mitigation"]]
    return {
        "status_counts": dict(status_counts),
        "risk_counts": dict(risk_counts),
        "violations": violations,
        "mitigations": mitigations,
    }


def render_html(system_name: str, merged: List[Dict[str, object]], summary: Dict[str, object]) -> str:
    def fmt_list(items: List[str]) -> str:
        return ", ".join(items) if items else "-"

    controls_rows = "\n".join(
        f"<tr><td>{m['check_id']}</td><td>{m['title']}</td><td>{fmt_list(m['iso27001'])}</td><td>{fmt_list(m['nist'])}</td><td>{m['status']}</td><td>{m['risk']}</td></tr>"
        for m in merged
    )
    violation_rows = "\n".join(
        f"<tr><td>{m['check_id']}</td><td>{m['status']}</td><td>{m['risk']}</td><td>{m['gap'] or '-'}</td><td>{m['evidence'] or '-'}</td></tr>"
        for m in summary["violations"]
    ) or "<tr><td colspan='5'>No violations or partial findings.</td></tr>"
    mitigation_rows = "\n".join(
        f"<tr><td>{m['check_id']}</td><td>{m['mitigation']}</td><td>{m['owner'] or '-'}</td><td>{m['due_date'] or '-'}</td></tr>"
        for m in summary["mitigations"]
    ) or "<tr><td colspan='4'>No mitigation actions recorded.</td></tr>"

    status_counts = summary["status_counts"]
    risk_counts = summary["risk_counts"]

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Compliance Dashboard - {system_name}</title>
  <style>
    :root {{
      --bg: #f2f5f9;
      --panel: #ffffff;
      --text: #1f2937;
      --muted: #5f6b7a;
      --accent: #005f73;
      --warn: #b45309;
      --bad: #b91c1c;
      --border: #d9e2ec;
    }}
    body {{
      margin: 0;
      font-family: "IBM Plex Sans", "Segoe UI", sans-serif;
      color: var(--text);
      background: linear-gradient(180deg, #eaf2f8, var(--bg));
    }}
    .wrap {{ max-width: 1100px; margin: 0 auto; padding: 24px; }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 16px;
      margin-bottom: 16px;
      box-shadow: 0 6px 16px rgba(5, 23, 41, 0.06);
    }}
    h1, h2 {{ margin: 0 0 10px 0; }}
    h1 {{ font-size: 28px; color: var(--accent); }}
    h2 {{ font-size: 18px; }}
    p {{ margin: 8px 0; color: var(--muted); }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ text-align: left; padding: 8px; border-bottom: 1px solid var(--border); vertical-align: top; }}
    th {{ background: #f8fafc; }}
    .kpis {{ display: grid; grid-template-columns: repeat(4, minmax(120px, 1fr)); gap: 12px; }}
    .kpi {{ border: 1px solid var(--border); border-radius: 10px; padding: 10px; background: #fcfdff; }}
    .kpi strong {{ display: block; font-size: 20px; margin-top: 6px; }}
    .risk-high {{ color: var(--bad); }}
    .risk-medium {{ color: var(--warn); }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="panel">
      <h1>ISO 27001 / NIST Compliance Dashboard</h1>
      <p>System: {system_name}</p>
      <p>Generated: {utc_now()}</p>
    </div>

    <div class="panel">
      <h2>Risk and Status Overview</h2>
      <div class="kpis">
        <div class="kpi"><span>Violations</span><strong>{status_counts.get("violation", 0)}</strong></div>
        <div class="kpi"><span>Partial</span><strong>{status_counts.get("partial", 0)}</strong></div>
        <div class="kpi"><span>Compliant</span><strong>{status_counts.get("compliant", 0)}</strong></div>
        <div class="kpi"><span>Not Assessed</span><strong>{status_counts.get("not_assessed", 0)}</strong></div>
      </div>
      <p class="risk-high">High/Critical risk findings: {risk_counts.get("high", 0) + risk_counts.get("critical", 0)}</p>
      <p class="risk-medium">Medium risk findings: {risk_counts.get("medium", 0)}</p>
    </div>

    <div class="panel">
      <h2>Controls Map View</h2>
      <table>
        <thead>
          <tr><th>Check ID</th><th>Control</th><th>ISO 27001</th><th>NIST</th><th>Status</th><th>Risk</th></tr>
        </thead>
        <tbody>
          {controls_rows}
        </tbody>
      </table>
    </div>

    <div class="panel">
      <h2>Violation View</h2>
      <table>
        <thead>
          <tr><th>Check ID</th><th>Status</th><th>Risk</th><th>Gap</th><th>Evidence</th></tr>
        </thead>
        <tbody>
          {violation_rows}
        </tbody>
      </table>
    </div>

    <div class="panel">
      <h2>Mitigation View</h2>
      <table>
        <thead>
          <tr><th>Check ID</th><th>Mitigation</th><th>Owner</th><th>Due Date</th></tr>
        </thead>
        <tbody>
          {mitigation_rows}
        </tbody>
      </table>
    </div>
  </div>
</body>
</html>
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ISO 27001/NIST dashboard scaffold for OpenClaw")
    parser.add_argument(
        "--controls-file",
        default=str(default_controls_path()),
        help="Controls map JSON file",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    init_cmd = sub.add_parser("init-assessment", help="Create scaffold assessment JSON")
    init_cmd.add_argument("--system", default="OpenClaw", help="System name")
    init_cmd.add_argument(
        "--output",
        default="cyber-security-engineer/assessments/openclaw-assessment.json",
        help="Output path for assessment scaffold",
    )

    render_cmd = sub.add_parser("render", help="Render dashboard from controls+assessment")
    render_cmd.add_argument(
        "--assessment-file",
        default="cyber-security-engineer/assessments/openclaw-assessment.json",
        help="Assessment input JSON path",
    )
    render_cmd.add_argument(
        "--output-html",
        default="cyber-security-engineer/assessments/compliance-dashboard.html",
        help="Output HTML dashboard path",
    )
    render_cmd.add_argument(
        "--output-summary",
        default="cyber-security-engineer/assessments/compliance-summary.json",
        help="Output summary JSON path",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    controls = load_json(Path(args.controls_file).expanduser())
    if not isinstance(controls, list):
        raise ValueError("Controls file must be a JSON array.")

    if args.command == "init-assessment":
        scaffold = init_assessment(controls, args.system)
        out = Path(args.output)
        write_json(out, scaffold)
        print(json.dumps({"status": "ok", "created": str(out), "checks": len(scaffold["checks"])}))
        return 0

    if args.command == "render":
        assessment_path = Path(args.assessment_file)
        assessment = load_json(assessment_path)
        validate_assessment(assessment)

        merged = merge_controls(controls, assessment)
        summary = summarize(merged)
        system_name = assessment.get("metadata", {}).get("system", "OpenClaw")

        html = render_html(system_name, merged, summary)
        out_html = Path(args.output_html)
        out_html.parent.mkdir(parents=True, exist_ok=True)
        out_html.write_text(html, encoding="utf-8")

        out_summary = Path(args.output_summary)
        write_json(
            out_summary,
            {
                "generated_at_utc": utc_now(),
                "system": system_name,
                "summary": summary,
                "controls": merged,
            },
        )
        print(
            json.dumps(
                {
                    "status": "ok",
                    "output_html": str(out_html),
                    "output_summary": str(out_summary),
                    "violations_or_partial": len(summary["violations"]),
                }
            )
        )
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
