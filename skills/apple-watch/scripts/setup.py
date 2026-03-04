"""
Health Auto Export one-click setup.

Usage:
    python setup.py

No git required. No Docker required.
Everything stays in the health-sync skill directory.
"""

import json
import os
import re
import sys
import socket
import subprocess
import base64
import secrets
import urllib.request
import zipfile
import io
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = SKILL_DIR / "data"
TEMPLATE_DIR = SKILL_DIR / "templates"
SERVER_SCRIPT = SKILL_DIR / "server.py"
DASHBOARD_FILE = SKILL_DIR / "dashboard.html"
UPSTREAM_DIR = SKILL_DIR / "upstream"
CONFIG_FILE = SKILL_DIR / ".env.json"
REPO_URL = "https://github.com/HealthyApps/health-auto-export-server"
REPO_ZIP = "https://github.com/HealthyApps/health-auto-export-server/archive/refs/heads/main.zip"
PORT = 3001


def load_config():
    """Load or generate config. API key stored in .env.json (gitignored)."""
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    api_key = "sk-health-" + secrets.token_hex(16)
    config = {"api_key": api_key}
    CONFIG_FILE.write_text(json.dumps(config, indent=2), encoding="utf-8")
    print(f"  Generated new API key -> .env.json")
    return config


def ensure_flask():
    """Install flask if not present."""
    try:
        import flask  # noqa: F401
    except ImportError:
        print("  Flask not found, installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])
        print("  Flask installed.")


def get_lan_ip():
    # Windows: ipconfig
    if sys.platform == "win32":
        try:
            out = subprocess.check_output(["ipconfig"], text=False).decode("gbk", errors="ignore")
            ips = re.findall(r"192\.168\.\d+\.\d+", out)
            if ips:
                return ips[0]
        except Exception:
            pass
    # macOS / Linux: ip or ifconfig
    else:
        for cmd in [["ip", "-4", "addr"], ["ifconfig"]]:
            try:
                out = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
                ips = re.findall(r"192\.168\.\d+\.\d+", out)
                if ips:
                    return ips[0]
            except (FileNotFoundError, subprocess.CalledProcessError):
                continue
    # universal fallback: UDP socket trick
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        if not ip.startswith("198.18"):
            return ip
    except Exception:
        pass
    return "YOUR_LAN_IP"


DATA_TYPES = {
    "1": {
        "label": "Health Metrics (all)",
        "key": "healthMetrics",
        "includeHealthMetrics": True,
        "includeWorkouts": False,
        "metrics": [
            "Heart Rate", "Resting Heart Rate", "Heart Rate Variability",
            "Sleep Analysis", "Blood Oxygen Saturation", "Respiratory Rate",
            "Step Count", "Walking + Running Distance", "Flights Climbed",
            "Active Energy", "Basal Energy Burned", "Apple Exercise Time",
            "Apple Stand Hour", "Apple Stand Time", "Apple Move Time",
            "Walking Speed", "Walking Step Length", "Walking Asymmetry Percentage",
            "Walking Double Support Percentage", "Walking Heart Rate Average",
            "VO2 Max", "Body Temperature", "Apple Sleeping Wrist Temperature",
            "Headphone Audio Exposure", "Environmental Audio Exposure",
            "Time in Daylight", "Breathing Disturbances",
            "Weight & Body Mass", "Body Fat Percentage", "Body Mass Index",
            "Lean Body Mass", "Height",
            "Blood Pressure", "Blood Glucose",
            "Caffeine", "Dietary Energy", "Protein", "Carbohydrates",
            "Total Fat", "Dietary Water",
            "Physical Effort", "Mindful Minutes",
        ],
    },
    "2": {
        "label": "Sleep only",
        "key": "healthMetrics",
        "includeHealthMetrics": True,
        "includeWorkouts": False,
        "metrics": [
            "Sleep Analysis", "Heart Rate", "Resting Heart Rate",
            "Heart Rate Variability", "Blood Oxygen Saturation",
            "Respiratory Rate", "Apple Sleeping Wrist Temperature",
            "Breathing Disturbances",
        ],
    },
    "3": {
        "label": "Heart & Vitals",
        "key": "healthMetrics",
        "includeHealthMetrics": True,
        "includeWorkouts": False,
        "metrics": [
            "Heart Rate", "Resting Heart Rate", "Heart Rate Variability",
            "Blood Oxygen Saturation", "Blood Pressure", "Respiratory Rate",
            "Body Temperature", "VO2 Max",
        ],
    },
    "4": {
        "label": "Activity & Fitness",
        "key": "healthMetrics",
        "includeHealthMetrics": True,
        "includeWorkouts": False,
        "metrics": [
            "Step Count", "Walking + Running Distance", "Flights Climbed",
            "Active Energy", "Basal Energy Burned", "Apple Exercise Time",
            "Apple Stand Hour", "Walking Speed", "Walking Step Length",
            "Physical Effort", "VO2 Max",
        ],
    },
    "5": {
        "label": "Workouts",
        "key": "workouts",
        "includeHealthMetrics": False,
        "includeWorkouts": True,
        "metrics": [],
    },
}


def step_upstream():
    """Clone or download upstream repo for reference + Grafana dashboards."""
    if UPSTREAM_DIR.exists():
        print("  [skip] upstream/ already exists")
        return

    # try git first
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
        has_git = True
    except (FileNotFoundError, subprocess.CalledProcessError):
        has_git = False

    if has_git:
        print(f"  git clone -> upstream/")
        env = os.environ.copy()
        for k in ["https_proxy", "http_proxy", "HTTPS_PROXY", "HTTP_PROXY"]:
            env.pop(k, None)
        result = subprocess.run(
            ["git", "clone", REPO_URL, str(UPSTREAM_DIR)],
            env=env,
        )
        if result.returncode == 0:
            print("  done")
            return
        print("  git clone failed, trying zip download...")

    # fallback: download zip
    print(f"  Downloading zip (no git needed)...")
    try:
        # bypass proxy for github download
        no_proxy_handler = urllib.request.ProxyHandler({})
        opener = urllib.request.build_opener(no_proxy_handler)
        req = urllib.request.Request(REPO_ZIP)
        with opener.open(req, timeout=30) as resp:
            zip_data = resp.read()
        with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
            UPSTREAM_DIR.mkdir(parents=True, exist_ok=True)
            for member in zf.namelist():
                # strip top-level dir (health-auto-export-server-main/)
                parts = member.split("/", 1)
                if len(parts) < 2 or not parts[1]:
                    continue
                target = UPSTREAM_DIR / parts[1]
                if member.endswith("/"):
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(zf.read(member))
        print("  done")
    except Exception as e:
        print(f"  [warn] download failed: {e}")
        print("  Not critical - upstream repo is only for Grafana dashboards reference")


def step_server(api_key):
    if SERVER_SCRIPT.exists():
        print(f"  [skip] server.py exists")
        return

    print("  Writing server.py ...")
    code = '''import json
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
CONFIG_FILE = BASE_DIR / ".env.json"
DASHBOARD_FILE = BASE_DIR / "dashboard.html"


def get_api_key():
    if CONFIG_FILE.exists():
        cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        return cfg.get("api_key", "")
    return ""


@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, api-key"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


def check_auth():
    return request.headers.get("api-key", "") == get_api_key()


def save_json(category, name, records):
    category_dir = DATA_DIR / category
    category_dir.mkdir(exist_ok=True)
    filepath = category_dir / f"{name}.jsonl"
    with open(filepath, "a", encoding="utf-8") as f:
        for record in records:
            record["_received_at"] = datetime.now().isoformat()
            f.write(json.dumps(record, default=str, ensure_ascii=False) + "\\n")
    return len(records)


@app.route("/api/data", methods=["POST"])
def ingest():
    if not check_auth():
        return jsonify({"error": "unauthorized"}), 401
    body = request.json
    if not body or "data" not in body:
        return jsonify({"error": "no data"}), 400
    data = body["data"]
    result = {}
    for metric in data.get("metrics", []):
        name = metric.get("name", "unknown").lower().replace(" ", "_")
        records = metric.get("data", [])
        for r in records:
            r["_metric_name"] = metric.get("name")
            r["_units"] = metric.get("units", "")
        count = save_json("metrics", name, records)
        result[name] = {"success": True, "count": count}
    workouts = data.get("workouts", [])
    if workouts:
        count = save_json("workouts", "workouts", workouts)
        result["workouts"] = {"success": True, "count": count}
    return jsonify(result), 200


@app.route("/api/latest/<category>/<name>", methods=["GET"])
def get_latest(category, name):
    if not check_auth():
        return jsonify({"error": "unauthorized"}), 401
    filepath = DATA_DIR / category / f"{name}.jsonl"
    if not filepath.exists():
        return jsonify({"error": "not found"}), 404
    n = int(request.args.get("n", 10))
    lines = filepath.read_text(encoding="utf-8").strip().split("\\n")
    latest = [json.loads(line) for line in lines[-n:]]
    return jsonify(latest), 200


@app.route("/api/summary", methods=["GET"])
def summary():
    if not check_auth():
        return jsonify({"error": "unauthorized"}), 401
    result = {}
    for category_dir in DATA_DIR.iterdir():
        if not category_dir.is_dir():
            continue
        category = category_dir.name
        result[category] = {}
        for f in category_dir.glob("*.jsonl"):
            lines = f.read_text(encoding="utf-8").strip().split("\\n")
            last = json.loads(lines[-1]) if lines and lines[0] else None
            result[category][f.stem] = {
                "total_records": len(lines),
                "last_record": last
            }
    return jsonify(result), 200


@app.route("/dashboard", methods=["GET"])
def dashboard():
    if DASHBOARD_FILE.exists():
        return DASHBOARD_FILE.read_text(encoding="utf-8"), 200, {"Content-Type": "text/html"}
    return "dashboard.html not found - run setup.py first", 404


if __name__ == "__main__":
    api_key = get_api_key()
    if not api_key:
        print("ERROR: .env.json not found. Run setup.py first.")
        exit(1)
    print(f"Health data server on http://0.0.0.0:''' + str(PORT) + '''")
    print(f"Dashboard: http://localhost:''' + str(PORT) + '''/dashboard")
    print(f"API key: {api_key}")
    print(f"Data dir: {DATA_DIR}")
    app.run(host="0.0.0.0", port=''' + str(PORT) + ''')
'''
    SERVER_SCRIPT.write_text(code, encoding="utf-8")
    print(f"  Written: {SERVER_SCRIPT}")


def step_dashboard(api_key):
    if DASHBOARD_FILE.exists():
        print(f"  [skip] dashboard.html exists")
        return

    print("  Writing dashboard.html ...")
    html = '''<!doctype html>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Health Dashboard</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0a0a0a;color:#e0e0e0;font:14px/1.5 -apple-system,system-ui,sans-serif;padding:20px}
h1{font-size:20px;margin-bottom:16px;color:#fff}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:12px}
.card{background:#161616;border:1px solid #222;border-radius:10px;padding:16px}
.card h2{font-size:14px;color:#888;margin-bottom:8px;text-transform:uppercase;letter-spacing:0.5px}
.card .value{font-size:28px;font-weight:700;color:#fff}
.card .unit{font-size:13px;color:#666;margin-left:4px}
.card .time{font-size:11px;color:#555;margin-top:4px}
.status{margin-bottom:16px;font-size:12px;color:#555}
.status.ok{color:#4caf50}
.status.err{color:#f44336}
#refresh{background:#222;border:1px solid #333;color:#fff;padding:6px 14px;border-radius:6px;cursor:pointer;font-size:12px;margin-bottom:16px}
</style>
<h1>Health Dashboard</h1>
<div class="status" id="status">loading...</div>
<button id="refresh" onclick="load()">refresh</button>
<div class="grid" id="grid"></div>
<script>
const API='http://localhost:''' + str(PORT) + '''';
const KEY=''' + json.dumps(api_key) + ''';
const IMPORTANT=['sleep_analysis','heart_rate','resting_heart_rate','step_count',
'active_energy','walking_running_distance','heart_rate_variability',
'blood_oxygen_saturation','respiratory_rate','basal_energy_burned',
'headphone_audio_exposure','time_in_daylight','walking_speed'];
async function api(path){const r=await fetch(API+path,{headers:{'api-key':KEY}});return r.json();}
function fmt(d){if(!d)return'-';const s=String(d);const m=s.match(/(\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2})/);return m?m[1]:s.slice(0,16);}
function renderCard(name,info){
const last=info.last_record||{};let val='-';let unit=last._units||'';
if(last.qty!==undefined)val=Math.round(last.qty*100)/100;
else if(last.Avg!==undefined)val=last.Min+'-'+last.Avg+'-'+last.Max;
else if(last.sleepStart!==undefined){val=Math.round(((last.core||0)+(last.rem||0)+(last.deep||0))/6)/10;unit='hrs';}
return '<div class="card"><h2>'+name.replace(/_/g,' ')+'</h2><div class="value">'+val+'<span class="unit">'+unit+'</span></div><div class="time">'+fmt(last.date)+' | '+info.total_records+' records</div></div>';}
async function load(){
const st=document.getElementById('status'),grid=document.getElementById('grid');
try{const data=await api('/api/summary');const m=data.metrics||{};let h='';
for(const n of IMPORTANT){if(m[n])h+=renderCard(n,m[n]);}
for(const[n,i]of Object.entries(m)){if(!IMPORTANT.includes(n))h+=renderCard(n,i);}
for(const[n,i]of Object.entries(data.workouts||{})){h+=renderCard('workout: '+n,i);}
grid.innerHTML=h;st.className='status ok';st.textContent='connected | '+new Date().toLocaleTimeString();
}catch(e){st.className='status err';st.textContent='error: '+e.message;grid.innerHTML='';}}
load();setInterval(load,30000);
</script>'''
    DASHBOARD_FILE.write_text(html, encoding="utf-8")
    print(f"  Written: {DASHBOARD_FILE}")


def make_template(name, data_type, lan_ip, api_key):
    headers_b64 = base64.b64encode(json.dumps([{"api-key": api_key}]).encode()).decode()
    return {
        "includeSymptoms": False,
        "notifyOnUpdate": True,
        "workoutTypes": [],
        "metrics": data_type["metrics"],
        "exportAggregation": "Minutes",
        "includeWorkouts": data_type.get("includeWorkouts", False),
        "includeHeartRateNotifications": False,
        "includeHealthMetrics": data_type.get("includeHealthMetrics", False),
        "includeWorkoutMetadata": True,
        "exportDataType": data_type["key"],
        "notifyWhenRun": True,
        "name": name,
        "aggregateData": True,
        "batchRequests": True,
        "aggregateSleep": True,
        "exportFileLength": "day",
        "exportVersion": "ExportVersion.v2",
        "exportDestination": "restApi",
        "workoutsMetadaInterval": "minutes",
        "includeECG": False,
        "syncCadenceInterval": "hours",
        "headers": headers_b64,
        "includeStateOfMind": False,
        "requestTimeout": 60,
        "metadata": {},
        "includeRoutes": True,
        "syncCadenceNumber": 1,
        "exportPeriod": "Since Last Sync",
        "convertToGoogleSheet": False,
        "exportFormat": "JSON",
        "urlString": f"http://{lan_ip}:{PORT}/api/data",
    }


def step_templates(lan_ip, api_key):
    print()
    print("  Data types:")
    for k, v in DATA_TYPES.items():
        print(f"    [{k}] {v['label']}")
    print()
    print("  Select (comma separated, e.g. 1,5):")
    print("  Enter for [1] Health Metrics (all):")

    choice = input("  > ").strip() or "1"
    TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)

    for sel in [c.strip() for c in choice.split(",")]:
        if sel not in DATA_TYPES:
            print(f"  Unknown: {sel}, skip")
            continue
        dt = DATA_TYPES[sel]
        name = f"claw-{dt['key']}" if sel != "5" else "claw-workouts"
        filepath = TEMPLATE_DIR / f"hae_export_{name}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(make_template(name, dt, lan_ip, api_key), f, indent=2, ensure_ascii=False)
        print(f"  Generated: {filepath}")


