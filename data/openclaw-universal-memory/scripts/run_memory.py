#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def _find_repo_root() -> Path:
    here = Path(__file__).resolve()
    return here.parents[3]


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="OpenClaw universal memory launcher")
    p.add_argument(
        "--action",
        required=True,
        choices=[
            "init-schema",
            "ingest-json",
            "ingest-connector",
            "validate-connector",
            "search",
            "events",
            "doctor",
            "configure-dsn",
        ],
    )
    p.add_argument("--dsn", default="")
    p.add_argument(
        "--dsn-env",
        default="DATABASE_DSN",
        help="Environment variable to read DSN from if --dsn is not provided",
    )
    p.add_argument("--dsn-file", default="", help="Path to env-style file with DATABASE_DSN=...")
    p.add_argument("--dsn-key", default="DATABASE_DSN")
    p.add_argument("--source")
    p.add_argument("--connector")
    p.add_argument("--connector-config", default="")
    p.add_argument("--account")
    p.add_argument("--entity-type")
    p.add_argument("--input")
    p.add_argument("--query")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--cursor", default="")
    p.add_argument("--id-field", default="id")
    p.add_argument("--title-field", default="title")
    p.add_argument("--body-field", default="body")
    p.add_argument("--config-path", default="")
    p.add_argument("--force", action="store_true")
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    repo_root = _find_repo_root()
    subprocess_env = os.environ.copy()
    if args.dsn.strip():
        subprocess_env[args.dsn_env] = args.dsn.strip()
    repo_src = str((repo_root / "src").resolve())
    existing_pythonpath = subprocess_env.get("PYTHONPATH", "").strip()
    subprocess_env["PYTHONPATH"] = f"{repo_src}:{existing_pythonpath}" if existing_pythonpath else repo_src

    base = [
        sys.executable,
        "-m",
        "openclaw_memory.cli",
        args.action,
        "--dsn-env",
        args.dsn_env,
        "--dsn-file",
        args.dsn_file,
        "--dsn-key",
        args.dsn_key,
    ]
    if args.action == "configure-dsn":
        if args.dsn.strip():
            base.extend(["--dsn", args.dsn.strip()])
        if args.config_path.strip():
            base.extend(["--config-path", args.config_path.strip()])
        if args.force:
            base.append("--force")
        result = subprocess.run(base, cwd=repo_root, capture_output=True, text=True, env=subprocess_env)
        if result.stdout:
            print(result.stdout.strip())
        if result.stderr:
            print(result.stderr.strip(), file=sys.stderr)
        raise SystemExit(result.returncode)
    if args.action == "ingest-json":
        required = {
            "source": args.source,
            "account": args.account,
            "entity_type": args.entity_type,
            "input": args.input,
        }
        missing = [k for k, v in required.items() if not v]
        if missing:
            print(json.dumps({"ok": False, "error": f"Missing required args: {', '.join(missing)}"}, indent=2))
            raise SystemExit(2)
        base.extend(
            [
                "--source",
                args.source,
                "--account",
                args.account,
                "--entity-type",
                args.entity_type,
                "--input",
                args.input,
                "--limit",
                str(args.limit),
                "--cursor",
                args.cursor,
                "--id-field",
                args.id_field,
                "--title-field",
                args.title_field,
                "--body-field",
                args.body_field,
            ]
        )
    elif args.action in {"ingest-connector", "validate-connector"}:
        required = {
            "connector": args.connector,
            "account": args.account,
        }
        missing = [k for k, v in required.items() if not v]
        if missing:
            print(json.dumps({"ok": False, "error": f"Missing required args: {', '.join(missing)}"}, indent=2))
            raise SystemExit(2)
        base.extend(
            [
                "--connector",
                args.connector,
                "--account",
                args.account,
                "--limit",
                str(args.limit),
                "--cursor",
                args.cursor,
                "--connector-config",
                args.connector_config,
            ]
        )
        if args.source:
            base.extend(["--source", args.source])
        if args.action == "ingest-connector" and args.entity_type:
            base.extend(["--entity-type", args.entity_type])
    elif args.action == "search":
        if not args.query:
            print(json.dumps({"ok": False, "error": "Missing required arg: --query"}, indent=2))
            raise SystemExit(2)
        base.extend(["--query", args.query, "--limit", str(args.limit)])
        if args.source:
            base.extend(["--source", args.source])
        if args.account:
            base.extend(["--account", args.account])
        if args.entity_type:
            base.extend(["--entity-type", args.entity_type])
    elif args.action == "events":
        base.extend(["--limit", str(args.limit)])

    result = subprocess.run(base, cwd=repo_root, capture_output=True, text=True, env=subprocess_env)
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip(), file=sys.stderr)
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
