#!/usr/bin/env python3
"""
Clawned Agent — Discovers installed OpenClaw skills and syncs to server.
Usage:
    python3 agent.py sync
    python3 agent.py scan --path <dir>
    python3 agent.py inventory
    python3 agent.py status
"""

import argparse, hashlib, json, os, platform, signal, sys, time, urllib.request, urllib.error
from datetime import datetime, timezone

CLAWNED_SERVER = os.getenv("CLAWNED_SERVER", "https://api.clawned.io")
CLAWNED_API_KEY = os.getenv("CLAWNED_API_KEY", "")
STATE_FILE = os.path.expanduser("~/.openclaw/clawned_agent.json")
SCAN_BUNDLED = False
BUNDLED_OWNER = "steipete"

def api_request(endpoint, data=None, method="POST"):
    if not CLAWNED_API_KEY:
        print("[!] CLAWNED_API_KEY not set. Get your key at https://clawned.io/settings"); sys.exit(1)
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(f"{CLAWNED_SERVER}{endpoint}", data=body, method=method,
        headers={"Authorization": f"Bearer {CLAWNED_API_KEY}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"[!] API error {e.code}: {e.read().decode() if e.fp else ''}"); sys.exit(1)
    except urllib.error.URLError as e:
        print(f"[!] Cannot reach server: {e.reason}"); sys.exit(1)

def load_state():
    if os.path.exists(STATE_FILE):
        try: return json.load(open(STATE_FILE))
        except: pass
    return {}

def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    json.dump(state, open(STATE_FILE, "w"), indent=2)

def get_skill_dirs():
    """Locate skill directories. Reads openclaw.json only for extraDirs paths — no secrets or credentials are read from config."""
    dirs, home = [], os.path.expanduser("~")
    # Check both possible managed skill locations
    for managed in [os.path.join(home, ".openclaw", "workspace", "skills"),
                    os.path.join(home, ".openclaw", "skills")]:
        if os.path.isdir(managed): dirs.append((managed, "managed"))
    try:
        cfg = json.load(open(os.path.join(home, ".openclaw", "openclaw.json")))
        # Only reads the extraDirs list to know where skills are installed
        for d in cfg.get("skills", {}).get("load", {}).get("extraDirs", []):
            exp = os.path.expanduser(d)
            if os.path.isdir(exp): dirs.append((exp, "extra"))
    except: pass
    for p in [os.path.join(home, ".npm-global", "lib", "node_modules", "openclaw", "skills"),
              "/Applications/OpenClaw.app/Contents/Resources/skills"]:
        if os.path.isdir(p): dirs.append((p, "bundled"))
    return dirs

SCANNABLE_EXTS = {".md", ".py", ".js", ".ts", ".sh", ".mjs", ".cjs", ".jsx", ".tsx",
    ".mts", ".bash", ".zsh", ".rb", ".pl", ".yaml", ".yml", ".json", ".toml",
    ".cfg", ".conf", ".lua", ".go", ".rs", ".r", ".ps1", ".bat", ".cmd", ".txt", ".ini"}
# NOTE: .env is intentionally excluded to avoid leaking secrets
MAX_FILE_SIZE = 512 * 1024  # 512KB per file
MAX_FILES = 30

def collect_skill_files(path):
    """Read scannable files from a skill directory. Only called during explicit 'scan' command, never during 'sync'."""
    files = {}
    for root, _dirs, fnames in os.walk(path):
        for fname in sorted(fnames):
            if len(files) >= MAX_FILES:
                return files
            fpath = os.path.join(root, fname)
            rel = os.path.relpath(fpath, path)
            lower = fname.lower()
            # Check scannable
            if lower in ("makefile", "dockerfile", "skill.md"):
                pass  # always include
            elif not any(lower.endswith(ext) for ext in SCANNABLE_EXTS):
                continue
            try:
                sz = os.path.getsize(fpath)
                if sz == 0 or sz > MAX_FILE_SIZE:
                    continue
                files[rel] = open(fpath, errors="replace").read()
            except:
                continue
    return files

def read_skill(name, path, source, dir_owner="", include_files=False):
    """Read a skill directory. Only reads _meta.json or SKILL.md for metadata.
    Full file collection only happens when include_files=True (explicit scan)."""
    meta_path = os.path.join(path, "_meta.json")
    if os.path.isfile(meta_path):
        try:
            meta = json.load(open(meta_path))
            owner = meta.get("owner", "") or dir_owner
            result = {
                "owner": owner,
                "slug": meta.get("slug", name),
                "displayName": meta.get("displayName", name),
                "latest": meta.get("latest", {"version": "", "publishedAt": 0, "commit": ""}),
            }
            if include_files:
                result["files"] = collect_skill_files(path)
            return result
        except Exception as e:
            print(f"[!] Failed to read _meta.json for {name}: {e}")
            pass

    # Fallback: construct from SKILL.md (use directory name as slug)
    sm = os.path.join(path, "SKILL.md")
    try: content = open(sm, errors="replace").read()
    except: return None
    desc = ""
    for line in content.split("\n"):
        if line.strip().startswith("description:"):
            desc = line.split(":", 1)[1].strip().strip("'\""); break
    fhash = hashlib.sha256(content.encode()).hexdigest()
    owner = dir_owner or os.path.basename(os.path.dirname(path))
    if owner == "skills": owner = "unknown"
    display = name
    if desc:
        display = desc[:120] if len(desc) > 120 else desc
    result = {
        "owner": owner,
        "slug": name,
        "displayName": display,
        "latest": {"version": "", "publishedAt": 0, "commit": fhash},
    }
    if include_files:
        result["files"] = collect_skill_files(path)
    return result

def discover_skills():
    skills, seen = [], set()
    for d, src in get_skill_dirs():
        if src == "bundled" and not SCAN_BUNDLED:
            print(f"[*] Skipping bundled skills: {d} (use --include-bundled to include)")
            continue
        print(f"[*] Scanning directory: {d} ({src})")
        # For bundled skills, owner is always BUNDLED_OWNER
        default_owner = BUNDLED_OWNER if src == "bundled" else ""
        for owner_name in sorted(os.listdir(d)):
            owner_path = os.path.join(d, owner_name)
            if not os.path.isdir(owner_path): continue
            # Check if this is a direct skill dir (has _meta.json or SKILL.md)
            if os.path.isfile(os.path.join(owner_path, "_meta.json")) or os.path.isfile(os.path.join(owner_path, "SKILL.md")):
                key = owner_name
                if key == "clawned" or key in seen: continue
                seen.add(key)
                s = read_skill(owner_name, owner_path, src, dir_owner=default_owner)
                if s: skills.append(s)
                continue
            # Otherwise, this is an owner directory — look for slug dirs inside
            for slug_name in sorted(os.listdir(owner_path)):
                slug_path = os.path.join(owner_path, slug_name)
                if not os.path.isdir(slug_path): continue
                if not os.path.isfile(os.path.join(slug_path, "_meta.json")) and not os.path.isfile(os.path.join(slug_path, "SKILL.md")):
                    continue
                key = f"{owner_name}/{slug_name}"
                if key in seen: continue
                seen.add(key)
                s = read_skill(slug_name, slug_path, src, dir_owner=owner_name)
                if s: skills.append(s)
    return skills

def cmd_sync():
    """Sync skill metadata to dashboard. Only sends: skill name, owner, version, slug.
    No file contents are uploaded during sync — files are never collected here."""
    state = load_state()
    if "agent_id" not in state:
        print("[*] Registering agent...")
        # Sends only hostname and OS for agent registration
        r = api_request("/api/skills/agent/register", {"hostname": platform.node(), "os_platform": platform.system().lower()})
        state["agent_id"] = r["agent_id"]; save_state(state)
        print(f"[+] Agent: {r['agent_id']}")
    print("[*] Discovering skills...")
    skills = discover_skills()  # include_files=False by default — no file contents collected
    print(f"[*] Found {len(skills)} skills, syncing...")
    # Sends only metadata: {owner, slug, displayName, latest:{version, publishedAt, commit}}
    result = api_request("/api/skills/agent/sync", {"agent_id": state["agent_id"], "skills": skills})
    state["last_sync"] = datetime.now(timezone.utc).isoformat()
    state["last_count"] = len(skills); save_state(state)
    pending = result.get('pending_scans', 0)
    print(f"\n{'='*60}\n  CLAWNED SYNC COMPLETE\n  Processed: {result['processed']}  Pending scans: {pending}\n{'='*60}")
    for r in result.get("results", []):
        status = r.get("status", "")
        if status == "queued":
            print(f"  🔄 {r['skill_name']}: queued for scanning")
        elif status == "linked":
            rec = r.get("recommendation", "")
            e = {"SAFE": "✅", "REVIEW": "⚠️", "REJECT": "🚨"}.get(rec, "❓")
            print(f"  {e} {r['skill_name']}: {rec} (linked existing scan)")
        else:
            print(f"  ⏭️  {r['skill_name']}: {status}")
    if pending: print(f"\n  🔄 {pending} skill(s) queued — scans running in background on server")

def cmd_inventory():
    skills = discover_skills()
    print(f"\n  INSTALLED SKILLS ({len(skills)})\n{'='*60}")
    for s in skills:
        name = s.get("displayName") or s.get("slug", "unknown")
        owner = s.get("owner", "unknown")
        version = s.get("latest", {}).get("version", "")
        print(f"  {owner}/{s.get('slug', '?')}")
        print(f"    Display: {name}  Version: {version or 'n/a'}\n")

def cmd_scan(path=None, slug=None):
    if path:
        sd = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, sd)
        try:
            from scan import SkillScanner, print_report_text
            print_report_text(SkillScanner(path).scan())
        except ImportError:
            print("[!] Local scanner not found, sending to server via URL...")
            s = read_skill(os.path.basename(path), path, "manual", include_files=True)
            if s:
                skill_path = f"{s['owner']}/{s['slug']}" if s['owner'] else s['slug']
                url = f"https://github.com/openclaw/skills/blob/main/skills/{skill_path}"
                print(json.dumps(api_request("/api/scans/url", {"url": url}), indent=2))
    elif slug:
        # slug can be a GitHub URL or owner/slug shorthand
        url = slug if slug.startswith("http") else f"https://github.com/openclaw/skills/blob/main/skills/{slug}"
        print(json.dumps(api_request("/api/scans/url", {"url": url}), indent=2))

def cmd_status():
    state = load_state()
    print(f"\n{'='*60}\n  CLAWNED AGENT STATUS\n{'='*60}")
    print(f"  Server:    {CLAWNED_SERVER}")
    print(f"  API Key:   {'configured' if CLAWNED_API_KEY else 'NOT SET'}")
    print(f"  Agent ID:  {state.get('agent_id', 'not registered')}")
    print(f"  Last sync: {state.get('last_sync', 'never')}")
    print(f"  Skills:    {state.get('last_count', 'unknown')}")
    print(f"  Host:      {platform.node()} ({platform.system()})\n{'='*60}")

def get_skill_snapshot():
    """Return a set of owner/slug keys for all currently discovered skills."""
    return {f"{s.get('owner','')}/{s.get('slug','')}" for s in discover_skills()}

def cmd_watch(interval=5):
    """Watch skills directory and auto-sync when skills are added or removed."""
    print(f"[*] Watching for skill changes (every {interval}s). Press Ctrl+C to stop.")
    running = True
    def stop(sig, frame): nonlocal running; running = False; print("\n[*] Stopping watcher...")
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    prev = get_skill_snapshot()
    print(f"[*] Currently tracking {len(prev)} skill(s)")

    while running:
        time.sleep(interval)
        current = get_skill_snapshot()
        added = current - prev
        removed = prev - current
        if added or removed:
            for s in added: print(f"[+] New skill detected: {s}")
            for s in removed: print(f"[-] Skill removed: {s}")
            print("[*] Changes detected, running sync...")
            try:
                cmd_sync()
            except SystemExit:
                pass
            prev = current

def main():
    global SCAN_BUNDLED
    p = argparse.ArgumentParser(description="Clawned Agent")
    p.add_argument("--include-bundled", action="store_true", help="Include bundled OpenClaw skills in scan/sync")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("sync"); sub.add_parser("inventory"); sub.add_parser("status")
    wp = sub.add_parser("watch")
    wp.add_argument("--interval", type=int, default=5, help="Poll interval in seconds")
    sp = sub.add_parser("scan")
    g = sp.add_mutually_exclusive_group(required=True)
    g.add_argument("--path"); g.add_argument("--slug")
    args = p.parse_args()
    SCAN_BUNDLED = args.include_bundled
    {"sync": cmd_sync, "inventory": cmd_inventory, "status": cmd_status,
     "watch": lambda: cmd_watch(args.interval if hasattr(args, 'interval') else 5),
     "scan": lambda: cmd_scan(args.path if hasattr(args, 'path') else None, args.slug if hasattr(args, 'slug') else None)}[args.cmd]()

if __name__ == "__main__":
    main()
