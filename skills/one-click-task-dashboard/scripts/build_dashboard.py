#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import pathlib
import plistlib
import re
import subprocess
from typing import Any, Dict, List, Optional

try:
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover
    ZoneInfo = None


TZ = ZoneInfo("Asia/Shanghai") if ZoneInfo else None
KNOWN_LABELS = [
    "ai.x.xiaoe-daily-leads",
    "ai.x.xiaoe-monthly-leads",
    "ai.xiazai.feishu-pv-uv",
    "ai.x.tax-refund-reminder",
    "ai.x.prevent-sleep",
    "ai.openclaw.gateway",
]
LABEL_ALIAS = {
    "ai.x.xiaoe-daily-leads": "小鹅通日新增统计",
    "ai.x.xiaoe-monthly-leads": "小鹅通月新增统计",
    "ai.xiazai.feishu-pv-uv": "飞书 PV/UV 夜间采集",
    "ai.x.tax-refund-reminder": "退税提醒广播",
    "ai.x.prevent-sleep": "防休眠守护",
    "ai.openclaw.gateway": "OpenClaw 网关服务",
}
CRON_ALIAS = {"ip_wechat_family_daily": "公众号自动发文（日更）"}


def now_local() -> dt.datetime:
    if TZ:
        return dt.datetime.now(TZ)
    return dt.datetime.now()


def resolve_openclaw_bin() -> str:
    candidates: List[pathlib.Path] = [
        pathlib.Path("/opt/homebrew/bin/openclaw"),
        pathlib.Path.home() / ".local/bin/openclaw",
        pathlib.Path.home() / ".npm-global/bin/openclaw",
    ]
    nvm_root = pathlib.Path.home() / ".nvm/versions/node"
    if nvm_root.exists():
        for p in sorted(nvm_root.glob("*/bin/openclaw"), reverse=True):
            candidates.append(p)
    for p in candidates:
        if p.exists():
            return str(p)
    return "openclaw"


def run_cmd(args: List[str]) -> str:
    env = os.environ.copy()
    if args and args[0] == "openclaw":
        args = list(args)
        args[0] = resolve_openclaw_bin()
        env["HOME"] = str(pathlib.Path.home())
        bin_dir = str(pathlib.Path(args[0]).parent) if "/" in args[0] else ""
        base = env.get("PATH", "/usr/bin:/bin:/usr/sbin:/sbin")
        if bin_dir and bin_dir not in base.split(":"):
            env["PATH"] = f"{bin_dir}:{base}"
    try:
        cp = subprocess.run(args, capture_output=True, text=True, check=False, env=env)
        return (cp.stdout or "").strip()
    except Exception:
        return ""


def run_json(args: List[str]) -> Optional[Dict[str, Any]]:
    raw = run_cmd(args)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except Exception:
        return None


def parse_time(text: str) -> Optional[dt.datetime]:
    if not text:
        return None
    text = text.strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            v = dt.datetime.strptime(text, fmt)
            if TZ:
                v = v.replace(tzinfo=TZ)
            return v
        except ValueError:
            continue
    return None


def fmt_dt(v: Optional[dt.datetime]) -> str:
    if not v:
        return "-"
    return v.strftime("%Y-%m-%d %H:%M:%S")


def read_last_jsonl(path: pathlib.Path, ok_only: bool = False) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    for line in reversed(lines):
        s = line.strip()
        if not s:
            continue
        try:
            obj = json.loads(s)
        except json.JSONDecodeError:
            continue
        if ok_only and str(obj.get("status", "")).upper() != "OK":
            continue
        return obj
    return None


def launchctl_state_map() -> Dict[str, Dict[str, str]]:
    out = run_cmd(["launchctl", "list"])
    result: Dict[str, Dict[str, str]] = {}
    for line in out.splitlines():
        line = line.strip()
        if not line or line.startswith("PID"):
            continue
        parts = re.split(r"\s+", line)
        if len(parts) < 3:
            continue
        pid, status, label = parts[0], parts[1], parts[2]
        result[label] = {"pid": pid, "status": status}
    return result


