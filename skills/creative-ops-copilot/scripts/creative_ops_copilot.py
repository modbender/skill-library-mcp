#!/usr/bin/env python
"""Creative Ops Copilot

Deterministic-ish generator that turns a brief into:
- docs/creative-ops/plan.md
- docs/creative-ops/estimate.json
- docs/creative-ops/invoice-draft.json
Optionally creates a project skeleton and/or POSTs invoice draft.

This script intentionally avoids any external LLM calls; the OpenClaw agent can
run it after it has already drafted the structured content.

If you want LLM-powered extraction, do it in the agent, then pass --data-json.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import re
import sys
import urllib.request


def _now_stamp() -> str:
    return dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def _read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _safe_name(s: str) -> str:
    s = s.strip()
    s = re.sub(r"[^a-zA-Z0-9\- _]+", "", s)
    s = re.sub(r"\s+", " ", s)
    return s[:80] if s else "project"


def _load_config(skill_dir: pathlib.Path) -> dict:
    cfg_path = skill_dir / "references" / "config.json"
    if cfg_path.exists():
        return json.loads(cfg_path.read_text(encoding="utf-8"))
    # fall back to example
    example = skill_dir / "references" / "config.example.json"
    return json.loads(example.read_text(encoding="utf-8"))


def _mkdir(p: pathlib.Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _write(p: pathlib.Path, content: str) -> None:
    _mkdir(p.parent)
    p.write_text(content, encoding="utf-8")


def _write_json(p: pathlib.Path, obj: dict) -> None:
    _mkdir(p.parent)
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _default_estimate(cfg: dict, project_name: str) -> dict:
    hourly = cfg.get("rateCard", {}).get("hourlyRate", 150)
    currency = cfg.get("rateCard", {}).get("currency", "AUD")
    contingency_rate = cfg.get("rateCard", {}).get("contingencyRate", 0.1)

    items = [
        {"code": "PREPRO", "name": "Pre-production (briefing, boards, styleframes)", "hours": 6, "rate": hourly},
        {"code": "PROD", "name": "Production (animation/3D/compositing)", "hours": 18, "rate": hourly},
        {"code": "REVIS", "name": "Revisions (included rounds)", "hours": 6, "rate": hourly},
        {"code": "EXPORT", "name": "Exports, versions, delivery", "hours": 3, "rate": hourly},
        {"code": "PM", "name": "Project management / admin", "hours": 2, "rate": hourly},
    ]

    subtotal = sum(i["hours"] * i["rate"] for i in items)
    contingency = round(subtotal * contingency_rate, 2)
    total_ex_gst = round(subtotal + contingency, 2)

    return {
        "projectName": project_name,
        "currency": currency,
        "items": items,
        "summary": {
            "subtotal": round(subtotal, 2),
            "contingency": contingency,
            "totalExGst": total_ex_gst,
        },
    }


def _invoice_draft(cfg: dict, estimate: dict, client_name: str | None) -> dict:
    gst_rate = cfg.get("rateCard", {}).get("gstRate", 0.1)
    total_ex = estimate["summary"]["totalExGst"]
    gst = round(total_ex * gst_rate, 2)
    total_inc = round(total_ex + gst, 2)

    return {
        "clientName": client_name or "",
        "projectName": estimate.get("projectName", ""),
        "currency": estimate.get("currency", "AUD"),
        "lineItems": [
            {
                "description": f"{i['code']} - {i['name']}",
                "quantity": i["hours"],
                "unit": "hour",
                "unitPrice": i["rate"],
            }
            for i in estimate.get("items", [])
        ],
        "totals": {"exGst": total_ex, "gst": gst, "incGst": total_inc},
        "meta": {"generatedAt": dt.datetime.now().isoformat()},
    }


def _render_plan_md(project_name: str, brief: str, cfg: dict, estimate: dict) -> str:
    rr = cfg.get("defaults", {}).get("reviewRoundsIncluded", 2)
    aspects = cfg.get("defaults", {}).get("delivery", {}).get("aspects", [])
    formats = cfg.get("defaults", {}).get("delivery", {}).get("formats", [])

    est_total = estimate.get("summary", {}).get("totalExGst", "")
    currency = estimate.get("currency", "AUD")

    return f"""# {project_name} — Creative Ops Plan

## Project summary
{_one_liner(brief)}

## Goals / success criteria
- (Define what ‘good’ looks like)

## Deliverables (matrix)
- Primary deliverable(s): (fill in)
- Aspect ratios: {', '.join(aspects) if aspects else '(confirm)'}
- Formats: {', '.join(formats) if formats else '(confirm)'}
- Versions: (e.g., cutdowns, alt supers, language versions)

## Workflow assumptions
- Included review rounds: **{rr}**
- Client supplies: brand kit, logos, product info, legal copy (as needed)
- Turnaround depends on feedback timing and source assets

