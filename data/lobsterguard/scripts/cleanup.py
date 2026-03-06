#!/usr/bin/env python3
"""LobsterGuard - Cleanup ghost OpenClaw processes."""
import subprocess
import os
import sys
import time

def get_processes():
    """Get all openclaw processes."""
    try:
        out = subprocess.check_output(
            "ps aux | grep openclaw | grep -v grep | grep -v cleanup",
            shell=True, text=True
        ).strip()
        if not out:
            return []
        procs = []
        for line in out.split("\n"):
            parts = line.split()
            if len(parts) >= 11:
                pid = int(parts[1])
                cmd = " ".join(parts[10:])
                procs.append({"pid": pid, "cmd": cmd})
        return procs
    except subprocess.CalledProcessError:
        return []

def get_ppid(pid):
    """Get parent PID."""
    try:
        out = subprocess.check_output(
            f"ps -o ppid= -p {pid}", shell=True, text=True
        ).strip()
        return int(out)
    except:
        return -1

def main(silent=False):
    before = get_processes()
    if not before:
        if not silent:
            print("✅ No hay procesos OpenClaw corriendo")
        return

    # Find gateway PID (the main process)
    gateway_pid = None
    for p in before:
        if "openclaw-gateway" in p["cmd"] or "gateway" in p["cmd"]:
            gateway_pid = p["pid"]
            break

    if not gateway_pid:
        # Use the oldest process as gateway
        gateway_pid = before[0]["pid"]

    # Find which PIDs are direct children of gateway (needed)
    needed_pids = {gateway_pid}
    for p in before:
        ppid = get_ppid(p["pid"])
        if ppid == gateway_pid:
            needed_pids.add(p["pid"])

    # Kill orphan processes (not gateway, not direct children of gateway)
    killed = 0
    for p in before:
        if p["pid"] not in needed_pids:
            try:
                os.kill(p["pid"], 15)  # SIGTERM
                killed += 1
            except ProcessLookupError:
                pass
            except PermissionError:
                pass

    if killed > 0:
        time.sleep(2)
        # Force kill remaining
        for p in before:
            if p["pid"] not in needed_pids:
                try:
                    os.kill(p["pid"], 9)  # SIGKILL
                except:
                    pass
        time.sleep(1)

    after = get_processes()
    if not silent:
        print(f"🧹 Limpieza completada")
    if not silent:
        print(f"Antes: {len(before)} procesos")
    if not silent:
        print(f"Ahora: {len(after)} procesos")
    if not silent:
        print(f"Eliminados: {killed} procesos fantasma")
    if not silent and len(after) <= 3:
        print(f"✅ Sistema limpio")
    elif not silent:
        print(f"⚠️ Aun quedan {len(after)} procesos (gateway + hijos directos)")

if __name__ == "__main__":
    silent = "--silent" in sys.argv
    main(silent=silent)
