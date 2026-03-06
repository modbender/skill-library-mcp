#!/usr/bin/env python3
"""TBOT status + discovery (read-only).

Purpose:
- Provide a *single* read-only probe endpoint that can infer where TBOT is running.
- Return structured JSON so OpenClaw can proceed without asking the user when possible.

This file MUST remain read-only:
- no start/stop/restart
- no writes
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import subprocess
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib.error import URLError
from urllib.request import Request, urlopen


def _run_capture(cmd: List[str], cwd: str | None = None) -> Tuple[int, str, str]:
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def _which_ok(bin_name: str) -> bool:
    rc, _, _ = _run_capture(["bash", "-lc", f"command -v {bin_name} >/dev/null 2>&1"])
    return rc == 0


@dataclass(frozen=True)
class ResolvedRuntime:
    mode: str  # "docker" | "systemd"
    compose_dir: str | None = None
    service_name: str | None = None
    systemd_user: int | None = None  # 1 or 0
    confidence: float = 0.0
    reason: str = ""

    def to_json(self) -> Dict[str, Any]:
        return {
            "mode": self.mode,
            "compose_dir": self.compose_dir,
            "service_name": self.service_name,
            "systemd_user": self.systemd_user,
            "confidence": self.confidence,
            "reason": self.reason,
        }


def _env_contract_probe() -> Optional[ResolvedRuntime]:
    mode = os.getenv("MODE", "").strip()
    if not mode:
        return None

    if mode == "docker":
        compose_dir = os.getenv("COMPOSE_DIR", "").strip()
        if compose_dir:
            return ResolvedRuntime(
                mode="docker",
                compose_dir=compose_dir,
                confidence=1.0,
                reason="MODE and COMPOSE_DIR set in environment",
            )
        return ResolvedRuntime(
            mode="docker",
            compose_dir=None,
            confidence=0.4,
            reason="MODE=docker set, but COMPOSE_DIR missing",
        )

    if mode == "systemd":
        service = os.getenv("SERVICE_NAME", "").strip()
        sys_user = 1 if os.getenv("SYSTEMD_USER", "1") == "1" else 0
        if service:
            return ResolvedRuntime(
                mode="systemd",
                service_name=service,
                systemd_user=sys_user,
                confidence=1.0,
                reason="MODE and SERVICE_NAME set in environment",
            )
        return ResolvedRuntime(
            mode="systemd",
            service_name=None,
            systemd_user=sys_user,
            confidence=0.4,
            reason="MODE=systemd set, but SERVICE_NAME missing",
        )

    # Unknown MODE value
    return ResolvedRuntime(
        mode=mode,
        confidence=0.2,
        reason="Unknown MODE value in environment",
    )


def _find_compose_files(start_dir: Path, max_depth: int = 4) -> List[Path]:
    # Read-only heuristic: look for docker-compose/compose files nearby.
    names = {"docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"}
    results: List[Path] = []

    def depth(p: Path) -> int:
        try:
            return len(p.relative_to(start_dir).parts)
        except Exception:
            return 999

    for p in start_dir.rglob("*"):
        if p.is_file() and p.name in names:
            d = depth(p)
            if d <= max_depth:
                results.append(p)
    return results


def _docker_compose_probe(repo_root: Path) -> List[ResolvedRuntime]:
    out: List[ResolvedRuntime] = []
    if not _which_ok("docker"):
        return out

    # Prefer compose files near this repo (common dev setup).
    candidates = _find_compose_files(repo_root.parent, max_depth=4)

    def score_path(p: Path) -> float:
        """Heuristic preference:
        - Prefer openclaw-on-tradingboat
        - De-prioritize ib-gateway-docker
        - Prefer shallower paths (closer to repo_root.parent)
        """
        s = 0.0
        parts = [x.lower() for x in p.parts]
        joined = "/".join(parts)
        if "openclaw-on-tradingboat" in joined:
            s += 10.0
        if "ib-gateway-docker" in joined:
            s -= 5.0
        # Shallower is better
        try:
            depth = len(p.relative_to(repo_root.parent).parts)
        except Exception:
            depth = 999
        s -= float(depth) * 0.25
        return s

    # Sort by preference so the most likely compose dir becomes the top candidate.
    candidates = sorted(candidates, key=score_path, reverse=True)

    for f in candidates:
        compose_dir = str(f.parent)
        # Validate compose config is parseable (read-only).
        rc, _, _ = _run_capture(["docker", "compose", "-f", str(f), "config"])
        if rc == 0:
            # Confidence reflects that we found a parseable compose file; boost if it matches preferred stack.
            conf = 0.6
            low = str(f).lower()
            if "openclaw-on-tradingboat" in low:
                conf = 0.8
            if "ib-gateway-docker" in low:
                conf = 0.45

            out.append(
                ResolvedRuntime(
                    mode="docker",
                    compose_dir=compose_dir,
                    confidence=conf,
                    reason=f"Found compose file: {f}",
                )
            )

    return out


def _docker_ps_probe() -> List[ResolvedRuntime]:
    out: List[ResolvedRuntime] = []
    if not _which_ok("docker"):
        return out

    rc, stdout, _ = _run_capture(["docker", "ps", "--format", "{{.Names}}\t{{.Image}}"])
    if rc != 0:
        return out

    hits = []
    for line in stdout.splitlines():
        low = line.lower()
        # Match common container names in openclaw-on-tradingboat
        if any(k in low for k in ("tbot", "tradingboat", "tvwb", "ib-gateway", "ibgateway", "redis-on-tradingboat")):
            hits.append(line)

    if hits:
        out.append(
            ResolvedRuntime(
                mode="docker",
                confidence=0.5,
                reason=f"Found running containers matching tbot/tradingboat/tvwb: {hits[:5]}",
            )
        )
    return out


def _systemd_probe() -> List[ResolvedRuntime]:
    out: List[ResolvedRuntime] = []
    if not _which_ok("systemctl"):
        return out

    # Probe --user first (most common for OpenClaw-style daemons).
    for sys_user in (1, 0):
        cmd = ["systemctl"]
        if sys_user == 1:
            cmd.append("--user")
        cmd += ["list-units", "--type=service", "--all", "--no-pager"]

        rc, stdout, _ = _run_capture(cmd)
        if rc != 0:
            continue

        services = []
        for line in stdout.splitlines():
            low = line.lower()
            if any(k in low for k in ("tbot", "tradingboat", "tvwb")):
                # First column tends to be service name.
                parts = line.split()
                if parts:
                    services.append(parts[0])

        # Deduplicate
        services = sorted(set(services))
        for s in services:
            out.append(
                ResolvedRuntime(
                    mode="systemd",
                    service_name=s,
                    systemd_user=sys_user,
                    confidence=0.55,
                    reason=f"Matched systemd unit listing (SYSTEMD_USER={sys_user})",
                )
            )
    return out


def discover(repo_root: Path) -> Dict[str, Any]:
    env_hint = _env_contract_probe()

    candidates: List[ResolvedRuntime] = []
    if env_hint is not None:
        # If env provides a fully resolved config, return it as selected.
        if env_hint.confidence >= 0.99 and (
            (env_hint.mode == "docker" and env_hint.compose_dir)
            or (env_hint.mode == "systemd" and env_hint.service_name)
        ):
            return {
                "selected": env_hint.to_json(),
                "candidates": [],
                "needs_input": False,
                "how_to_use": _how_to_use(env_hint),
            }
        # Otherwise keep it as a candidate/hint and continue probing.
        candidates.append(env_hint)

    candidates.extend(_docker_compose_probe(repo_root))
    candidates.extend(_docker_ps_probe())
    candidates.extend(_systemd_probe())

    # Pick highest confidence *with required fields present*.
    best: Optional[ResolvedRuntime] = None
    for c in candidates:
        ok = (c.mode == "docker" and c.compose_dir) or (c.mode == "systemd" and c.service_name)
        if not ok:
            continue
        if best is None or c.confidence > best.confidence:
            best = c

    # If multiple plausible docker compose dirs exist, keep them as candidates.
    needs_input = best is None

    return {
        "selected": best.to_json() if best else None,
        "candidates": [c.to_json() for c in candidates],
        "needs_input": needs_input,
        "ask_user": (
            "Provide COMPOSE_DIR (folder containing docker-compose.yml/compose.yaml) "
            "or SERVICE_NAME (+ SYSTEMD_USER=1/0) if discovery is ambiguous."
        )
        if needs_input
        else None,
        "how_to_use": _how_to_use(best) if best else None,
    }


def _how_to_use(rt: Optional[ResolvedRuntime]) -> Dict[str, str] | None:
    if rt is None:
        return None
    if rt.mode == "docker" and rt.compose_dir:
        return {
            "status": f'MODE=docker COMPOSE_DIR="{rt.compose_dir}" bash scripts/tbot.sh ctl status',
            "logs": f'MODE=docker COMPOSE_DIR="{rt.compose_dir}" bash scripts/tbot.sh ctl logs --tail 200',
        }
    if rt.mode == "systemd" and rt.service_name is not None and rt.systemd_user is not None:
        return {
            "status": (
                f'MODE=systemd SERVICE_NAME="{rt.service_name}" SYSTEMD_USER="{rt.systemd_user}" '
                "bash scripts/tbot.sh ctl status"
            ),
            "logs": (
                f'MODE=systemd SERVICE_NAME="{rt.service_name}" SYSTEMD_USER="{rt.systemd_user}" '
                "bash scripts/tbot.sh ctl logs --tail 200"
            ),
        }
    return None


def cmd_discover(_: argparse.Namespace) -> int:
    repo_root = Path(__file__).resolve().parent
    result = discover(repo_root)
    print(json.dumps(result, indent=2))
    return 0


def _resolve_db_path(cli_path: str | None) -> str:
    if cli_path:
        return cli_path
    env_path = os.getenv("TBOT_DB_PATH", "").strip()
    if env_path:
        return env_path
    env_office = os.getenv("TBOT_DB_OFFICE", "").strip()
    if env_office:
        return env_office
    return ""


def _connect_db_ro(path: str) -> sqlite3.Connection:
    if not path:
        raise SystemExit(
            "DB path not provided. Set TBOT_DB_PATH or TBOT_DB_OFFICE or pass --db-path."
        )
    if not Path(path).exists():
        raise SystemExit(
            f"DB file not found: {path}\n"
            "If TBOT runs in Docker, bind-mount its DB directory to the host first."
        )
    # Enforce read-only connection.
    return sqlite3.connect(f"file:{path}?mode=ro", uri=True)


def _query_rows(conn: sqlite3.Connection, sql: str, params: Tuple[Any, ...]) -> List[Dict[str, Any]]:
    conn.row_factory = sqlite3.Row
    cur = conn.execute(sql, params)
    rows = cur.fetchall()
    return [{k: row[k] for k in row.keys()} for row in rows]


def _fmt_money(v: Any) -> str:
    try:
        return f"{float(v):,.2f}"
    except Exception:
        return str(v)


def _fmt_num(v: Any) -> str:
    try:
        f = float(v)
        if f.is_integer():
            return str(int(f))
        return f"{f:,.4f}".rstrip("0").rstrip(".")
    except Exception:
        return str(v)


def _format_table(headers: List[str], rows: Iterable[List[str]]) -> str:
    rows_list = [headers] + [list(r) for r in rows]
    widths = [0] * len(headers)
    for row in rows_list:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))
    lines: List[str] = []
    lines.append(" | ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(headers)))
    lines.append("-+-".join("-" * w for w in widths))
    for row in rows_list[1:]:
        lines.append(" | ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(row)))
    return "\n".join(lines)


def _summary_portfolio(rows: List[Dict[str, Any]]) -> str:
    headers = ["TICKER", "POS", "MRKVAL", "UnrealPnL", "AVGPX", "TV_PX", "STATUS"]
    table_rows: List[List[str]] = []
    totals = defaultdict(float)
    for r in rows:
        totals["mrkvalue"] += float(r.get("mrkvalue") or 0)
        totals["unrealizedpnl"] += float(r.get("unrealizedpnl") or 0)
        totals["realizedpnl"] += float(r.get("realizedpnl") or 0)
        table_rows.append(
            [
                str(r.get("ticker", "")),
                _fmt_num(r.get("position", "")),
                _fmt_money(r.get("mrkvalue", "")),
                _fmt_money(r.get("unrealizedpnl", "")),
                _fmt_num(r.get("avgprice", "")),
                _fmt_num(r.get("tv_price", "")),
                str(r.get("orderstatus", "")),
            ]
        )
    out = []
    out.append("Totals:")
    out.append(f"- Market value: {_fmt_money(totals['mrkvalue'])}")
    out.append(f"- Unrealized PnL: {_fmt_money(totals['unrealizedpnl'])}")
    out.append(f"- Realized PnL: {_fmt_money(totals['realizedpnl'])}")
    out.append("")
    out.append(_format_table(headers, table_rows))
    return "\n".join(out)


def _summary_orders(rows: List[Dict[str, Any]]) -> str:
    headers = [
        "TBOT_TIME",
        "ORD_TIME",
        "TICKER",
        "TV_Close",
        "ACTION",
        "TYPE",
        "QTY",
        "LIMIT",
        "STOP",
        "ORDERID",
        "ORDERREF",
        "STATUS",
        "POS",
        "MRKVAL",
        "AVGF",
        "UnrealPnL",
        "RealPnL",
    ]
    table_rows: List[List[str]] = []
    totals = defaultdict(float)
    for r in rows:
        totals["mrkvalue"] += float(r.get("mrkvalue") or 0)
        totals["unrealizedpnl"] += float(r.get("unrealizedpnl") or 0)
        totals["realizedpnl"] += float(r.get("realizedpnl") or 0)
        table_rows.append(
            [
                str(r.get("uniquekey", "")),
                str(r.get("timestamp", "")),
                str(r.get("ticker", "")),
                _fmt_num(r.get("tv_price", "")),
                str(r.get("action", "")),
                str(r.get("ordertype", "")),
                _fmt_num(r.get("qty", "")),
                _fmt_num(r.get("lmtprice", "")),
                _fmt_num(r.get("auxprice", "")),
                str(r.get("orderid", "")),
                str(r.get("orderref", "")),
                str(r.get("orderstatus", "")),
                _fmt_num(r.get("position", "")),
                _fmt_money(r.get("mrkvalue", "")),
                _fmt_num(r.get("avgfillprice", "")),
                _fmt_money(r.get("unrealizedpnl", "")),
                _fmt_money(r.get("realizedpnl", "")),
            ]
        )
    out = []
    out.append("Totals:")
    out.append(f"- Market value: {_fmt_money(totals['mrkvalue'])}")
    out.append(f"- Unrealized PnL: {_fmt_money(totals['unrealizedpnl'])}")
    out.append(f"- Realized PnL: {_fmt_money(totals['realizedpnl'])}")
    out.append("")
    out.append(_format_table(headers, table_rows))
    return "\n".join(out)


def _summary_alerts(rows: List[Dict[str, Any]]) -> str:
    headers = [
        "TV_TIME",
        "TBOT_TIME",
        "TICKER",
        "DIRECTION",
        "QTY",
        "ORDERREF",
        "ALERTSTAT",
        "ENTLMT",
        "ENTSTP",
        "EXTLMT",
        "EXTSTP",
        "PRICE",
    ]
    table_rows = [
        [
            str(r.get("tv_timestamp", "")),
            str(r.get("uniquekey", "")),
            str(r.get("ticker", "")),
            str(r.get("direction", "")),
            _fmt_num(r.get("qty", "")),
            str(r.get("orderref", "")),
            str(r.get("alertstatus", "")),
            _fmt_num(r.get("entrylimit", "")),
            _fmt_num(r.get("entrystop", "")),
            _fmt_num(r.get("exitlimit", "")),
            _fmt_num(r.get("exitstop", "")),
            _fmt_num(r.get("tv_price", "")),
        ]
        for r in rows
    ]
    return _format_table(headers, table_rows)


def _summary_errors(rows: List[Dict[str, Any]]) -> str:
    headers = ["TBOT_TIME", "REQID", "ERRCODE", "SYMBOL", "ERRSTR"]
    table_rows = [
        [
            str(r.get("timestamp", "")),
            str(r.get("reqid", "")),
            str(r.get("errcode", "")),
            str(r.get("symbol", "")),
            str(r.get("errstr", "")),
        ]
        for r in rows
    ]
    return _format_table(headers, table_rows)


def _summary_tbot(rows: List[Dict[str, Any]]) -> str:
    headers = [
        "TV_TIME",
        "TBOT_TIME",
        "ORD_TIME",
        "TICKER",
        "TV_$",
        "AVG_$",
        "DIRECTION",
        "ACT",
        "TYPE",
        "QTY",
        "POS",
        "O_REF",
        "STATUS",
    ]
    table_rows = [
        [
            str(r.get("tv_timestamp", "")),
            str(r.get("uniquekey", "")),
            str(r.get("timestamp", "")),
            str(r.get("ticker", "")),
            _fmt_num(r.get("tv_price", "")),
            _fmt_num(r.get("avgprice", "")),
            str(r.get("direction", "")),
            str(r.get("action", "")),
            str(r.get("ordertype", "")),
            _fmt_num(r.get("qty", "")),
            _fmt_num(r.get("position", "")),
            str(r.get("orderref", "")),
            str(r.get("orderstatus", "")),
        ]
        for r in rows
    ]
    return _format_table(headers, table_rows)


def cmd_db(args: argparse.Namespace) -> int:
    db_path = _resolve_db_path(args.db_path)
    conn = _connect_db_ro(db_path)

    limit = int(args.limit)
    if limit <= 0 or limit > 5000:
        raise SystemExit("--limit must be between 1 and 5000")

    if args.table == "orders":
        sql = "SELECT * FROM TBOTORDERS ORDER BY rowid DESC LIMIT ?"
        rows = _query_rows(conn, sql, (limit,))
    elif args.table == "alerts":
        sql = "SELECT * FROM TBOTALERTS ORDER BY rowid DESC LIMIT ?"
        rows = _query_rows(conn, sql, (limit,))
    elif args.table == "errors":
        sql = "SELECT * FROM TBOTERRORS ORDER BY rowid DESC LIMIT ?"
        rows = _query_rows(conn, sql, (limit,))
    elif args.table == "tbot":
        sql = (
            "SELECT "
            "TBOTORDERS.timestamp, "
            "TBOTORDERS.uniquekey, "
            "TBOTALERTS.tv_timestamp, "
            "TBOTALERTS.ticker, "
            "TBOTALERTS.tv_price, "
            "TBOTORDERS.avgprice, "
            "TBOTALERTS.direction, "
            "TBOTORDERS.action, "
            "TBOTORDERS.ordertype, "
            "TBOTORDERS.qty, "
            "TBOTORDERS.position, "
            "TBOTALERTS.orderref, "
            "TBOTORDERS.orderstatus "
            "FROM TBOTORDERS INNER JOIN TBOTALERTS "
            "ON TBOTALERTS.orderref = TBOTORDERS.orderref "
            "AND TBOTALERTS.uniquekey = TBOTORDERS.uniquekey "
            "ORDER BY TBOTORDERS.uniquekey DESC "
            "LIMIT ?"
        )
        rows = _query_rows(conn, sql, (limit,))
    else:
        raise SystemExit(f"Unknown table: {args.table}")

    if args.format == "json":
        print(json.dumps({"data": rows}, indent=2))
        return 0
    if args.table == "orders":
        print(_summary_orders(rows))
        return 0
    if args.table == "alerts":
        print(_summary_alerts(rows))
        return 0
    if args.table == "errors":
        print(_summary_errors(rows))
        return 0
    if args.table == "tbot":
        print(_summary_tbot(rows))
        return 0
    raise SystemExit(f"Unknown table: {args.table}")


def cmd_portfolio(args: argparse.Namespace) -> int:
    db_path = _resolve_db_path(args.db_path)
    conn = _connect_db_ro(db_path)
    limit = int(args.limit)
    if limit <= 0 or limit > 5000:
        raise SystemExit("--limit must be between 1 and 5000")

    sql = (
        "SELECT * FROM TBOTORDERS "
        "WHERE orderstatus = 'Portfolio' "
        "ORDER BY rowid DESC LIMIT ?"
    )
    rows = _query_rows(conn, sql, (limit,))

    if args.format == "json":
        print(json.dumps({"data": rows}, indent=2))
        return 0
    print(_summary_portfolio(rows))
    return 0


def cmd_errors(args: argparse.Namespace) -> int:
    db_path = _resolve_db_path(args.db_path)
    conn = _connect_db_ro(db_path)
    limit = int(args.limit)
    if limit <= 0 or limit > 5000:
        raise SystemExit("--limit must be between 1 and 5000")

    sql = "SELECT * FROM TBOTERRORS ORDER BY rowid DESC LIMIT ?"
    rows = _query_rows(conn, sql, (limit,))

    if args.group:
        # Group by errcode + errstr for quick diagnosis.
        counts: Dict[str, int] = defaultdict(int)
        for r in rows:
            key = f"{r.get('errcode')} | {r.get('errstr')}"
            counts[key] += 1
        headers = ["COUNT", "ERRCODE | ERRSTR"]
        table_rows = [[str(v), k] for k, v in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))]
        print(_format_table(headers, table_rows))
        return 0

    if args.format == "json":
        print(json.dumps({"data": rows}, indent=2))
        return 0
    print(_summary_errors(rows))
    return 0


def _http_get_json(url: str, timeout_s: int = 4) -> Tuple[int, Optional[Dict[str, Any]], str]:
    try:
        req = Request(url, headers={"User-Agent": "openclaw-skill-tbot-controller"})
        with urlopen(req, timeout=timeout_s) as resp:
            status = getattr(resp, "status", 200)
            body = resp.read().decode("utf-8", errors="replace")
            try:
                return status, json.loads(body), ""
            except Exception:
                return status, None, body[:200]
    except URLError as e:
        return 0, None, str(e)


def cmd_health(args: argparse.Namespace) -> int:
    base = args.base_url.rstrip("/")
    endpoints = ["/orders/data", "/tbot/data"]
    rows_out: List[List[str]] = []
    for ep in endpoints:
        url = f"{base}{ep}"
        status, data, extra = _http_get_json(url, timeout_s=args.timeout)
        if status == 0:
            rows_out.append([ep, "ERR", extra or "connection error", "-"])
            continue
        if isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
            rows_out.append([ep, str(status), "ok", str(len(data["data"]))])
        else:
            rows_out.append([ep, str(status), "non-json", extra or "-"])
    print(_format_table(["ENDPOINT", "STATUS", "RESULT", "ROWS"], rows_out))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="tbotstatus", description="TBOT read-only probe & discovery")
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("discover", help="Infer MODE/COMPOSE_DIR/SERVICE_NAME (read-only)")
    db = sub.add_parser("db", help="Read TBOT sqlite DB (read-only)")
    db.add_argument(
        "--table",
        required=True,
        choices=["orders", "alerts", "errors", "tbot"],
        help="Which dataset to read",
    )
    db.add_argument("--format", choices=["json", "summary"], default="json")
    db.add_argument("--limit", type=int, default=100)
    db.add_argument("--db-path", help="Override DB path (defaults to TBOT_DB_PATH or TBOT_DB_OFFICE)")

    portfolio = sub.add_parser("portfolio", help="Portfolio snapshot from TBOTORDERS (read-only)")
    portfolio.add_argument("--format", choices=["json", "summary"], default="summary")
    portfolio.add_argument("--limit", type=int, default=200)
    portfolio.add_argument("--db-path", help="Override DB path (defaults to TBOT_DB_PATH or TBOT_DB_OFFICE)")

    errors = sub.add_parser("errors", help="Tail TBOT errors (read-only)")
    errors.add_argument("--format", choices=["json", "summary"], default="summary")
    errors.add_argument("--limit", type=int, default=200)
    errors.add_argument("--group", action="store_true", help="Group by errcode+errstr")
    errors.add_argument("--db-path", help="Override DB path (defaults to TBOT_DB_PATH or TBOT_DB_OFFICE)")

    health = sub.add_parser("health", help="HTTP health checks for TBOT UI (read-only)")
    health.add_argument("--base-url", default="http://127.0.0.1:5001")
    health.add_argument("--timeout", type=int, default=4)
    return p


def main(argv: List[str]) -> int:
    p = build_parser()
    args = p.parse_args(argv)

    if not args.cmd:
        p.print_help()
        return 0

    if args.cmd == "discover":
        return cmd_discover(args)
    if args.cmd == "db":
        return cmd_db(args)
    if args.cmd == "portfolio":
        return cmd_portfolio(args)
    if args.cmd == "errors":
        return cmd_errors(args)
    if args.cmd == "health":
        return cmd_health(args)

    raise SystemExit(f"Unknown command: {args.cmd}")


if __name__ == "__main__":
    raise SystemExit(main(os.sys.argv[1:]))
