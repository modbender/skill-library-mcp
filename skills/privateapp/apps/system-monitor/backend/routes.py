"""System Monitor app routes.

Provides real-time system stats at /api/system/stats.
Mounted at api_prefix: /api/system (see app.json).
"""
from __future__ import annotations

import os
import platform
import socket
import subprocess
import time

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/stats")
async def system_stats():
    """Real-time system statistics: CPU, RAM, disk, GPU, uptime."""
    try:
        import psutil
    except ImportError:
        raise HTTPException(500, "psutil not installed — run install.py")

    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    cpu_freq = psutil.cpu_freq()
    boot_time = psutil.boot_time()
    cpu_pct = psutil.cpu_percent(interval=None)

    try:
        load_1, load_5, load_15 = os.getloadavg()
    except AttributeError:
        load_1 = load_5 = load_15 = 0.0

    # GPU — nvidia-smi
    gpu: list[dict] | None = None
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,utilization.gpu,memory.used,memory.total,"
                "temperature.gpu,power.draw,power.limit",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            gpu = []
            for line in result.stdout.strip().splitlines():
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 7:
                    def _fv(s: str) -> float | None:
                        return float(s) if s not in ("[N/A]", "N/A", "") else None
                    gpu.append({
                        "name": parts[0],
                        "utilization_percent": _fv(parts[1]),
                        "memory_used_mb": _fv(parts[2]),
                        "memory_total_mb": _fv(parts[3]),
                        "temperature_c": _fv(parts[4]),
                        "power_draw_w": _fv(parts[5]),
                        "power_limit_w": _fv(parts[6]),
                    })
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # AMD sysfs (always check — may coexist with NVIDIA)
    try:
        import glob as _glob
        for card_path in _glob.glob("/sys/class/drm/card*/device/gpu_busy_percent"):
            device_dir = os.path.dirname(card_path)

            def _rsi(p: str) -> int | None:
                try:
                    with open(p) as f:
                        return int(f.read().strip())
                except Exception:
                    return None

            # Read AMD GPU name from sysfs
            amd_name = "AMD GPU"
            try:
                result = subprocess.run(
                    ["lspci", "-s", os.path.basename(
                        os.path.dirname(os.path.dirname(card_path))
                    ).split("-", 1)[-1] if "-" in os.path.basename(
                        os.path.dirname(os.path.dirname(card_path))
                    ) else "", "-mm"],
                    capture_output=True, text=True, timeout=3,
                )
            except Exception:
                pass

            util = _rsi(card_path)
            vram_used = _rsi(os.path.join(device_dir, "mem_info_vram_used"))
            vram_total = _rsi(os.path.join(device_dir, "mem_info_vram_total"))
            temp = _rsi(os.path.join(device_dir, "hwmon", "hwmon*", "temp1_input")) if False else None
            # Try hwmon for temperature
            try:
                import glob
                hwmon_paths = glob.glob(os.path.join(device_dir, "hwmon", "hwmon*", "temp1_input"))
                if hwmon_paths:
                    temp = _rsi(hwmon_paths[0])
                    if temp is not None:
                        temp = temp // 1000  # millidegrees → degrees
            except Exception:
                pass

            if gpu is None:
                gpu = []
            gpu.append({
                "name": amd_name,
                "utilization_percent": float(util) if util is not None else None,
                "memory_used_mb": round(vram_used / 1048576, 1) if vram_used else None,
                "memory_total_mb": round(vram_total / 1048576, 1) if vram_total else None,
                "temperature_c": float(temp) if temp is not None else None,
                "power_draw_w": None,
                "power_limit_w": None,
            })
    except Exception:
        pass

    services = _get_service_statuses()

    return {
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "uptime_seconds": int(time.time() - boot_time),
        "cpu": {
            "cores": psutil.cpu_count(logical=False),
            "threads": psutil.cpu_count(logical=True),
            "percent": cpu_pct,
            "freq_mhz": round(cpu_freq.current) if cpu_freq else None,
            "load_1m": round(load_1, 2),
            "load_5m": round(load_5, 2),
            "load_15m": round(load_15, 2),
        },
        "memory": {
            "total": mem.total,
            "used": mem.used,
            "available": mem.available,
            "percent": mem.percent,
        },
        "disk": {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent,
        },
        "gpu": gpu,
        "services": services,
    }


