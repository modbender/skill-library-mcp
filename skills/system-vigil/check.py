import subprocess
import json
import re

def get_disk_usage():
    try:
        # Check root partition
        out = subprocess.check_output(['df', '-h', '/']).decode('utf-8')
        # Extract percentage
        match = re.search(r'(\d+)%', out)
        if match:
            return int(match.group(1))
    except:
        return None
    return None

def get_memory_usage():
    try:
        out = subprocess.check_output(['free', '-m']).decode('utf-8')
        lines = out.split('\n')
        mem_line = [l for l in lines if l.startswith('Mem:')][0]
        parts = mem_line.split()
        total = int(parts[1])
        used = int(parts[2])
        return round((used / total) * 100, 1)
    except:
        return None

def get_load_avg():
    try:
        with open('/proc/loadavg', 'r') as f:
            content = f.read()
            return float(content.split()[2]) # 15-min load
    except:
        return None

def check():
    disk = get_disk_usage()
    mem = get_memory_usage()
    load = get_load_avg()

    status = "ok"
    warnings = []

    if disk and disk > 85:
        status = "warning"
        warnings.append(f"Disk usage high ({disk}%)")
    if disk and disk > 95:
        status = "critical"
        
    if mem and mem > 90:
        status = "warning"
        warnings.append(f"Memory usage high ({mem}%)")
    
    report = {
        "status": status,
        "metrics": {
            "disk_used_percent": disk,
            "memory_used_percent": mem,
            "load_avg_15m": load
        },
        "warnings": warnings
    }
    
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    check()
