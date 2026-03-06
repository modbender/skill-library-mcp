#!/usr/bin/env python3
"""
AWS Health Monitor
轮询 AWS Health Dashboard，监控活跃故障，变更时推送通知。

忽略配置：aws-health-ignore.json
"""

import json
import os
import sys
import re
import urllib.request
import hashlib
import subprocess
from datetime import datetime, timezone, timedelta

# ── 配置 ──────────────────────────────────────────────────────────────────────
# 代理：优先读环境变量（export HTTPS_PROXY=http://host:port），未设置则直连
PROXY = (
    os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy") or
    os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy") or
    None
)
AWS_HEALTH_URL = "https://health.aws.amazon.com/public/currentevents"
# 通知渠道：export AWS_HEALTH_NOTIFY_CHANNEL=feishu  (feishu/telegram/slack/discord 等)
NOTIFY_CHANNEL = os.environ.get("AWS_HEALTH_NOTIFY_CHANNEL", "feishu")
# 通知目标：export AWS_HEALTH_NOTIFY_TARGET=ou_xxxx (open_id / chat_id / @username 等)
NOTIFY_TARGET = os.environ.get("AWS_HEALTH_NOTIFY_TARGET", "")

# 监控范围：默认全部 issue
# 可通过环境变量缩小范围（逗号分隔）：
#   export AWS_HEALTH_WATCH_REGIONS=eu-central-1,ap-northeast-1,me-central-1
#   export AWS_HEALTH_WATCH_SERVICES=Amazon EC2,Amazon RDS
# 不设置 = 不过滤（监控所有 region / 所有服务）
_watch_regions_raw = os.environ.get("AWS_HEALTH_WATCH_REGIONS", "")
_watch_services_raw = os.environ.get("AWS_HEALTH_WATCH_SERVICES", "")
WATCH_REGIONS  = {r.strip().lower() for r in _watch_regions_raw.split(",") if r.strip()}
WATCH_SERVICES = {s.strip().lower() for s in _watch_services_raw.split(",") if s.strip()}

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE  = os.path.join(SCRIPT_DIR, ".aws-health-state.json")
IGNORE_FILE = os.path.join(SCRIPT_DIR, "aws-health-ignore.json")

CST = timezone(timedelta(hours=8))

SEVERITY_LABEL = {
    "1": "故障",
    "2": "降级",
    "3": "调查中",
    "0": "已恢复",
}

# ── 工具函数 ──────────────────────────────────────────────────────────────────

def fetch_events():
    proxy_handler = urllib.request.ProxyHandler({"http": PROXY, "https": PROXY})
    opener = urllib.request.build_opener(proxy_handler)
    req = urllib.request.Request(
        AWS_HEALTH_URL,
        headers={"User-Agent": "aws-health-monitor/1.0"},
    )
    with opener.open(req, timeout=30) as resp:
        raw = resp.read()
    return json.loads(raw.decode("utf-16"))


def load_ignore():
    if not os.path.exists(IGNORE_FILE):
        return set(), []
    with open(IGNORE_FILE) as f:
        cfg = json.load(f)
    ignored_arns = set(cfg.get("arns", []))
    ignored_services = [s.lower() for s in cfg.get("services", [])]
    return ignored_arns, ignored_services


def is_ignored(event, ignored_arns, ignored_services):
    arn = event.get("arn", "")
    service_name = (event.get("service_name") or "").lower()
    if arn in ignored_arns:
        return True
    for svc in ignored_services:
        if svc in service_name:
            return True
    return False


def is_watched(event):
    """默认放行所有 issue；若配置了白名单，则按 region / service 过滤。"""
    # 无任何过滤配置 → 全部监控
    if not WATCH_REGIONS and not WATCH_SERVICES:
        return True

    region = (event.get("region_name") or "").lower()
    service_name = (event.get("service_name") or "").lower()
    service = (event.get("service") or "").lower()
    arn = (event.get("arn") or "").lower()

    region_ok = True
    if WATCH_REGIONS:
        region_ok = any(r in region or r in service or r in arn for r in WATCH_REGIONS)

    service_ok = True
    if WATCH_SERVICES:
        service_ok = any(s in service_name or s in service for s in WATCH_SERVICES)

    return region_ok and service_ok


def event_fingerprint(event):
    arn = event.get("arn", "")
    logs = event.get("event_log", [])
    last_msg = logs[-1].get("message", "") if logs else ""
    last_status = str(logs[-1].get("status", "")) if logs else ""
    return hashlib.md5(f"{arn}|{last_status}|{last_msg}".encode()).hexdigest()


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def fmt_ts(ts):
    try:
        return datetime.fromtimestamp(int(ts), tz=CST).strftime("%Y-%m-%d %H:%M CST")
    except Exception:
        return str(ts)


# ── 根因提炼 ──────────────────────────────────────────────────────────────────

