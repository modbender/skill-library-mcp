#!/usr/bin/env python3
"""
LobsterGuard Skill Scanner — 4-layer pre-installation security analysis.
Layer 1: SKILL.md / README pattern matching
Layer 2: Script static analysis (.py, .sh, .js, .ts, etc.)
Layer 3: GitHub publisher reputation (conditional — only if L1/L2 find issues)
Layer 4: SHA-256 hash blacklist
"""
import os
import sys
import json
import re
import hashlib
import subprocess
from datetime import datetime, timezone
from telegram_utils import get_telegram_config, send_telegram

BOT_TOKEN, CHAT_ID = get_telegram_config()



SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "data")
BLACKLIST_FILE = os.path.join(DATA_DIR, "skill_blacklist.json")

# ─── Layer 1: Documentation Patterns ──────────────────────────────────────────

LAYER1_CRITICAL = [
    (r'curl\s+.*\|\s*(?:sudo\s+)?(?:ba)?sh', "curl piped to shell (remote code execution)"),
    (r'wget\s+.*\|\s*(?:sudo\s+)?(?:ba)?sh', "wget piped to shell (remote code execution)"),
    (r'(?:base64\s+(?:-d|--decode)\s*\|)', "base64 decode piped to execution"),
    (r'eval\s*\(.*(?:base64|atob|Buffer\.from)', "eval with base64 encoded data"),
]

LAYER1_SUSPICIOUS = [
    (r'(?:bit\.ly|tinyurl|t\.co|goo\.gl|is\.gd|rb\.gy|short\.io)/', "shortened URL (hides real destination)"),
    (r'chmod\s+\+x', "makes files executable"),
    (r'sudo\s+', "requires sudo/root access"),
    (r'(?:copy|paste|run)\s+(?:this|the\s+following)\s+(?:command|code|script)\s+in\s+(?:your\s+)?(?:terminal|cmd|powershell|console)', "ClickFix-style social engineering"),
    (r'npm\s+install\s+-g\s+(?!openclaw)', "global npm install of unknown package"),
    (r'pip\s+install\s+(?!openclaw)', "pip install of unknown package"),
    (r'docker\s+run\s+', "runs Docker container"),
    (r'systemctl\s+(?:enable|start)\s+', "enables/starts system service"),
    (r'crontab\s+', "modifies scheduled tasks"),
    (r'\.onion\b', "Tor .onion address"),
    (r'discord\.gg/|t\.me/', "external chat invite link"),
]

def analyze_layer1(skill_dir):
    """Analyze SKILL.md and README for suspicious patterns."""
    findings = {"critical": [], "suspicious": [], "info": []}
    
    doc_files = []
    for name in ["SKILL.md", "README.md", "INSTALL.md", "setup.md", "INSTRUCTIONS.md"]:
        path = os.path.join(skill_dir, name)
        if os.path.exists(path):
            doc_files.append(path)
    
    for sub in os.listdir(skill_dir):
        subpath = os.path.join(skill_dir, sub)
        if os.path.isdir(subpath):
            for name in ["SKILL.md", "README.md"]:
                path = os.path.join(subpath, name)
                if os.path.exists(path):
                    doc_files.append(path)
    
    if not doc_files:
        findings["info"].append("No documentation files found")
        return findings
    
    for fpath in doc_files:
        try:
            content = open(fpath, errors="ignore").read()
            fname = os.path.relpath(fpath, skill_dir)
            
            for pattern, desc in LAYER1_CRITICAL:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    findings["critical"].append(f"{fname}: {desc} ({len(matches)}x)")
            
            for pattern, desc in LAYER1_SUSPICIOUS:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    findings["suspicious"].append(f"{fname}: {desc} ({len(matches)}x)")
        except OSError:
            pass
    
    return findings

# ─── Layer 2: Script Analysis ────────────────────────────────────────────────

