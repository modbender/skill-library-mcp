#!/usr/bin/env python3
\"\"\"Run cross-temporal alerts and print JSON to stdout (and optional file).\"\"\"

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _bootstrap import ensure_pkg_on_path

ensure_pkg_on_path()

from skill_health.analysis.cross_alerts import build_cross_alerts, load_metrics_from_outputs_dir


def main() -> int:
    parser = argparse.ArgumentParser(description=\"Cross-temporal alerts from output files.\")
    parser.add_argument(\"--outputs-dir\", type=Path, required=True, help=\"Directory with outputs JSON files.\")
    parser.add_argument(\"--output-dir\", type=Path, default=None, help=\"Directory to save JSON output.\")
    args = parser.parse_args()

    context = load_metrics_from_outputs_dir(args.outputs_dir)
    alerts = build_cross_alerts(context)
    payload = {\"alerts\": alerts, \"count\": len(alerts)}
    json_str = json.dumps(payload, indent=2, ensure_ascii=False)

    if args.output_dir is not None:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        out_path = args.output_dir / \"cross_alerts.json\"
        out_path.write_text(json_str, encoding=\"utf-8\")
        print(f\"Wrote {out_path}\", file=sys.stderr)

    print(json_str)
    return 0


if __name__ == \"__main__\":
    raise SystemExit(main())