def parse_schedule(v: Any) -> str:
    if v is None:
        return "-"
    if isinstance(v, int):
        return f"每 {v} 秒"
    if isinstance(v, dict):
        day = v.get("Day")
        hour = int(v.get("Hour", 0))
        minute = int(v.get("Minute", 0))
        if day is not None:
            return f"每月{int(day)}日 {hour:02d}:{minute:02d}"
        return f"每日 {hour:02d}:{minute:02d}"
    if isinstance(v, list):
        slots = []
        for it in v:
            if isinstance(it, dict):
                slots.append(f"{int(it.get('Hour', 0)):02d}:{int(it.get('Minute', 0)):02d}")
        if slots:
            return "每日 " + ", ".join(slots)
    return str(v)


def calc_run_state(last_run: Optional[dt.datetime], schedule_text: str) -> str:
    now = now_local()
    if last_run and last_run.date() == now.date():
        return "已跑"
    m_daily = re.match(r"每日 (\d{2}):(\d{2})$", schedule_text)
    if m_daily:
        h, m = int(m_daily.group(1)), int(m_daily.group(2))
        target = now.replace(hour=h, minute=m, second=0, microsecond=0)
        return "未跑" if now >= target else "待跑"
    return "待跑"


def get_wechat_latest() -> Dict[str, str]:
    logs_dir = pathlib.Path("/Users/dong/.openclaw/shrimp_workspaces/ip_ops_xia/output/wechat/logs")
    files = sorted(logs_dir.glob("*-run.md"), reverse=True)
    if not files:
        return {"status": "UNKNOWN", "title": "-", "publish_link": "无", "time": "-", "note": "无日志"}
    p = files[0]
    txt = p.read_text(encoding="utf-8", errors="ignore")
    m_status = re.search(r"- 状态：(.+)", txt)
    m_title = re.search(r"- 最终选题：(.+)", txt)
    m_link = re.search(r"- 发布链接：(.+)", txt)
    m_time = re.search(r"- 运行时间戳：(.+)", txt)
    return {
        "status": (m_status.group(1).strip() if m_status else "UNKNOWN"),
        "title": (m_title.group(1).strip() if m_title else "-"),
        "publish_link": (m_link.group(1).strip() if m_link else "无"),
        "time": (m_time.group(1).strip() if m_time else dt.datetime.fromtimestamp(p.stat().st_mtime, TZ).strftime("%Y-%m-%d %H:%M:%S")),
        "note": p.name,
    }