LAYER2_CRITICAL = [
    (r'curl\s+.*\|\s*(?:sudo\s+)?(?:ba)?sh', "curl piped to shell"),
    (r'wget\s+.*\|\s*(?:sudo\s+)?(?:ba)?sh', "wget piped to shell"),
    (r'eval\s*\(.*(?:base64|atob|Buffer\.from)', "eval with encoded data"),
    (r'exec\s*\(.*(?:base64|decode|decompress)', "exec with encoded data"),
    (r'(?:nc|ncat|netcat)\s+-[elp]', "netcat listener (reverse shell)"),
    (r'bash\s+-i\s+>&\s+/dev/tcp/', "bash reverse shell"),
    (r'python3?\s+-c.*socket.*connect', "python reverse shell"),
    (r'(?:rm\s+-rf\s+[~/]|rm\s+-rf\s+/(?!tmp))', "destructive rm -rf on system paths"),
    (r'(?:mkfifo|mknod).*(?:/dev/tcp|nc\b)', "named pipe reverse shell"),
    (r'(?:ssh-keygen|ssh-copy-id|authorized_keys)', "SSH key manipulation"),
]

LAYER2_SUSPICIOUS = [
    (r'(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?', "hardcoded IP address"),
    (r'~/.(?:ssh|openclaw/credentials|env|gnupg|aws|config/gcloud)', "accesses sensitive dotfiles"),
    (r'(?:ANTHROPIC_API_KEY|OPENAI_API_KEY|AWS_SECRET|GITHUB_TOKEN)', "references API keys/secrets"),
    (r'/etc/(?:passwd|shadow|sudoers)', "accesses system auth files"),
    (r'base64\s+(?:-d|--decode)', "base64 decoding"),
    (r'(?:urllib|requests|httpx|aiohttp)\.(?:get|post|put)\s*\(', "makes HTTP requests"),
    (r'subprocess\.(?:call|run|Popen)\s*\(', "runs subprocesses"),
    (r'os\.(?:system|popen|exec)', "executes system commands"),
    (r'(?:\.env|\.env\.local|\.env\.secure)', "references environment files"),
    (r'(?:wget|curl)\s+(?:-[sS]?\s+)?https?://(?!github\.com|registry\.npmjs)', "downloads from non-standard URL"),
    (r'(?:keylog|screenshot|clipboard|xdotool|xclip)', "potential spyware behavior"),
    (r'(?:cryptominer|stratum|xmrig|minerd)', "cryptocurrency mining reference"),
    (r'\\x[0-9a-f]{2}(?:\\x[0-9a-f]{2}){5,}', "hex-encoded strings (obfuscation)"),
    (r'String\.fromCharCode\s*\(', "JS character code obfuscation"),
    (r'chr\s*\(\s*\d+\s*\)\s*\+\s*chr', "Python character code obfuscation"),
]

SCRIPT_EXTENSIONS = {".sh", ".bash", ".py", ".js", ".ts", ".mjs", ".cjs", ".rb", ".pl"}

def analyze_layer2(skill_dir):
    """Analyze all scripts for dangerous patterns."""
    findings = {"critical": [], "suspicious": [], "info": []}
    scripts_found = 0
    
    for root, dirs, files in os.walk(skill_dir):
        dirs[:] = [d for d in dirs if d not in ("node_modules", ".git", "__pycache__", ".venv")]
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext not in SCRIPT_EXTENSIONS:
                continue
            
            fpath = os.path.join(root, fname)
            rel_path = os.path.relpath(fpath, skill_dir)
            scripts_found += 1
            
            try:
                content = open(fpath, errors="ignore").read()
                
                for pattern, desc in LAYER2_CRITICAL:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        findings["critical"].append(f"{rel_path}: {desc} ({len(matches)}x)")
                
                for pattern, desc in LAYER2_SUSPICIOUS:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        findings["suspicious"].append(f"{rel_path}: {desc} ({len(matches)}x)")
            except OSError:
                pass
    
    findings["info"].append(f"Scanned {scripts_found} script files")
    return findings