## Exclusions (avoid scope creep)
- Major concept pivots after sign-off
- New deliverables not listed above
- Unlimited revisions

## Open questions (answer these to lock scope)
- Target runtime(s)?
- Delivery specs (codec, bitrates, platform)?
- Brand references / competitor examples?
- Who is the final approver?
- Deadline(s) and any immovable dates?

## Production plan
- Phase 1: Brief + style direction
- Phase 2: Build + first pass
- Phase 3: Revisions (round 1)
- Phase 4: Revisions (round 2) + final delivery

## Risks / dependencies
- Late or incomplete assets
- Multi-stakeholder approvals causing delays
- Footage/licensing constraints

## Estimate (ballpark, ex GST)
- Estimated total (ex GST): **{currency} {est_total}**
- See `docs/creative-ops/estimate.json` for line items.

## Next actions
- Confirm open questions
- Approve estimate + timeline
- Provide assets (brand kit, copy, logos)
"""


def _one_liner(brief: str) -> str:
    brief = (brief or "").strip().replace("\r", "")
    if not brief:
        return "(Brief not provided yet.)"
    first = brief.split("\n")[0].strip()
    if len(first) > 180:
        first = first[:177] + "..."
    return first


def _create_skeleton(out_root: pathlib.Path, project_name: str) -> pathlib.Path:
    base = out_root / _safe_name(project_name)
    # avoid collisions
    if base.exists():
        base = out_root / f"{_safe_name(project_name)}-{_now_stamp()}"

    dirs = [
        base / "docs",
        base / "assets" / "client",
        base / "assets" / "brand",
        base / "ae" / "project",
        base / "c4d" / "project",
        base / "renders" / "previews",
        base / "renders" / "final",
        base / "exports" / "deliveries",
        base / "cache",
    ]
    for d in dirs:
        _mkdir(d)

    _write(base / "docs" / "README.md", f"# {project_name}\n\n(Autogenerated project skeleton)\n")
    return base


def _post_invoice(cfg: dict, payload: dict) -> tuple[int, str]:
    api = cfg.get("invoicingApi", {})
    base = api.get("baseUrl", "").rstrip("/")
    path = api.get("createInvoicePath", "/api/invoices/draft")
    url = f"{base}{path}"
    if not base:
        raise RuntimeError("invoicingApi.baseUrl not set")

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")

    api_key = (api.get("apiKey") or "").strip()
    if api_key:
        req.add_header("Authorization", f"Bearer {api_key}")

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return resp.status, body
    except Exception as e:
        return 0, f"ERROR: {e}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--brief", default=None, help="Brief text")
    parser.add_argument("--brief-file", default=None, help="Path to a text file containing the brief")
    parser.add_argument("--data-json", default=None, help="Optional structured JSON to use (bypass defaults)")
    parser.add_argument("--out", default=".", help="Output root (repo/project root)")
    parser.add_argument("--project-name", default=None, help="Override project name")
    parser.add_argument("--client-name", default=None, help="Client name")
    parser.add_argument("--skeleton", action="store_true", help="Create a project folder skeleton")
    parser.add_argument("--push-invoice", action="store_true", help="POST invoice draft to local invoicing API")

    args = parser.parse_args()

    skill_dir = pathlib.Path(__file__).resolve().parents[1]
    cfg = _load_config(skill_dir)

    brief = args.brief
    if args.brief_file:
        brief = _read_text_file(args.brief_file)
    if brief is None:
        brief = ""

    project_name = args.project_name or "Untitled Motion/VFX Project"

    # If structured data provided, use it; else generate sensible defaults.
    if args.data_json:
        data = json.loads(args.data_json)
        project_name = data.get("projectName") or project_name
        estimate = data.get("estimate") or _default_estimate(cfg, project_name)
    else:
        estimate = _default_estimate(cfg, project_name)

    invoice = _invoice_draft(cfg, estimate, args.client_name)

    out_root = pathlib.Path(args.out).resolve()

    # optional skeleton
    skeleton_path = None
    if args.skeleton:
        skeleton_path = _create_skeleton(out_root, project_name)

    # default output location: either skeleton/docs/... or repo/docs/...
    docs_root = (skeleton_path / "docs") if skeleton_path else (out_root / "docs")
    out_docs = docs_root / "creative-ops"

    _write(out_docs / "plan.md", _render_plan_md(project_name, brief, cfg, estimate))
    _write_json(out_docs / "estimate.json", estimate)
    _write_json(out_docs / "invoice-draft.json", invoice)

    if args.push_invoice:
        status, body = _post_invoice(cfg, invoice)
        _write(out_docs / "invoice-push-result.txt", f"status={status}\n\n{body}\n")

    print(str(out_docs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