def get_jobs() -> List[Dict[str, Any]]:
    jobs: List[Dict[str, Any]] = []
    now = now_local()

    cron = run_json(["openclaw", "cron", "list", "--json"]) or {"jobs": []}
    for j in cron.get("jobs", []):
        st = j.get("state", {})
        last_ms = st.get("lastRunAtMs")
        next_ms = st.get("nextRunAtMs")
        last_run = dt.datetime.fromtimestamp(last_ms / 1000, TZ) if last_ms else None
        next_run = dt.datetime.fromtimestamp(next_ms / 1000, TZ) if next_ms else None
        raw_name = str(j.get("name") or "openclaw_cron_task")
        pretty = CRON_ALIAS.get(raw_name, raw_name)
        wechat = get_wechat_latest() if j.get("agentId") == "ip_ops_xia" else {}
        jobs.append(
            {
                "task": pretty,
                "task_id": f"{raw_name} · OpenClaw",
                "schedule": f"cron: {j.get('schedule', {}).get('expr', '-')}",
                "state": "已跑" if last_run and last_run.date() == now.date() else ("待跑" if next_run and next_run > now else "未跑"),
                "result": str(st.get("lastRunStatus") or st.get("lastStatus") or "-").upper(),
                "last_run": fmt_dt(last_run),
                "next_run": fmt_dt(next_run),
                "summary": (
                    f"自动发文状态: {wechat.get('status', '-')} | 标题: {wechat.get('title', '-')}" if wechat else "-"
                ),
                "metric": (f"自动发文链接: {wechat.get('publish_link', '无')}" if wechat else "-"),
            }
        )

    launch_map = launchctl_state_map()
    launch_dir = pathlib.Path.home() / "Library/LaunchAgents"
    dynamic_labels = [k for k in launch_map if k.startswith("ai.")]
    labels = sorted(set(KNOWN_LABELS + dynamic_labels))

    daily_latest = read_last_jsonl(pathlib.Path("/Users/dong/.openclaw/workflows/xiaoe_monthly_leads/logs/daily_runs.jsonl"))
    daily_ok = read_last_jsonl(pathlib.Path("/Users/dong/.openclaw/workflows/xiaoe_monthly_leads/logs/daily_runs.jsonl"), ok_only=True)
    monthly_ok = read_last_jsonl(pathlib.Path("/Users/dong/.openclaw/workflows/xiaoe_monthly_leads/logs/runs.jsonl"), ok_only=True)
    feishu_ok = read_last_jsonl(pathlib.Path("/Users/dong/.openclaw/workflows/feishu_pv_uv/logs/runs.jsonl"), ok_only=True)

    for label in labels:
        plist = launch_dir / f"{label}.plist"
        if not plist.exists():
            continue
        try:
            cfg = plistlib.loads(plist.read_bytes())
        except Exception:
            cfg = {}
        schedule = parse_schedule(cfg.get("StartCalendarInterval") or cfg.get("StartInterval") or ("常驻" if cfg.get("KeepAlive") else None))
        st = launch_map.get(label, {"pid": "-", "status": "-"})
        summary, metric, last_run = "-", "-", None
        forced_result = None

        if label == "ai.x.xiaoe-daily-leads" and daily_latest:
            last_run = parse_time(str(daily_latest.get("time", "")))
            if str(daily_latest.get("status", "")).upper() == "OK":
                owner = daily_latest.get("owner_daily_added", {}) or {}
                summary = f"整体昨日新增: {((daily_latest.get('overall') or {}).get('added'))}"
                metric = f"陈硕: {owner.get('陈硕', 0)} | 王一淼: {owner.get('王一淼', 0)}"
            else:
                forced_result = "WARN"
                summary = "最近一次执行失败（已触发）"
                if daily_ok:
                    owner = daily_ok.get("owner_daily_added", {}) or {}
                    metric = f"上次成功 陈硕:{owner.get('陈硕', 0)} 王一淼:{owner.get('王一淼', 0)}"
        elif label == "ai.x.xiaoe-monthly-leads" and monthly_ok:
            last_run = parse_time(str(monthly_ok.get("time", "")))
            owner = monthly_ok.get("owner_monthly_added", {}) or {}
            summary = f"{monthly_ok.get('report_month', '-')} 月新增汇总"
            metric = f"陈硕: {owner.get('陈硕', 0)} | 王一淼: {owner.get('王一淼', 0)}"
        elif label == "ai.xiazai.feishu-pv-uv" and feishu_ok:
            last_run = parse_time(str(feishu_ok.get("timestamp", "")))
            summary = f"今日新增 PV/UV: {feishu_ok.get('daily_pv', '-')} / {feishu_ok.get('daily_uv', '-')}"
            metric = f"总 PV/UV: {feishu_ok.get('pv', '-')} / {feishu_ok.get('uv', '-')}"
        else:
            outp = cfg.get("StandardOutPath")
            if outp and pathlib.Path(outp).exists():
                last_run = dt.datetime.fromtimestamp(pathlib.Path(outp).stat().st_mtime, TZ)

        if label in ("ai.x.prevent-sleep", "ai.openclaw.gateway"):
            run_state = "运行中" if st.get("pid", "-") not in ("-", "0") else "未运行"
            result = "OK" if run_state == "运行中" else "ERROR"
        else:
            run_state = calc_run_state(last_run, schedule)
            result = "OK" if run_state in ("已跑", "待跑") else "WARN"
            if forced_result:
                result = forced_result

        jobs.append(
            {
                "task": LABEL_ALIAS.get(label, label),
                "task_id": label,
                "schedule": schedule,
                "state": run_state,
                "result": result,
                "last_run": fmt_dt(last_run),
                "next_run": "-",
                "summary": summary,
                "metric": metric,
            }
        )

    return jobs