# ─── Layer 3: Publisher Reputation ────────────────────────────────────────────

def analyze_layer3(skill_name, skill_dir=None):
    """Check publisher reputation via GitHub API."""
    findings = {"critical": [], "suspicious": [], "info": []}
    
    github_url = None
    github_user = None
    
    for search_file in ["package.json", "SKILL.md", "README.md"]:
        for root, dirs, files in os.walk(skill_dir or "."):
            dirs[:] = [d for d in dirs if d not in ("node_modules", ".git")]
            if search_file in files:
                fpath = os.path.join(root, search_file)
                try:
                    content = open(fpath, errors="ignore").read()
                    gh_match = re.search(r'github\.com/([a-zA-Z0-9_-]+)/([a-zA-Z0-9_.-]+)', content)
                    if gh_match:
                        github_user = gh_match.group(1)
                        github_url = f"https://api.github.com/repos/{gh_match.group(1)}/{gh_match.group(2)}"
                        break
                except OSError:
                    pass
            if github_url:
                break
        if github_url:
            break
    
    if not github_user:
        findings["info"].append("No GitHub repository found — cannot check publisher reputation")
        return findings
    
    findings["info"].append(f"Publisher: {github_user}")
    
    try:
        user_result = subprocess.run(
            ["curl", "-m", "10", "-s", f"https://api.github.com/users/{github_user}"],
            capture_output=True, text=True, timeout=15
        )
        if user_result.returncode == 0:
            user_data = json.loads(user_result.stdout)
            
            created_at = user_data.get("created_at", "")
            public_repos = user_data.get("public_repos", 0)
            followers = user_data.get("followers", 0)
            
            if created_at:
                created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                age_days = (datetime.now(timezone.utc) - created).days
                findings["info"].append(f"Account age: {age_days} days, repos: {public_repos}, followers: {followers}")
                
                if age_days < 30:
                    findings["critical"].append(f"Account created only {age_days} days ago (< 30 days)")
                elif age_days < 90:
                    findings["suspicious"].append(f"Account relatively new ({age_days} days old)")
                
                if public_repos < 2 and age_days < 90:
                    findings["suspicious"].append(f"New account with very few repos ({public_repos})")
        
        if github_url:
            repo_result = subprocess.run(
                ["curl", "-m", "10", "-s", github_url],
                capture_output=True, text=True, timeout=15
            )
            if repo_result.returncode == 0:
                repo_data = json.loads(repo_result.stdout)
                stars = repo_data.get("stargazers_count", 0)
                forks = repo_data.get("forks_count", 0)
                repo_created = repo_data.get("created_at", "")
                
                if repo_created:
                    rc = datetime.fromisoformat(repo_created.replace("Z", "+00:00"))
                    repo_age = (datetime.now(timezone.utc) - rc).days
                    findings["info"].append(f"Repo age: {repo_age} days, stars: {stars}, forks: {forks}")
                    
                    if repo_age < 7:
                        findings["critical"].append(f"Repository created only {repo_age} days ago")
                    elif repo_age < 30:
                        findings["suspicious"].append(f"Repository is relatively new ({repo_age} days)")
                        
    except (subprocess.TimeoutExpired, json.JSONDecodeError, KeyError, ValueError):
        findings["info"].append("Could not check GitHub API")
    
    return findings

# ─── Layer 4: Hash Blacklist ────────────────────────────────────────────────

