#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path

from common import RateLimiter, configure_vnstock_api_key, ensure_outdir, timestamp, write_json


def parse_json_arg(raw: str, name: str):
    try:
        parsed = json.loads(raw)
        if not isinstance(parsed, dict):
            raise ValueError(f"{name} must be a JSON object")
        return parsed
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON for {name}: {e}") from e


def parse_json_list_arg(raw: str, name: str):
    try:
        parsed = json.loads(raw)
        if not isinstance(parsed, list):
            raise ValueError(f"{name} must be a JSON array")
        return parsed
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON for {name}: {e}") from e


def to_serializable(result):
    # pandas DataFrame / Series
    try:
        import pandas as pd

        if isinstance(result, pd.DataFrame):
            return {
                "type": "dataframe",
                "shape": list(result.shape),
                "columns": [str(c) for c in result.columns],
                "records": result.to_dict(orient="records"),
            }
        if isinstance(result, pd.Series):
            return {"type": "series", "name": str(result.name), "values": result.to_dict()}
    except Exception:
        pass

    if isinstance(result, (dict, list, str, int, float, bool)) or result is None:
        return {"type": "native", "value": result}

    # fallback repr
    return {"type": "repr", "value": repr(result)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Invoke arbitrary vnstock class + method with JSON kwargs")
    parser.add_argument("--module", default="vnstock", help="Module path containing class, default vnstock")
    parser.add_argument("--class-name", required=True, help="vnstock exported class name, e.g. Quote")
    parser.add_argument("--init-kwargs", default="{}", help="JSON object for class initialization kwargs")
    parser.add_argument("--method", required=True, help="Method name to call")
    parser.add_argument("--method-args", default="[]", help="JSON array for positional method args")
    parser.add_argument("--method-kwargs", default="{}", help="JSON object for method kwargs")
    parser.add_argument("--outdir", default="./outputs", help="Output directory")
    parser.add_argument("--min-interval-sec", type=float, default=3.2, help="Optional pacing for free-tier safety")
    parser.add_argument("--api-key", default="", help="Optional VNStock API key override")
    args = parser.parse_args()

    init_kwargs = parse_json_arg(args.init_kwargs, "init-kwargs")
    method_args = parse_json_list_arg(args.method_args, "method-args")
    method_kwargs = parse_json_arg(args.method_kwargs, "method-kwargs")
    configure_vnstock_api_key(args.api_key or None)

    mod = importlib.import_module(args.module)

    if not hasattr(mod, args.class_name):
        raise AttributeError(f"Class not found in module {args.module}: {args.class_name}")

    cls = getattr(mod, args.class_name)
    client = cls(**init_kwargs)

    if not hasattr(client, args.method):
        raise AttributeError(f"Method not found on {args.class_name}: {args.method}")

    method = getattr(client, args.method)

    limiter = RateLimiter(min_interval_sec=args.min_interval_sec)
    limiter.wait()

    result = method(*method_args, **method_kwargs)
    serial = to_serializable(result)

    outdir = ensure_outdir(args.outdir)
    ts = timestamp()
    json_path = Path(outdir) / f"invoke_{args.class_name}_{args.method}_{ts}.json"
    md_path = Path(outdir) / f"invoke_{args.class_name}_{args.method}_{ts}.md"

    payload = {
        "generated_at": ts,
        "module": args.module,
        "class_name": args.class_name,
        "init_kwargs": init_kwargs,
        "method": args.method,
        "method_args": method_args,
        "method_kwargs": method_kwargs,
        "result": serial,
    }
    write_json(json_path, payload)

    lines = [
        f"# VNStock Invocation Result ({ts})",
        "",
        f"- Class: `{args.class_name}`",
        f"- Method: `{args.method}`",
        f"- Module: `{args.module}`",
        f"- Init kwargs: `{json.dumps(init_kwargs, ensure_ascii=False)}`",
        f"- Method args: `{json.dumps(method_args, ensure_ascii=False)}`",
        f"- Method kwargs: `{json.dumps(method_kwargs, ensure_ascii=False)}`",
        f"- Result type: `{serial.get('type')}`",
    ]

    if serial.get("type") == "dataframe":
        lines.append(f"- Shape: `{serial.get('shape')}`")
        cols = serial.get("columns", [])[:20]
        lines.append(f"- Columns sample: `{cols}`")
    md_path.write_text("\n".join(lines), encoding="utf-8")

    (Path(outdir) / "invoke_latest.json").write_text(str(json_path), encoding="utf-8")
    (Path(outdir) / "invoke_latest.md").write_text(str(md_path), encoding="utf-8")

    print(f"Saved: {json_path}")
    print(f"Saved: {md_path}")


if __name__ == "__main__":
    main()