def _get_service_statuses() -> list[dict]:
    """Auto-discover services related to this app, OpenClaw, and crawlers.

    Discovery strategy:
    1. Scan user systemd units (~/.config/systemd/user/) for .service and .timer files
    2. Scan system units for known patterns (matrix-synapse, openclaw, litellm, ollama)
    3. Detect watchdog-managed processes (litellm, openclaw)
    No hardcoded list — works for any user's setup.
    """
    if platform.system() != "Linux":
        return []

    services: list[dict] = []
    seen: set[str] = set()

    def _display_name(unit: str) -> str:
        return unit.replace(".service", "").replace(".timer", "")

    def _check_unit(unit: str, scope: str) -> dict | None:
        cmd = ["systemctl"]
        if scope == "user":
            cmd.append("--user")
        cmd += ["is-active", unit]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=3)
            return {
                "name": _display_name(unit),
                "unit": unit,
                "active": r.stdout.strip() == "active",
                "scope": scope,
            }
        except Exception:
            return None

    # 1. Auto-discover user systemd units
    user_unit_dir = os.path.expanduser("~/.config/systemd/user")
    if os.path.isdir(user_unit_dir):
        for fname in sorted(os.listdir(user_unit_dir)):
            if not (fname.endswith(".service") or fname.endswith(".timer")):
                continue
            # Skip .timer if matching .service already found (avoid duplicates)
            base = fname.rsplit(".", 1)[0]
            if fname.endswith(".timer") and base + ".service" in seen:
                continue
            # For oneshot services with timers, prefer the timer
            if fname.endswith(".service"):
                timer_path = os.path.join(user_unit_dir, base + ".timer")
                if os.path.exists(timer_path):
                    continue  # will be picked up as .timer
            # Skip disabled/masked units (only show enabled or currently active)
            try:
                er = subprocess.run(
                    ["systemctl", "--user", "is-enabled", fname],
                    capture_output=True, text=True, timeout=3,
                )
                state = er.stdout.strip()
                if state in ("disabled", "masked"):
                    continue
            except Exception:
                pass
            result = _check_unit(fname, "user")
            if result:
                services.append(result)
                seen.add(fname)

    # 2. Auto-discover relevant system services
    #    Scan for common patterns: openclaw, synapse, matrix, litellm, ollama
    SYSTEM_PATTERNS = ["openclaw", "matrix", "synapse", "litellm", "ollama"]
    try:
        r = subprocess.run(
            ["systemctl", "list-unit-files", "--type=service", "--no-legend", "--no-pager"],
            capture_output=True, text=True, timeout=5,
        )
        if r.returncode == 0:
            for line in r.stdout.strip().splitlines():
                parts = line.split()
                if not parts:
                    continue
                unit = parts[0]
                if any(p in unit.lower() for p in SYSTEM_PATTERNS):
                    if unit not in seen:
                        result = _check_unit(unit, "system")
                        if result:
                            services.append(result)
                            seen.add(unit)
    except Exception:
        pass

    # 3. Detect watchdog-managed processes (not in systemd)
    #    Common pattern: processes managed by watchdog scripts or nohup
    PROCESS_PATTERNS = [
        ("litellm", "litellm.*--port"),
        ("privateapp", r"server\.py.*--port"),
    ]
    for name, pattern in PROCESS_PATTERNS:
        # Skip if already found via systemd
        if any(s["name"] == name for s in services):
            continue
        try:
            r = subprocess.run(
                ["pgrep", "-f", pattern],
                capture_output=True, text=True, timeout=3,
            )
            if r.stdout.strip():  # process found
                services.append({
                    "name": name,
                    "unit": "process",
                    "active": True,
                    "scope": "process",
                })
        except Exception:
            pass

    return services


# ── System Actions (restart, shutdown, update) ───────────────────────

_IS_MACOS = platform.system() == "Darwin"
_IS_LINUX = platform.system() == "Linux"


@router.post("/action/restart")
async def action_restart():
    """Restart the system."""
    try:
        if _IS_MACOS:
            subprocess.Popen(["sudo", "shutdown", "-r", "now"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.Popen(["sudo", "reboot"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return {"status": "ok", "message": "System is restarting..."}
    except Exception as e:
        raise HTTPException(500, f"Failed to restart: {e}")


@router.post("/action/shutdown")
async def action_shutdown():
    """Shutdown the system."""
    try:
        subprocess.Popen(["sudo", "shutdown", "-h", "now"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return {"status": "ok", "message": "System is shutting down..."}
    except Exception as e:
        raise HTTPException(500, f"Failed to shutdown: {e}")


# ── Standalone mode ───────────────────────────────────────────────────
if __name__ == "__main__":
    from fastapi import FastAPI
    from fastapi.staticfiles import StaticFiles
    import uvicorn

    standalone_app = FastAPI(title="System Monitor")
    standalone_app.include_router(router, prefix="/api/system")

    # Serve own frontend/dist/ if built
    dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
    if os.path.isdir(dist):
        standalone_app.mount("/app/system-monitor", StaticFiles(directory=dist, html=True), name="static")

    uvicorn.run(standalone_app, host="0.0.0.0", port=8801)