def analyze_layer4(skill_dir, skill_name):
    """Check against known-bad skill hashes and names."""
    findings = {"critical": [], "suspicious": [], "info": []}
    
    os.makedirs(DATA_DIR, exist_ok=True)
    
    if not os.path.exists(BLACKLIST_FILE):
        json.dump({
            "hashes": {},
            "names": {
                "clawhavoc": "Known malicious skill family",
                "free-tokens": "Token stealing skill",
                "openclaw-boost": "Fake performance skill with backdoor",
            },
        }, open(BLACKLIST_FILE, "w"), indent=2)
    
    try:
        blacklist = json.load(open(BLACKLIST_FILE))
    except (json.JSONDecodeError, OSError):
        blacklist = {"hashes": {}, "names": {}}
    
    # Check name
    name_lower = skill_name.lower()
    if name_lower in blacklist.get("names", {}):
        findings["critical"].append(f"Blacklisted skill name: {blacklist['names'][name_lower]}")
    
    # Check file hashes
    bad_hashes = blacklist.get("hashes", {})
    if bad_hashes:
        for root, dirs, files in os.walk(skill_dir):
            dirs[:] = [d for d in dirs if d not in ("node_modules", ".git")]
            for fname in files:
                fpath = os.path.join(root, fname)
                try:
                    h = hashlib.sha256(open(fpath, "rb").read()).hexdigest()
                    if h in bad_hashes:
                        rel = os.path.relpath(fpath, skill_dir)
                        findings["critical"].append(f"Blacklisted file hash: {rel} — {bad_hashes[h]}")
                except OSError:
                    pass
    
    return findings

# ─── Human-friendly descriptions (EN/ES) ────────────────────────────────────
FRIENDLY_DESC = {
    "curl piped to shell (remote code execution)": ("Descarga y ejecuta codigo remoto", "Downloads and runs remote code"),
    "curl piped to shell": ("Descarga y ejecuta codigo remoto", "Downloads and runs remote code"),
    "wget piped to shell": ("Descarga y ejecuta codigo remoto", "Downloads and runs remote code"),
    "wget piped to shell (remote code execution)": ("Descarga y ejecuta codigo remoto", "Downloads and runs remote code"),
    "eval with encoded data": ("Ejecuta codigo oculto/codificado", "Runs hidden/encoded code"),
    "exec with encoded data": ("Ejecuta codigo oculto/codificado", "Runs hidden/encoded code"),
    "base64 decode piped to execution": ("Ejecuta codigo codificado en base64", "Runs base64-encoded code"),
    "eval with base64 encoded data": ("Ejecuta codigo codificado en base64", "Runs base64-encoded code"),
    "netcat listener (reverse shell)": ("Abre acceso remoto al servidor", "Opens remote access to server"),
    "bash reverse shell": ("Abre acceso remoto al servidor", "Opens remote access to server"),
    "python reverse shell": ("Abre acceso remoto al servidor", "Opens remote access to server"),
    "named pipe reverse shell": ("Abre acceso remoto al servidor", "Opens remote access to server"),
    "destructive rm -rf on system paths": ("Borra archivos criticos del sistema", "Deletes critical system files"),
    "SSH key manipulation": ("Manipula llaves SSH", "Manipulates SSH keys"),
    "shortened URL (hides real destination)": ("URL acortada (oculta destino real)", "Shortened URL (hides destination)"),
    "requires sudo/root access": ("Pide permisos de administrador", "Requests admin/root access"),
    "makes files executable": ("Hace archivos ejecutables", "Makes files executable"),
    "ClickFix-style social engineering": ("Ingenieria social tipo ClickFix", "ClickFix social engineering"),
    "global npm install of unknown package": ("Instala paquete npm global desconocido", "Installs unknown global npm package"),
    "pip install of unknown package": ("Instala paquete pip desconocido", "Installs unknown pip package"),
    "runs Docker container": ("Ejecuta contenedor Docker", "Runs Docker container"),
    "enables/starts system service": ("Activa servicio del sistema", "Enables system service"),
    "modifies scheduled tasks": ("Modifica tareas programadas", "Modifies scheduled tasks"),
    "hardcoded IP address": ("IP sospechosa fija en el codigo", "Suspicious hardcoded IP"),
    "accesses sensitive dotfiles": ("Accede a archivos sensibles", "Accesses sensitive files"),
    "references API keys/secrets": ("Referencia claves API/secretos", "References API keys/secrets"),
    "accesses system auth files": ("Accede a archivos de autenticacion", "Accesses auth files"),
    "base64 decoding": ("Decodifica contenido oculto", "Decodes hidden content"),
    "makes HTTP requests": ("Hace conexiones HTTP externas", "Makes external HTTP connections"),
    "runs subprocesses": ("Ejecuta subprocesos del sistema", "Runs system subprocesses"),
    "executes system commands": ("Ejecuta comandos del sistema", "Runs system commands"),
    "references environment files": ("Accede a variables de entorno", "Accesses environment variables"),
    "downloads from non-standard URL": ("Descarga desde URL no estandar", "Downloads from non-standard URL"),
    "potential spyware behavior": ("Comportamiento tipo spyware", "Potential spyware behavior"),
    "cryptocurrency mining reference": ("Mineria de criptomonedas", "Cryptocurrency mining"),
    "hex-encoded strings (obfuscation)": ("Codigo ofuscado (hex)", "Obfuscated code (hex)"),
    "Tor .onion address": ("Direccion Tor .onion", "Tor .onion address"),
    "external chat invite link": ("Enlace a chat externo", "External chat invite"),
}


