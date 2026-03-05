#!/usr/bin/env python3
"""agentic-devops — Production-grade agent DevOps toolkit.

Docker management, process inspection, log analysis, health monitoring,
and full system diagnostics. Stdlib-only (no external deps). Built by
engineers who run production systems.

Part of the Anvil AI toolkit — https://anvil-ai.io
"""

import argparse
import os
import platform
import re
import shlex
import shutil
import socket
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime

# ---------------------------------------------------------------------------
# ANSI colour helpers
# ---------------------------------------------------------------------------

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
WHITE = "\033[97m"
MAGENTA = "\033[95m"

NO_COLOR = os.environ.get("NO_COLOR") is not None or not sys.stdout.isatty()


def c(text, *codes):
    """Wrap *text* with ANSI escape codes (respects NO_COLOR)."""
    if NO_COLOR:
        return str(text)
    return "".join(codes) + str(text) + RESET


# ---------------------------------------------------------------------------
# Box-drawing helpers
# ---------------------------------------------------------------------------

BOX_TL = "\u250c"
BOX_TR = "\u2510"
BOX_BL = "\u2514"
BOX_BR = "\u2518"
BOX_H = "\u2500"
BOX_V = "\u2502"
BOX_ML = "\u251c"
BOX_MR = "\u2524"

BLOCK_FULL = "\u2588"
BLOCK_LIGHT = "\u2591"


def strip_ansi(s):
    """Remove ANSI escape sequences for length calculations."""
    return re.sub(r"\033\[[0-9;]*m", "", s)


def term_width(default=80):
    """Return usable terminal width."""
    try:
        cols = shutil.get_terminal_size((default, 24)).columns
    except Exception:
        cols = default
    return max(cols, 50)


def box_top(w=60):
    return BOX_TL + BOX_H * w + BOX_TR


def box_bottom(w=60):
    return BOX_BL + BOX_H * w + BOX_BR


def box_sep(w=60):
    return BOX_ML + BOX_H * w + BOX_MR


def box_row(text, w=60):
    """Left-aligned text inside box borders."""
    visible = len(strip_ansi(text))
    pad = max(w - visible - 1, 0)
    return f"{BOX_V} {text}{' ' * pad}{BOX_V}"


def box_empty(w=60):
    return box_row("", w)


def print_box(title, rows, w=60):
    """Print a titled box."""
    print(box_top(w))
    print(box_row(c(title, BOLD, CYAN), w))
    print(box_sep(w))
    for row in rows:
        print(box_row(row, w))
    print(box_bottom(w))


def usage_bar(value, max_val, width=30, warn_pct=70, crit_pct=90):
    """Render a horizontal bar with colour thresholds."""
    if max_val <= 0:
        pct = 0
    else:
        pct = (value / max_val) * 100
    filled = int(round(pct / 100 * width))
    filled = max(0, min(filled, width))
    empty = width - filled
    if pct >= crit_pct:
        clr = RED
    elif pct >= warn_pct:
        clr = YELLOW
    else:
        clr = GREEN
    return c(BLOCK_FULL * filled, clr) + c(BLOCK_LIGHT * empty, DIM) + f" {pct:.1f}%"


def status_dot(ok):
    """Return a coloured status indicator."""
    if ok is True:
        return "\U0001f7e2"  # green circle
    elif ok is False:
        return "\U0001f534"  # red circle
    return "\U0001f7e1"  # yellow circle


# ---------------------------------------------------------------------------
# Shell execution helpers
# ---------------------------------------------------------------------------

