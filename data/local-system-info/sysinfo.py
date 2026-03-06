import psutil
import argparse
import json
import sys

def get_cpu():
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "cpu_count": psutil.cpu_count(),
        "load_avg": [x / psutil.cpu_count() for x in psutil.getloadavg()] if hasattr(psutil, "getloadavg") else []
    }

def get_memory():
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    return {
        "total": mem.total,
        "available": mem.available,
        "percent": mem.percent,
        "swap_percent": swap.percent
    }

def get_disk():
    usage = psutil.disk_usage('/')
    return {
        "total": usage.total,
        "used": usage.used,
        "free": usage.free,
        "percent": usage.percent
    }

def get_processes(limit=20):
    procs = []
    for p in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
        try:
            p_info = p.info
            procs.append(p_info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    # Sort by CPU usage descending
    procs.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
    return procs[:limit]

def get_summary():
    return {
        "cpu": get_cpu(),
        "memory": get_memory(),
        "disk": get_disk()
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Local System Info Skill")
    parser.add_argument("action", choices=["summary", "cpu", "memory", "disk", "processes"], help="Action to perform")
    parser.add_argument("--limit", type=int, default=20, help="Limit for process list")
    
    args = parser.parse_args()
    
    result = {}
    try:
        if args.action == "summary":
            result = get_summary()
        elif args.action == "cpu":
            result = get_cpu()
        elif args.action == "memory":
            result = get_memory()
        elif args.action == "disk":
            result = get_disk()
        elif args.action == "processes":
            result = get_processes(args.limit)
            
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