def _friendly(raw_desc):
    """Convert technical description to friendly ES/EN version."""
    core = raw_desc
    if ": " in core:
        core = core.split(": ", 1)[1]
    core = re.sub(r"\s*\(\d+x\)$", "", core)
    entry = FRIENDLY_DESC.get(core)
    if entry:
        return f"{entry[0]} / {entry[1]}"
    return core


def _send_telegram(text):
    """Send a message chunk to Telegram."""
    import urllib.request as _ur
    try:
        data = json.dumps({"chat_id": CHAT_ID, "text": text}).encode()
        req = _ur.Request(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data=data, headers={"Content-Type": "application/json"}, method="POST"
        )
        _ur.urlopen(req, timeout=10)
    except Exception:
        pass


def _format_skill_result(skill_name, results):
    """Format a single skill scan result with friendly descriptions."""
    n_crit = sum(len(r["critical"]) for r in results.values())
    n_susp = sum(len(r["suspicious"]) for r in results.values())

    if n_crit > 0:
        icon = "\U0001f534"
        label = f"{n_crit} peligro(s) / danger(s)"
        if n_susp > 0:
            label += f", {n_susp} advertencia(s) / warning(s)"
    elif n_susp > 0:
        icon = "\U0001f7e1"
        label = f"{n_susp} advertencia(s) / warning(s)"
    else:
        icon = "\U0001f7e2"
        label = "Segura / Safe"

    lines = [f"{icon} {skill_name} \u2014 {label}"]

    crit_items = []
    for lr in results.values():
        crit_items.extend(lr["critical"])
    for item in crit_items[:3]:
        lines.append(f"  \u274c {_friendly(item)}")

    susp_items = []
    for lr in results.values():
        susp_items.extend(lr["suspicious"])
    remaining = max(0, 5 - min(len(crit_items), 3))
    for item in susp_items[:remaining]:
        lines.append(f"  \u26a0\ufe0f {_friendly(item)}")

    hidden = max(0, len(crit_items) - 3) + max(0, len(susp_items) - remaining)
    if hidden > 0:
        lines.append(f"  ... +{hidden} mas / more")

    return lines, n_crit, n_susp