def step_gitignore():
    gitignore = SKILL_DIR / ".gitignore"
    if gitignore.exists():
        content = gitignore.read_text(encoding="utf-8")
        needed = []
        for entry in [".env.json", "data/", "upstream/"]:
            if entry not in content:
                needed.append(entry)
        if needed:
            with open(gitignore, "a", encoding="utf-8") as f:
                f.write("\n" + "\n".join(needed) + "\n")
    else:
        gitignore.write_text(".env.json\ndata/\nupstream/\n", encoding="utf-8")


def main():
    print()
    print("=" * 56)
    print("  Health Auto Export - One Click Setup")
    print("=" * 56)
    print()
    print("  Before you start, make sure you have:")
    print()
    print("    [Hardware]")
    print("      - Apple Watch (watchOS 9+)")
    print("      - iPhone (paired with the watch)")
    print("      - PC/Mac on the same Wi-Fi as the iPhone")
    print()
    print("    [Phone App]")
    print("      - Health Auto Export (iOS)")
    print("        https://apps.apple.com/us/app/health-auto-export-json-csv/id1115567069")
    print("        Premium required for auto-sync ($24.99 lifetime)")
    print()
    print("  Press Enter to continue (or Ctrl+C to quit)... ", end="")
    input()

    ensure_flask()
    config = load_config()
    api_key = config["api_key"]
    lan_ip = get_lan_ip()

    print()
    print(f"  Skill dir:   {SKILL_DIR}")
    print(f"  LAN IP:      {lan_ip}")
    print(f"  Server:      http://{lan_ip}:{PORT}/api/data")
    print(f"  Dashboard:   http://localhost:{PORT}/dashboard")
    print(f"  API Key:     {api_key}")
    print()

    step_gitignore()

    print("[1/4] Download upstream repo (Grafana dashboards reference)")
    step_upstream()
    print()
    print("[2/4] Setup server (Python only, no Docker)")
    step_server(api_key)
    print()
    print("[3/4] Generate dashboard")
    step_dashboard(api_key)
    print()
    print("[4/4] Generate automation templates")
    step_templates(lan_ip, api_key)

    print()
    print("  " + "=" * 46)
    print("  SETUP COMPLETE")
    print()
    print("  Structure:")
    print(f"    {SKILL_DIR}/")
    print(f"      server.py        <- run this")
    print(f"      dashboard.html   <- or http://localhost:{PORT}/dashboard")
    print(f"      data/            <- received health data")
    print(f"      templates/       <- phone automation configs")
    print(f"      upstream/        <- original repo (Grafana etc)")
    print(f"      scripts/setup.py <- this script")
    print(f"      SKILL.md         <- agent docs")
    print(f"      .env.json        <- API key (auto-generated, gitignored)")
    print()
    print("  Phone setup (Health Auto Export app):")
    print()
    print(f"    1. Send templates/hae_export_*.json to iPhone (AirDrop, email, etc)")
    print(f"    2. Open the file on iPhone -> auto-imports into app")
    print(f"    3. IMPORTANT: manually add API key header after import:")
    print(f"         Open automation -> Headers -> Add Header")
    print(f"         Key:   api-key")
    print(f"         Value: {api_key}")
    print(f"    4. Tap 'Manual Export' to test")
    print(f"    5. Check http://localhost:{PORT}/dashboard")
    print()

    print(f"  Next: start the server separately:")
    print(f"    python server.py")
    print()


if __name__ == "__main__":
    main()