# 关键词 → 根因标签映射
ROOT_CAUSE_PATTERNS = [
    (r"power (issue|outage|failure|loss)",                              "电源故障"),
    (r"fire|sparks|struck.*data.?center|struck the data",              "数据中心火灾/物理损坏"),
    (r"\bnetwork(ing)? (issue|failure|degradation)\b",                 "网络故障"),
    (r"\bconnectivity (issue|problem|loss)\b",                         "网络连通性问题"),
    (r"\bhardware (failure|issue|fault)\b",                            "硬件故障"),
    (r"\b(software bug|software defect)\b",                            "软件 Bug"),
    (r"\bmisconfigur|\bconfiguration (change|issue|error)\b",          "配置变更/错误"),
    (r"\b(bad deploy|failed deploy|deployment issue|erroneous release)\b", "变更发布问题"),
    (r"\b(capacity issue|resource exhaustion)\b",                      "容量/资源耗尽"),
    (r"\bdns (issue|failure|resolution failure)\b",                    "DNS 解析问题"),
    (r"\b(certificate expired|TLS issue|SSL error)\b",                 "证书/TLS 问题"),
    (r"\b(storage failure|disk failure)\b",                            "存储故障"),
    (r"\bmemory (leak|exhaustion)\b",                                  "内存问题"),
    (r"\b(DDoS|traffic flood|traffic spike)\b",                        "流量异常/DDoS"),
    (r"\b(third.?party|upstream provider|upstream service)\b",         "上游/第三方问题"),
]

def extract_root_cause(event):
    """
    分析 event_log 的所有消息，提炼根因。
    返回：(根因标签, 简要说明) 或 (None, None)
    """
    logs = event.get("event_log", [])
    if not logs:
        return None, None

    # 合并所有消息文本，优先分析早期 log（根因通常出现在初始描述）
    all_text = " ".join(e.get("message", "") for e in logs).lower()

    matched_labels = []
    for pattern, label in ROOT_CAUSE_PATTERNS:
        if re.search(pattern, all_text, re.IGNORECASE):
            matched_labels.append(label)

    # 提炼一句简要说明：取第一条 log 里的核心句（通常最简洁）
    first_msg = logs[0].get("message", "")
    # 截取第一句或前 150 字
    brief = re.split(r'[.。\n]', first_msg)[0].strip()
    if len(brief) > 150:
        brief = brief[:150] + "…"

    return matched_labels, brief


# ── 通知格式 ──────────────────────────────────────────────────────────────────

def build_notification(event, is_new):
    arn = event.get("arn", "")
    region = event.get("region_name") or "Global"
    service_name = event.get("service_name", "Unknown Service")
    summary = event.get("summary", "")
    logs = event.get("event_log", [])

    last_log = logs[-1] if logs else {}
    status_code = str(last_log.get("status", event.get("status", "?")))
    last_msg = last_log.get("message", "")
    last_ts = last_log.get("timestamp", "")
    first_ts = logs[0].get("timestamp", "") if logs else ""

    severity = SEVERITY_LABEL.get(status_code, f"状态{status_code}")
    prefix = "[新故障]" if is_new else "[故障更新]"

    # 根因提炼
    root_cause_labels, root_cause_brief = extract_root_cause(event)
    if root_cause_labels:
        rc_line = "、".join(root_cause_labels)
    else:
        rc_line = "暂无明确根因"

    lines = [
        f"{prefix} | AWS Health Dashboard",
        f"",
        f"Region：{region}",
        f"服务：{service_name}",
        f"状态：{severity}（{summary}）",
        f"首发：{fmt_ts(first_ts)}",
        f"更新：{fmt_ts(last_ts)}",
        f"",
        f"根因：{rc_line}",
        root_cause_brief if root_cause_brief else "",
        f"",
        f"最新进展：",
        last_msg[:600] + ("…" if len(last_msg) > 600 else ""),
        f"",
        f"https://health.aws.amazon.com/health/status",
    ]
    # 去掉空的行但保留段落间的空行
    return "\n".join(line for line in lines if line is not None)


# ── 主逻辑 ────────────────────────────────────────────────────────────────────

def main():
    try:
        events = fetch_events()
    except Exception as e:
        print(f"[ERROR] fetch failed: {e}", file=sys.stderr)
        sys.exit(1)

    ignored_arns, ignored_services = load_ignore()
    watched = [
        e for e in events
        if is_watched(e) and not is_ignored(e, ignored_arns, ignored_services)
    ]

    state = load_state()
    new_state = {}
    notifications = []

    for event in watched:
        arn = event.get("arn", "")
        fp = event_fingerprint(event)
        new_state[arn] = fp

        if arn not in state:
            notifications.append(build_notification(event, is_new=True))
        elif state[arn] != fp:
            notifications.append(build_notification(event, is_new=False))

    # 检测已消失的事件（已解决）
    for arn in state:
        if arn not in new_state:
            notifications.append(
                f"[已解决] AWS Health Dashboard\n\n该事件已从 AWS Health Dashboard 移除。\nARN: {arn}\n\nhttps://health.aws.amazon.com/health/status"
            )

    save_state(new_state)

    now = datetime.now(CST).strftime("%Y-%m-%d %H:%M:%S")
    if notifications:
        for msg in notifications:
            result = subprocess.run(
                ["openclaw", "message", "send",
                 "--channel", NOTIFY_CHANNEL,
                 "--target", NOTIFY_TARGET,
                 "--message", msg],
                capture_output=True, text=True,
            )
            if result.returncode != 0:
                print(f"[WARN] notify send failed ({NOTIFY_CHANNEL}): {result.stderr}", file=sys.stderr)
        print(f"[{now}] Sent {len(notifications)} notification(s). Watching {len(watched)} event(s).")
    else:
        print(f"[{now}] No changes. Watching {len(watched)} event(s).")


if __name__ == "__main__":
    main()