def scan_all_skills(telegram=False):
    """Scan all installed skills. Groups by risk, sends in chunks if needed."""
    import glob as _glob

    CHUNK_SIZE = 5

    skills_dirs = _glob.glob(os.path.expanduser("~/.openclaw/skills/*/"))
    skills_dirs = [d for d in skills_dirs if os.path.basename(d.rstrip("/")) != "lobsterguard"]

    if not skills_dirs:
        msg = "\U0001f6e1 LobsterGuard Skill Scanner\n\nNo hay otras skills instaladas para escanear.\n\U0001f7e2 Solo LobsterGuard esta presente (excluido del auto-escaneo)"
        msg += "\n\nNo other skills installed to scan.\n\U0001f7e2 Only LobsterGuard is present (excluded from self-scan)"
        if telegram:
            print(msg)
        else:
            print(json.dumps({"success": True, "message": "No other skills installed"}))
        return

    total = len(skills_dirs)
    header = f"\U0001f6e1 LobsterGuard Skill Scanner\nEscaneando / Scanning {total} skill(s)...\n"

    if telegram and total > CHUNK_SIZE:
        _send_telegram(header)

    safe_skills = []
    warn_skills = []
    danger_skills = []
    total_critical = 0
    total_suspicious = 0

    for skill_path in sorted(skills_dirs):
        skill_name = os.path.basename(skill_path.rstrip("/"))

        results = {}
        results["layer1"] = analyze_layer1(skill_path)
        results["layer2"] = analyze_layer2(skill_path)

        l12_issues = sum(len(r["critical"]) + len(r["suspicious"]) for r in results.values())
        if l12_issues > 0:
            results["layer3"] = analyze_layer3(skill_name, skill_path)
        else:
            results["layer3"] = {"critical": [], "suspicious": [], "info": []}

        results["layer4"] = analyze_layer4(skill_path, skill_name)

        skill_lines, n_crit, n_susp = _format_skill_result(skill_name, results)
        total_critical += n_crit
        total_suspicious += n_susp

        if n_crit > 0:
            danger_skills.append(skill_lines)
        elif n_susp > 0:
            warn_skills.append(skill_lines)
        else:
            safe_skills.append(skill_lines)

    # Build grouped output
    body_lines = []
    for sl in safe_skills:
        body_lines.append(sl[0])
    if safe_skills and (warn_skills or danger_skills):
        body_lines.append("")
    for sl in warn_skills:
        body_lines.extend(sl)
    if warn_skills and danger_skills:
        body_lines.append("")
    for sl in danger_skills:
        body_lines.extend(sl)

    n_safe = len(safe_skills)
    n_warn = len(warn_skills)
    n_danger = len(danger_skills)
    footer_lines = [
        "",
        "\u2501" * 18,
        f"\U0001f4ca {total}/{total} escaneadas / scanned",
        f"\U0001f7e2 {n_safe} segura(s) | \U0001f7e1 {n_warn} revision | \U0001f534 {n_danger} peligrosa(s)",
    ]
    if n_danger > 0:
        footer_lines.append("\u26a0\ufe0f Desinstala las skills en rojo / Uninstall red skills")

    if telegram:
        if total > CHUNK_SIZE:
            all_groups = safe_skills + warn_skills + danger_skills
            chunk = []
            count = 0
            for group in all_groups:
                chunk.extend(group)
                count += 1
                if count % CHUNK_SIZE == 0 and count < len(all_groups):
                    _send_telegram("\n".join(chunk))
                    chunk = []
            chunk.extend(footer_lines)
            _send_telegram("\n".join(chunk))
        else:
            all_lines = [header] + body_lines + footer_lines
            print("\n".join(all_lines))
    else:
        all_lines = body_lines + footer_lines
        print(json.dumps({
            "action": "checkskill",
            "critical": total_critical,
            "suspicious": total_suspicious,
            "formatted": "\n".join(all_lines),
        }, ensure_ascii=False))


def resolve_skill(name_or_path):
    """Resolve a skill name or path to an actual directory."""
    if os.path.isdir(name_or_path):
        return os.path.abspath(name_or_path)
    
    skills_base = os.path.expanduser("~/.openclaw/skills")
    candidate = os.path.join(skills_base, name_or_path)
    if os.path.isdir(candidate):
        return candidate
    
    return None


