#!/usr/bin/env python3
\"\"\"Run daily analysis and print JSON to stdout (and optional file).\"\"\"

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from _bootstrap import ensure_pkg_on_path

ensure_pkg_on_path()

from skill_health.analysis.daily import build_daily_report, infer_target_date_from_bundle
from skill_health.load import load_health_data_from_directory, load_health_data_from_path


def main() -> int:
    parser = argparse.ArgumentParser(description=\"Daily analysis (previous day by default).\")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(\"--data-dir\", type=Path, help=\"Directory with health_data_* folder(s) or ZIP(s).\")
    group.add_argument(\"--data-path\", type=Path, help=\"Path to health_data_* directory or ZIP.\")
    parser.add_argument(\"--date\", type=str, default=None, help=\"Target date (YYYY-MM-DD).\")
    parser.add_argument(\"--output-dir\", type=Path, default=None, help=\"Directory to save JSON output.\")
    args = parser.parse_args()

    if args.data_dir is not None:
        bundle = load_health_data_from_directory(args.data_dir)
    else:
        bundle = load_health_data_from_path(args.data_path)

    target_date = (
        datetime.fromisoformat(args.date).date()
        if args.date is not None
        else infer_target_date_from_bundle(bundle)
    )
    payload = build_daily_report(bundle, target_date=target_date)
    json_str = json.dumps(payload, indent=2, ensure_ascii=False)

    if args.output_dir is not None:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        filename = f\"daily_{target_date.isoformat()}\.json\"
        out_path = args.output_dir / filename
        out_path.write_text(json_str, encoding=\"utf-8\")
        print(f\"Wrote {out_path}\", file=sys.stderr)

    print(json_str)
    return 0


if __name__ == \"__main__\":
    raise SystemExit(main())