def run(cmd, timeout=15, shell=True):
    """Run a shell command and return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd, shell=shell, capture_output=True, text=True, timeout=timeout
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except FileNotFoundError:
        return -1, "", "Command not found"
    except Exception as e:
        return -1, "", str(e)


def has_command(name):
    """Check if a command is available on PATH."""
    return shutil.which(name) is not None


def docker_available():
    """Check if Docker CLI is installed and the daemon is responsive."""
    if not has_command("docker"):
        return False
    rc, _, _ = run("docker info", timeout=5)
    return rc == 0


# ---------------------------------------------------------------------------
# System resource helpers
# ---------------------------------------------------------------------------

def get_cpu_count():
    """Return the number of CPU cores."""
    try:
        return os.cpu_count() or 1
    except Exception:
        return 1


def get_load_avg():
    """Return 1m, 5m, 15m load averages."""
    try:
        return os.getloadavg()
    except (OSError, AttributeError):
        # Windows or unavailable
        return None


def get_memory_info():
    """Parse /proc/meminfo and return (total_mb, used_mb, available_mb)."""
    try:
        with open("/proc/meminfo", "r") as f:
            info = {}
            for line in f:
                parts = line.split()
                if len(parts) >= 2:
                    key = parts[0].rstrip(":")
                    val = int(parts[1])  # in kB
                    info[key] = val
            total = info.get("MemTotal", 0) / 1024
            available = info.get("MemAvailable", info.get("MemFree", 0)) / 1024
            used = total - available
            return total, used, available
    except Exception:
        return None, None, None


def get_disk_info(path="/"):
    """Return (total_gb, used_gb, free_gb) for the given mount point."""
    try:
        st = os.statvfs(path)
        total = (st.f_blocks * st.f_frsize) / (1024 ** 3)
        free = (st.f_bavail * st.f_frsize) / (1024 ** 3)
        used = total - free
        return total, used, free
    except Exception:
        return None, None, None


def get_uptime():
    """Return system uptime string."""
    try:
        with open("/proc/uptime", "r") as f:
            secs = float(f.read().split()[0])
        days = int(secs // 86400)
        hours = int((secs % 86400) // 3600)
        mins = int((secs % 3600) // 60)
        parts = []
        if days:
            parts.append(f"{days}d")
        if hours:
            parts.append(f"{hours}h")
        parts.append(f"{mins}m")
        return " ".join(parts)
    except Exception:
        return "unknown"


# ---------------------------------------------------------------------------
# Docker commands
# ---------------------------------------------------------------------------

def cmd_docker_status(_args):
    """Show Docker container status overview."""
    if not docker_available():
        print(c("  Docker is not available. Skipping.", YELLOW))
        return

    w = min(term_width(), 80)
    rc, out, _ = run("docker ps -a --format '{{.ID}}\t{{.Names}}\t{{.Status}}\t{{.Image}}\t{{.Ports}}'")
    if rc != 0 or not out:
        print_box("Docker Containers", [c("  No containers found.", DIM)], w)
        return

    rows = []
    for line in out.strip().split("\n"):
        parts = line.split("\t")
        if len(parts) < 4:
            continue
        cid, name, status, image = parts[0][:12], parts[1][:20], parts[2], parts[3][:30]
        ports = parts[4] if len(parts) > 4 else ""

        if "Up" in status:
            dot = status_dot(True)
            status_c = c(status[:25], GREEN)
        elif "Exited" in status:
            dot = status_dot(False)
            status_c = c(status[:25], RED)
        else:
            dot = status_dot(None)
            status_c = c(status[:25], YELLOW)

        rows.append(f"  {dot} {c(name, BOLD, WHITE):<28s}  {status_c}")
        rows.append(f"      {c(image, DIM)}  {c(ports[:40], DIM)}")

    print()
    print_box("Docker Containers", rows, w)
    _print_footer()


def cmd_docker_logs(args):
    """Tail container logs with optional grep."""
    if not docker_available():
        print(c("  Docker is not available.", YELLOW))
        return

    container = args.container
    tail = args.tail
    grep_pat = args.grep

    cmd_str = f"docker logs --tail {tail} {shlex.quote(container)} 2>&1"
    rc, out, err = run(cmd_str, timeout=30)

    if rc != 0:
        print(c(f"  Error: {err or out}", RED))
        return

    lines = out.split("\n")
    if grep_pat:
        pattern = re.compile(grep_pat, re.IGNORECASE)
        lines = [l for l in lines if pattern.search(l)]

    w = min(term_width(), 120)
    print()
    print(box_top(w))
    print(box_row(c(f"Logs: {container} (last {tail})", BOLD, CYAN), w))
    print(box_sep(w))

    for line in lines[-100:]:  # cap output
        if grep_pat and re.search(grep_pat, line, re.IGNORECASE):
            # Highlight matches
            highlighted = re.sub(
                grep_pat,
                lambda m: c(m.group(0), BOLD, RED),
                line,
                flags=re.IGNORECASE,
            )
            print(box_row(f"  {highlighted}"[:w - 2], w))
        else:
            print(box_row(f"  {line}"[:w - 2], w))

    print(box_bottom(w))
    _print_footer()


def cmd_docker_health(_args):
    """Docker health summary: running, stopped, unhealthy counts."""
    if not docker_available():
        print(c("  Docker is not available. Skipping.", YELLOW))
        return

    w = min(term_width(), 70)
    rc, out, _ = run("docker ps -a --format '{{.Status}}\t{{.Names}}'")
    if rc != 0 or not out:
        print_box("Docker Health", [c("  No containers found.", DIM)], w)
        return

    running, stopped, unhealthy = 0, 0, 0
    unhealthy_names = []

    for line in out.strip().split("\n"):
        parts = line.split("\t")
        status = parts[0] if parts else ""
        name = parts[1] if len(parts) > 1 else "unknown"

        if "Up" in status:
            running += 1
            if "unhealthy" in status.lower():
                unhealthy += 1
                unhealthy_names.append(name)
        else:
            stopped += 1

    rows = [
        f"  {status_dot(True)} Running:    {c(str(running), BOLD, GREEN)}",
        f"  {status_dot(False)} Stopped:    {c(str(stopped), BOLD, RED if stopped else DIM)}",
        f"  {status_dot(None)} Unhealthy:  {c(str(unhealthy), BOLD, YELLOW if unhealthy else DIM)}",
    ]
    if unhealthy_names:
        rows.append("")
        rows.append(c("  Unhealthy containers:", YELLOW))
        for name in unhealthy_names:
            rows.append(f"    - {c(name, RED)}")

    print()
    print_box("Docker Health", rows, w)
    _print_footer()


def cmd_docker_compose_status(args):
    """Show Docker Compose service status."""
    if not docker_available():
        print(c("  Docker is not available. Skipping.", YELLOW))
        return

    compose_file = args.file
    w = min(term_width(), 80)

    # Try docker compose (v2) first, fall back to docker-compose (v1)
    cmd_str = f"docker compose -f {shlex.quote(compose_file)} ps --format json 2>/dev/null"
    rc, out, _ = run(cmd_str, timeout=10)

    if rc != 0 or not out:
        cmd_str = f"docker-compose -f {shlex.quote(compose_file)} ps 2>&1"
        rc, out, _ = run(cmd_str, timeout=10)
        if rc != 0:
            print_box("Compose Status", [c(f"  Could not read {compose_file}", RED)], w)
            return
        # Plain text fallback
        rows = []
        for line in out.strip().split("\n"):
            rows.append(f"  {line}"[:w - 2])
        print()
        print_box(f"Compose: {compose_file}", rows, w)
        _print_footer()
        return

    # Parse JSON output (docker compose v2)
    import json
    rows = []
    try:
        # docker compose ps --format json outputs one JSON per line
        for json_line in out.strip().split("\n"):
            svc = json.loads(json_line)
            name = svc.get("Name", svc.get("Service", "unknown"))[:25]
            state = svc.get("State", svc.get("Status", "unknown"))
            health = svc.get("Health", "")

            if state == "running":
                dot = status_dot(True)
                state_c = c(state, GREEN)
            elif state == "exited":
                dot = status_dot(False)
                state_c = c(state, RED)
            else:
                dot = status_dot(None)
                state_c = c(state, YELLOW)

            health_str = f"  ({c(health, YELLOW)})" if health and health != "healthy" else ""
            rows.append(f"  {dot} {c(name, BOLD, WHITE):<28s}  {state_c}{health_str}")
    except Exception:
        rows.append(c("  Could not parse compose output.", DIM))

    print()
    print_box(f"Compose: {compose_file}", rows, w)
    _print_footer()


# ---------------------------------------------------------------------------
# Process management commands
# ---------------------------------------------------------------------------

def cmd_proc_list(args):
    """List top processes sorted by CPU or memory."""
    sort_key = args.sort
    count = args.count
    w = min(term_width(), 100)

    if sort_key == "mem":
        sort_flag = "--sort=-%mem"
    else:
        sort_flag = "--sort=-%cpu"

    rc, out, _ = run(f"ps aux {sort_flag} 2>/dev/null | head -n {count + 1}")
    if rc != 0 or not out:
        print(c("  Could not list processes.", RED))
        return

    lines = out.strip().split("\n")
    rows = []

    if lines:
        # Header
        header = lines[0]
        rows.append(c(f"  {header[:w - 4]}", DIM))
        rows.append(f"  {'─' * (w - 4)}")

    for line in lines[1:]:
        parts = line.split(None, 10)
        if len(parts) < 11:
            rows.append(f"  {line[:w - 4]}")
            continue

        cpu = float(parts[2]) if parts[2].replace(".", "").isdigit() else 0
        mem = float(parts[3]) if parts[3].replace(".", "").isdigit() else 0

        if cpu > 80 or mem > 80:
            clr = RED
        elif cpu > 50 or mem > 50:
            clr = YELLOW
        else:
            clr = WHITE

        rows.append(c(f"  {line[:w - 4]}", clr))

    print()
    print_box(f"Top Processes (by {sort_key})", rows, w)
    _print_footer()


def cmd_proc_ports(_args):
    """Show ports in use."""
    w = min(term_width(), 90)

    # Try ss first, fall back to netstat
    rc, out, _ = run("ss -tlnp 2>/dev/null")
    if rc != 0 or not out:
        rc, out, _ = run("netstat -tlnp 2>/dev/null")

    if rc != 0 or not out:
        print(c("  Could not retrieve port information.", YELLOW))
        return

    lines = out.strip().split("\n")
    rows = []

    for line in lines[:30]:
        rows.append(f"  {line[:w - 4]}")

    print()
    print_box("Listening Ports", rows, w)
    _print_footer()


def cmd_proc_zombies(_args):
    """Detect zombie processes."""
    w = min(term_width(), 80)

    rc, out, _ = run("ps aux 2>/dev/null | awk '$8 ~ /Z/ {print}'")
    rows = []

    if rc != 0:
        rows.append(c("  Could not check for zombie processes.", YELLOW))
    elif not out.strip():
        rows.append(f"  {status_dot(True)} No zombie processes detected.")
    else:
        zombies = out.strip().split("\n")
        rows.append(f"  {status_dot(False)} {c(str(len(zombies)), BOLD, RED)} zombie process(es) found:")
        rows.append("")
        for z in zombies[:20]:
            rows.append(c(f"    {z[:w - 6]}", RED))

    print()
    print_box("Zombie Processes", rows, w)
    _print_footer()


# ---------------------------------------------------------------------------
# Log analysis commands
# ---------------------------------------------------------------------------

def cmd_logs_analyze(args):
    """Analyze a log file for patterns."""
    log_file = args.file
    pattern = args.pattern
    w = min(term_width(), 100)

    if not os.path.isfile(log_file):
        print(c(f"  File not found: {log_file}", RED))
        return

    try:
        regex = re.compile(pattern, re.IGNORECASE)
    except re.error as e:
        print(c(f"  Invalid regex pattern: {e}", RED))
        return

    matches = []
    total_lines = 0

    try:
        with open(log_file, "r", errors="replace") as f:
            for line in f:
                total_lines += 1
                if regex.search(line):
                    matches.append(line.rstrip())
    except PermissionError:
        print(c(f"  Permission denied: {log_file}", RED))
        return

    rows = [
        f"  File:       {c(log_file, WHITE)}",
        f"  Pattern:    {c(pattern, CYAN)}",
        f"  Total lines: {c(str(total_lines), WHITE)}",
        f"  Matches:    {c(str(len(matches)), BOLD, RED if matches else GREEN)}",
        "",
    ]

    if matches:
        rows.append(c("  Last 20 matches:", CYAN))
        rows.append(f"  {'─' * (w - 4)}")
        for m in matches[-20:]:
            # Highlight the pattern
            highlighted = re.sub(
                f"({pattern})",
                lambda x: c(x.group(1), BOLD, RED),
                m[:w - 4],
                flags=re.IGNORECASE,
            )
            rows.append(f"  {highlighted}")

    print()
    print_box("Log Analysis", rows, w)
    _print_footer()


def cmd_logs_tail(args):
    """Tail a log file with highlighted patterns."""
    log_file = args.file
    highlight = args.highlight
    num = args.num
    w = min(term_width(), 120)

    if not os.path.isfile(log_file):
        print(c(f"  File not found: {log_file}", RED))
        return

    try:
        with open(log_file, "r", errors="replace") as f:
            lines = f.readlines()
    except PermissionError:
        print(c(f"  Permission denied: {log_file}", RED))
        return

    tail_lines = lines[-num:]

    rows = []
    if highlight:
        try:
            pat = re.compile(highlight, re.IGNORECASE)
        except re.error:
            pat = None
    else:
        pat = None

    for line in tail_lines:
        line = line.rstrip()[:w - 4]
        if pat and pat.search(line):
            line = re.sub(
                f"({highlight})",
                lambda x: c(x.group(1), BOLD, RED),
                line,
                flags=re.IGNORECASE,
            )
        rows.append(f"  {line}")

    print()
    print_box(f"Log Tail: {os.path.basename(log_file)} (last {num})", rows, w)
    _print_footer()


def cmd_logs_frequency(args):
    """Frequency analysis of log patterns."""
    log_file = args.file
    top_n = args.top
    w = min(term_width(), 90)

    if not os.path.isfile(log_file):
        print(c(f"  File not found: {log_file}", RED))
        return

    # Extract meaningful tokens from each log line
    counter = Counter()
    total = 0

    try:
        with open(log_file, "r", errors="replace") as f:
            for line in f:
                total += 1
                # Extract common log levels and keywords
                for match in re.findall(
                    r"\b(ERROR|WARN(?:ING)?|CRITICAL|FATAL|INFO|DEBUG|EXCEPTION|FAIL(?:ED|URE)?|TIMEOUT|REFUSED|DENIED)\b",
                    line, re.IGNORECASE
                ):
                    counter[match.upper()] += 1
    except PermissionError:
        print(c(f"  Permission denied: {log_file}", RED))
        return

    rows = [
        f"  File:        {c(log_file, WHITE)}",
        f"  Total lines: {c(str(total), WHITE)}",
        "",
    ]

    if counter:
        max_count = max(counter.values())
        bar_w = max(w - 40, 10)
        rows.append(c("  Pattern Frequency:", CYAN))
        rows.append(f"  {'─' * (w - 4)}")

        for pattern, count in counter.most_common(top_n):
            pct = (count / total * 100) if total > 0 else 0
            filled = int(round(count / max_count * bar_w))
            bar_str = c(BLOCK_FULL * filled, RED if pattern in ("ERROR", "CRITICAL", "FATAL") else YELLOW) + c(BLOCK_LIGHT * (bar_w - filled), DIM)
            rows.append(f"  {pattern:<12s} {bar_str} {count:>6,}  ({pct:.1f}%)")
    else:
        rows.append(c("  No recognized log patterns found.", DIM))

    print()
    print_box("Log Frequency Analysis", rows, w)
    _print_footer()


# ---------------------------------------------------------------------------
# Health check commands
# ---------------------------------------------------------------------------

def cmd_health_check(args):
    """Check HTTP endpoint health."""
    url = args.url
    w = min(term_width(), 80)

    import urllib.request
    import urllib.error

    rows = [f"  Endpoint: {c(url, CYAN)}"]
    rows.append("")

    start = time.time()
    try:
        req = urllib.request.Request(url, method="GET")
        req.add_header("User-Agent", "agentic-devops/1.0")
        with urllib.request.urlopen(req, timeout=10) as resp:
            status_code = resp.getcode()
            elapsed = (time.time() - start) * 1000
            body = resp.read().decode("utf-8", errors="replace")[:500]

            if 200 <= status_code < 300:
                rows.append(f"  {status_dot(True)} Status: {c(str(status_code), BOLD, GREEN)}  ({elapsed:.0f}ms)")
            elif 300 <= status_code < 400:
                rows.append(f"  {status_dot(None)} Status: {c(str(status_code), BOLD, YELLOW)}  ({elapsed:.0f}ms)")
            else:
                rows.append(f"  {status_dot(False)} Status: {c(str(status_code), BOLD, RED)}  ({elapsed:.0f}ms)")

            if body:
                rows.append("")
                rows.append(c("  Response (first 200 chars):", DIM))
                rows.append(f"  {body[:200]}")

    except urllib.error.HTTPError as e:
        elapsed = (time.time() - start) * 1000
        rows.append(f"  {status_dot(False)} Status: {c(str(e.code), BOLD, RED)}  ({elapsed:.0f}ms)")
        rows.append(f"  {c(str(e.reason), RED)}")
    except urllib.error.URLError as e:
        elapsed = (time.time() - start) * 1000
        rows.append(f"  {status_dot(False)} {c('Connection failed', BOLD, RED)}  ({elapsed:.0f}ms)")
        rows.append(f"  {c(str(e.reason), RED)}")
    except Exception as e:
        elapsed = (time.time() - start) * 1000
        rows.append(f"  {status_dot(False)} {c('Error', BOLD, RED)}  ({elapsed:.0f}ms)")
        rows.append(f"  {c(str(e), RED)}")

    print()
    print_box("Health Check", rows, w)
    _print_footer()


def cmd_health_ports(args):
    """Scan specific ports."""
    ports_str = args.ports
    w = min(term_width(), 70)

    try:
        ports = [int(p.strip()) for p in ports_str.split(",") if p.strip()]
    except ValueError:
        print(c("  Invalid port list. Use comma-separated numbers.", RED))
        return

    rows = []
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(("127.0.0.1", port))
            sock.close()

            if result == 0:
                rows.append(f"  {status_dot(True)} Port {c(str(port), BOLD, WHITE):>8s}  {c('OPEN', GREEN)}")
            else:
                rows.append(f"  {status_dot(False)} Port {c(str(port), BOLD, WHITE):>8s}  {c('CLOSED', RED)}")
        except Exception as e:
            rows.append(f"  {status_dot(None)} Port {c(str(port), BOLD, WHITE):>8s}  {c(f'ERROR: {e}', YELLOW)}")

    print()
    print_box("Port Scan (localhost)", rows, w)
    _print_footer()


def cmd_health_system(_args):
    """System resource health: CPU, memory, disk."""
    w = min(term_width(), 70)

    rows = []

    # Hostname & OS
    hostname = platform.node() or "unknown"
    os_info = platform.platform()
    rows.append(f"  Host: {c(hostname, BOLD, WHITE)}")
    rows.append(f"  OS:   {c(os_info, DIM)}")
    rows.append(f"  Up:   {c(get_uptime(), WHITE)}")
    rows.append("")

    # CPU
    cpu_count = get_cpu_count()
    load = get_load_avg()
    if load:
        load_1, load_5, load_15 = load
        cpu_pct = (load_1 / cpu_count) * 100
        rows.append(c("  CPU", CYAN))
        bar_w = max(w - 30, 10)
        rows.append(f"    Cores: {cpu_count}   Load: {load_1:.2f} / {load_5:.2f} / {load_15:.2f}")
        rows.append(f"    {usage_bar(load_1, cpu_count, bar_w)}")
        rows.append("")

    # Memory
    mem_total, mem_used, mem_avail = get_memory_info()
    if mem_total:
        rows.append(c("  Memory", CYAN))
        bar_w = max(w - 30, 10)
        rows.append(f"    Total: {mem_total:.0f} MB   Used: {mem_used:.0f} MB   Free: {mem_avail:.0f} MB")
        rows.append(f"    {usage_bar(mem_used, mem_total, bar_w)}")
        rows.append("")

    # Disk
    disk_total, disk_used, disk_free = get_disk_info("/")
    if disk_total:
        rows.append(c("  Disk (/)", CYAN))
        bar_w = max(w - 30, 10)
        rows.append(f"    Total: {disk_total:.1f} GB   Used: {disk_used:.1f} GB   Free: {disk_free:.1f} GB")
        rows.append(f"    {usage_bar(disk_used, disk_total, bar_w)}")

    print()
    print_box("System Health", rows, w)
    _print_footer()


# ---------------------------------------------------------------------------
# Diagnostics — the killer feature
# ---------------------------------------------------------------------------

def cmd_diag(_args):
    """Full system diagnostics — one command to see everything."""
    w = min(term_width(), 80)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print()
    print(box_top(w))
    print(box_row(c("System Diagnostics", BOLD, CYAN), w))
    print(box_row(c(f"Generated: {now}", DIM), w))
    print(box_sep(w))

    # ── System Resources ──────────────────────────────────────────────────
    print(box_row(c("SYSTEM RESOURCES", BOLD, MAGENTA), w))
    print(box_row("", w))

    hostname = platform.node() or "unknown"
    os_info = platform.platform()
    print(box_row(f"  Host: {c(hostname, BOLD, WHITE)}  |  OS: {c(os_info[:40], DIM)}", w))
    print(box_row(f"  Uptime: {c(get_uptime(), WHITE)}", w))
    print(box_row("", w))

    # CPU
    cpu_count = get_cpu_count()
    load = get_load_avg()
    bar_w = max(w - 35, 10)
    if load:
        load_1, load_5, load_15 = load
        print(box_row(f"  CPU ({cpu_count} cores)  Load: {load_1:.2f} / {load_5:.2f} / {load_15:.2f}", w))
        print(box_row(f"    {usage_bar(load_1, cpu_count, bar_w)}", w))
    else:
        print(box_row(f"  CPU: {cpu_count} cores (load unavailable)", w))

    # Memory
    mem_total, mem_used, mem_avail = get_memory_info()
    if mem_total:
        print(box_row(f"  Memory   {mem_used:.0f} / {mem_total:.0f} MB", w))
        print(box_row(f"    {usage_bar(mem_used, mem_total, bar_w)}", w))

    # Disk
    disk_total, disk_used, disk_free = get_disk_info("/")
    if disk_total:
        print(box_row(f"  Disk (/) {disk_used:.1f} / {disk_total:.1f} GB", w))
        print(box_row(f"    {usage_bar(disk_used, disk_total, bar_w)}", w))

    print(box_sep(w))

    # ── Docker ────────────────────────────────────────────────────────────
    print(box_row(c("DOCKER", BOLD, MAGENTA), w))
    print(box_row("", w))

    if docker_available():
        rc, out, _ = run("docker ps -a --format '{{.Names}}\t{{.Status}}'")
        if rc == 0 and out:
            running, stopped, unhealthy = 0, 0, 0
            for line in out.strip().split("\n"):
                parts = line.split("\t")
                status = parts[1] if len(parts) > 1 else ""
                if "Up" in status:
                    running += 1
                    if "unhealthy" in status.lower():
                        unhealthy += 1
                else:
                    stopped += 1

            print(box_row(f"  {status_dot(True)} Running: {c(str(running), BOLD, GREEN)}   "
                          f"{status_dot(False)} Stopped: {c(str(stopped), BOLD, RED if stopped else DIM)}   "
                          f"{status_dot(None)} Unhealthy: {c(str(unhealthy), BOLD, YELLOW if unhealthy else DIM)}", w))

            # Show container list
            for line in out.strip().split("\n")[:10]:
                parts = line.split("\t")
                name = parts[0][:25] if parts else "unknown"
                status = parts[1][:30] if len(parts) > 1 else "unknown"
                if "Up" in status:
                    dot = status_dot(True)
                    sc = c(status, GREEN)
                elif "Exited" in status:
                    dot = status_dot(False)
                    sc = c(status, RED)
                else:
                    dot = status_dot(None)
                    sc = c(status, YELLOW)
                print(box_row(f"    {dot} {c(name, WHITE):<28s} {sc}", w))
        else:
            print(box_row(f"  {status_dot(True)} Docker running — no containers.", w))
    else:
        print(box_row(c("  Docker not available — skipped.", DIM), w))

    print(box_sep(w))

    # ── Key Ports ─────────────────────────────────────────────────────────
    print(box_row(c("KEY PORTS", BOLD, MAGENTA), w))
    print(box_row("", w))

    common_ports = [22, 80, 443, 3000, 3306, 5432, 6379, 8080, 8443, 9090]
    port_results = []
    for port in common_ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex(("127.0.0.1", port))
            sock.close()
            if result == 0:
                port_results.append((port, True))
        except Exception:
            pass

    if port_results:
        port_strs = [f"{status_dot(True)} {c(str(p), BOLD, WHITE)}" for p, _ in port_results]
        # Print ports in rows of 4
        for i in range(0, len(port_strs), 4):
            chunk = port_strs[i:i + 4]
            print(box_row("  " + "   ".join(chunk), w))
    else:
        print(box_row(c("  No common ports open on localhost.", DIM), w))

    print(box_sep(w))

    # ── Recent Errors ─────────────────────────────────────────────────────
    print(box_row(c("RECENT ERRORS", BOLD, MAGENTA), w))
    print(box_row("", w))

    log_locations = [
        "/var/log/syslog",
        "/var/log/messages",
        "/var/log/kern.log",
        "/var/log/auth.log",
    ]

    found_errors = False
    for log_path in log_locations:
        if not os.path.isfile(log_path):
            continue
        try:
            with open(log_path, "r", errors="replace") as f:
                lines = f.readlines()
            # Check last 500 lines for errors
            recent = lines[-500:]
            errors = [l.rstrip() for l in recent if re.search(r"\b(error|critical|fatal|panic)\b", l, re.IGNORECASE)]
            if errors:
                found_errors = True
                print(box_row(f"  {c(log_path, CYAN)}: {c(str(len(errors)), BOLD, RED)} error(s) in last 500 lines", w))
                for e in errors[-3:]:
                    print(box_row(c(f"    {e[:w - 8]}", RED), w))
        except PermissionError:
            continue

    if not found_errors:
        print(box_row(f"  {status_dot(True)} No recent errors in common log files.", w))

    print(box_sep(w))

    # ── Top Processes ─────────────────────────────────────────────────────
    print(box_row(c("TOP PROCESSES (by CPU)", BOLD, MAGENTA), w))
    print(box_row("", w))

    rc, out, _ = run("ps aux --sort=-%cpu 2>/dev/null | head -n 8")
    if rc == 0 and out:
        lines = out.strip().split("\n")
        if lines:
            # Compact header
            print(box_row(c(f"  {'USER':<10s} {'PID':>6s} {'%CPU':>5s} {'%MEM':>5s} COMMAND", DIM), w))
            for line in lines[1:]:
                parts = line.split(None, 10)
                if len(parts) < 11:
                    continue
                user = parts[0][:9]
                pid = parts[1]
                cpu = parts[2]
                mem = parts[3]
                cmd = parts[10][:w - 36]

                cpu_val = float(cpu) if cpu.replace(".", "").isdigit() else 0
                if cpu_val > 80:
                    clr = RED
                elif cpu_val > 50:
                    clr = YELLOW
                else:
                    clr = WHITE

                print(box_row(c(f"  {user:<10s} {pid:>6s} {cpu:>5s} {mem:>5s} {cmd}", clr), w))

    print(box_sep(w))

    # ── Footer ────────────────────────────────────────────────────────────
    print(box_row(c("Part of the Anvil AI toolkit — https://anvil-ai.io", DIM), w))
    print(box_bottom(w))
    print()


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

def _print_footer():
    """Print subtle Anvil AI branding footer."""
    print(c("  Part of the Anvil AI toolkit — https://anvil-ai.io", DIM))
    print()


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        prog="agentic-devops",
        description="Production-grade agent DevOps toolkit — Docker, process management, log analysis, health monitoring.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Part of the Anvil AI toolkit — https://anvil-ai.io",
    )
    sub = parser.add_subparsers(dest="command")

    # ── docker ────────────────────────────────────────────────────────────
    p_docker = sub.add_parser("docker", help="Docker operations")
    docker_sub = p_docker.add_subparsers(dest="docker_cmd")

    docker_sub.add_parser("status", help="Container status overview")

    p_docker_logs = docker_sub.add_parser("logs", help="Tail container logs")
    p_docker_logs.add_argument("container", help="Container name or ID")
    p_docker_logs.add_argument("--tail", type=int, default=50, help="Number of lines (default: 50)")
    p_docker_logs.add_argument("--grep", default=None, help="Filter pattern (regex)")

    docker_sub.add_parser("health", help="Docker health summary")

    p_docker_compose = docker_sub.add_parser("compose-status", help="Compose service status")
    p_docker_compose.add_argument("--file", default="docker-compose.yml", help="Compose file path")

    # ── proc ──────────────────────────────────────────────────────────────
    p_proc = sub.add_parser("proc", help="Process management")
    proc_sub = p_proc.add_subparsers(dest="proc_cmd")

    p_proc_list = proc_sub.add_parser("list", help="List top processes")
    p_proc_list.add_argument("--sort", choices=["cpu", "mem"], default="cpu", help="Sort by (default: cpu)")
    p_proc_list.add_argument("--count", type=int, default=15, help="Number of processes (default: 15)")

    proc_sub.add_parser("ports", help="Show ports in use")
    proc_sub.add_parser("zombies", help="Detect zombie processes")

    # ── logs ──────────────────────────────────────────────────────────────
    p_logs = sub.add_parser("logs", help="Log analysis")
    logs_sub = p_logs.add_subparsers(dest="logs_cmd")

    p_logs_analyze = logs_sub.add_parser("analyze", help="Analyze log file")
    p_logs_analyze.add_argument("file", help="Log file path")
    p_logs_analyze.add_argument("--pattern", default="error|fail|critical", help="Search pattern (regex)")

    p_logs_tail = logs_sub.add_parser("tail", help="Tail log file")
    p_logs_tail.add_argument("file", help="Log file path")
    p_logs_tail.add_argument("--highlight", default=None, help="Highlight pattern (regex)")
    p_logs_tail.add_argument("--num", type=int, default=50, help="Number of lines (default: 50)")

    p_logs_freq = logs_sub.add_parser("frequency", help="Pattern frequency analysis")
    p_logs_freq.add_argument("file", help="Log file path")
    p_logs_freq.add_argument("--top", type=int, default=20, help="Top N patterns (default: 20)")

    # ── health ────────────────────────────────────────────────────────────
    p_health = sub.add_parser("health", help="Health checks")
    health_sub = p_health.add_subparsers(dest="health_cmd")

    p_health_check = health_sub.add_parser("check", help="HTTP endpoint check")
    p_health_check.add_argument("url", help="URL to check")

    p_health_ports = health_sub.add_parser("ports", help="Port scan")
    p_health_ports.add_argument("ports", help="Comma-separated ports (e.g. 80,443,8080)")

    health_sub.add_parser("system", help="System resource health")

    # ── diag ──────────────────────────────────────────────────────────────
    sub.add_parser("diag", help="Full system diagnostics")

    # ── Parse & dispatch ──────────────────────────────────────────────────
    args = parser.parse_args()

    if args.command is None:
        # Default to diag
        cmd_diag(args)
        return

    if args.command == "diag":
        cmd_diag(args)
    elif args.command == "docker":
        docker_dispatch = {
            "status": cmd_docker_status,
            "logs": cmd_docker_logs,
            "health": cmd_docker_health,
            "compose-status": cmd_docker_compose_status,
        }
        handler = docker_dispatch.get(args.docker_cmd)
        if handler:
            handler(args)
        else:
            print(c("  Usage: devops.py docker {status|logs|health|compose-status}", YELLOW))
    elif args.command == "proc":
        proc_dispatch = {
            "list": cmd_proc_list,
            "ports": cmd_proc_ports,
            "zombies": cmd_proc_zombies,
        }
        handler = proc_dispatch.get(args.proc_cmd)
        if handler:
            handler(args)
        else:
            print(c("  Usage: devops.py proc {list|ports|zombies}", YELLOW))
    elif args.command == "logs":
        logs_dispatch = {
            "analyze": cmd_logs_analyze,
            "tail": cmd_logs_tail,
            "frequency": cmd_logs_frequency,
        }
        handler = logs_dispatch.get(args.logs_cmd)
        if handler:
            handler(args)
        else:
            print(c("  Usage: devops.py logs {analyze|tail|frequency}", YELLOW))
    elif args.command == "health":
        health_dispatch = {
            "check": cmd_health_check,
            "ports": cmd_health_ports,
            "system": cmd_health_system,
        }
        handler = health_dispatch.get(args.health_cmd)
        if handler:
            handler(args)
        else:
            print(c("  Usage: devops.py health {check|ports|system}", YELLOW))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