def render_html(payload: Dict[str, Any]) -> str:
    jobs = payload["jobs"]
    total = len(jobs)
    ran = sum(1 for j in jobs if j["state"] == "已跑")
    waiting = sum(1 for j in jobs if j["state"] in ("待跑", "运行中"))
    missed = sum(1 for j in jobs if j["state"] in ("未跑", "未运行"))
    issues = sum(1 for j in jobs if j["result"] in ("WARN", "ERROR"))

    def chip_state(s: str) -> str:
        if s == "已跑":
            cls = "done"
        elif s == "待跑":
            cls = "wait"
        elif s == "运行中":
            cls = "live"
        else:
            cls = "bad"
        return f'<span class="chip {cls}">{html.escape(s)}</span>'

    rows = []
    for j in jobs:
        row_cls = "resident-row" if j.get("schedule") == "常驻" else ""
        rows.append(
            f"<tr class=\"{row_cls}\">"
            f"<td><div class=\"task-name\">{html.escape(j['task'])}</div><div class=\"task-id\">{html.escape(j.get('task_id', '-'))}</div></td>"
            f"<td>{html.escape(j['schedule'])}</td>"
            f"<td>{html.escape(j['last_run'])}</td>"
            f"<td>{chip_state(j['state'])}</td>"
            f"<td>{html.escape(j['summary'])}</td>"
            f"<td>{html.escape(j['metric'])}</td>"
            "</tr>"
        )

    refresh = html.escape(payload["generated_at"])
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>自动化任务数据大屏</title>
  <style>
    :root {{
      --bg:#f6f7f8; --card:#fff; --text:#111; --muted:#666; --line:#e7e7e7;
      --done:#d9f7e6; --wait:#dbeafe; --bad:#fee2e2; --live:#dcfce7;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin:0; background:var(--bg); color:var(--text); font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif; }}
    .wrap {{ max-width: 1180px; margin: 30px auto; padding: 0 18px; }}
    h1 {{ margin:0 0 10px; font-size:26px; font-weight:640; letter-spacing:0.4px; }}
    .meta {{ color:var(--muted); font-size:13px; margin-bottom:16px; }}
    .grid {{ display:grid; grid-template-columns: repeat(5, minmax(140px, 1fr)); gap: 10px; margin-bottom:18px; }}
    .card {{ background:var(--card); border:1px solid var(--line); border-radius:14px; padding:12px 14px; }}
    .k {{ font-size:12px; color:var(--muted); margin-bottom:6px; }}
    .v {{ font-size:26px; font-weight:640; letter-spacing:0.3px; }}
    table {{ width:100%; border-collapse: collapse; background:var(--card); border:1px solid var(--line); border-radius:14px; overflow:hidden; }}
    th, td {{ text-align:left; border-bottom:1px solid var(--line); padding:10px 12px; font-size:13px; vertical-align:top; }}
    th {{ color:#444; font-weight:600; background:#fafafa; }}
    tr:last-child td {{ border-bottom:none; }}
    .task-name {{ font-size:14px; font-weight:560; color:#111; margin-bottom:3px; }}
    .task-id {{ font-size:11px; color:#8a8a8a; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
    .chip {{ display:inline-flex; align-items:center; padding:4px 10px; border-radius:999px; font-size:12px; font-weight:600; border:1px solid rgba(0,0,0,0.05); }}
    .chip.done {{ background:var(--done); }}
    .chip.wait {{ background:var(--wait); }}
    .chip.bad {{ background:var(--bad); }}
    .chip.live {{ background:var(--live); }}
    .resident-row td {{ background:#f2fbf5; }}
    @media (max-width: 980px) {{
      .grid {{ grid-template-columns: repeat(2, minmax(140px, 1fr)); }}
      th:nth-child(2), td:nth-child(2), th:nth-child(6), td:nth-child(6) {{ display:none; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>自动化任务数据大屏</h1>
    <div class="meta">最后刷新：{refresh}</div>
    <div class="grid">
      <div class="card"><div class="k">任务总数</div><div class="v">{total}</div></div>
      <div class="card"><div class="k">已跑</div><div class="v">{ran}</div></div>
      <div class="card"><div class="k">待跑/运行中</div><div class="v">{waiting}</div></div>
      <div class="card"><div class="k">未跑/未运行</div><div class="v">{missed}</div></div>
      <div class="card"><div class="k">异常关注</div><div class="v">{issues}</div></div>
    </div>
    <table>
      <thead>
        <tr><th>任务</th><th>调度</th><th>上次执行</th><th>状态</th><th>摘要</th><th>数据</th></tr>
      </thead>
      <tbody>
        {''.join(rows)}
      </tbody>
    </table>
  </div>
</body>
</html>"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Build local task dashboard for OpenClaw + launchctl")
    parser.add_argument("--output-dir", default=str(pathlib.Path.home() / ".openclaw/dashboard"), help="Output folder")
    args = parser.parse_args()

    out_dir = pathlib.Path(args.output_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    jobs = get_jobs()
    payload = {"generated_at": now_local().strftime("%Y-%m-%d %H:%M:%S"), "jobs": jobs}

    (out_dir / "data.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "index.html").write_text(render_html(payload), encoding="utf-8")
    print(str(out_dir / "index.html"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