def format_result(results, skill_name, telegram=False):
    """Format scan results for output."""
    layer_names = {
        "layer1": "\U0001f4c4 Capa 1 — Documentacion / Layer 1 — Documentation",
        "layer2": "\U0001f50d Capa 2 — Scripts / Layer 2 — Scripts",
        "layer3": "\U0001f464 Capa 3 — Reputacion / Layer 3 — Reputation",
        "layer4": "\U0001f6ab Capa 4 — Blacklist / Layer 4 — Blacklist",
    }
    
    total_crit = sum(len(r.get("critical", [])) for r in results.values())
    total_susp = sum(len(r.get("suspicious", [])) for r in results.values())
    
    if total_crit > 0:
        verdict = "\U0001f534 PELIGROSA / DANGEROUS"
    elif total_susp > 0:
        verdict = "\U0001f7e1 SOSPECHOSA / SUSPICIOUS"
    else:
        verdict = "\U0001f7e2 SEGURA / SAFE"
    
    lines = [
        f"\U0001f6e1 LobsterGuard Skill Scanner",
        f"Skill: {skill_name}",
        f"Veredicto / Verdict: {verdict}",
        "",
    ]
    
    for key in ["layer1", "layer2", "layer3", "layer4"]:
        if key not in results:
            continue
        r = results[key]
        if not r["critical"] and not r["suspicious"] and not r.get("info"):
            continue
        lines.append(layer_names.get(key, key))
        for item in r["critical"]:
            lines.append(f"  \u274c {_friendly(item)}")
        for item in r["suspicious"]:
            lines.append(f"  \u26a0\ufe0f {_friendly(item)}")
        for item in r.get("info", []):
            lines.append(f"  \u2139\ufe0f {item}")
        lines.append("")
    
    lines.append(f"\U0001f4ca Total: {total_crit} critico(s), {total_susp} sospechoso(s)")
    
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error_es": "Uso: skill_scanner.py <skill-name|all> [--telegram]"}))
        sys.exit(1)
    
    skill_input = sys.argv[1]
    telegram = "--telegram" in sys.argv
    
    # Scan all installed skills
    if skill_input == "all":
        scan_all_skills(telegram=telegram)
        sys.exit(0)
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(BLACKLIST_FILE), exist_ok=True)
    
    # Initialize blacklist if missing
    if not os.path.exists(BLACKLIST_FILE):
        json.dump({
            "hashes": {},
            "names": {
                "clawhavoc": "Known malicious skill family",
                "free-tokens": "Token stealing skill",
                "openclaw-boost": "Fake performance skill with backdoor",
            },
        }, open(BLACKLIST_FILE, "w"), indent=2)
    
    # Resolve skill path
    skill_dir = resolve_skill(skill_input)
    if not skill_dir:
        msg = f"Skill '{skill_input}' not found"
        if telegram:
            print(f"\u274c {msg}")
        else:
            print(json.dumps({"success": False, "error": msg}))
        sys.exit(1)
    
    skill_name = os.path.basename(skill_dir)
    
    # Run all layers
    results = {}
    results["layer1"] = analyze_layer1(skill_dir)
    results["layer2"] = analyze_layer2(skill_dir)
    
    l12_issues = sum(len(r["critical"]) + len(r["suspicious"]) for r in results.values())
    if l12_issues > 0:
        results["layer3"] = analyze_layer3(skill_name, skill_dir)
    else:
        results["layer3"] = {"critical": [], "suspicious": [], "info": ["Skipped (skill clean)"]}
    
    results["layer4"] = analyze_layer4(skill_dir, skill_name)
    
    output = format_result(results, skill_name, telegram)
    
    if telegram:
        print(output)
    else:
        total_crit = sum(len(r["critical"]) for r in results.values())
        total_susp = sum(len(r["suspicious"]) for r in results.values())
        print(json.dumps({
            "action": "checkskill",
            "skill": skill_name,
            "critical": total_crit,
            "suspicious": total_susp,
            "formatted": output,
        }, ensure_ascii=False))


if __name__ == "__main__":
    main()
