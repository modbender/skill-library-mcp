#!/usr/bin/env bash
# System Watchdog — check.sh (macOS)
# Delegates to Python for reliable JSON generation.
set -euo pipefail
export PATH="/usr/sbin:/sbin:$PATH"

python3 << 'PYEOF'
import subprocess, json, re

THRESH_RAM_MB = 4096
THRESH_CPU_PCT = 50
THRESH_STALE_DAYS = 2
THRESH_DISK_PCT = 80

SKIP = {"launchd","kernel_task","WindowServer","loginwindow","opendirectoryd",
    "mds_stores","mds","Finder","Dock","SystemUIServer","airportd","bluetoothd",
    "coreduetd","fseventsd","logd","notifyd","powerd","securityd","syslogd",
    "trustd","configd","distnoted","UserEventAgent","tailscaled","sshd","cron",
    "syncthing","coreaudiod","swd","remoted","symptomsd","watchdogd","sandboxd",
    "diskarbitrationd","timed","node","openclaw","bun","openclaw-gatewa",
    "containermanage","runningboardd","rapportd","sharingd","suggestd","nsurlsessiond"}

def parse_elapsed(s):
    """Parse ps etime like '2-03:15:30' or '03:15' to seconds."""
    s = s.strip()
    days = 0
    if '-' in s:
        d, s = s.split('-', 1)
        days = int(d)
    parts = s.split(':')
    parts = [int(p) for p in parts]
    if len(parts) == 3:
        return days*86400 + parts[0]*3600 + parts[1]*60 + parts[2]
    elif len(parts) == 2:
        return days*86400 + parts[0]*60 + parts[1]
    return days*86400 + parts[0]

def human_elapsed(secs):
    if secs >= 86400: return f"{secs//86400}d"
    if secs >= 3600: return f"{secs//3600}h"
    if secs >= 60: return f"{secs//60}m"
    return f"{secs}s"

# System stats
ram_total = int(subprocess.check_output(["sysctl", "-n", "hw.memsize"]).strip())
vm = subprocess.check_output(["vm_stat"]).decode()
page_size = int(re.search(r'(\d+)', vm.split('\n')[0]).group(1))
def vm_val(label):
    m = re.search(rf'{label}:\s+(\d+)', vm)
    return int(m.group(1)) if m else 0
ram_used = (vm_val("Pages active") + vm_val("Pages wired down") + vm_val("Pages occupied by compressor")) * page_size
ram_pct = round(ram_used * 100 / ram_total, 1)

swap = subprocess.check_output(["sysctl", "-n", "vm.swapusage"]).decode()
swap_total = float(re.search(r'total = ([\d.]+)M', swap).group(1)) if 'total' in swap else 0
swap_used = float(re.search(r'used = ([\d.]+)M', swap).group(1)) if 'used' in swap else 0

load = subprocess.check_output(["sysctl", "-n", "vm.loadavg"]).decode().strip().strip('{}').split()
cores = int(subprocess.check_output(["sysctl", "-n", "hw.ncpu"]).strip())

# Disk
df_out = subprocess.check_output(["df", "-g", "/"]).decode().split('\n')[1].split()
disk_total, disk_used = int(df_out[1]), int(df_out[2])
disk_pct = int(df_out[4].rstrip('%'))

# Processes
ps_out = subprocess.check_output(["ps", "axo", "pid=,pcpu=,rss=,etime=,ucomm=", "-r"]).decode()
issues = []
top_procs = []

for i, line in enumerate(ps_out.strip().split('\n')):
    parts = line.split(None, 4)
    if len(parts) < 5: continue
    pid, cpu, rss, elapsed, name = int(parts[0]), float(parts[1]), int(parts[2]), parts[3], parts[4].strip()
    mem_mb = rss // 1024
    try:
        elapsed_secs = parse_elapsed(elapsed)
    except:
        elapsed_secs = 0
    elapsed_h = human_elapsed(elapsed_secs)
    
    proc = {"pid": pid, "name": name, "cpu_pct": cpu, "mem_mb": mem_mb, "elapsed": elapsed_h}
    
    if i < 10:
        top_procs.append(proc)
    
    if name in SKIP or pid < 100:
        continue
    
    if mem_mb > THRESH_RAM_MB:
        issues.append({"type": "high_ram", "description": f"{name} (PID {pid}) {mem_mb}MB RAM", "details": proc})
    if cpu > THRESH_CPU_PCT:
        issues.append({"type": "high_cpu", "description": f"{name} (PID {pid}) {cpu}% CPU", "details": proc})
    if elapsed_secs > THRESH_STALE_DAYS * 86400 and (mem_mb > 100 or cpu > 1):
        issues.append({"type": "stale", "description": f"{name} (PID {pid}) running {elapsed_h}, {mem_mb}MB", "details": proc})

if disk_pct > THRESH_DISK_PCT:
    issues.append({"type": "disk", "description": f"Root disk at {disk_pct}%", "details": {"mount": "/", "used_pct": disk_pct, "used_gb": disk_used, "total_gb": disk_total}})

result = {
    "suspicious": len(issues) > 0,
    "summary": {
        "ram": f"{ram_used/1073741824:.1f}/{ram_total/1073741824:.1f} GB ({ram_pct}%)",
        "swap": f"{swap_used/1024:.1f}/{swap_total/1024:.1f} GB ({swap_used*100/max(swap_total,1):.0f}%)",
        "load": f"{load[0]}/{load[1]}/{load[2]}",
        "cores": cores,
        "disk": f"{disk_used}/{disk_total} GB ({disk_pct}%)",
    },
    "issues": issues,
    "top_processes": top_procs,
}
print(json.dumps(result, indent=2))
PYEOF
