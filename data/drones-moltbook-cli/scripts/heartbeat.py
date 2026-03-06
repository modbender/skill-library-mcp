#!/usr/bin/env python3
import json
import shutil
import subprocess
import time
from pathlib import Path

HB_OPT = Path('/root/.openclaw/workspace/skills/openclaw-token-optimizer/scripts/heartbeat_optimizer.py')
NOTIFY = Path('/opt/moltbook-cli/notify.sh')
LOG = Path('/var/log/openclaw-heartbeat.log')


def log(msg: str) -> None:
    ts = time.strftime('%Y-%m-%d %H:%M:%S')
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open('a') as f:
        f.write(f"[{ts}] {msg}\n")


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def should_run() -> bool:
    if not HB_OPT.exists():
        return False
    proc = run(['python3', str(HB_OPT), 'check', 'monitoring'])
    if proc.returncode != 0:
        log(f"heartbeat_optimizer error: {proc.stderr.strip()}")
        return False
    data = json.loads(proc.stdout)
    return bool(data.get('should_check'))


def record_run() -> None:
    if HB_OPT.exists():
        run(['python3', str(HB_OPT), 'record', 'monitoring'])


def check_openclaw() -> str | None:
    proc = run(['systemctl', 'is-active', 'openclaw'])
    status = proc.stdout.strip()
    if status != 'active':
        return f"OpenClaw service status: {status}"
    return None


def check_disk() -> str | None:
    usage = shutil.disk_usage('/')
    used_pct = int((usage.used / usage.total) * 100)
    if used_pct >= 90:
        return f"Disk usage high: {used_pct}%"
    return None


def notify(msg: str) -> None:
    if NOTIFY.exists():
        run([str(NOTIFY), msg])


def main():
    if not should_run():
        return

    alerts = []
    msg = check_openclaw()
    if msg:
        alerts.append(msg)

    msg = check_disk()
    if msg:
        alerts.append(msg)

    if alerts:
        text = "\n".join(["OpenClaw heartbeat alert:"] + alerts)
        notify(text)
        log(text)
    else:
        log("heartbeat ok")

    record_run()


if __name__ == '__main__':
    main()
