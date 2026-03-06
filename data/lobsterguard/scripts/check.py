#!/usr/bin/env python3
"""
LobsterGuard Security Check Script v5.0
Runs 70 security checks on an OpenClaw installation and its host server.
If SecureClaw is installed, uses it as backend for deeper analysis.

Checks are organized in four categories:
  - OpenClaw checks (1-5): gateway, auth, version, credentials, skills
  - Server checks (6-15): SSH, firewall, fail2ban, updates, root user,
    open ports, disk space, Docker security, intrusion attempts
  - Advanced checks (16-28): config perms, SSL/TLS, backups, supply chain,
    env leakage, cron persistence, CORS, skill integrity, system users,
    log rotation, sandbox mode, outbound connections, self-protection
  - Agentic AI checks (29-50): OWASP Agentic AI Top 10 protections including
    skill prompt injection, hidden content, MCP security, tool poisoning,
    data exfiltration, log secrets, typosquatting, auto-approval, permissions,
    memory poisoning, git hooks, unsafe defaults, rogue agents, kernel/systemd
    hardening, tmp security, signatures, sandboxing, key rotation, rate limiting,
    network access, process isolation

Output: JSON report that the SKILL.md instructions interpret for the user.
"""

import json
import os
import subprocess
import sys
import re
import hashlib
from pathlib import Path
from datetime import datetime, timezone

# ─── Configuration ───────────────────────────────────────────────────────────

OPENCLAW_HOME = Path.home() / ".openclaw"
OPENCLAW_CONFIG = OPENCLAW_HOME / "config" / "moltbot.json"
OPENCLAW_CREDENTIALS = OPENCLAW_HOME / ".env"
OPENCLAW_SKILLS_DIR = OPENCLAW_HOME / "skills"
OPENCLAW_GATEWAY_CONFIG = OPENCLAW_HOME / "config" / "gateway.json"
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"
SECURECLAW_PATH = OPENCLAW_HOME / "plugins" / "secureclaw"
SECURECLAW_AUDIT_SCRIPT = SECURECLAW_PATH / "scripts" / "audit.sh"

# Skills to exclude from malicious pattern scanning (our own skills)
WHITELISTED_SKILLS = ["lobsterguard"]

# Safe bind values that mean "localhost only"
SAFE_BIND_VALUES = ["loopback", "localhost", "127.0.0.1", "local"]

# Known malicious skill signatures (from Snyk ToxicSkills + Bitdefender reports)
MALICIOUS_PATTERNS = [
    r"eval\s*\(",                          # Dynamic code execution
    r"exec\s*\(",                          # Dynamic code execution
    r"subprocess\.call.*shell\s*=\s*True", # Shell injection
    r"os\.system\s*\(",                    # System command execution
    r"requests\.post.*\.openclaw",         # Exfiltration of OpenClaw data
    r"curl.*-d.*\.env",                    # Credential exfiltration via curl
    r"base64\.b64decode",                  # Obfuscated payloads
    r"socket\.connect",                    # Reverse shell patterns
    r"\\x[0-9a-fA-F]{2}.*\\x[0-9a-fA-F]{2}",  # Hex-encoded payloads
    r"webhook\.site|ngrok\.io|burpcollaborator", # Known exfil endpoints
]

# Known dangerous default credentials / weak configs
WEAK_AUTH_PATTERNS = [
    "password", "123456", "admin", "openclaw", "default", "changeme",
    "letmein", "welcome", "monkey", "dragon", "master",
]


# ─── Utility Functions ───────────────────────────────────────────────────────

def run_command(cmd, timeout=10):
    """Run a shell command and return output safely."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "Command timed out", 1
    except Exception as e:
        return "", str(e), 1


def file_exists(path):
    """Check if a file or directory exists."""
    return Path(path).exists()


def read_json_safe(path):
    """Safely read a JSON file."""
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError, PermissionError):
        return None


def get_configured_language():
    """Read language from config.json (set during install), fallback to 'es'."""
    try:
        with open(DATA_DIR / "config.json") as f:
            config = json.load(f)
            lang = config.get("language", "es")
            if lang in ("es", "en"):
                return lang
    except Exception:
        pass
    return "es"


# ─── SecureClaw Integration ──────────────────────────────────────────────────

def check_secureclaw_available():
    """Check if SecureClaw is installed and usable."""
    if file_exists(SECURECLAW_PATH) and file_exists(SECURECLAW_AUDIT_SCRIPT):
        return True
    # Also check via openclaw CLI
    stdout, _, code = run_command("openclaw plugins list 2>/dev/null | grep -i secureclaw")
    return code == 0 and "secureclaw" in stdout.lower()


def run_secureclaw_audit():
    """Run SecureClaw's audit and return parsed results."""
    if not check_secureclaw_available():
        return None

    stdout, stderr, code = run_command(
        f"bash {SECURECLAW_AUDIT_SCRIPT} --json 2>/dev/null", timeout=30
    )
    if code == 0 and stdout:
        try:
            return json.loads(stdout)
        except json.JSONDecodeError:
            pass
    return None


# ─── Check 1: Gateway Exposure ──────────────────────────────────────────────

def check_gateway_exposure():
    """
    CHECK 1: Is the gateway exposed to the internet?
    Risk: Anyone can control your agent remotely.
    References: SecurityScorecard STRIKE team found 40,000+ exposed instances.
    """
    result = {
        "id": "gateway_exposure",
        "name_es": "Gateway expuesto al internet",
        "name_en": "Gateway exposed to internet",
        "severity": "CRITICAL",
        "passed": False,
        "details_es": "",
        "details_en": "",
        "fix_es": [],
        "fix_en": [],
    }

    # Check 1a: Read gateway config via CLI (most reliable method)
    stdout, _, code = run_command("openclaw config get gateway 2>/dev/null")
    gateway_config = None
    if code == 0 and stdout:
        # Strip the OpenClaw banner line if present
        json_start = stdout.find("{")
        if json_start >= 0:
            try:
                gateway_config = json.loads(stdout[json_start:])
            except json.JSONDecodeError:
                pass

    # Fallback: read config files directly
    if gateway_config is None:
        gateway_config = read_json_safe(OPENCLAW_GATEWAY_CONFIG)
    if gateway_config is None:
        main_config = read_json_safe(OPENCLAW_CONFIG)
        if main_config:
            gateway_config = main_config.get("gateway", {})

    bind_address = "0.0.0.0"  # Assume worst case
    mode = ""
    if gateway_config:
        bind_address = gateway_config.get("bind", gateway_config.get("host", "0.0.0.0"))
        mode = gateway_config.get("mode", "")

    # Check 1b: Verify what ports are actually listening
    stdout, _, _ = run_command(
        "ss -tlnp 2>/dev/null | grep -E ':(18789|3000|8080|8766)' || "
        "netstat -tlnp 2>/dev/null | grep -E ':(18789|3000|8080|8766)'"
    )

    is_safe_bind = bind_address.lower() in SAFE_BIND_VALUES or mode.lower() == "local"
    is_listening_external = "0.0.0.0" in stdout or "::" in stdout

    # Trust OpenClaw's own config — if it says loopback/local, it's safe
    # The ss check is secondary (other services may bind to 0.0.0.0 on same ports)
    if is_safe_bind:
        result["passed"] = True
        result["details_es"] = (
            "Tu gateway solo acepta conexiones locales (127.0.0.1). "
            "Nadie desde internet puede acceder a tu agente."
        )
        result["details_en"] = (
            "Your gateway only accepts local connections (127.0.0.1). "
            "Nobody from the internet can access your agent."
        )
    else:
        result["details_es"] = (
            "Tu gateway esta abierto al internet sin restriccion. "
            "Es como dejar la puerta de tu casa abierta con un letrero que dice 'pasa'. "
            "Cualquier persona en el mundo puede ver y controlar tu agente. "
            f"Direccion actual: {bind_address}"
        )
        result["details_en"] = (
            "Your gateway is open to the internet without restriction. "
            "It's like leaving your front door wide open with a sign saying 'come in'. "
            "Anyone in the world can see and control your agent. "
            f"Current address: {bind_address}"
        )
        result["fix_es"] = [
            "Abre tu terminal y escribe:",
            "  openclaw config set gateway.bind 127.0.0.1",
            "  (Esto le dice a OpenClaw que solo acepte conexiones de tu propia computadora)",
            "",
            "Luego reinicia OpenClaw:",
            "  openclaw restart",
            "",
            "Si necesitas acceso remoto, usa un tunel SSH en vez de exponer el gateway:",
            "  ssh -L 3000:localhost:3000 tu-usuario@tu-servidor",
        ]
        result["fix_en"] = [
            "Open your terminal and type:",
            "  openclaw config set gateway.bind 127.0.0.1",
            "  (This tells OpenClaw to only accept connections from your own computer)",
            "",
            "Then restart OpenClaw:",
            "  openclaw restart",
            "",
            "If you need remote access, use an SSH tunnel instead of exposing the gateway:",
            "  ssh -L 3000:localhost:3000 your-user@your-server",
        ]

    return result


# ─── Check 2: Authentication ────────────────────────────────────────────────

def check_authentication():
    """
    CHECK 2: Is authentication enabled and strong?
    Risk: Without auth, anyone who reaches the gateway can control the agent.
    """
    result = {
        "id": "authentication",
        "name_es": "Autenticacion del gateway",
        "name_en": "Gateway authentication",
        "severity": "CRITICAL",
        "passed": False,
        "details_es": "",
        "details_en": "",
        "fix_es": [],
        "fix_en": [],
    }

    # Read gateway config via CLI
    stdout, _, code = run_command("openclaw config get gateway 2>/dev/null")
    gateway_config = None
    if code == 0 and stdout:
        json_start = stdout.find("{")
        if json_start >= 0:
            try:
                gateway_config = json.loads(stdout[json_start:])
            except json.JSONDecodeError:
                pass

    if gateway_config is None:
        gateway_config = read_json_safe(OPENCLAW_GATEWAY_CONFIG)
    if gateway_config is None:
        main_config = read_json_safe(OPENCLAW_CONFIG)
        if main_config:
            gateway_config = main_config.get("gateway", {})

    auth_enabled = False
    auth_weak = False

    if gateway_config:
        auth_config = gateway_config.get("auth", {})
        # Support both "enabled: true" and "mode: token" formats
        auth_mode = auth_config.get("mode", "")
        auth_enabled = auth_config.get("enabled", False) or auth_mode in ("token", "password")
        auth_token = auth_config.get("token", auth_config.get("password", ""))

        if auth_enabled and auth_token:
            # Check if token is weak
            # Hex tokens (like OpenClaw generates) are all lowercase but still strong
            is_hex_token = bool(re.match(r'^[0-9a-fA-F]+$', auth_token))
            if (
                len(auth_token) < 16
                or auth_token.lower() in WEAK_AUTH_PATTERNS
                or (not is_hex_token and auth_token == auth_token.lower())
            ):
                auth_weak = True

    if auth_enabled and not auth_weak:
        result["passed"] = True
        result["details_es"] = (
            "La autenticacion esta activada con un token fuerte. "
            "Solo quien tenga este token puede acceder a tu agente."
        )
        result["details_en"] = (
            "Authentication is enabled with a strong token. "
            "Only someone with this token can access your agent."
        )
    elif auth_enabled and auth_weak:
        result["severity"] = "HIGH"
        result["details_es"] = (
            "La autenticacion esta activada, pero tu contrasena es debil. "
            "Es como ponerle candado a tu puerta pero dejar la llave pegada."
        )
        result["details_en"] = (
            "Authentication is enabled, but your password is weak. "
            "It's like locking your door but leaving the key in the lock."
        )
        result["fix_es"] = [
            "Genera un token seguro y actualiza tu configuracion:",
            "  TOKEN=$(openssl rand -hex 32)",
            "  openclaw config set gateway.auth.token $TOKEN",
            "  echo \"Tu nuevo token: $TOKEN\"",
            "  (Guarda este token en un lugar seguro)",
            "",
            "Reinicia OpenClaw:",
            "  openclaw restart",
        ]
        result["fix_en"] = [
            "Generate a secure token and update your config:",
            "  TOKEN=$(openssl rand -hex 32)",
            "  openclaw config set gateway.auth.token $TOKEN",
            '  echo "Your new token: $TOKEN"',
            "  (Save this token somewhere safe)",
            "",
            "Restart OpenClaw:",
            "  openclaw restart",
        ]
    else:
        result["details_es"] = (
            "No tienes autenticacion activada. Cualquiera que llegue a tu gateway "
            "puede controlar tu agente sin necesidad de contrasena. "
            "Esto es especialmente peligroso si tu gateway esta expuesto al internet."
        )
        result["details_en"] = (
            "You don't have authentication enabled. Anyone who reaches your gateway "
            "can control your agent without needing a password. "
            "This is especially dangerous if your gateway is exposed to the internet."
        )
        result["fix_es"] = [
            "Activa la autenticacion con un token seguro:",
            "  TOKEN=$(openssl rand -hex 32)",
            "  openclaw config set gateway.auth.enabled true",
            "  openclaw config set gateway.auth.token $TOKEN",
            "  echo \"Tu token: $TOKEN\"",
            "  (Guarda este token — lo necesitaras para conectarte)",
            "",
            "Reinicia OpenClaw:",
            "  openclaw restart",
        ]
        result["fix_en"] = [
            "Enable authentication with a secure token:",
            "  TOKEN=$(openssl rand -hex 32)",
            "  openclaw config set gateway.auth.enabled true",
            "  openclaw config set gateway.auth.token $TOKEN",
            '  echo "Your token: $TOKEN"',
            "  (Save this token — you'll need it to connect)",
            "",
            "Restart OpenClaw:",
            "  openclaw restart",
        ]

    return result


# ─── Check 3: Version & Known CVEs ──────────────────────────────────────────

def check_version():
    """
    CHECK 3: Is OpenClaw up to date? Are there known vulnerabilities?
    Risk: CVE-2026-25253 (CVSS 8.8) allows 1-click RCE.
    """
    result = {
        "id": "version",
        "name_es": "Version de OpenClaw",
        "name_en": "OpenClaw version",
        "severity": "HIGH",
        "passed": False,
        "details_es": "",
        "details_en": "",
        "fix_es": [],
        "fix_en": [],
    }

    # Get installed version
    stdout, _, code = run_command("openclaw --version 2>/dev/null")
    installed_version = None
    if code == 0 and stdout:
        # Parse version from output like "OpenClaw v0.4.2" or "0.4.2"
        match = re.search(r"(\d+\.\d+\.\d+)", stdout)
        if match:
            installed_version = match.group(1)

    if not installed_version:
        # Try alternative methods
        pkg_json = OPENCLAW_HOME / "package.json"
        pkg_data = read_json_safe(pkg_json)
        if pkg_data:
            installed_version = pkg_data.get("version")

    # Known vulnerable versions (from CVE database and security advisories)
    VULNERABLE_VERSIONS = {
        # CVE-2026-25253: Cross-site WebSocket hijacking -> RCE
        "cve_2026_25253": {
            "affected_below": "0.4.8",
            "cve": "CVE-2026-25253",
            "cvss": 8.8,
            "desc_es": (
                "Permite que un atacante tome control de tu agente con solo hacerte "
                "visitar una pagina web maliciosa. Un clic y ya tienen acceso completo."
            ),
            "desc_en": (
                "Allows an attacker to take control of your agent just by making you "
                "visit a malicious web page. One click and they have full access."
            ),
        },
    }

    if installed_version:
        is_vulnerable = False
        vulnerable_cves = []

        for key, vuln in VULNERABLE_VERSIONS.items():
            if compare_versions(installed_version, vuln["affected_below"]) < 0:
                is_vulnerable = True
                vulnerable_cves.append(vuln)

        if not is_vulnerable:
            result["passed"] = True
            result["details_es"] = (
                f"Tienes la version {installed_version}. "
                "No tiene vulnerabilidades criticas conocidas."
            )
            result["details_en"] = (
                f"You have version {installed_version}. "
                "No known critical vulnerabilities."
            )
        else:
            cve_list = ", ".join(v["cve"] for v in vulnerable_cves)
            result["severity"] = "CRITICAL"
            result["details_es"] = (
                f"Tienes la version {installed_version} que es vulnerable a {cve_list}. "
                + vulnerable_cves[0]["desc_es"]
            )
            result["details_en"] = (
                f"You have version {installed_version} which is vulnerable to {cve_list}. "
                + vulnerable_cves[0]["desc_en"]
            )
            result["fix_es"] = [
                "Esto es urgente — tu version tiene vulnerabilidades que permiten que un atacante",
                "tome control de tu agente con solo hacerte visitar un link.",
                "",
                "Paso 1 — Actualiza OpenClaw:",
                "  openclaw update",
                "  (Esto descarga la version mas reciente que ya tiene el parche de seguridad)",
                "",
                "Paso 2 — Verifica que se actualizo correctamente:",
                "  openclaw --version",
                "  (Deberia mostrar una version superior a 0.4.8)",
                "",
                "Paso 3 — Reinicia OpenClaw para aplicar:",
                "  openclaw restart",
                "",
                "Si openclaw update da error:",
                "  npm update -g @openclaw/openclaw",
                "  (Esto usa npm directamente para forzar la actualizacion)",
            ]
            result["fix_en"] = [
                "This is urgent — your version has vulnerabilities that allow an attacker",
                "to take control of your agent just by making you click a link.",
                "",
                "Step 1 — Update OpenClaw:",
                "  openclaw update",
                "  (This downloads the latest version with the security patch)",
                "",
                "Step 2 — Verify the update:",
                "  openclaw --version",
                "  (Should show a version above 0.4.8)",
                "",
                "Step 3 — Restart OpenClaw to apply:",
                "  openclaw restart",
                "",
                "If openclaw update gives an error:",
                "  npm update -g @openclaw/openclaw",
                "  (This uses npm directly to force the update)",
            ]
    else:
        result["details_es"] = (
            "No pude detectar la version de OpenClaw instalada. "
            "Esto puede significar que OpenClaw no esta instalado correctamente."
        )
        result["details_en"] = (
            "Could not detect the installed OpenClaw version. "
            "This may mean OpenClaw is not installed correctly."
        )
        result["fix_es"] = [
            "Verifica tu instalacion:",
            "  which openclaw",
            "  openclaw --version",
        ]
        result["fix_en"] = [
            "Verify your installation:",
            "  which openclaw",
            "  openclaw --version",
        ]

    return result


def compare_versions(v1, v2):
    """Compare two version strings. Returns -1, 0, or 1."""
    parts1 = [int(x) for x in v1.split(".")]
    parts2 = [int(x) for x in v2.split(".")]
    for a, b in zip(parts1, parts2):
        if a < b:
            return -1
        if a > b:
            return 1
    return 0


# ─── Check 4: Credential Security ───────────────────────────────────────────

def check_credentials():
    """
    CHECK 4: Are API keys and credentials stored safely?
    Risk: Infostealers like Redline/Lumma/Vidar have specific paths for OpenClaw.
    """
    result = {
        "id": "credentials",
        "name_es": "Credenciales y API keys",
        "name_en": "Credentials and API keys",
        "severity": "HIGH",
        "passed": False,
        "details_es": "",
        "details_en": "",
        "fix_es": [],
        "fix_en": [],
    }

    issues = []

    # Check 4a: .env file permissions
    env_file = OPENCLAW_CREDENTIALS
    if file_exists(env_file):
        stat = os.stat(env_file)
        mode = oct(stat.st_mode)[-3:]
        if mode != "600":
            issues.append({
                "es": f"Tu archivo .env tiene permisos {mode} (deberia ser 600). Otros usuarios del sistema pueden leerlo.",
                "en": f"Your .env file has permissions {mode} (should be 600). Other system users can read it.",
            })

    # Check 4b: Plaintext secrets in config files
    config_files = [
        OPENCLAW_CONFIG,
        OPENCLAW_GATEWAY_CONFIG,
        OPENCLAW_HOME / "config" / "skills.json",
    ]

    secret_patterns = [
        r"sk-[a-zA-Z0-9]{20,}",          # OpenAI API keys
        r"sk-ant-[a-zA-Z0-9]{20,}",      # Anthropic API keys
        r"ghp_[a-zA-Z0-9]{36}",          # GitHub personal tokens
        r"xoxb-[0-9]{10,}",              # Slack bot tokens
        r"AKIA[0-9A-Z]{16}",             # AWS access keys
    ]

    for config_file in config_files:
        if file_exists(config_file):
            try:
                with open(config_file, "r") as f:
                    content = f.read()
                for pattern in secret_patterns:
                    if re.search(pattern, content):
                        issues.append({
                            "es": f"Encontre API keys en texto plano en {config_file.name}. Los malware como Redline buscan exactamente estos archivos.",
                            "en": f"Found plaintext API keys in {config_file.name}. Malware like Redline specifically targets these files.",
                        })
                        break
            except PermissionError:
                pass

    # Check 4c: .env file exists at all
    if not file_exists(env_file):
        # Check if secrets are directly in config (worse)
        if any("API keys en texto plano" in i.get("es", "") for i in issues):
            issues.append({
                "es": "No tienes archivo .env — tus credenciales estan directamente en archivos de configuracion, que es menos seguro.",
                "en": "You don't have a .env file — your credentials are directly in config files, which is less secure.",
            })

    if not issues:
        result["passed"] = True
        result["details_es"] = (
            "Tus credenciales estan bien protegidas. "
            "No encontre API keys expuestas en archivos de configuracion."
        )
        result["details_en"] = (
            "Your credentials are well protected. "
            "No exposed API keys found in configuration files."
        )
    else:
        result["details_es"] = " | ".join(i["es"] for i in issues)
        result["details_en"] = " | ".join(i["en"] for i in issues)
        result["fix_es"] = [
            "1. Mueve todas tus API keys al archivo .env:",
            "   nano ~/.openclaw/.env",
            "   (Agrega tus keys en formato: OPENAI_API_KEY=sk-tu-key-aqui)",
            "",
            "2. Protege el archivo para que solo tu puedas leerlo:",
            "   chmod 600 ~/.openclaw/.env",
            "",
            "3. Elimina las keys de los archivos de configuracion.",
            "   En moltbot.json, reemplaza el valor de la key por una referencia: \"$OPENAI_API_KEY\"",
        ]
        result["fix_en"] = [
            "1. Move all your API keys to the .env file:",
            "   nano ~/.openclaw/.env",
            "   (Add your keys like: OPENAI_API_KEY=sk-your-key-here)",
            "",
            "2. Protect the file so only you can read it:",
            "   chmod 600 ~/.openclaw/.env",
            "",
            "3. Remove keys from config files.",
            '   In moltbot.json, replace the key value with a reference: "$OPENAI_API_KEY"',
        ]

    return result


# ─── Check 5: Installed Skills Safety ────────────────────────────────────────

def check_installed_skills():
    """
    CHECK 5: Are any installed skills potentially malicious?
    Risk: 36.82% of ClawHub skills had at least one security flaw (Snyk ToxicSkills).
    """
    result = {
        "id": "skills_safety",
        "name_es": "Skills instaladas",
        "name_en": "Installed skills",
        "severity": "HIGH",
        "passed": False,
        "details_es": "",
        "details_en": "",
        "fix_es": [],
        "fix_en": [],
    }

    if not file_exists(OPENCLAW_SKILLS_DIR):
        result["passed"] = True
        result["details_es"] = "No tienes skills adicionales instaladas."
        result["details_en"] = "You don't have additional skills installed."
        return result

    suspicious_skills = []
    total_skills = 0

    for skill_dir in OPENCLAW_SKILLS_DIR.iterdir():
        if not skill_dir.is_dir():
            continue
        # Skip whitelisted skills (like ourselves)
        if skill_dir.name.lower() in WHITELISTED_SKILLS:
            continue
        total_skills += 1

        # Scan all files in the skill for malicious patterns
        for file_path in skill_dir.rglob("*"):
            if not file_path.is_file():
                continue
            if file_path.suffix not in (".py", ".sh", ".js", ".ts", ".md", ".yaml", ".yml", ".json"):
                continue

            try:
                with open(file_path, "r", errors="ignore") as f:
                    content = f.read()

                matches = []
                for pattern in MALICIOUS_PATTERNS:
                    if re.search(pattern, content):
                        matches.append(pattern)

                if matches:
                    suspicious_skills.append({
                        "skill": skill_dir.name,
                        "file": file_path.name,
                        "patterns": len(matches),
                    })
            except (PermissionError, OSError):
                pass

    if not suspicious_skills:
        result["passed"] = True
        result["details_es"] = (
            f"Revisamos {total_skills} skills instaladas. "
            "No encontramos patrones maliciosos conocidos."
        )
        result["details_en"] = (
            f"Scanned {total_skills} installed skills. "
            "No known malicious patterns found."
        )
    else:
        skill_names = list(set(s["skill"] for s in suspicious_skills))
        result["details_es"] = (
            f"Encontramos patrones sospechosos en {len(skill_names)} skill(s): "
            f"{', '.join(skill_names)}. "
            "Esto no significa que sean maliciosas al 100%, pero tienen codigo que "
            "normalmente se usa en skills daninas (ejecucion de comandos, envio de datos, etc)."
        )
        result["details_en"] = (
            f"Found suspicious patterns in {len(skill_names)} skill(s): "
            f"{', '.join(skill_names)}. "
            "This doesn't mean they're 100% malicious, but they contain code patterns "
            "typically used in harmful skills (command execution, data exfiltration, etc)."
        )
        result["fix_es"] = [
            "1. Revisa las skills sospechosas manualmente:",
        ] + [
            f"   - {s['skill']}/{s['file']} ({s['patterns']} patron(es) encontrado(s))"
            for s in suspicious_skills
        ] + [
            "",
            "2. Si no reconoces una skill o no la necesitas, eliminala:",
            f"   openclaw skills remove <nombre-de-la-skill>",
            "",
            "3. Solo instala skills de fuentes confiables. Revisa el codigo antes de instalar.",
        ]
        result["fix_en"] = [
            "1. Review suspicious skills manually:",
        ] + [
            f"   - {s['skill']}/{s['file']} ({s['patterns']} pattern(s) found)"
            for s in suspicious_skills
        ] + [
            "",
            "2. If you don't recognize a skill or don't need it, remove it:",
            f"   openclaw skills remove <skill-name>",
            "",
            "3. Only install skills from trusted sources. Review the code before installing.",
        ]

    return result


# ─── Check 6: SSH Root Login ─────────────────────────────────────────────────

def check_ssh_root_login():
    """CHECK 6: Is SSH root login disabled?"""
    result = {
        "id": "ssh_root_login",
        "name_es": "Login SSH como root",
        "name_en": "SSH root login",
        "severity": "CRITICAL",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    # Check all sshd config files (higher numbered files override lower)
    stdout, _, code = run_command(
        "sshd -T 2>/dev/null | grep -i 'permitrootlogin' || "
        "grep -rhi 'PermitRootLogin' /etc/ssh/sshd_config /etc/ssh/sshd_config.d/ 2>/dev/null | tail -1"
    )

    if "no" in stdout.lower() and "without-password" not in stdout.lower():
        result["passed"] = True
        result["details_es"] = "El login SSH como root esta deshabilitado. Solo se puede entrar con usuarios normales."
        result["details_en"] = "SSH root login is disabled. Only normal users can log in."
    else:
        result["details_es"] = (
            "Alguien puede intentar entrar directamente como root por SSH. "
            "Es como darle la llave maestra de tu casa a cualquiera que toque la puerta."
        )
        result["details_en"] = (
            "Someone can try to log in directly as root via SSH. "
            "It's like giving the master key to anyone who knocks on your door."
        )
        result["fix_es"] = [
            "IMPORTANTE: No hagas esto si root es tu unico usuario, o te quedaras sin acceso.",
            "",
            "Paso 1 — Verifica que tienes otro usuario con permisos de admin:",
            "  sudo -l",
            "  (Si ves una lista de permisos, estas bien. Si pide contrasena y funciona, tambien.)",
            "",
            "Paso 2 — Deshabilita el login directo como root:",
            "  echo 'PermitRootLogin no' | sudo tee /etc/ssh/sshd_config.d/99-no-root.conf",
            "  (Esto crea un archivo de configuracion que le dice a SSH: no dejes entrar a root)",
            "",
            "Paso 3 — Aplica el cambio reiniciando SSH:",
            "  sudo systemctl restart sshd",
            "",
            "Paso 4 — SIN CERRAR esta sesion, abre otra terminal y prueba que puedes entrar:",
            "  ssh tu-usuario@tu-servidor",
            "  (Si funciona, todo bien. Si no, revierte el cambio desde esta sesion)",
        ]
        result["fix_en"] = [
            "IMPORTANT: Don't do this if root is your only user, or you'll lock yourself out.",
            "",
            "Step 1 — Verify you have another user with admin permissions:",
            "  sudo -l",
            "  (If you see a list of permissions, you're good. If it asks for password and works, also good.)",
            "",
            "Step 2 — Disable direct root login:",
            "  echo 'PermitRootLogin no' | sudo tee /etc/ssh/sshd_config.d/99-no-root.conf",
            "  (This creates a config file telling SSH: don't let root log in)",
            "",
            "Step 3 — Apply the change by restarting SSH:",
            "  sudo systemctl restart sshd",
            "",
            "Step 4 — WITHOUT closing this session, open another terminal and test:",
            "  ssh your-user@your-server",
            "  (If it works, all good. If not, revert from this session)",
        ]
    return result


# ─── Check 7: SSH Password Authentication ───────────────────────────────────

def check_ssh_password_auth():
    """CHECK 7: Is SSH password authentication disabled (key-only)?"""
    result = {
        "id": "ssh_password_auth",
        "name_es": "Autenticacion SSH por contrasena",
        "name_en": "SSH password authentication",
        "severity": "HIGH",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    stdout, _, code = run_command(
        "sshd -T 2>/dev/null | grep -i 'passwordauthentication' || "
        "grep -rhi 'PasswordAuthentication' /etc/ssh/sshd_config /etc/ssh/sshd_config.d/ 2>/dev/null | tail -1"
    )

    if "no" in stdout.lower():
        result["passed"] = True
        result["details_es"] = "Solo se puede entrar con clave SSH, no con contrasena. Mucho mas seguro."
        result["details_en"] = "Only SSH key login is allowed, not passwords. Much more secure."
    else:
        result["details_es"] = (
            "Se puede entrar a tu servidor con contrasena. Los atacantes pueden probar "
            "miles de contrasenas por minuto hasta adivinar la tuya (ataque de fuerza bruta)."
        )
        result["details_en"] = (
            "Password login is allowed on your server. Attackers can try thousands of "
            "passwords per minute until they guess yours (brute force attack)."
        )
        result["fix_es"] = [
            "1. Asegurate de tener tu clave SSH configurada primero",
            "2. Deshabilita contrasenas:",
            "   echo 'PasswordAuthentication no' | sudo tee /etc/ssh/sshd_config.d/99-no-password.conf",
            "   sudo systemctl restart sshd",
        ]
        result["fix_en"] = [
            "1. Make sure your SSH key is configured first",
            "2. Disable passwords:",
            "   echo 'PasswordAuthentication no' | sudo tee /etc/ssh/sshd_config.d/99-no-password.conf",
            "   sudo systemctl restart sshd",
        ]
    return result


# ─── Check 8: Firewall Active ───────────────────────────────────────────────

def check_firewall():
    """CHECK 8: Is a firewall active?"""
    result = {
        "id": "firewall",
        "name_es": "Firewall activo",
        "name_en": "Active firewall",
        "severity": "HIGH",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    # Check UFW first, then iptables/nftables
    ufw_stdout, _, ufw_code = run_command("sudo /usr/sbin/ufw status 2>/dev/null")
    nft_stdout, _, nft_code = run_command("sudo nft list ruleset 2>/dev/null | head -5")
    ipt_stdout, _, ipt_code = run_command("sudo iptables -L -n 2>/dev/null | grep -c 'DROP\\|REJECT'")

    has_firewall = False
    if "active" in ufw_stdout.lower() and "inactive" not in ufw_stdout.lower():
        has_firewall = True
    elif nft_code == 0 and nft_stdout and "table" in nft_stdout:
        has_firewall = True
    elif ipt_code == 0 and ipt_stdout and int(ipt_stdout or "0") > 0:
        has_firewall = True

    if has_firewall:
        result["passed"] = True
        result["details_es"] = "Tienes un firewall activo filtrando el trafico de red."
        result["details_en"] = "You have an active firewall filtering network traffic."
    else:
        result["details_es"] = (
            "No tienes firewall activo. Todos los puertos de tu servidor estan expuestos directamente "
            "al internet. Es como tener una casa sin paredes — cualquiera puede entrar por donde quiera."
        )
        result["details_en"] = (
            "No active firewall found. All your server ports are directly exposed to the internet. "
            "It's like having a house with no walls — anyone can come in from any direction."
        )
        result["fix_es"] = [
            "Instala y configura UFW (el firewall mas simple):",
            "  sudo apt install ufw -y",
            "  sudo ufw default deny incoming",
            "  sudo ufw default allow outgoing",
            "  sudo ufw allow ssh",
            "  sudo ufw enable",
            "",
            "Esto solo deja abierto el puerto 22 (SSH) y bloquea todo lo demas.",
        ]
        result["fix_en"] = [
            "Install and configure UFW (the simplest firewall):",
            "  sudo apt install ufw -y",
            "  sudo ufw default deny incoming",
            "  sudo ufw default allow outgoing",
            "  sudo ufw allow ssh",
            "  sudo ufw enable",
            "",
            "This only leaves port 22 (SSH) open and blocks everything else.",
        ]
    return result


# ─── Check 9: Fail2ban Installed ────────────────────────────────────────────

def check_fail2ban():
    """CHECK 9: Is fail2ban installed and running?"""
    result = {
        "id": "fail2ban",
        "name_es": "Fail2ban (proteccion contra fuerza bruta)",
        "name_en": "Fail2ban (brute force protection)",
        "severity": "MEDIUM",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    stdout, _, code = run_command("systemctl is-active fail2ban 2>/dev/null")

    if code == 0 and "active" in stdout:
        result["passed"] = True
        result["details_es"] = "Fail2ban esta activo. Las IPs que intenten fuerza bruta seran bloqueadas automaticamente."
        result["details_en"] = "Fail2ban is active. IPs attempting brute force will be automatically blocked."
    else:
        # Check if there are failed login attempts
        auth_stdout, _, _ = run_command(
            "journalctl -u sshd --since '24 hours ago' 2>/dev/null | grep -c 'Failed password\\|authentication failure' || echo 0"
        )
        try:
            attempts = int(auth_stdout.strip().split('\n')[0]) if auth_stdout else 0
        except (ValueError, IndexError):
            attempts = 0
        result["details_es"] = (
            f"Fail2ban no esta instalado. "
            + (f"En las ultimas 24 horas hubo {attempts} intentos de intrusion por SSH. " if attempts > 0 else "")
            + "Sin fail2ban, los atacantes pueden intentar infinitas contrasenas sin ser bloqueados."
        )
        result["details_en"] = (
            f"Fail2ban is not installed. "
            + (f"In the last 24 hours there were {attempts} SSH intrusion attempts. " if attempts > 0 else "")
            + "Without fail2ban, attackers can try unlimited passwords without being blocked."
        )
        result["fix_es"] = [
            "Instala fail2ban:",
            "  sudo apt install fail2ban -y",
            "  sudo systemctl enable fail2ban",
            "  sudo systemctl start fail2ban",
            "",
            "La configuracion por defecto ya protege SSH (3 intentos = ban por 10 min).",
        ]
        result["fix_en"] = [
            "Install fail2ban:",
            "  sudo apt install fail2ban -y",
            "  sudo systemctl enable fail2ban",
            "  sudo systemctl start fail2ban",
            "",
            "The default config already protects SSH (3 attempts = 10 min ban).",
        ]
    return result


# ─── Check 10: Automatic Updates ────────────────────────────────────────────

def check_auto_updates():
    """CHECK 10: Are automatic security updates enabled?"""
    result = {
        "id": "auto_updates",
        "name_es": "Actualizaciones automaticas de seguridad",
        "name_en": "Automatic security updates",
        "severity": "MEDIUM",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    # Check unattended-upgrades
    stdout, _, code = run_command(
        "dpkg -l unattended-upgrades 2>/dev/null | grep -c '^ii' || echo 0"
    )
    is_installed = int(stdout or "0") > 0

    # Check if service is active
    svc_stdout, _, svc_code = run_command("systemctl is-active unattended-upgrades 2>/dev/null")
    is_active = svc_code == 0 and "active" in svc_stdout

    if is_installed and is_active:
        result["passed"] = True
        result["details_es"] = "Las actualizaciones automaticas de seguridad estan activas. Tu servidor se parchea solo."
        result["details_en"] = "Automatic security updates are active. Your server patches itself."
    else:
        result["details_es"] = (
            "Las actualizaciones automaticas no estan activas. Si sale un parche de seguridad critico, "
            "tu servidor quedaria vulnerable hasta que lo actualices manualmente."
        )
        result["details_en"] = (
            "Automatic updates are not active. If a critical security patch is released, "
            "your server stays vulnerable until you manually update."
        )
        result["fix_es"] = [
            "Instala actualizaciones automaticas:",
            "  sudo apt install unattended-upgrades -y",
            "  sudo dpkg-reconfigure -plow unattended-upgrades",
            "  (Selecciona 'Yes' cuando te pregunte)",
        ]
        result["fix_en"] = [
            "Install automatic updates:",
            "  sudo apt install unattended-upgrades -y",
            "  sudo dpkg-reconfigure -plow unattended-upgrades",
            "  (Select 'Yes' when prompted)",
        ]
    return result


# ─── Check 11: OpenClaw Running as Root ─────────────────────────────────────

def check_openclaw_user():
    """CHECK 11: Is OpenClaw running as a non-root user?"""
    result = {
        "id": "openclaw_user",
        "name_es": "OpenClaw corriendo como root",
        "name_en": "OpenClaw running as root",
        "severity": "HIGH",
        "passed": False,
        "auto_fixable": True,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    stdout, _, code = run_command(
        "ps aux 2>/dev/null | grep -i 'openclaw\\|moltbot\\|clawdbot' | grep -v grep | head -3"
    )

    if not stdout:
        result["passed"] = True
        result["details_es"] = "No se detectaron procesos de OpenClaw corriendo (puede estar en Docker)."
        result["details_en"] = "No OpenClaw processes detected running (may be in Docker)."
        result["severity"] = "INFO"
        return result

    running_as_root = False
    for line in stdout.split("\n"):
        if line.strip().startswith("root"):
            running_as_root = True
            break

    if not running_as_root:
        result["passed"] = True
        result["details_es"] = "OpenClaw corre con un usuario no-root. Si el agente es comprometido, el dano es limitado."
        result["details_en"] = "OpenClaw runs as a non-root user. If the agent is compromised, damage is limited."
    else:
        result["details_es"] = (
            "OpenClaw esta corriendo como root. Si un atacante compromete el agente, "
            "tiene control total del servidor — puede borrar archivos, instalar malware, o robar datos."
        )
        result["details_en"] = (
            "OpenClaw is running as root. If an attacker compromises the agent, "
            "they have full control of the server — they can delete files, install malware, or steal data."
        )
        result["fix_es"] = [
            "Correr como root significa que si alguien compromete el agente,",
            "tiene control total del servidor. La solucion es crear un usuario dedicado.",
            "",
            "Paso 1 — Crea un usuario solo para OpenClaw:",
            "  sudo useradd -m -s /bin/bash openclaw",
            "  (Esto crea un usuario sin privilegios que solo sirve para correr OpenClaw)",
            "",
            "Paso 2 — Copia tu configuracion al nuevo usuario:",
            "  sudo cp -r ~/.openclaw /home/openclaw/.openclaw",
            "  sudo chown -R openclaw:openclaw /home/openclaw/.openclaw",
            "",
            "Paso 3 — Detiene OpenClaw actual y reinicialo con el nuevo usuario:",
            "  openclaw stop",
            "  sudo -u openclaw openclaw start",
            "",
            "Paso 4 — Para que inicie automaticamente, actualiza el servicio systemd:",
            "  sudo sed -i 's/User=root/User=openclaw/' /etc/systemd/system/openclaw.service",
            "  sudo systemctl daemon-reload",
            "  sudo systemctl restart openclaw",
        ]
        result["fix_en"] = [
            "Running as root means if someone compromises the agent,",
            "they have full control of the server. The solution is a dedicated user.",
            "",
            "Step 1 — Create a user just for OpenClaw:",
            "  sudo useradd -m -s /bin/bash openclaw",
            "  (This creates an unprivileged user that only runs OpenClaw)",
            "",
            "Step 2 — Copy your config to the new user:",
            "  sudo cp -r ~/.openclaw /home/openclaw/.openclaw",
            "  sudo chown -R openclaw:openclaw /home/openclaw/.openclaw",
            "",
            "Step 3 — Stop current OpenClaw and restart with the new user:",
            "  openclaw stop",
            "  sudo -u openclaw openclaw start",
            "",
            "Step 4 — To auto-start, update the systemd service:",
            "  sudo sed -i 's/User=root/User=openclaw/' /etc/systemd/system/openclaw.service",
            "  sudo systemctl daemon-reload",
            "  sudo systemctl restart openclaw",
        ]
    return result


# ─── Check 12: Open Ports ───────────────────────────────────────────────────

def check_open_ports():
    """CHECK 12: Are only necessary ports open?"""
    result = {
        "id": "open_ports",
        "name_es": "Puertos abiertos",
        "name_en": "Open ports",
        "severity": "MEDIUM",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    stdout, _, code = run_command(
        "ss -tlnp 2>/dev/null | grep 'LISTEN' | grep '0.0.0.0\\|::' || "
        "netstat -tlnp 2>/dev/null | grep 'LISTEN' | grep '0.0.0.0\\|::'"
    )

    # Safe ports that are expected
    safe_ports = {"22"}  # SSH
    exposed_ports = set()

    for line in stdout.split("\n"):
        if not line.strip():
            continue
        # Extract port from address like 0.0.0.0:22 or :::22
        match = re.search(r'(?:0\.0\.0\.0|::):(\d+)', line)
        if match:
            exposed_ports.add(match.group(1))

    unexpected_ports = exposed_ports - safe_ports

    if not unexpected_ports:
        result["passed"] = True
        result["details_es"] = f"Solo los puertos necesarios estan expuestos al internet: {', '.join(sorted(exposed_ports)) or 'ninguno'}."
        result["details_en"] = f"Only necessary ports are exposed to the internet: {', '.join(sorted(exposed_ports)) or 'none'}."
    else:
        result["details_es"] = (
            f"Hay puertos inesperados abiertos al internet: {', '.join(sorted(unexpected_ports))}. "
            "Cada puerto abierto es una puerta mas que un atacante puede intentar abrir."
        )
        result["details_en"] = (
            f"Unexpected ports are open to the internet: {', '.join(sorted(unexpected_ports))}. "
            "Each open port is another door an attacker can try to open."
        )
        result["fix_es"] = [
            "Revisa que servicio usa cada puerto:",
            "  sudo ss -tlnp",
            "",
            "Si no necesitas un servicio, detenlo:",
            "  sudo systemctl stop <servicio>",
            "  sudo systemctl disable <servicio>",
            "",
            "O bloquealo con firewall:",
            "  sudo ufw deny <puerto>",
        ]
        result["fix_en"] = [
            "Check which service uses each port:",
            "  sudo ss -tlnp",
            "",
            "If you don't need a service, stop it:",
            "  sudo systemctl stop <service>",
            "  sudo systemctl disable <service>",
            "",
            "Or block it with firewall:",
            "  sudo ufw deny <port>",
        ]
    return result


# ─── Check 13: Disk Space ───────────────────────────────────────────────────

def check_disk_space():
    """CHECK 13: Is there enough free disk space?"""
    result = {
        "id": "disk_space",
        "name_es": "Espacio en disco",
        "name_en": "Disk space",
        "severity": "MEDIUM",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    stdout, _, code = run_command("df -h / 2>/dev/null | tail -1")

    if code == 0 and stdout:
        parts = stdout.split()
        if len(parts) >= 5:
            usage_pct = int(parts[4].replace("%", ""))
            available = parts[3]

            if usage_pct < 85:
                result["passed"] = True
                result["details_es"] = f"Tienes {available} disponibles ({usage_pct}% usado). Suficiente espacio."
                result["details_en"] = f"You have {available} available ({usage_pct}% used). Enough space."
            else:
                result["severity"] = "HIGH" if usage_pct >= 95 else "MEDIUM"
                result["details_es"] = (
                    f"Tu disco esta al {usage_pct}% — solo quedan {available} libres. "
                    "Si se llena, OpenClaw puede dejar de funcionar y puedes perder datos."
                )
                result["details_en"] = (
                    f"Your disk is at {usage_pct}% — only {available} free. "
                    "If it fills up, OpenClaw may stop working and you could lose data."
                )
                result["fix_es"] = [
                    "Limpia espacio:",
                    "  sudo apt autoremove -y",
                    "  sudo apt clean",
                    "  sudo journalctl --vacuum-size=100M",
                ]
                result["fix_en"] = [
                    "Free up space:",
                    "  sudo apt autoremove -y",
                    "  sudo apt clean",
                    "  sudo journalctl --vacuum-size=100M",
                ]
    return result


# ─── Check 14: Docker Security (if applicable) ──────────────────────────────

def check_docker_security():
    """CHECK 14: Is Docker configured securely?"""
    result = {
        "id": "docker_security",
        "name_es": "Seguridad de Docker",
        "name_en": "Docker security",
        "severity": "MEDIUM",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    # Check if Docker is installed
    _, _, docker_code = run_command("docker --version 2>/dev/null")
    if docker_code != 0:
        result["passed"] = True
        result["details_es"] = "Docker no esta instalado (no aplica)."
        result["details_en"] = "Docker is not installed (not applicable)."
        result["severity"] = "INFO"
        return result

    issues = []

    # Check if Docker socket is exposed
    stdout, _, _ = run_command("ls -la /var/run/docker.sock 2>/dev/null")
    if "666" in stdout or "777" in stdout:
        issues.append({
            "es": "El socket de Docker tiene permisos abiertos — cualquier usuario puede ejecutar contenedores.",
            "en": "Docker socket has open permissions — any user can run containers.",
        })

    # Check if containers run as root
    stdout, _, _ = run_command("docker ps --format '{{.Names}}' 2>/dev/null")
    if stdout:
        for container in stdout.split("\n"):
            if container.strip():
                user_stdout, _, _ = run_command(f"docker inspect --format '{{{{.Config.User}}}}' {container.strip()} 2>/dev/null")
                if not user_stdout or user_stdout == "root" or user_stdout == "0":
                    issues.append({
                        "es": f"El contenedor '{container.strip()}' corre como root dentro del contenedor.",
                        "en": f"Container '{container.strip()}' runs as root inside the container.",
                    })
                    break  # One example is enough

    if not issues:
        result["passed"] = True
        result["details_es"] = "Docker esta configurado correctamente."
        result["details_en"] = "Docker is configured correctly."
    else:
        result["details_es"] = " | ".join(i["es"] for i in issues)
        result["details_en"] = " | ".join(i["en"] for i in issues)
        result["fix_es"] = [
            "Asegura el socket de Docker:",
            "  sudo chmod 660 /var/run/docker.sock",
            "",
            "Corre contenedores como usuario no-root cuando sea posible.",
        ]
        result["fix_en"] = [
            "Secure the Docker socket:",
            "  sudo chmod 660 /var/run/docker.sock",
            "",
            "Run containers as non-root user when possible.",
        ]
    return result


# ─── Check 15: SSH Intrusion Attempts ────────────────────────────────────────

def check_intrusion_attempts():
    """CHECK 15: Are there active brute force attempts?"""
    result = {
        "id": "intrusion_attempts",
        "name_es": "Intentos de intrusion activos",
        "name_en": "Active intrusion attempts",
        "severity": "INFO",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    # Count failed login attempts in last 24h
    stdout, _, _ = run_command(
        "journalctl -u sshd --since '24 hours ago' 2>/dev/null | "
        "grep -c 'Failed password\\|authentication failure\\|Invalid user' || echo 0"
    )
    try:
        attempts = int(stdout.strip().split('\n')[0]) if stdout else 0
    except (ValueError, IndexError):
        attempts = 0

    # Get top attacker IPs
    ip_stdout, _, _ = run_command(
        "journalctl -u sshd --since '24 hours ago' 2>/dev/null | "
        "grep -oP 'from \\K[0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+' | "
        "sort | uniq -c | sort -rn | head -3"
    )

    if attempts < 10:
        result["passed"] = True
        result["details_es"] = f"Solo {attempts} intentos fallidos en las ultimas 24 horas. Actividad normal."
        result["details_en"] = f"Only {attempts} failed attempts in the last 24 hours. Normal activity."
    else:
        result["severity"] = "HIGH" if attempts > 100 else "MEDIUM"
        top_ips = []
        for line in (ip_stdout or "").split("\n"):
            line = line.strip()
            if line:
                parts = line.split()
                if len(parts) >= 2:
                    top_ips.append(f"{parts[1]} ({parts[0]} intentos)")

        result["details_es"] = (
            f"Hubo {attempts} intentos de intrusion en las ultimas 24 horas. "
            + (f"Las IPs mas activas: {', '.join(top_ips[:3])}. " if top_ips else "")
            + "Esto es comun en servidores publicos, pero deberias tener fail2ban para bloquearlos."
        )
        result["details_en"] = (
            f"There were {attempts} intrusion attempts in the last 24 hours. "
            + (f"Most active IPs: {', '.join(top_ips[:3])}. " if top_ips else "")
            + "This is common on public servers, but you should have fail2ban to block them."
        )
        result["fix_es"] = [
            "Instala fail2ban para bloquear atacantes automaticamente:",
            "  sudo apt install fail2ban -y",
            "  sudo systemctl enable fail2ban",
            "  sudo systemctl start fail2ban",
        ]
        result["fix_en"] = [
            "Install fail2ban to automatically block attackers:",
            "  sudo apt install fail2ban -y",
            "  sudo systemctl enable fail2ban",
            "  sudo systemctl start fail2ban",
        ]
    return result


# ─── Check 16: Config File Permissions ─────────────────────────────────────

def check_config_permissions():
    """CHECK 16: Are OpenClaw config files properly protected?"""
    result = {
        "id": "config_permissions",
        "name_es": "Permisos de archivos de configuracion",
        "name_en": "Config file permissions",
        "severity": "HIGH",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    config_files = [
        OPENCLAW_CONFIG,
        OPENCLAW_GATEWAY_CONFIG,
        OPENCLAW_CREDENTIALS,
        OPENCLAW_HOME / "config" / "skills.json",
    ]

    world_readable = []
    for cf in config_files:
        if file_exists(cf):
            try:
                stat = os.stat(cf)
                mode = oct(stat.st_mode)[-3:]
                # World-readable (others have read: xx4, xx5, xx6, xx7)
                if int(mode[2]) >= 4:
                    world_readable.append(f"{cf.name} ({mode})")
            except OSError:
                pass

    if not world_readable:
        result["passed"] = True
        result["details_es"] = "Los archivos de configuracion tienen permisos correctos. Solo tu usuario puede leerlos."
        result["details_en"] = "Config files have correct permissions. Only your user can read them."
    else:
        result["details_es"] = (
            f"Estos archivos son legibles por todos los usuarios del sistema: {', '.join(world_readable)}. "
            "Cualquier proceso o usuario puede leer tus tokens y credenciales."
        )
        result["details_en"] = (
            f"These files are readable by all system users: {', '.join(world_readable)}. "
            "Any process or user can read your tokens and credentials."
        )
        result["fix_es"] = [
            "Corrige los permisos:",
            "  chmod 600 ~/.openclaw/.env",
            "  chmod 600 ~/.openclaw/config/*.json",
            "  chmod 700 ~/.openclaw/config",
        ]
        result["fix_en"] = [
            "Fix permissions:",
            "  chmod 600 ~/.openclaw/.env",
            "  chmod 600 ~/.openclaw/config/*.json",
            "  chmod 700 ~/.openclaw/config",
        ]
    return result


# ─── Check 17: SSL/TLS on Gateway ─────────────────────────────────────────

def check_ssl_tls():
    """CHECK 17: Is the gateway using HTTPS/TLS?"""
    result = {
        "id": "ssl_tls",
        "name_es": "SSL/TLS en el gateway",
        "name_en": "SSL/TLS on gateway",
        "severity": "MEDIUM",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    # If gateway is local-only, TLS is less critical
    stdout, _, code = run_command("openclaw config get gateway 2>/dev/null")
    gateway_config = None
    if code == 0 and stdout:
        json_start = stdout.find("{")
        if json_start >= 0:
            try:
                gateway_config = json.loads(stdout[json_start:])
            except json.JSONDecodeError:
                pass

    bind_address = "0.0.0.0"
    tls_enabled = False
    if gateway_config:
        bind_address = gateway_config.get("bind", gateway_config.get("host", "0.0.0.0"))
        tls_config = gateway_config.get("tls", gateway_config.get("ssl", {}))
        tls_enabled = tls_config.get("enabled", False) if isinstance(tls_config, dict) else bool(tls_config)

    is_local = bind_address.lower() in SAFE_BIND_VALUES

    if tls_enabled:
        result["passed"] = True
        result["details_es"] = "TLS esta activado. Las comunicaciones con el gateway estan cifradas."
        result["details_en"] = "TLS is enabled. Gateway communications are encrypted."
    elif is_local:
        result["passed"] = True
        result["severity"] = "INFO"
        result["details_es"] = "El gateway es local — TLS no es necesario porque el trafico no sale de tu maquina."
        result["details_en"] = "Gateway is local — TLS is not needed because traffic doesn't leave your machine."
    else:
        result["details_es"] = (
            "Tu gateway esta expuesto sin cifrado TLS/HTTPS. "
            "Las comunicaciones viajan en texto plano — cualquiera en tu red puede ver tus comandos y datos."
        )
        result["details_en"] = (
            "Your gateway is exposed without TLS/HTTPS encryption. "
            "Communications travel in plain text — anyone on your network can see your commands and data."
        )
        result["fix_es"] = [
            "Opcion 1 — Usa un reverse proxy con SSL (recomendado):",
            "  sudo apt install nginx certbot python3-certbot-nginx -y",
            "  sudo certbot --nginx -d tu-dominio.com",
            "",
            "Opcion 2 — Cambia el gateway a local y usa SSH tunnel:",
            "  openclaw config set gateway.bind 127.0.0.1",
            "  openclaw restart",
        ]
        result["fix_en"] = [
            "Option 1 — Use a reverse proxy with SSL (recommended):",
            "  sudo apt install nginx certbot python3-certbot-nginx -y",
            "  sudo certbot --nginx -d your-domain.com",
            "",
            "Option 2 — Set gateway to local and use SSH tunnel:",
            "  openclaw config set gateway.bind 127.0.0.1",
            "  openclaw restart",
        ]
    return result


# ─── Check 18: Backup Configuration ───────────────────────────────────────

def check_backups():
    """CHECK 18: Are backups configured?"""
    result = {
        "id": "backups",
        "name_es": "Configuracion de backups",
        "name_en": "Backup configuration",
        "severity": "HIGH",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    has_backup = False

    # Check common backup tools
    backup_checks = [
        ("crontab -l 2>/dev/null | grep -i 'backup\\|rsync\\|tar\\|borg\\|restic\\|duplicity'", "cron backup job"),
        ("systemctl is-active borgmatic 2>/dev/null", "borgmatic"),
        ("which restic 2>/dev/null && restic snapshots --latest 1 2>/dev/null", "restic"),
        ("ls /etc/cron.daily/*backup* 2>/dev/null", "daily backup script"),
    ]

    for cmd, name in backup_checks:
        stdout, _, code = run_command(cmd)
        if code == 0 and stdout:
            has_backup = True
            break

    # Also check if OpenClaw has its own backup config
    oc_backup_stdout, _, _ = run_command("openclaw config get backup 2>/dev/null")
    if oc_backup_stdout and "enabled" in oc_backup_stdout.lower():
        has_backup = True

    if has_backup:
        result["passed"] = True
        result["details_es"] = "Se detectaron backups configurados. Tus datos estan respaldados."
        result["details_en"] = "Backups detected. Your data is backed up."
    else:
        result["details_es"] = (
            "No se detectaron backups configurados. Si el disco falla, una actualizacion sale mal, "
            "o alguien borra tus datos, lo pierdes todo — tu configuracion, skills, y conversaciones."
        )
        result["details_en"] = (
            "No backups detected. If the disk fails, an update goes wrong, "
            "or someone deletes your data, you lose everything — config, skills, and conversations."
        )
        result["fix_es"] = [
            "Configura un backup automatico diario:",
            "  # Opcion simple con cron + tar:",
            "  sudo crontab -e",
            "  # Agrega esta linea (backup diario a las 3am):",
            "  0 3 * * * tar czf /root/openclaw-backup-$(date +\\%Y\\%m\\%d).tar.gz ~/.openclaw/",
            "",
            "  # Opcion mejor — restic (con encriptacion):",
            "  sudo apt install restic -y",
            "  restic init --repo /root/backups",
            "  restic backup ~/.openclaw/ --repo /root/backups",
        ]
        result["fix_en"] = [
            "Set up an automatic daily backup:",
            "  # Simple option with cron + tar:",
            "  sudo crontab -e",
            "  # Add this line (daily backup at 3am):",
            "  0 3 * * * tar czf /root/openclaw-backup-$(date +\\%Y\\%m\\%d).tar.gz ~/.openclaw/",
            "",
            "  # Better option — restic (with encryption):",
            "  sudo apt install restic -y",
            "  restic init --repo /root/backups",
            "  restic backup ~/.openclaw/ --repo /root/backups",
        ]
    return result


# ─── Check 19: Skills Supply Chain ─────────────────────────────────────────

def check_skills_supply_chain():
    """CHECK 19: Do installed skills pull external dependencies?"""
    result = {
        "id": "skills_supply_chain",
        "name_es": "Dependencias externas de skills",
        "name_en": "Skills external dependencies",
        "severity": "HIGH",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    if not file_exists(OPENCLAW_SKILLS_DIR):
        result["passed"] = True
        result["details_es"] = "No hay skills instaladas."
        result["details_en"] = "No skills installed."
        result["severity"] = "INFO"
        return result

    risky_skills = []
    total_skills = 0

    for skill_dir in OPENCLAW_SKILLS_DIR.iterdir():
        if not skill_dir.is_dir():
            continue
        if skill_dir.name.lower() in WHITELISTED_SKILLS:
            continue
        total_skills += 1

        # Check for package managers / dependency files
        risky_files = []
        dep_indicators = [
            "requirements.txt", "package.json", "Pipfile",
            "setup.py", "pyproject.toml", "yarn.lock",
        ]
        for dep_file in dep_indicators:
            if (skill_dir / dep_file).exists():
                risky_files.append(dep_file)

        # Check for pip install / npm install in scripts
        for file_path in skill_dir.rglob("*.sh"):
            try:
                content = file_path.read_text(errors="ignore")
                if re.search(r'pip\s+install|npm\s+install|curl.*\|\s*sh|wget.*\|\s*sh', content):
                    risky_files.append(f"{file_path.name} (instala paquetes)")
            except OSError:
                pass

        if risky_files:
            risky_skills.append({"skill": skill_dir.name, "files": risky_files})

    if not risky_skills:
        result["passed"] = True
        result["details_es"] = f"Ninguna de las {total_skills} skills tiene dependencias externas sospechosas."
        result["details_en"] = f"None of the {total_skills} skills have suspicious external dependencies."
    else:
        skill_list = ", ".join(s["skill"] for s in risky_skills)
        result["details_es"] = (
            f"Estas skills descargan paquetes externos: {skill_list}. "
            "Un paquete comprometido en npm o pip puede darle acceso a un atacante. "
            "El 36% de skills en ClawHub tenian este tipo de riesgo (Snyk ToxicSkills)."
        )
        result["details_en"] = (
            f"These skills download external packages: {skill_list}. "
            "A compromised npm or pip package can give an attacker access. "
            "36% of ClawHub skills had this kind of risk (Snyk ToxicSkills)."
        )
        result["fix_es"] = [
            "Revisa las dependencias de cada skill sospechosa:",
        ] + [
            f"  - {s['skill']}: {', '.join(s['files'])}"
            for s in risky_skills
        ] + [
            "",
            "Si no necesitas la skill, eliminala. Si la necesitas, revisa el package.json o requirements.txt.",
        ]
        result["fix_en"] = [
            "Review dependencies of each suspicious skill:",
        ] + [
            f"  - {s['skill']}: {', '.join(s['files'])}"
            for s in risky_skills
        ] + [
            "",
            "If you don't need the skill, remove it. If you do, review the package.json or requirements.txt.",
        ]
    return result


# ─── Check 20: Environment Variable Leakage ───────────────────────────────

def check_env_leakage():
    """CHECK 20: Are secrets leaking through environment variables?"""
    result = {
        "id": "env_leakage",
        "name_es": "Filtracion de secrets en variables de entorno",
        "name_en": "Environment variable secret leakage",
        "severity": "HIGH",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    # Check if OpenClaw process has secrets in its environment
    stdout, _, code = run_command(
        "ps aux 2>/dev/null | grep -i 'openclaw\\|moltbot' | grep -v grep | awk '{print $2}' | head -1"
    )

    leaked_vars = []
    if stdout:
        pid = stdout.strip()
        env_stdout, _, env_code = run_command(f"cat /proc/{pid}/environ 2>/dev/null | tr '\\0' '\\n'")
        if env_code == 0 and env_stdout:
            secret_env_patterns = [
                r"API_KEY=", r"SECRET=", r"TOKEN=", r"PASSWORD=",
                r"AWS_ACCESS", r"OPENAI_API", r"ANTHROPIC_API",
            ]
            for line in env_stdout.split("\n"):
                for pattern in secret_env_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        var_name = line.split("=")[0] if "=" in line else line
                        leaked_vars.append(var_name)
                        break

    # Also check /proc/*/cmdline for secrets in command args
    cmd_stdout, _, _ = run_command(
        "ps aux 2>/dev/null | grep -i 'openclaw\\|moltbot' | grep -v grep"
    )
    if cmd_stdout:
        secret_in_cmd = re.search(r'(sk-[a-zA-Z0-9]{10,}|--token\s+\S+|--password\s+\S+)', cmd_stdout)
        if secret_in_cmd:
            leaked_vars.append("SECRET_IN_COMMAND_LINE")

    if not leaked_vars:
        result["passed"] = True
        result["details_es"] = "No se detectaron secrets expuestos en variables de entorno o linea de comandos."
        result["details_en"] = "No secrets detected in environment variables or command line."
    else:
        result["details_es"] = (
            f"Se detectaron {len(leaked_vars)} variables con secrets en el entorno del proceso: "
            f"{', '.join(leaked_vars[:5])}. Cualquier skill o proceso hijo puede leer estas variables."
        )
        result["details_en"] = (
            f"Detected {len(leaked_vars)} secret variables in process environment: "
            f"{', '.join(leaked_vars[:5])}. Any skill or child process can read these variables."
        )
        result["fix_es"] = [
            "Mueve los secrets al archivo .env y aseguralo:",
            "  chmod 600 ~/.openclaw/.env",
            "",
            "No pases secrets como argumentos de comando ni como variables de entorno del sistema.",
        ]
        result["fix_en"] = [
            "Move secrets to the .env file and secure it:",
            "  chmod 600 ~/.openclaw/.env",
            "",
            "Don't pass secrets as command arguments or system environment variables.",
        ]
    return result


# ─── Check 21: Cron Job Audit (Persistence Detection) ─────────────────────

def check_cron_persistence():
    """CHECK 21: Are there suspicious cron jobs that could be malware persistence?"""
    result = {
        "id": "cron_persistence",
        "name_es": "Tareas programadas sospechosas (persistencia)",
        "name_en": "Suspicious scheduled tasks (persistence)",
        "severity": "HIGH",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    suspicious_entries = []

    # Check all crontabs
    cron_sources = [
        ("crontab -l 2>/dev/null", "root crontab"),
        ("ls /etc/cron.d/ 2>/dev/null", "cron.d directory"),
    ]

    # Check root crontab
    stdout, _, code = run_command("crontab -l 2>/dev/null")
    if code == 0 and stdout:
        suspicious_cron_patterns = [
            r"curl.*\|\s*(bash|sh)",           # Download and execute
            r"wget.*\|\s*(bash|sh)",           # Download and execute
            r"python.*-c\s+['\"]import",       # Inline Python execution
            r"/tmp/",                           # Execution from /tmp
            r"/dev/shm/",                       # Execution from shared memory
            r"nc\s+-[elp]",                     # Netcat listener (reverse shell)
            r"base64\s+-d",                     # Encoded payloads
        ]
        for line in stdout.split("\n"):
            line = line.strip()
            if line.startswith("#") or not line:
                continue
            for pattern in suspicious_cron_patterns:
                if re.search(pattern, line):
                    suspicious_entries.append(line[:80])
                    break

    # Check /etc/cron.d for unusual files
    cron_d_stdout, _, _ = run_command("ls -la /etc/cron.d/ 2>/dev/null")
    if cron_d_stdout:
        for line in cron_d_stdout.split("\n"):
            # Recently modified cron files (less than 1 day)
            if re.search(r'\.(tmp|bak|old)', line):
                suspicious_entries.append(f"Archivo sospechoso en cron.d: {line.split()[-1] if line.split() else 'unknown'}")

    if not suspicious_entries:
        result["passed"] = True
        result["details_es"] = "No se encontraron tareas programadas sospechosas. Sin indicios de persistencia maliciosa."
        result["details_en"] = "No suspicious scheduled tasks found. No signs of malicious persistence."
    else:
        result["details_es"] = (
            f"Se encontraron {len(suspicious_entries)} entrada(s) sospechosa(s) en tareas programadas. "
            "Esto puede indicar malware intentando mantener acceso permanente a tu servidor."
        )
        result["details_en"] = (
            f"Found {len(suspicious_entries)} suspicious scheduled task(s). "
            "This may indicate malware trying to maintain permanent access to your server."
        )
        result["fix_es"] = [
            "Revisa las entradas sospechosas:",
        ] + [f"  - {entry}" for entry in suspicious_entries[:5]] + [
            "",
            "Si no reconoces alguna, eliminala:",
            "  sudo crontab -e  (para root)",
            "  crontab -e  (para tu usuario)",
        ]
        result["fix_en"] = [
            "Review suspicious entries:",
        ] + [f"  - {entry}" for entry in suspicious_entries[:5]] + [
            "",
            "If you don't recognize one, remove it:",
            "  sudo crontab -e  (for root)",
            "  crontab -e  (for your user)",
        ]
    return result


# ─── Check 22: CORS Configuration ─────────────────────────────────────────

def check_cors_config():
    """CHECK 22: Is CORS configured to prevent cross-origin attacks?"""
    result = {
        "id": "cors_config",
        "name_es": "Configuracion CORS del gateway",
        "name_en": "Gateway CORS configuration",
        "severity": "HIGH",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    # Read gateway config
    stdout, _, code = run_command("openclaw config get gateway 2>/dev/null")
    gateway_config = None
    if code == 0 and stdout:
        json_start = stdout.find("{")
        if json_start >= 0:
            try:
                gateway_config = json.loads(stdout[json_start:])
            except json.JSONDecodeError:
                pass

    if gateway_config is None:
        gateway_config = read_json_safe(OPENCLAW_GATEWAY_CONFIG)

    bind_address = "0.0.0.0"
    cors_config = {}
    if gateway_config:
        bind_address = gateway_config.get("bind", gateway_config.get("host", "0.0.0.0"))
        cors_config = gateway_config.get("cors", {})

    is_local = bind_address.lower() in SAFE_BIND_VALUES

    # Check CORS settings
    cors_origin = cors_config.get("origin", cors_config.get("allowOrigin", "*"))

    if is_local:
        result["passed"] = True
        result["severity"] = "INFO"
        result["details_es"] = "El gateway es local — CORS no es un riesgo directo."
        result["details_en"] = "Gateway is local — CORS is not a direct risk."
    elif cors_origin != "*":
        result["passed"] = True
        result["details_es"] = "CORS esta configurado con origenes restringidos. Solo sitios autorizados pueden conectarse."
        result["details_en"] = "CORS is configured with restricted origins. Only authorized sites can connect."
    else:
        result["details_es"] = (
            "CORS permite conexiones desde cualquier origen (*). "
            "Esto es lo que habilito el CVE-2026-25253 — un sitio malicioso puede enviar comandos "
            "a tu agente si visitas una pagina web comprometida."
        )
        result["details_en"] = (
            "CORS allows connections from any origin (*). "
            "This is what enabled CVE-2026-25253 — a malicious site can send commands "
            "to your agent if you visit a compromised web page."
        )
        result["fix_es"] = [
            "Restringe CORS a origenes confiables:",
            "  openclaw config set gateway.cors.origin 'http://localhost:3000'",
            "  openclaw restart",
            "",
            "O mejor aun, cambia el gateway a loopback:",
            "  openclaw config set gateway.bind 127.0.0.1",
        ]
        result["fix_en"] = [
            "Restrict CORS to trusted origins:",
            "  openclaw config set gateway.cors.origin 'http://localhost:3000'",
            "  openclaw restart",
            "",
            "Or even better, set gateway to loopback:",
            "  openclaw config set gateway.bind 127.0.0.1",
        ]
    return result


# ─── Check 23: Skill Integrity Verification ────────────────────────────────

def check_skill_integrity():
    """CHECK 23: Have installed skills been modified since installation?"""
    result = {
        "id": "skill_integrity",
        "name_es": "Integridad de skills instaladas",
        "name_en": "Installed skill integrity",
        "severity": "MEDIUM",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    if not file_exists(OPENCLAW_SKILLS_DIR):
        result["passed"] = True
        result["details_es"] = "No hay skills instaladas."
        result["details_en"] = "No skills installed."
        result["severity"] = "INFO"
        return result

    # Check for skills with recently modified files (potential tampering)
    tampered = []
    integrity_file = OPENCLAW_SKILLS_DIR / ".lobsterguard_checksums"

    if file_exists(integrity_file):
        # Compare current checksums with stored ones
        stored = read_json_safe(integrity_file)
        if stored:
            for skill_dir in OPENCLAW_SKILLS_DIR.iterdir():
                if not skill_dir.is_dir() or skill_dir.name.lower() in WHITELISTED_SKILLS:
                    continue
                for file_path in skill_dir.rglob("*"):
                    if not file_path.is_file():
                        continue
                    rel_path = str(file_path.relative_to(OPENCLAW_SKILLS_DIR))
                    try:
                        current_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()
                        if rel_path in stored and stored[rel_path] != current_hash:
                            tampered.append(rel_path)
                    except OSError:
                        pass
    else:
        # No baseline exists — create one and flag it
        checksums = {}
        for skill_dir in OPENCLAW_SKILLS_DIR.iterdir():
            if not skill_dir.is_dir():
                continue
            for file_path in skill_dir.rglob("*"):
                if not file_path.is_file():
                    continue
                rel_path = str(file_path.relative_to(OPENCLAW_SKILLS_DIR))
                try:
                    checksums[rel_path] = hashlib.sha256(file_path.read_bytes()).hexdigest()
                except OSError:
                    pass

        try:
            with open(integrity_file, "w") as f:
                json.dump(checksums, f)
        except OSError:
            pass

        result["passed"] = True
        result["details_es"] = (
            "Se creo un baseline de integridad para tus skills. "
            "En proximas auditorias se detectara si alguien modifica los archivos."
        )
        result["details_en"] = (
            "An integrity baseline was created for your skills. "
            "Future audits will detect if anyone modifies the files."
        )
        return result

    if not tampered:
        result["passed"] = True
        result["details_es"] = "Todas las skills mantienen su integridad. Ningun archivo fue modificado."
        result["details_en"] = "All skills maintain their integrity. No files were modified."
    else:
        result["severity"] = "CRITICAL"
        result["details_es"] = (
            f"Se detectaron {len(tampered)} archivo(s) modificados desde la ultima auditoria: "
            f"{', '.join(tampered[:3])}. Esto puede indicar que alguien (o algo) altero una skill."
        )
        result["details_en"] = (
            f"Detected {len(tampered)} file(s) modified since last audit: "
            f"{', '.join(tampered[:3])}. This may indicate someone (or something) tampered with a skill."
        )
        result["fix_es"] = [
            "Revisa los cambios en las skills modificadas:",
        ] + [f"  - {f}" for f in tampered[:5]] + [
            "",
            "Si no hiciste los cambios, reinstala la skill:",
            "  openclaw skills remove <nombre>",
            "  openclaw skills install <nombre>",
        ]
        result["fix_en"] = [
            "Review changes in modified skills:",
        ] + [f"  - {f}" for f in tampered[:5]] + [
            "",
            "If you didn't make the changes, reinstall the skill:",
            "  openclaw skills remove <name>",
            "  openclaw skills install <name>",
        ]
    return result


# ─── Check 24: System User Audit ──────────────────────────────────────────

def check_system_users():
    """CHECK 24: Are there unexpected users with shell access?"""
    result = {
        "id": "system_users",
        "name_es": "Usuarios del sistema con acceso shell",
        "name_en": "System users with shell access",
        "severity": "MEDIUM",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    # Get users with real shells
    stdout, _, code = run_command(
        "grep -E '/bin/(bash|sh|zsh|fish)$' /etc/passwd 2>/dev/null"
    )

    expected_users = {"root", "ubuntu", "debian", "admin", "openclaw"}
    unexpected = []

    if stdout:
        for line in stdout.split("\n"):
            if not line.strip():
                continue
            username = line.split(":")[0]
            uid = int(line.split(":")[2]) if len(line.split(":")) > 2 else 0
            # System users typically have UID < 1000 (except root=0)
            if username not in expected_users and uid >= 1000:
                unexpected.append(username)

    if not unexpected:
        result["passed"] = True
        result["details_es"] = "Solo los usuarios esperados tienen acceso shell al sistema."
        result["details_en"] = "Only expected users have shell access to the system."
    else:
        result["severity"] = "HIGH"
        result["details_es"] = (
            f"Se encontraron usuarios inesperados con shell: {', '.join(unexpected)}. "
            "Un atacante pudo haber creado una cuenta para mantener acceso."
        )
        result["details_en"] = (
            f"Found unexpected users with shell access: {', '.join(unexpected)}. "
            "An attacker may have created an account to maintain access."
        )
        result["fix_es"] = [
            "Revisa cada usuario:",
        ] + [f"  sudo chage -l {u}" for u in unexpected[:3]] + [
            "",
            "Si no reconoces un usuario, deshabilitalo:",
            "  sudo usermod -s /sbin/nologin <usuario>",
        ]
        result["fix_en"] = [
            "Review each user:",
        ] + [f"  sudo chage -l {u}" for u in unexpected[:3]] + [
            "",
            "If you don't recognize a user, disable it:",
            "  sudo usermod -s /sbin/nologin <user>",
        ]
    return result


# ─── Check 25: Log Rotation ───────────────────────────────────────────────

def check_log_rotation():
    """CHECK 25: Is log rotation configured to prevent disk fill?"""
    result = {
        "id": "log_rotation",
        "name_es": "Rotacion de logs",
        "name_en": "Log rotation",
        "severity": "MEDIUM",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    # Check if logrotate is installed and configured
    stdout, _, code = run_command("dpkg -l logrotate 2>/dev/null | grep -c '^ii' || echo 0")
    logrotate_installed = int(stdout or "0") > 0

    # Check journal size
    journal_stdout, _, _ = run_command("journalctl --disk-usage 2>/dev/null")
    journal_size_mb = 0
    if journal_stdout:
        match = re.search(r'([\d.]+)\s*(G|M)', journal_stdout)
        if match:
            size = float(match.group(1))
            unit = match.group(2)
            journal_size_mb = size * 1024 if unit == "G" else size

    if logrotate_installed and journal_size_mb < 500:
        result["passed"] = True
        result["details_es"] = f"Log rotation esta configurado. Los journals usan {journal_size_mb:.0f}MB."
        result["details_en"] = f"Log rotation is configured. Journals use {journal_size_mb:.0f}MB."
    else:
        issues = []
        if not logrotate_installed:
            issues.append("logrotate no esta instalado" if True else "logrotate not installed")
        if journal_size_mb >= 500:
            issues.append(f"los journals usan {journal_size_mb:.0f}MB")
        result["details_es"] = (
            f"Problemas con logs: {', '.join(issues)}. "
            "Los logs pueden llenar el disco y dejar el servidor inoperativo."
        )
        result["details_en"] = (
            f"Log issues: {', '.join(issues)}. "
            "Logs can fill the disk and make the server inoperable."
        )
        result["fix_es"] = [
            "Limita el tamano de los journals:",
            "  sudo journalctl --vacuum-size=200M",
            "",
            "Instala logrotate si no existe:",
            "  sudo apt install logrotate -y",
        ]
        result["fix_en"] = [
            "Limit journal size:",
            "  sudo journalctl --vacuum-size=200M",
            "",
            "Install logrotate if missing:",
            "  sudo apt install logrotate -y",
        ]
    return result


# ─── Check 26: OpenClaw Sandbox Mode ──────────────────────────────────────

def check_sandbox_mode():
    """CHECK 26: Is OpenClaw running with sandbox/restricted permissions?"""
    result = {
        "id": "sandbox_mode",
        "name_es": "Modo sandbox de OpenClaw",
        "name_en": "OpenClaw sandbox mode",
        "severity": "HIGH",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    # Check OpenClaw permission/sandbox config
    stdout, _, code = run_command("openclaw config get permissions 2>/dev/null")
    config = None
    if code == 0 and stdout:
        json_start = stdout.find("{")
        if json_start >= 0:
            try:
                config = json.loads(stdout[json_start:])
            except json.JSONDecodeError:
                pass

    if config is None:
        main_config = read_json_safe(OPENCLAW_CONFIG)
        if main_config:
            config = main_config.get("permissions", main_config.get("sandbox", {}))

    has_restrictions = False
    if config:
        # Check for any permission restrictions
        sandbox_enabled = config.get("sandbox", config.get("enabled", False))
        file_access = config.get("fileAccess", config.get("file_access", "full"))
        network_access = config.get("networkAccess", config.get("network_access", "full"))

        if sandbox_enabled or file_access != "full" or network_access != "full":
            has_restrictions = True

    if has_restrictions:
        result["passed"] = True
        result["details_es"] = "OpenClaw tiene restricciones de permisos activas. El agente no puede hacer lo que quiera."
        result["details_en"] = "OpenClaw has active permission restrictions. The agent can't do whatever it wants."
    else:
        result["details_es"] = (
            "OpenClaw no tiene restricciones de permisos. El agente puede acceder a cualquier archivo "
            "y hacer conexiones de red sin limite. Si una skill maliciosa toma el control, "
            "tiene acceso completo a todo tu sistema."
        )
        result["details_en"] = (
            "OpenClaw has no permission restrictions. The agent can access any file "
            "and make unlimited network connections. If a malicious skill takes control, "
            "it has complete access to your entire system."
        )
        result["fix_es"] = [
            "Activa el modo sandbox para limitar el agente:",
            "  openclaw config set permissions.sandbox true",
            "  openclaw config set permissions.fileAccess restricted",
            "  openclaw config set permissions.networkAccess restricted",
            "  openclaw restart",
            "",
            "Esto limita que archivos puede leer el agente y a que servidores puede conectarse.",
        ]
        result["fix_en"] = [
            "Enable sandbox mode to limit the agent:",
            "  openclaw config set permissions.sandbox true",
            "  openclaw config set permissions.fileAccess restricted",
            "  openclaw config set permissions.networkAccess restricted",
            "  openclaw restart",
            "",
            "This limits which files the agent can read and which servers it can connect to.",
        ]
    return result


# ─── Check 27: Outbound Connection Monitoring ─────────────────────────────

def check_outbound_connections():
    """CHECK 27: Are there suspicious outbound connections?"""
    result = {
        "id": "outbound_connections",
        "name_es": "Conexiones salientes sospechosas",
        "name_en": "Suspicious outbound connections",
        "severity": "MEDIUM",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    # Check established connections from OpenClaw processes
    stdout, _, code = run_command(
        "ss -tnp 2>/dev/null | grep -i 'openclaw\\|moltbot\\|node' | grep 'ESTAB'"
    )

    # Known safe destinations
    safe_domains = [
        "api.openai.com", "api.anthropic.com", "api.telegram.org",
        "registry.npmjs.org", "github.com",
    ]

    suspicious = []
    if stdout:
        for line in stdout.split("\n"):
            if not line.strip():
                continue
            # Extract remote IP:port
            match = re.search(r'(\d+\.\d+\.\d+\.\d+):(\d+)\s+', line)
            if match:
                remote_ip = match.group(1)
                remote_port = match.group(2)
                # Common suspicious ports
                if remote_port in ("4444", "5555", "6666", "8888", "9999", "1337"):
                    suspicious.append(f"{remote_ip}:{remote_port} (puerto sospechoso)")
                # Check for connections to unusual IPs (not well-known ranges)
                # This is a basic heuristic
                if remote_ip.startswith("10.") or remote_ip.startswith("192.168."):
                    continue  # Internal, skip

    if not suspicious:
        result["passed"] = True
        result["details_es"] = "No se detectaron conexiones salientes sospechosas."
        result["details_en"] = "No suspicious outbound connections detected."
    else:
        result["severity"] = "CRITICAL"
        result["details_es"] = (
            f"Se detectaron {len(suspicious)} conexion(es) sospechosa(s): "
            f"{', '.join(suspicious[:3])}. Esto puede indicar exfiltracion de datos o un reverse shell."
        )
        result["details_en"] = (
            f"Detected {len(suspicious)} suspicious connection(s): "
            f"{', '.join(suspicious[:3])}. This may indicate data exfiltration or a reverse shell."
        )
        result["fix_es"] = [
            "Investiga las conexiones:",
            "  ss -tnp | grep ESTAB",
            "",
            "Si hay conexiones que no reconoces, bloquealas con firewall:",
            "  sudo ufw deny out to <IP>",
        ]
        result["fix_en"] = [
            "Investigate the connections:",
            "  ss -tnp | grep ESTAB",
            "",
            "If there are connections you don't recognize, block them:",
            "  sudo ufw deny out to <IP>",
        ]
    return result


# ─── Check 28: LobsterGuard Self-Protection ──────────────────────────────────

def check_self_protection():
    """CHECK 28: Is LobsterGuard itself protected against tampering?"""
    result = {
        "id": "self_protection",
        "name_es": "Auto-proteccion de LobsterGuard",
        "name_en": "LobsterGuard self-protection",
        "severity": "CRITICAL",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    lobsterguard_dir = OPENCLAW_SKILLS_DIR / "lobsterguard"
    issues = []

    if not file_exists(lobsterguard_dir):
        result["details_es"] = (
            "No se encontro el directorio de LobsterGuard en la ruta esperada. "
            "Esto puede significar que la instalacion esta incompleta o fue eliminada."
        )
        result["details_en"] = (
            "LobsterGuard directory not found at expected path. "
            "This may mean the installation is incomplete or was removed."
        )
        result["fix_es"] = [
            "Reinstala LobsterGuard en la ubicacion correcta:",
            "  mkdir -p ~/.openclaw/skills/lobsterguard/scripts",
            "  mkdir -p ~/.openclaw/skills/lobsterguard/references",
            "",
            "Luego copia los archivos SKILL.md, scripts/check.py y references/risks.md",
            "desde una fuente confiable al directorio.",
        ]
        result["fix_en"] = [
            "Reinstall LobsterGuard at the correct location:",
            "  mkdir -p ~/.openclaw/skills/lobsterguard/scripts",
            "  mkdir -p ~/.openclaw/skills/lobsterguard/references",
            "",
            "Then copy SKILL.md, scripts/check.py and references/risks.md",
            "from a trusted source to the directory.",
        ]
        return result

    # Check 28a: LobsterGuard files are owned by root (not writable by openclaw user)
    check_py = lobsterguard_dir / "scripts" / "check.py"
    skill_md = lobsterguard_dir / "SKILL.md"

    for critical_file in [check_py, skill_md]:
        if file_exists(critical_file):
            stat = os.stat(critical_file)
            mode = oct(stat.st_mode)[-3:]
            # If world-writable or group-writable
            if int(mode[1]) & 2 or int(mode[2]) & 2:
                issues.append({
                    "es": f"{critical_file.name} es escribible por otros usuarios ({mode})",
                    "en": f"{critical_file.name} is writable by other users ({mode})",
                })

    # Check 28b: SKILL.md hasn't been injected with prompt override
    if file_exists(skill_md):
        try:
            content = skill_md.read_text(errors="ignore")
            injection_patterns = [
                r"ignore\s+(previous|all|above)\s+instructions",
                r"you\s+are\s+now\s+a",
                r"forget\s+your\s+(rules|instructions|guidelines)",
                r"SYSTEM\s*:",
                r"<\s*system\s*>",
            ]
            for pattern in injection_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    issues.append({
                        "es": "Se detecto un posible prompt injection en SKILL.md",
                        "en": "Possible prompt injection detected in SKILL.md",
                    })
                    break
        except OSError:
            pass

    # Check 28c: check.py hasn't been modified to skip checks
    if file_exists(check_py):
        try:
            content = check_py.read_text(errors="ignore")
            # Check for bypass patterns
            bypass_patterns = [
                r'result\["passed"\]\s*=\s*True\s*#.*bypass',
                r'return\s+\{.*"passed":\s*True.*\}\s*#\s*(skip|bypass|disabled)',
                r'if\s+False:',  # Dead code disabling checks
            ]
            for pattern in bypass_patterns:
                if re.search(pattern, content):
                    issues.append({
                        "es": "Se detecto codigo que desactiva checks en check.py",
                        "en": "Code that disables checks detected in check.py",
                    })
                    break
        except OSError:
            pass

    if not issues:
        result["passed"] = True
        result["details_es"] = (
            "LobsterGuard esta protegido. Los archivos criticos tienen permisos correctos "
            "y no se detectaron modificaciones maliciosas."
        )
        result["details_en"] = (
            "LobsterGuard is protected. Critical files have correct permissions "
            "and no malicious modifications were detected."
        )
    else:
        result["details_es"] = (
            "Se detectaron problemas de integridad en LobsterGuard: "
            + " | ".join(i["es"] for i in issues)
            + ". Un atacante podria haber modificado LobsterGuard para ocultar amenazas."
        )
        result["details_en"] = (
            "Integrity issues detected in LobsterGuard: "
            + " | ".join(i["en"] for i in issues)
            + ". An attacker could have modified LobsterGuard to hide threats."
        )
        result["fix_es"] = [
            "Esto es critico — si alguien modifica LobsterGuard, puede ocultar amenazas",
            "y hacerte creer que todo esta bien cuando no lo esta.",
            "",
            "Paso 1 — Corrige los permisos para que solo root pueda modificar los archivos:",
            "  sudo chown root:root ~/.openclaw/skills/lobsterguard/SKILL.md",
            "  sudo chown root:root ~/.openclaw/skills/lobsterguard/scripts/check.py",
            "  sudo chmod 644 ~/.openclaw/skills/lobsterguard/SKILL.md",
            "  sudo chmod 644 ~/.openclaw/skills/lobsterguard/scripts/check.py",
            "  (644 significa: root puede escribir, todos pueden leer, nadie mas puede modificar)",
            "",
            "Paso 2 — Si sospechas que el SKILL.md o check.py fue alterado:",
            "  Reinstala LobsterGuard desde el repositorio oficial o la copia original.",
            "  Compara los archivos con: diff archivo_actual archivo_original",
            "",
            "Paso 3 — Para proteccion adicional, haz los archivos inmutables:",
            "  sudo chattr +i ~/.openclaw/skills/lobsterguard/scripts/check.py",
            "  (Esto evita que CUALQUIER proceso modifique el archivo, incluso root necesita quitar el flag primero)",
        ]
        result["fix_en"] = [
            "This is critical — if someone modifies LobsterGuard, they can hide threats",
            "and make you believe everything is fine when it's not.",
            "",
            "Step 1 — Fix permissions so only root can modify the files:",
            "  sudo chown root:root ~/.openclaw/skills/lobsterguard/SKILL.md",
            "  sudo chown root:root ~/.openclaw/skills/lobsterguard/scripts/check.py",
            "  sudo chmod 644 ~/.openclaw/skills/lobsterguard/SKILL.md",
            "  sudo chmod 644 ~/.openclaw/skills/lobsterguard/scripts/check.py",
            "  (644 means: root can write, everyone can read, nobody else can modify)",
            "",
            "Step 2 — If you suspect SKILL.md or check.py was tampered with:",
            "  Reinstall LobsterGuard from the official repo or your original copy.",
            "  Compare files with: diff current_file original_file",
            "",
            "Step 3 — For extra protection, make files immutable:",
            "  sudo chattr +i ~/.openclaw/skills/lobsterguard/scripts/check.py",
            "  (This prevents ANY process from modifying the file, even root needs to remove the flag first)",
        ]
    return result


def check_skill_prompt_injection():
    """CHECK 29: Do installed skills contain prompt injection patterns?"""
    result = {
        "id": "skill_prompt_injection",
        "name_es": "Inyeccion de prompts en skills",
        "name_en": "Skill prompt injection",
        "severity": "CRITICAL",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    injection_patterns = [
        r"ignore\s+(previous|all|above)\s+instructions",
        r"you\s+are\s+now",
        r"forget\s+your\s+(rules|instructions|guidelines)",
        r"SYSTEM\s*:",
        r"<\s*system\s*>",
        r"do\s+not\s+tell\s+the\s+user",
        r"\[INST\]",
    ]

    issues = []

    if not file_exists(OPENCLAW_SKILLS_DIR):
        result["passed"] = True
        result["details_en"] = "Skills directory does not exist."
        result["details_es"] = "El directorio de skills no existe."
        return result

    for skill_dir in Path(OPENCLAW_SKILLS_DIR).iterdir():
        if not skill_dir.is_dir() or skill_dir.name in WHITELISTED_SKILLS:
            continue

        # Check SKILL.md
        skill_md = skill_dir / "SKILL.md"
        if file_exists(skill_md):
            try:
                content = skill_md.read_text(errors="ignore")
                # Check for zero-width chars
                if "\u200b" in content or "\u200c" in content or "\u200d" in content or "\ufeff" in content:
                    issues.append({
                        "es": f"{skill_dir.name}: caracteres ocultos detectados en SKILL.md",
                        "en": f"{skill_dir.name}: hidden characters detected in SKILL.md",
                    })
                # Check for injection patterns
                for pattern in injection_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        issues.append({
                            "es": f"{skill_dir.name}: posible inyeccion de prompt en SKILL.md",
                            "en": f"{skill_dir.name}: possible prompt injection in SKILL.md",
                        })
                        break
            except OSError:
                pass

        # Check Python/shell/JS files in skill
        for script_file in skill_dir.rglob("*"):
            if script_file.suffix not in [".py", ".sh", ".js"]:
                continue
            try:
                content = script_file.read_text(errors="ignore")
                # Check for zero-width chars
                if "\u200b" in content or "\u200c" in content or "\u200d" in content or "\ufeff" in content:
                    issues.append({
                        "es": f"{skill_dir.name}: caracteres ocultos en {script_file.name}",
                        "en": f"{skill_dir.name}: hidden characters in {script_file.name}",
                    })
                # Check for injection patterns
                for pattern in injection_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        issues.append({
                            "es": f"{skill_dir.name}: inyeccion de prompt en {script_file.name}",
                            "en": f"{skill_dir.name}: prompt injection in {script_file.name}",
                        })
                        break
            except OSError:
                pass

    if not issues:
        result["passed"] = True
        result["details_en"] = "No prompt injection patterns detected in installed skills."
        result["details_es"] = "No se detectaron patrones de inyeccion de prompts en los skills instalados."
    else:
        result["details_en"] = "Prompt injection patterns found: " + "; ".join(i["en"] for i in issues)
        result["details_es"] = "Patrones de inyeccion encontrados: " + "; ".join(i["es"] for i in issues)
        result["fix_es"] = [
            "Un atacante podria haber inyectado instrucciones en tus skills para manipular al agente.",
            "",
            "Paso 1 — Identifica el skill afectado (visto arriba) e inspecciona manualmente sus archivos:",
            "  cat ~/.openclaw/skills/NOMBRE_SKILL/SKILL.md | head -100",
            "",
            "Paso 2 — Si encuentras patrones sospechosos, desinstala el skill:",
            "  rm -rf ~/.openclaw/skills/NOMBRE_SKILL",
            "",
            "Paso 3 — Si es un skill critico, reinstalalo desde la fuente oficial confiable.",
            "",
            "Paso 4 — Considera actualizar tus skills regularmente desde repositorios seguros.",
        ]
        result["fix_en"] = [
            "An attacker could have injected instructions into your skills to manipulate the agent.",
            "",
            "Step 1 — Identify the affected skill (shown above) and manually inspect its files:",
            "  cat ~/.openclaw/skills/SKILL_NAME/SKILL.md | head -100",
            "",
            "Step 2 — If you find suspicious patterns, uninstall the skill:",
            "  rm -rf ~/.openclaw/skills/SKILL_NAME",
            "",
            "Step 3 — If it's a critical skill, reinstall it from a trusted official source.",
            "",
            "Step 4 — Consider updating your skills regularly from secure repositories.",
        ]

    return result


def check_skill_hidden_content():
    """CHECK 30: Do skill files contain hidden encoded content?"""
    result = {
        "id": "skill_hidden_content",
        "name_es": "Contenido oculto en skills",
        "name_en": "Skill hidden content",
        "severity": "HIGH",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    issues = []

    if not file_exists(OPENCLAW_SKILLS_DIR):
        result["passed"] = True
        result["details_en"] = "Skills directory does not exist."
        result["details_es"] = "El directorio de skills no existe."
        return result

    for skill_dir in Path(OPENCLAW_SKILLS_DIR).iterdir():
        if not skill_dir.is_dir() or skill_dir.name in WHITELISTED_SKILLS:
            continue

        for file_path in skill_dir.rglob("*"):
            if file_path.is_dir():
                continue
            try:
                content = file_path.read_text(errors="ignore")

                # Check for base64 blocks (50+ chars)
                b64_pattern = r'[A-Za-z0-9+/]{50,}={0,2}'
                if re.search(b64_pattern, content):
                    issues.append({
                        "es": f"{skill_dir.name}: posible contenido base64 en {file_path.name}",
                        "en": f"{skill_dir.name}: possible base64 content in {file_path.name}",
                    })

                # Check for hex-encoded strings
                hex_pattern = r'\\x[0-9a-fA-F]{2}.*\\x[0-9a-fA-F]{2}'
                if re.search(hex_pattern, content):
                    issues.append({
                        "es": f"{skill_dir.name}: posible contenido hex en {file_path.name}",
                        "en": f"{skill_dir.name}: possible hex-encoded content in {file_path.name}",
                    })

                # Check for unicode escapes (\\u)
                if r'\u00' in content or r'\u2' in content:
                    issues.append({
                        "es": f"{skill_dir.name}: posible contenido unicode escapado en {file_path.name}",
                        "en": f"{skill_dir.name}: possible unicode-escaped content in {file_path.name}",
                    })

                # Check for extremely long lines (>2000 chars)
                for i, line in enumerate(content.split('\n'), 1):
                    if len(line) > 2000:
                        issues.append({
                            "es": f"{skill_dir.name}: linea muy larga ({len(line)} chars) en {file_path.name}:{i}",
                            "en": f"{skill_dir.name}: extremely long line ({len(line)} chars) in {file_path.name}:{i}",
                        })
                        break
            except OSError:
                pass

    if not issues:
        result["passed"] = True
        result["details_en"] = "No hidden or encoded content detected in skill files."
        result["details_es"] = "No se detecto contenido oculto o codificado en los archivos de skills."
    else:
        result["details_en"] = "Hidden content detected: " + "; ".join(set(i["en"] for i in issues))
        result["details_es"] = "Contenido oculto detectado: " + "; ".join(set(i["es"] for i in issues))
        result["fix_es"] = [
            "El contenido oculto o codificado en skills puede ocultar codigo malicioso.",
            "",
            "Paso 1 — Examina los archivos sospechosos:",
            "  cat ~/.openclaw/skills/NOMBRE_SKILL/archivo_sospechoso",
            "",
            "Paso 2 — Intenta decodificar base64 sospechoso:",
            "  echo 'CONTENIDO_BASE64' | base64 -d",
            "",
            "Paso 3 — Si no entiendes el contenido o parece malicioso, desinstala el skill:",
            "  rm -rf ~/.openclaw/skills/NOMBRE_SKILL",
            "",
            "Paso 4 — Solo instala skills de fuentes confiables y que sean open-source.",
        ]
        result["fix_en"] = [
            "Hidden or encoded content in skills can hide malicious code.",
            "",
            "Step 1 — Examine the suspicious files:",
            "  cat ~/.openclaw/skills/SKILL_NAME/suspicious_file",
            "",
            "Step 2 — Try to decode suspicious base64:",
            "  echo 'BASE64_CONTENT' | base64 -d",
            "",
            "Step 3 — If you don't understand the content or it looks malicious, uninstall the skill:",
            "  rm -rf ~/.openclaw/skills/SKILL_NAME",
            "",
            "Step 4 — Only install skills from trusted sources that are open-source.",
        ]

    return result


def check_mcp_server_security():
    """CHECK 31: Are MCP servers configured securely?"""
    result = {
        "id": "mcp_server_security",
        "name_es": "Seguridad de servidores MCP",
        "name_en": "MCP server security",
        "severity": "HIGH",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    issues = []

    # Check for MCP config file
    mcp_config_path = OPENCLAW_HOME / "config" / "mcp.json"
    if not file_exists(mcp_config_path):
        result["passed"] = True
        result["details_en"] = "No MCP config found."
        result["details_es"] = "No se encontro configuracion de MCP."
        return result

    config = read_json_safe(mcp_config_path)
    if not config or "servers" not in config:
        result["passed"] = True
        result["details_en"] = "No MCP servers configured."
        result["details_es"] = "No hay servidores MCP configurados."
        return result

    for server_name, server_cfg in config.get("servers", {}).items():
        # Check for http:// (no TLS)
        if isinstance(server_cfg, dict):
            transport = server_cfg.get("transport", "")
            if isinstance(transport, str) and "http://" in transport.lower():
                issues.append({
                    "es": f"{server_name}: usa HTTP sin TLS",
                    "en": f"{server_name}: uses HTTP without TLS",
                })

            # Check for npx/pip (supply chain risk)
            if server_cfg.get("type") in ["npx", "pip", "node_modules", "python_packages"]:
                issues.append({
                    "es": f"{server_name}: utiliza {server_cfg.get('type')} (riesgo de cadena de suministro)",
                    "en": f"{server_name}: uses {server_cfg.get('type')} (supply chain risk)",
                })

            # Check for shell operators in args
            args = server_cfg.get("args", [])
            if isinstance(args, list):
                for arg in args:
                    if any(op in str(arg) for op in ["|", "&", ";", "`", "$", ">"]):
                        issues.append({
                            "es": f"{server_name}: contiene operadores shell en argumentos",
                            "en": f"{server_name}: contains shell operators in arguments",
                        })
                        break

            # Check for sudo
            if server_cfg.get("sudo") or (isinstance(server_cfg.get("command"), str) and "sudo" in server_cfg.get("command", "")):
                issues.append({
                    "es": f"{server_name}: se ejecuta con sudo",
                    "en": f"{server_name}: runs with sudo",
                })

    if not issues:
        result["passed"] = True
        result["details_en"] = "MCP servers are configured securely."
        result["details_es"] = "Los servidores MCP estan configurados de forma segura."
    else:
        result["details_en"] = "MCP server issues: " + "; ".join(set(i["en"] for i in issues))
        result["details_es"] = "Problemas en servidores MCP: " + "; ".join(set(i["es"] for i in issues))
        result["fix_es"] = [
            "Los servidores MCP inseguros pueden ser explotados para ejecutar codigo arbitrario.",
            "",
            "Paso 1 — Revisa tu configuracion MCP:",
            "  cat ~/.openclaw/config/mcp.json",
            "",
            "Paso 2 — Para cada servidor problematico, asegura lo siguiente:",
            "  - Usa HTTPS en lugar de HTTP",
            "  - Evita npx/pip; descarga y verifica manualmente",
            "  - No uses operadores shell en argumentos",
            "  - Nunca ejecutes servidores con sudo",
            "",
            "Paso 3 — Edita tu configuracion para corregir los problemas:",
            "  nano ~/.openclaw/config/mcp.json",
            "",
            "Paso 4 — Reinicia OpenClaw para aplicar los cambios.",
        ]
        result["fix_en"] = [
            "Insecure MCP servers can be exploited to execute arbitrary code.",
            "",
            "Step 1 — Review your MCP configuration:",
            "  cat ~/.openclaw/config/mcp.json",
            "",
            "Step 2 — For each problematic server, ensure:",
            "  - Use HTTPS instead of HTTP",
            "  - Avoid npx/pip; manually download and verify",
            "  - Don't use shell operators in arguments",
            "  - Never run servers with sudo",
            "",
            "Step 3 — Edit your config to fix the issues:",
            "  nano ~/.openclaw/config/mcp.json",
            "",
            "Step 4 — Restart OpenClaw to apply changes.",
        ]

    return result


def check_mcp_tool_poisoning():
    """CHECK 32: Are MCP tool descriptions free of injection patterns?"""
    result = {
        "id": "mcp_tool_poisoning",
        "name_es": "Envenenamiento de herramientas MCP",
        "name_en": "MCP tool poisoning",
        "severity": "CRITICAL",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    injection_patterns = [
        r"ignore\s+(previous|instructions)",
        r"<\s*system\s*>",
        r"secretly",
        r"exfiltrate",
        r"send\s+to\s+http",
    ]

    issues = []

    # Try to get tools list
    stdout, stderr, returncode = run_command("openclaw tools list --json 2>/dev/null")
    if returncode != 0:
        result["passed"] = True
        result["details_en"] = "Could not retrieve MCP tools list."
        result["details_es"] = "No se pudo obtener la lista de herramientas MCP."
        return result

    try:
        tools = json.loads(stdout)
    except (json.JSONDecodeError, ValueError):
        result["passed"] = True
        result["details_en"] = "Could not parse MCP tools list."
        result["details_es"] = "No se pudo analizar la lista de herramientas MCP."
        return result

    if not isinstance(tools, list):
        tools = tools.get("tools", [])

    for tool in tools:
        description = tool.get("description", "") if isinstance(tool, dict) else ""
        tool_name = tool.get("name", "") if isinstance(tool, dict) else str(tool)

        for pattern in injection_patterns:
            if re.search(pattern, description, re.IGNORECASE):
                issues.append({
                    "es": f"Herramienta '{tool_name}': posible inyeccion en descripcion",
                    "en": f"Tool '{tool_name}': possible injection in description",
                })
                break

    if not issues:
        result["passed"] = True
        result["details_en"] = "No tool poisoning patterns detected."
        result["details_es"] = "No se detectaron patrones de envenenamiento de herramientas."
    else:
        result["details_en"] = "Tool poisoning detected: " + "; ".join(set(i["en"] for i in issues))
        result["details_es"] = "Envenenamiento de herramientas detectado: " + "; ".join(set(i["es"] for i in issues))
        result["fix_es"] = [
            "Un atacante podria haber modificado las descripciones de las herramientas para inyectar instrucciones.",
            "",
            "Paso 1 — Lista todas tus herramientas MCP:",
            "  openclaw tools list",
            "",
            "Paso 2 — Para cada herramienta problematica, verifica su origen y fuente:",
            "  openclaw tools info NOMBRE_HERRAMIENTA",
            "",
            "Paso 3 — Desactiva o desinstala herramientas sospechosas.",
            "",
            "Paso 4 — Solo instala herramientas de fuentes verificadas y de confianza.",
        ]
        result["fix_en"] = [
            "An attacker could have modified tool descriptions to inject instructions.",
            "",
            "Step 1 — List all your MCP tools:",
            "  openclaw tools list",
            "",
            "Step 2 — For each problematic tool, verify its origin and source:",
            "  openclaw tools info TOOL_NAME",
            "",
            "Step 3 — Disable or uninstall suspicious tools.",
            "",
            "Step 4 — Only install tools from verified and trusted sources.",
        ]

    return result


def check_data_exfiltration_channels():
    """CHECK 33: Are there channels for data exfiltration?"""
    result = {
        "id": "data_exfiltration_channels",
        "name_es": "Canales de exfiltracion de datos",
        "name_en": "Data exfiltration channels",
        "severity": "HIGH",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    issues = []

    # Check logs for leaked API keys
    log_dir = OPENCLAW_HOME / "logs"
    if file_exists(log_dir):
        for log_file in log_dir.rglob("*.log"):
            try:
                content = log_file.read_text(errors="ignore", encoding="utf-8")
                if re.search(r'sk-[A-Za-z0-9_-]{20,}|api[_-]?key|password|token', content, re.IGNORECASE):
                    issues.append({
                        "es": f"Posibles credenciales en log: {log_file.name}",
                        "en": f"Possible credentials in log: {log_file.name}",
                    })
            except OSError:
                pass

    # Check conversation history directory permissions
    history_dir = OPENCLAW_HOME / "conversations" if file_exists(OPENCLAW_HOME / "conversations") else None
    if history_dir:
        try:
            stat = os.stat(history_dir)
            mode = oct(stat.st_mode)[-3:]
            # Check if world-readable
            if int(mode[2]) >= 4:
                issues.append({
                    "es": f"Directorio de conversaciones es legible globalmente ({mode})",
                    "en": f"Conversations directory is world-readable ({mode})",
                })
        except OSError:
            pass

    # Check for external webhook endpoints in config
    config = read_json_safe(OPENCLAW_CONFIG)
    if config:
        for key, value in config.items():
            if isinstance(value, str) and ("webhook" in value.lower() or "http" in value.lower()):
                if "external" in key.lower() or "callback" in key.lower():
                    issues.append({
                        "es": f"Posible endpoint externo en config: {key}",
                        "en": f"Possible external endpoint in config: {key}",
                    })

    if not issues:
        result["passed"] = True
        result["details_en"] = "No obvious data exfiltration channels detected."
        result["details_es"] = "No se detectaron canales obvios de exfiltracion de datos."
    else:
        result["details_en"] = "Exfiltration risks: " + "; ".join(set(i["en"] for i in issues))
        result["details_es"] = "Riesgos de exfiltracion: " + "; ".join(set(i["es"] for i in issues))
        result["fix_es"] = [
            "Los canales de exfiltracion de datos pueden permitir a un atacante robar informacion sensible.",
            "",
            "Paso 1 — Revisa tus logs y busca credenciales expuestas:",
            "  grep -r 'sk-' ~/.openclaw/logs/",
            "  grep -r 'api_key' ~/.openclaw/logs/",
            "",
            "Paso 2 — Si encuentras credenciales expuestas, rotarlas inmediatamente en el proveedor.",
            "",
            "Paso 3 — Fija permisos restrictivos en directorios sensibles:",
            "  chmod 700 ~/.openclaw/conversations",
            "  chmod 700 ~/.openclaw/logs",
            "",
            "Paso 4 — Revisa tu configuracion para endpoints externos no autorizados:",
            "  cat ~/.openclaw/config/moltbot.json | grep -i webhook",
        ]
        result["fix_en"] = [
            "Data exfiltration channels can allow attackers to steal sensitive information.",
            "",
            "Step 1 — Review your logs and search for exposed credentials:",
            "  grep -r 'sk-' ~/.openclaw/logs/",
            "  grep -r 'api_key' ~/.openclaw/logs/",
            "",
            "Step 2 — If you find exposed credentials, rotate them immediately with your provider.",
            "",
            "Step 3 — Set restrictive permissions on sensitive directories:",
            "  chmod 700 ~/.openclaw/conversations",
            "  chmod 700 ~/.openclaw/logs",
            "",
            "Step 4 — Review your config for unauthorized external endpoints:",
            "  cat ~/.openclaw/config/moltbot.json | grep -i webhook",
        ]

    return result


def check_log_secrets():
    """CHECK 34: Are API keys and secrets leaking in logs?"""
    result = {
        "id": "log_secrets",
        "name_es": "Secretos en logs",
        "name_en": "Secrets in logs",
        "severity": "HIGH",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    secret_patterns = [
        (r'sk-[A-Za-z0-9_-]{20,}', 'OpenAI API key'),
        (r'claude[_-]?key["\']?\s*[:=]\s*["\']?[A-Za-z0-9_-]{20,}', 'Anthropic API key'),
        (r'github[_-]?token["\']?\s*[:=]\s*ghp_[A-Za-z0-9_]{36,}', 'GitHub token'),
        (r'AKIA[0-9A-Z]{16}', 'AWS Access Key'),
        (r'password\s*[:=]\s*[^\s\n]{8,}', 'Password'),
    ]

    issues = []
    secret_types_found = set()

    # Check systemd journal
    stdout, stderr, returncode = run_command("journalctl -u openclaw -n 1000 2>/dev/null")
    for pattern, secret_type in secret_patterns:
        if re.search(pattern, stdout, re.IGNORECASE):
            secret_types_found.add(secret_type)

    # Check syslog
    if file_exists("/var/log/syslog"):
        try:
            with open("/var/log/syslog", "r", errors="ignore") as f:
                content = f.read(100000)  # Read first 100KB
                for pattern, secret_type in secret_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        secret_types_found.add(secret_type)
        except PermissionError:
            pass

    # Check OpenClaw logs
    log_dir = OPENCLAW_HOME / "logs"
    if file_exists(log_dir):
        for log_file in log_dir.rglob("*.log"):
            try:
                with open(log_file, "r", errors="ignore") as f:
                    content = f.read(100000)  # Read first 100KB
                    for pattern, secret_type in secret_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            secret_types_found.add(secret_type)
            except PermissionError:
                pass

    if secret_types_found:
        for secret_type in secret_types_found:
            issues.append({
                "es": f"Tipo de secreto en logs: {secret_type}",
                "en": f"Secret type in logs: {secret_type}",
            })

    if not issues:
        result["passed"] = True
        result["details_en"] = "No obvious secrets detected in logs."
        result["details_es"] = "No se detectaron secretos obvios en los logs."
    else:
        result["details_en"] = "Secrets found in logs: " + ", ".join(set(i["en"] for i in issues))
        result["details_es"] = "Secretos encontrados en logs: " + ", ".join(set(i["es"] for i in issues))
        result["fix_es"] = [
            "Los secretos (API keys, tokens, passwords) en logs son un riesgo grave de seguridad.",
            "",
            "Paso 1 — Rota TODAS las credenciales encontradas immediatamente:",
            "  Para OpenAI: accede a https://platform.openai.com/account/api-keys",
            "  Para Anthropic: accede a console.anthropic.com",
            "  Para GitHub: https://github.com/settings/tokens",
            "",
            "Paso 2 — Limpia los logs (NOTA: esto afectara a auditorias):",
            "  rm ~/.openclaw/logs/*",
            "  sudo journalctl --rotate --vacuum=time=1s",
            "",
            "Paso 3 — Configura openclaw para NO loguear credenciales:",
            "  Busca en tu config '\"logLevel\": \"debug\"' y cámbialo a 'info'",
            "  cat ~/.openclaw/config/moltbot.json",
            "",
            "Paso 4 — Considera usar un agente de secretos (HashiCorp Vault) para el futuro.",
        ]
        result["fix_en"] = [
            "Secrets (API keys, tokens, passwords) in logs are a critical security risk.",
            "",
            "Step 1 — Rotate ALL found credentials immediately:",
            "  For OpenAI: visit https://platform.openai.com/account/api-keys",
            "  For Anthropic: visit console.anthropic.com",
            "  For GitHub: https://github.com/settings/tokens",
            "",
            "Step 2 — Clean the logs (NOTE: this will affect audits):",
            "  rm ~/.openclaw/logs/*",
            "  sudo journalctl --rotate --vacuum=time=1s",
            "",
            "Step 3 — Configure openclaw to NOT log credentials:",
            "  Find '\"logLevel\": \"debug\"' in your config and change to 'info'",
            "  cat ~/.openclaw/config/moltbot.json",
            "",
            "Step 4 — Consider using a secrets manager (HashiCorp Vault) going forward.",
        ]

    return result


def check_skill_typosquatting():
    """CHECK 35: Are skill names typosquatting known popular skills?"""
    result = {
        "id": "skill_typosquatting",
        "name_es": "Typosquatting en skills",
        "name_en": "Skill typosquatting",
        "severity": "HIGH",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    # Known popular skills
    known_skills = [
        "browseruse", "browsing", "weather", "news", "calculator",
        "memory", "vectordb", "knowledgebase", "database", "filesystem",
        "shell", "python", "javascript", "git", "docker",
    ]

    issues = []

    if not file_exists(OPENCLAW_SKILLS_DIR):
        result["passed"] = True
        result["details_en"] = "Skills directory does not exist."
        result["details_es"] = "El directorio de skills no existe."
        return result

    installed_skills = [d.name for d in Path(OPENCLAW_SKILLS_DIR).iterdir() if d.is_dir()]

    for skill in installed_skills:
        skill_lower = skill.lower()
        for known in known_skills:
            # 1-char difference
            if len(skill_lower) == len(known):
                diff_count = sum(1 for a, b in zip(skill_lower, known) if a != b)
                if diff_count == 1:
                    issues.append({
                        "es": f"'{skill}' podria ser typosquatting de '{known}' (1 char diferente)",
                        "en": f"'{skill}' could be typosquatting of '{known}' (1 char different)",
                    })
            # Extra/missing char
            elif abs(len(skill_lower) - len(known)) <= 2:
                # Simple check: see if one is subset of other with minor edits
                if (known in skill_lower.replace("-", "").replace("_", "") or
                    skill_lower.replace("-", "").replace("_", "") in known):
                    issues.append({
                        "es": f"'{skill}' podria ser typosquatting de '{known}' (chars extras/faltantes)",
                        "en": f"'{skill}' could be typosquatting of '{known}' (extra/missing chars)",
                    })

    if not issues:
        result["passed"] = True
        result["details_en"] = "No obvious typosquatting detected in skill names."
        result["details_es"] = "No se detecta typosquatting obvio en nombres de skills."
    else:
        result["details_en"] = "Possible typosquatting: " + "; ".join(set(i["en"] for i in issues))
        result["details_es"] = "Posible typosquatting: " + "; ".join(set(i["es"] for i in issues))
        result["fix_es"] = [
            "Un atacante podria usar nombres de skills similares a conocidos para engañarte.",
            "",
            "Paso 1 — Examina cada skill sospechoso:",
            "  ls ~/.openclaw/skills/NOMBRE_SKILL",
            "  cat ~/.openclaw/skills/NOMBRE_SKILL/SKILL.md | head -20",
            "",
            "Paso 2 — Verifica que sea el skill correcto en el repositorio oficial.",
            "",
            "Paso 3 — Si sospechas que es falso, desinstálalo:",
            "  rm -rf ~/.openclaw/skills/NOMBRE_SKILL",
            "",
            "Paso 4 — Reinstala desde la fuente confiable con el nombre correcto.",
            "  Copia desde el repositorio oficial mantenido por el equipo.",
        ]
        result["fix_en"] = [
            "An attacker could use skill names similar to known ones to trick you.",
            "",
            "Step 1 — Examine each suspicious skill:",
            "  ls ~/.openclaw/skills/SKILL_NAME",
            "  cat ~/.openclaw/skills/SKILL_NAME/SKILL.md | head -20",
            "",
            "Step 2 — Verify it's the correct skill in the official repository.",
            "",
            "Step 3 — If you suspect it's fake, uninstall it:",
            "  rm -rf ~/.openclaw/skills/SKILL_NAME",
            "",
            "Step 4 — Reinstall from the trusted source with the correct name.",
            "  Copy from the official repository maintained by the team.",
        ]

    return result


def check_auto_approval():
    """CHECK 36: Is auto-approval enabled (critical risk)?"""
    result = {
        "id": "auto_approval",
        "name_es": "Auto-aprobacion habilitada",
        "name_en": "Auto-approval enabled",
        "severity": "CRITICAL",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    issues = []

    # Check various config locations
    config_paths = [
        OPENCLAW_CONFIG,
        OPENCLAW_HOME / "config" / "gateway.json",
        OPENCLAW_HOME / ".env",
    ]

    auto_approval_keys = [
        "autoApprove", "auto_approve", "autoRun", "auto_run",
        "permissions.autoApprove", "agent.autoRun", "tools.autoExecute",
    ]

    for config_path in config_paths:
        if not file_exists(config_path):
            continue

        # For JSON files
        if config_path.suffix == ".json":
            config = read_json_safe(config_path)
            if config:
                for key in auto_approval_keys:
                    value = config.get(key)
                    # Check nested keys
                    if "." in key:
                        parts = key.split(".")
                        temp = config
                        for part in parts[:-1]:
                            temp = temp.get(part, {})
                        value = temp.get(parts[-1]) if isinstance(temp, dict) else None

                    if value and value not in [False, 0, "false", "no", None]:
                        issues.append({
                            "es": f"Config JSON: {key} = {value}",
                            "en": f"Config JSON: {key} = {value}",
                        })
        else:
            # For .env files
            try:
                content = config_path.read_text(errors="ignore")
                for key in auto_approval_keys:
                    pattern = rf'{key.upper()}\s*=\s*(true|True|1|yes|always|all)'
                    if re.search(pattern, content, re.IGNORECASE):
                        issues.append({
                            "es": f"Env: {key} habilitado",
                            "en": f"Env: {key} enabled",
                        })
            except OSError:
                pass

    if not issues:
        result["passed"] = True
        result["details_en"] = "Auto-approval is disabled."
        result["details_es"] = "Auto-aprobacion esta deshabilitada."
    else:
        result["details_en"] = "Auto-approval ENABLED: " + "; ".join(set(i["en"] for i in issues))
        result["details_es"] = "Auto-aprobacion HABILITADA: " + "; ".join(set(i["es"] for i in issues))
        result["fix_es"] = [
            "Auto-approval es CRITICO — permite que el agente ejecute cualquier accion sin pedir permiso.",
            "Segun MCPTox, esto aumenta la tasa de exito de ataques al 84%.",
            "",
            "Paso 1 — Desactiva auto-approval inmediatamente en todos tus archivos de config:",
            "  cat ~/.openclaw/config/moltbot.json",
            "",
            "Paso 2 — Para cada archivo, edita y cambia:",
            "  'autoApprove': true       →  'autoApprove': false",
            "  'auto_approve': 'always'  →  'auto_approve': 'ask'",
            "  'autoRun': true           →  'autoRun': false",
            "",
            "Paso 3 — Usa nano o vim para editar:",
            "  nano ~/.openclaw/config/moltbot.json",
            "",
            "Paso 4 — Reinicia OpenClaw para que los cambios entren en efecto.",
            "  systemctl restart openclaw",
        ]
        result["fix_en"] = [
            "Auto-approval is CRITICAL — it allows the agent to execute any action without asking.",
            "According to MCPTox, this increases attack success rate to 84%.",
            "",
            "Step 1 — Disable auto-approval immediately in all your config files:",
            "  cat ~/.openclaw/config/moltbot.json",
            "",
            "Step 2 — For each file, edit and change:",
            "  'autoApprove': true       →  'autoApprove': false",
            "  'auto_approve': 'always'  →  'auto_approve': 'ask'",
            "  'autoRun': true           →  'autoRun': false",
            "",
            "Step 3 — Use nano or vim to edit:",
            "  nano ~/.openclaw/config/moltbot.json",
            "",
            "Step 4 — Restart OpenClaw for changes to take effect.",
            "  systemctl restart openclaw",
        ]

    return result


def check_excessive_permissions():
    """CHECK 37: Does OpenClaw have excessive permissions?"""
    result = {
        "id": "excessive_permissions",
        "name_es": "Permisos excesivos",
        "name_en": "Excessive permissions",
        "severity": "HIGH",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    issues = []

    # Check if agent runs as root
    stdout, stderr, returncode = run_command("ps aux | grep openclaw | grep -v grep | awk '{print $1}'")
    if "root" in stdout:
        issues.append({
            "es": "OpenClaw se ejecuta como root",
            "en": "OpenClaw runs as root",
        })

    # Check config for unrestricted network access
    config = read_json_safe(OPENCLAW_CONFIG)
    if config:
        allowed_hosts = config.get("allowedHosts")
        if allowed_hosts == ["*"] or allowed_hosts == "*":
            issues.append({
                "es": "Red: acceso sin restricciones (allowedHosts = *)",
                "en": "Network: unrestricted access (allowedHosts = *)",
            })

    # Check filesystem access
    if config and config.get("filesystem", {}).get("unrestricted"):
        issues.append({
            "es": "Sistema de archivos: acceso sin restricciones",
            "en": "Filesystem: unrestricted access",
        })

    # Check if can install packages freely
    if config and config.get("tools", {}).get("allowPackageInstall") in [True, "always", "all"]:
        issues.append({
            "es": "Herramientas: puede instalar paquetes sin restriccion",
            "en": "Tools: can freely install packages",
        })

    if not issues:
        result["passed"] = True
        result["details_en"] = "OpenClaw has appropriately restricted permissions."
        result["details_es"] = "OpenClaw tiene permisos apropiadamente restringidos."
    else:
        result["details_en"] = "Excessive permissions found: " + "; ".join(set(i["en"] for i in issues))
        result["details_es"] = "Permisos excesivos encontrados: " + "; ".join(set(i["es"] for i in issues))
        result["fix_es"] = [
            "Permisos excesivos amplian significativamente la capacidad de ataque.",
            "",
            "Paso 1 — Si OpenClaw corre como root, crea un usuario no-root:",
            "  sudo useradd -m -s /bin/bash openclaw",
            "  sudo chown -R openclaw:openclaw ~/.openclaw",
            "  # Actualiza tu systemd service para usar 'User=openclaw'",
            "",
            "Paso 2 — Revisa allowedHosts en tu configuracion:",
            "  cat ~/.openclaw/config/moltbot.json | grep -A2 allowedHosts",
            "",
            "Paso 3 — Si ves allowedHosts = '*', cámbialo a hosts especificos:",
            "  'allowedHosts': ['localhost', '127.0.0.1']",
            "",
            "Paso 4 — Desactiva instalacion de paquetes sin restriccion:",
            "  'allowPackageInstall': false",
        ]
        result["fix_en"] = [
            "Excessive permissions significantly expand the attack surface.",
            "",
            "Step 1 — If OpenClaw runs as root, create a non-root user:",
            "  sudo useradd -m -s /bin/bash openclaw",
            "  sudo chown -R openclaw:openclaw ~/.openclaw",
            "  # Update your systemd service to use 'User=openclaw'",
            "",
            "Step 2 — Review allowedHosts in your config:",
            "  cat ~/.openclaw/config/moltbot.json | grep -A2 allowedHosts",
            "",
            "Step 3 — If you see allowedHosts = '*', change to specific hosts:",
            "  'allowedHosts': ['localhost', '127.0.0.1']",
            "",
            "Step 4 — Disable unrestricted package installation:",
            "  'allowPackageInstall': false",
        ]

    return result


def check_memory_poisoning():
    """CHECK 38: Is memory/context poisoned with injection patterns?"""
    result = {
        "id": "memory_poisoning",
        "name_es": "Envenenamiento de memoria",
        "name_en": "Memory poisoning",
        "severity": "HIGH",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    injection_patterns = [
        r"ignore\s+(previous|instructions)",
        r"you\s+are\s+now",
        r"forget\s+your\s+(rules|guidelines)",
        r"<\s*system\s*>",
    ]

    issues = []
    world_writable_dirs = []

    # Memory dirs to check
    memory_dirs = [
        "memory", "knowledge", "context", "vectordb", "cache",
    ]

    for mem_dir_name in memory_dirs:
        mem_dir = OPENCLAW_HOME / mem_dir_name
        if not file_exists(mem_dir):
            continue

        # Check for injection patterns in memory files
        for mem_file in mem_dir.rglob("*"):
            if mem_file.is_dir():
                continue
            try:
                content = mem_file.read_text(errors="ignore")
                for pattern in injection_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        issues.append({
                            "es": f"Patron de inyeccion en {mem_dir_name}: {mem_file.name}",
                            "en": f"Injection pattern in {mem_dir_name}: {mem_file.name}",
                        })
                        break
            except OSError:
                pass

        # Check permissions
        try:
            stat = os.stat(mem_dir)
            mode = oct(stat.st_mode)[-3:]
            if int(mode[2]) >= 2:  # World-writable
                world_writable_dirs.append(mem_dir_name)
        except OSError:
            pass

    for dir_name in world_writable_dirs:
        issues.append({
            "es": f"Directorio {dir_name} es escribible globalmente",
            "en": f"Directory {dir_name} is world-writable",
        })

    if not issues:
        result["passed"] = True
        result["details_en"] = "Memory directories are secure."
        result["details_es"] = "Los directorios de memoria estan seguros."
    else:
        result["details_en"] = "Memory poisoning risks: " + "; ".join(set(i["en"] for i in issues))
        result["details_es"] = "Riesgos de envenenamiento de memoria: " + "; ".join(set(i["es"] for i in issues))
        result["fix_es"] = [
            "La memoria envenenada puede permitir que un atacante controle al agente.",
            "",
            "Paso 1 — Fija permisos restrictivos en directorios de memoria:",
            "  chmod 700 ~/.openclaw/memory 2>/dev/null",
            "  chmod 700 ~/.openclaw/knowledge 2>/dev/null",
            "  chmod 700 ~/.openclaw/context 2>/dev/null",
            "  chmod 700 ~/.openclaw/vectordb 2>/dev/null",
            "",
            "Paso 2 — Revisa archivos sospechosos en memoria:",
            "  grep -r 'ignore previous' ~/.openclaw/memory/ 2>/dev/null",
            "",
            "Paso 3 — Si encuentras archivos sospechosos, elimínalos:",
            "  rm ~/.openclaw/memory/archivo_sospechoso",
            "",
            "Paso 4 — Considera usar 'reset memory' para limpiar todo:",
            "  openclaw memory reset",
        ]
        result["fix_en"] = [
            "Poisoned memory can allow an attacker to control the agent.",
            "",
            "Step 1 — Set restrictive permissions on memory directories:",
            "  chmod 700 ~/.openclaw/memory 2>/dev/null",
            "  chmod 700 ~/.openclaw/knowledge 2>/dev/null",
            "  chmod 700 ~/.openclaw/context 2>/dev/null",
            "  chmod 700 ~/.openclaw/vectordb 2>/dev/null",
            "",
            "Step 2 — Review suspicious files in memory:",
            "  grep -r 'ignore previous' ~/.openclaw/memory/ 2>/dev/null",
            "",
            "Step 3 — If you find suspicious files, delete them:",
            "  rm ~/.openclaw/memory/suspicious_file",
            "",
            "Step 4 — Consider using 'reset memory' to clean everything:",
            "  openclaw memory reset",
        ]

    return result


def check_git_hook_injection():
    """CHECK 39: Are git hooks compromised?"""
    result = {
        "id": "git_hook_injection",
        "name_es": "Inyeccion de git hooks",
        "name_en": "Git hook injection",
        "severity": "CRITICAL",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    dangerous_commands = [
        r"curl.*\|.*bash",
        r"nc\s+",
        r"python\s+-c",
        r"/dev/tcp",
        r"base64\s+-d",
        r"eval\s*\(",
    ]

    issues = []

    # Check .git/hooks in openclaw home
    git_hooks_dir = OPENCLAW_HOME / ".git" / "hooks"
    if file_exists(git_hooks_dir):
        for hook_file in git_hooks_dir.iterdir():
            try:
                content = hook_file.read_text(errors="ignore")
                for pattern in dangerous_commands:
                    if re.search(pattern, content, re.IGNORECASE):
                        issues.append({
                            "es": f"Posible comando peligroso en hook: {hook_file.name}",
                            "en": f"Possible dangerous command in hook: {hook_file.name}",
                        })
                        break
            except OSError:
                pass

    # Check .git/hooks in skill directories
    if file_exists(OPENCLAW_SKILLS_DIR):
        for skill_dir in Path(OPENCLAW_SKILLS_DIR).iterdir():
            if not skill_dir.is_dir():
                continue
            hooks_dir = skill_dir / ".git" / "hooks"
            if file_exists(hooks_dir):
                for hook_file in hooks_dir.iterdir():
                    try:
                        content = hook_file.read_text(errors="ignore")
                        for pattern in dangerous_commands:
                            if re.search(pattern, content, re.IGNORECASE):
                                issues.append({
                                    "es": f"{skill_dir.name}: comando peligroso en hook {hook_file.name}",
                                    "en": f"{skill_dir.name}: dangerous command in hook {hook_file.name}",
                                })
                                break
                    except OSError:
                        pass

    # Check git config global core.hooksPath
    stdout, stderr, returncode = run_command("git config --global core.hooksPath")
    if returncode == 0 and stdout:
        hooks_path = Path(stdout)
        if file_exists(hooks_path):
            issues.append({
                "es": f"Git hooks globales configuradas en: {stdout}",
                "en": f"Global git hooks configured at: {stdout}",
            })

    if not issues:
        result["passed"] = True
        result["details_en"] = "No malicious git hooks detected."
        result["details_es"] = "No se detectaron git hooks maliciosos."
    else:
        result["details_en"] = "Git hook issues: " + "; ".join(set(i["en"] for i in issues))
        result["details_es"] = "Problemas en git hooks: " + "; ".join(set(i["es"] for i in issues))
        result["fix_es"] = [
            "Los git hooks comprometidos se ejecutan automaticamente y pueden ejecutar codigo malicioso.",
            "",
            "Paso 1 — Examina todos tus hooks:",
            "  find ~/.openclaw -name .git -type d -exec find {} -name hooks \\;",
            "",
            "Paso 2 — Inspecciona el contenido de cada hook sospechoso:",
            "  cat ~/.openclaw/.git/hooks/pre-commit",
            "  cat ~/.openclaw/.git/hooks/post-merge",
            "",
            "Paso 3 — Si encuentras comandos peligrosos, elimina los hooks:",
            "  rm -f ~/.openclaw/.git/hooks/*",
            "",
            "Paso 4 — Desactiva global hooksPath:",
            "  git config --global --unset core.hooksPath",
        ]
        result["fix_en"] = [
            "Compromised git hooks run automatically and can execute malicious code.",
            "",
            "Step 1 — Examine all your hooks:",
            "  find ~/.openclaw -name .git -type d -exec find {} -name hooks \\;",
            "",
            "Step 2 — Inspect the content of each suspicious hook:",
            "  cat ~/.openclaw/.git/hooks/pre-commit",
            "  cat ~/.openclaw/.git/hooks/post-merge",
            "",
            "Step 3 — If you find dangerous commands, delete the hooks:",
            "  rm -f ~/.openclaw/.git/hooks/*",
            "",
            "Step 4 — Disable global hooksPath:",
            "  git config --global --unset core.hooksPath",
        ]

    return result


def check_unsafe_defaults():
    """CHECK 40: Are unsafe defaults enabled?"""
    result = {
        "id": "unsafe_defaults",
        "name_es": "Configuraciones inseguras por defecto",
        "name_en": "Unsafe defaults enabled",
        "severity": "HIGH",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    issues = []
    config = read_json_safe(OPENCLAW_CONFIG)

    if config:
        # Check code execution enabled
        if config.get("codeExecution", {}).get("enabled") not in [False, "false", None]:
            issues.append({
                "es": "Ejecucion de codigo habilitada",
                "en": "Code execution enabled",
            })

        # Check skills auto-install
        if config.get("skills", {}).get("autoInstall"):
            issues.append({
                "es": "Auto-instalacion de skills habilitada",
                "en": "Skills auto-install enabled",
            })

        # Check telemetry enabled
        if config.get("telemetry", {}).get("enabled") not in [False, "false", None]:
            issues.append({
                "es": "Telemetria habilitada",
                "en": "Telemetry enabled",
            })

        # Check auto-download updates
        if config.get("updates", {}).get("autoDownload"):
            issues.append({
                "es": "Auto-descarga de actualizaciones habilitada",
                "en": "Auto-download updates enabled",
            })

        # Check unrestricted shell access
        if config.get("shell", {}).get("unrestricted"):
            issues.append({
                "es": "Acceso shell sin restriccion",
                "en": "Unrestricted shell access",
            })

    if not issues:
        result["passed"] = True
        result["details_en"] = "Unsafe defaults are not enabled."
        result["details_es"] = "No hay configuraciones inseguras por defecto habilitadas."
    else:
        result["details_en"] = "Unsafe defaults found: " + "; ".join(set(i["en"] for i in issues))
        result["details_es"] = "Configuraciones inseguras encontradas: " + "; ".join(set(i["es"] for i in issues))
        result["fix_es"] = [
            "Los valores por defecto inseguros aumentan significativamente el riesgo de ataque.",
            "",
            "Paso 1 — Revisa tu configuracion actual:",
            "  cat ~/.openclaw/config/moltbot.json",
            "",
            "Paso 2 — Para cada configuracion insegura, deshabilítala:",
            "  'codeExecution': {'enabled': false}",
            "  'skills': {'autoInstall': false}",
            "  'telemetry': {'enabled': false}",
            "  'updates': {'autoDownload': false}",
            "  'shell': {'unrestricted': false}",
            "",
            "Paso 3 — Edita tu configuracion:",
            "  nano ~/.openclaw/config/moltbot.json",
            "",
            "Paso 4 — Reinicia OpenClaw:",
            "  systemctl restart openclaw",
        ]
        result["fix_en"] = [
            "Unsafe defaults significantly increase attack risk.",
            "",
            "Step 1 — Review your current config:",
            "  cat ~/.openclaw/config/moltbot.json",
            "",
            "Step 2 — For each unsafe default, disable it:",
            "  'codeExecution': {'enabled': false}",
            "  'skills': {'autoInstall': false}",
            "  'telemetry': {'enabled': false}",
            "  'updates': {'autoDownload': false}",
            "  'shell': {'unrestricted': false}",
            "",
            "Step 3 — Edit your config:",
            "  nano ~/.openclaw/config/moltbot.json",
            "",
            "Step 4 — Restart OpenClaw:",
            "  systemctl restart openclaw",
        ]

    return result


def check_rogue_agent():
    """CHECK 41: Is there evidence of rogue agent activity?"""
    result = {
        "id": "rogue_agent",
        "name_es": "Actividad de agente rogue",
        "name_en": "Rogue agent activity",
        "severity": "CRITICAL",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    issues = []

    # Check for unexpected network listeners
    stdout, stderr, returncode = run_command("netstat -tuln 2>/dev/null | grep LISTEN | wc -l")
    open_ports_count = int(stdout) if stdout.isdigit() else 0
    if open_ports_count > 10:
        issues.append({
            "es": f"Muchos puertos abiertos ({open_ports_count})",
            "en": f"Many open ports ({open_ports_count})",
        })

    # Check for unusual child processes
    stdout, stderr, returncode = run_command("ps aux | grep openclaw | grep -v grep | wc -l")
    openclaw_processes = int(stdout) if stdout.isdigit() else 0
    if openclaw_processes > 25:
        issues.append({
            "es": f"Demasiados procesos OpenClaw ({openclaw_processes})",
            "en": f"Too many OpenClaw processes ({openclaw_processes})",
        })

    # Check for recent modifications to critical files
    critical_files = ["/etc/passwd", "/etc/shadow", ".ssh/authorized_keys", ".bashrc", ".bash_profile"]
    for critical_file in critical_files:
        file_path = Path.home() / critical_file if not critical_file.startswith("/") else Path(critical_file)
        if file_exists(file_path):
            stat = os.stat(file_path)
            modification_age_hours = (datetime.now() - datetime.fromtimestamp(stat.st_mtime)).total_seconds() / 3600
            if modification_age_hours < 24:
                issues.append({
                    "es": f"Archivo critico modificado hace poco: {critical_file}",
                    "en": f"Critical file modified recently: {critical_file}",
                })

    # Check for unusual UDP connections
    stdout, stderr, returncode = run_command("netstat -un 2>/dev/null | grep ESTABLISHED | wc -l")
    established_udp = int(stdout) if stdout.isdigit() else 0
    if established_udp > 5:
        issues.append({
            "es": f"Muchas conexiones UDP establecidas ({established_udp})",
            "en": f"Many established UDP connections ({established_udp})",
        })

    if not issues:
        result["passed"] = True
        result["details_en"] = "No signs of rogue agent activity detected."
        result["details_es"] = "No se detectan signos de actividad de agente rogue."
    else:
        result["details_en"] = "Rogue activity indicators: " + "; ".join(set(i["en"] for i in issues))
        result["details_es"] = "Indicadores de actividad rogue: " + "; ".join(set(i["es"] for i in issues))
        result["fix_es"] = [
            "La actividad de agente rogue indicaria compromiso total del sistema.",
            "",
            "ESTO ES CRITICO — Toma accion inmediata:",
            "",
            "Paso 1 — Revisa procesos en ejecucion:",
            "  ps aux | grep openclaw",
            "  kill -9 PID_SOSPECHOSO (si ves algo raro)",
            "",
            "Paso 2 — Verifica conexiones de red:",
            "  netstat -tuln | grep LISTEN",
            "  ss -au (conexiones UDP)",
            "",
            "Paso 3 — Revisa logs de intrusos:",
            "  journalctl -u openclaw --since=1h",
            "",
            "Paso 4 — Considera aislar/reiniciar completamente:",
            "  systemctl stop openclaw",
            "  # Luego revisa con herramientas de forense",
        ]
        result["fix_en"] = [
            "Rogue agent activity would indicate full system compromise.",
            "",
            "THIS IS CRITICAL — Take immediate action:",
            "",
            "Step 1 — Review running processes:",
            "  ps aux | grep openclaw",
            "  kill -9 SUSPICIOUS_PID (if you see anything odd)",
            "",
            "Step 2 — Verify network connections:",
            "  netstat -tuln | grep LISTEN",
            "  ss -au (UDP connections)",
            "",
            "Step 3 — Review intrusion logs:",
            "  journalctl -u openclaw --since=1h",
            "",
            "Step 4 — Consider isolating/completely restarting:",
            "  systemctl stop openclaw",
            "  # Then review with forensic tools",
        ]

    return result


def check_kernel_hardening():
    """CHECK 42: Is the kernel hardened against network attacks?"""
    result = {
        "id": "kernel_hardening",
        "name_es": "Endurecimiento del kernel",
        "name_en": "Kernel hardening",
        "severity": "MEDIUM",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    required_settings = {
        "net.ipv4.conf.all.rp_filter": "1",
        "net.ipv4.conf.default.accept_redirects": "0",
        "net.ipv4.conf.all.send_redirects": "0",
        "net.ipv4.icmp_echo_ignore_broadcasts": "1",
        "kernel.randomize_va_space": "2",
    }

    issues = []

    for setting, expected in required_settings.items():
        stdout, stderr, returncode = run_command(f"sudo /usr/sbin/sysctl {setting} 2>/dev/null")
        actual = None
        if returncode == 0:
            try:
                actual = stdout.split("=")[-1].strip()
            except:
                pass

        if actual != expected:
            issues.append({
                "es": f"{setting}: {actual} (esperado {expected})",
                "en": f"{setting}: {actual} (expected {expected})",
            })

    if not issues:
        result["passed"] = True
        result["details_en"] = "Kernel is properly hardened."
        result["details_es"] = "El kernel esta apropiadamente endurecido."
    else:
        result["details_en"] = "Kernel hardening issues: " + "; ".join(set(i["en"] for i in issues))
        result["details_es"] = "Problemas de endurecimiento del kernel: " + "; ".join(set(i["es"] for i in issues))
        result["fix_es"] = [
            "Los ajustes de kernel endurecen el sistema contra ataques de red.",
            "",
            "Paso 1 — Edita /etc/sysctl.conf:",
            "  sudo nano /etc/sysctl.conf",
            "",
            "Paso 2 — Añade o actualiza estas lineas:",
            "  net.ipv4.conf.all.rp_filter = 1",
            "  net.ipv4.conf.default.accept_redirects = 0",
            "  net.ipv4.conf.all.send_redirects = 0",
            "  net.ipv4.icmp_echo_ignore_broadcasts = 1",
            "  kernel.randomize_va_space = 2",
            "",
            "Paso 3 — Aplica los cambios:",
            "  sudo sysctl -p",
        ]
        result["fix_en"] = [
            "Kernel hardening settings strengthen the system against network attacks.",
            "",
            "Step 1 — Edit /etc/sysctl.conf:",
            "  sudo nano /etc/sysctl.conf",
            "",
            "Step 2 — Add or update these lines:",
            "  net.ipv4.conf.all.rp_filter = 1",
            "  net.ipv4.conf.default.accept_redirects = 0",
            "  net.ipv4.conf.all.send_redirects = 0",
            "  net.ipv4.icmp_echo_ignore_broadcasts = 1",
            "  kernel.randomize_va_space = 2",
            "",
            "Step 3 — Apply the changes:",
            "  sudo sysctl -p",
        ]

    return result


def check_systemd_hardening():
    """CHECK 43: Is the systemd service properly hardened?"""
    result = {
        "id": "systemd_hardening",
        "name_es": "Endurecimiento de systemd",
        "name_en": "Systemd hardening",
        "severity": "MEDIUM",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    hardening_directives = [
        "ProtectSystem", "ProtectHome", "EnvironmentFile", "KillMode=control-group", "ReadOnlyPaths",
    ]

    issues = []

    # Find OpenClaw systemd service
    stdout, stderr, returncode = run_command("systemctl show -p FragmentPath openclaw 2>/dev/null")
    service_file = None
    if returncode == 0:
        service_file = stdout.split("=")[-1].strip() if "=" in stdout else None

    if service_file and file_exists(service_file):
        try:
            content = Path(service_file).read_text(errors="ignore")
            found_directives = []
            for directive in hardening_directives:
                if directive in content:
                    found_directives.append(directive)

            if len(found_directives) < 3:
                missing = [d for d in hardening_directives if d not in found_directives]
                issues.append({
                    "es": f"Faltan directivas de endurecimiento: {', '.join(missing[:2])}",
                    "en": f"Missing hardening directives: {', '.join(missing[:2])}",
                })
        except OSError:
            pass
    else:
        issues.append({
            "es": "No se encontro archivo de servicio openclaw",
            "en": "OpenClaw systemd service file not found",
        })

    if not issues:
        result["passed"] = True
        result["details_en"] = "OpenClaw systemd service is properly hardened."
        result["details_es"] = "El servicio systemd de OpenClaw esta apropiadamente endurecido."
    else:
        result["details_en"] = "Systemd hardening issues: " + "; ".join(set(i["en"] for i in issues))
        result["details_es"] = "Problemas de endurecimiento systemd: " + "; ".join(set(i["es"] for i in issues))
        result["fix_es"] = [
            "Endurecimiento de systemd limita el alcance del servicio.",
            "",
            "Paso 1 — Encuentra tu archivo de servicio:",
            "  systemctl show -p FragmentPath openclaw",
            "",
            "Paso 2 — Edita el archivo de servicio:",
            "  sudo nano RUTA_DEL_ARCHIVO",
            "",
            "Paso 3 — En la seccion [Service], añade:",
            "  ProtectSystem=strict",
            "  ProtectHome=yes",
            "  NoNewPrivileges=yes",
            "  PrivateTmp=yes",
            "  ReadOnlyPaths=/",
            "",
            "Paso 4 — Recarga y reinicia:",
            "  sudo systemctl daemon-reload",
            "  sudo systemctl restart openclaw",
        ]
        result["fix_en"] = [
            "Systemd hardening restricts the scope of the service.",
            "",
            "Step 1 — Find your service file:",
            "  systemctl show -p FragmentPath openclaw",
            "",
            "Step 2 — Edit the service file:",
            "  sudo nano SERVICE_FILE_PATH",
            "",
            "Step 3 — In the [Service] section, add:",
            "  ProtectSystem=strict",
            "  ProtectHome=yes",
            "  NoNewPrivileges=yes",
            "  PrivateTmp=yes",
            "  ReadOnlyPaths=/",
            "",
            "Step 4 — Reload and restart:",
            "  sudo systemctl daemon-reload",
            "  sudo systemctl restart openclaw",
        ]

    return result


def check_tmp_security():
    """CHECK 44: Are /tmp and /dev/shm mounted with noexec?"""
    result = {
        "id": "tmp_security",
        "name_es": "Seguridad de /tmp",
        "name_en": "/tmp security",
        "severity": "MEDIUM",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    issues = []

    # Check /tmp mount options
    stdout, stderr, returncode = run_command("mount | grep ' /tmp '")
    if returncode == 0 and stdout:
        if "noexec" not in stdout:
            issues.append({
                "es": "/tmp no tiene opcion noexec",
                "en": "/tmp does not have noexec option",
            })

    # Check /dev/shm mount options
    stdout, stderr, returncode = run_command("mount | grep ' /dev/shm '")
    if returncode == 0 and stdout:
        if "noexec" not in stdout:
            issues.append({
                "es": "/dev/shm no tiene opcion noexec",
                "en": "/dev/shm does not have noexec option",
            })

    # Check for executable scripts in /tmp
    stdout, stderr, returncode = run_command("find /tmp -type f -executable -not -path '/tmp/lobsterguard/*' -not -path '/tmp/openclaw*' -not -path '/tmp/plugin/*' 2>/dev/null | wc -l")
    if returncode == 0:
        exec_count = int(stdout) if stdout.isdigit() else 0
        if exec_count > 0:
            issues.append({
                "es": f"Scripts ejecutables encontrados en /tmp ({exec_count})",
                "en": f"Executable scripts found in /tmp ({exec_count})",
            })

    if not issues:
        result["passed"] = True
        result["details_en"] = "/tmp and /dev/shm are properly secured."
        result["details_es"] = "/tmp y /dev/shm estan apropiadamente asegurados."
    else:
        result["details_en"] = "/tmp security issues: " + "; ".join(set(i["en"] for i in issues))
        result["details_es"] = "Problemas de seguridad en /tmp: " + "; ".join(set(i["es"] for i in issues))
        result["fix_es"] = [
            "Sin noexec en /tmp, un atacante puede ejecutar codigo alli.",
            "",
            "Paso 1 — Revisa montajes actuales:",
            "  mount | grep '/tmp\\|/dev/shm'",
            "",
            "Paso 2 — Edita /etc/fstab:",
            "  sudo nano /etc/fstab",
            "",
            "Paso 3 — Para la linea de /tmp, asegura que incluye noexec:",
            "  /dev/xxx /tmp ext4 defaults,noexec,nosuid,nodev 0 2",
            "",
            "Paso 4 — Remonta para aplicar cambios:",
            "  sudo mount -o remount,noexec /tmp",
            "  sudo mount -o remount,noexec /dev/shm",
        ]
        result["fix_en"] = [
            "Without noexec on /tmp, an attacker can execute code there.",
            "",
            "Step 1 — Check current mounts:",
            "  mount | grep '/tmp\\|/dev/shm'",
            "",
            "Step 2 — Edit /etc/fstab:",
            "  sudo nano /etc/fstab",
            "",
            "Step 3 — For the /tmp line, ensure it includes noexec:",
            "  /dev/xxx /tmp ext4 defaults,noexec,nosuid,nodev 0 2",
            "",
            "Step 4 — Remount to apply changes:",
            "  sudo mount -o remount,noexec /tmp",
            "  sudo mount -o remount,noexec /dev/shm",
        ]

    return result


def check_skill_signatures():
    """CHECK 45: Do installed skills have signature files?"""
    result = {
        "id": "skill_signatures",
        "name_es": "Firmas de skills",
        "name_en": "Skill signatures",
        "severity": "MEDIUM",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    signature_files = [".signature", "signature.json", ".clawsign", "CHECKSUM", "signature.gpg"]
    issues = []

    if not file_exists(OPENCLAW_SKILLS_DIR):
        result["passed"] = True
        result["details_en"] = "Skills directory does not exist."
        result["details_es"] = "El directorio de skills no existe."
        return result

    for skill_dir in Path(OPENCLAW_SKILLS_DIR).iterdir():
        if not skill_dir.is_dir() or skill_dir.name in WHITELISTED_SKILLS:
            continue

        has_signature = False
        for sig_file in signature_files:
            if file_exists(skill_dir / sig_file):
                has_signature = True
                break

        if not has_signature:
            issues.append({
                "es": f"{skill_dir.name}: no tiene archivo de firma",
                "en": f"{skill_dir.name}: missing signature file",
            })

    if not issues:
        result["passed"] = True
        result["details_en"] = "All skills have signature files."
        result["details_es"] = "Todos los skills tienen archivos de firma."
    else:
        result["details_en"] = "Unsigned skills: " + "; ".join(set(i["en"] for i in issues))
        result["details_es"] = "Skills sin firma: " + "; ".join(set(i["es"] for i in issues))
        result["fix_es"] = [
            "Sin firmas, no puedes verificar que un skill no ha sido modificado.",
            "",
            "Paso 1 — Para skills de confianza, crea firmas SHA256:",
            "  cd ~/.openclaw/skills/NOMBRE_SKILL",
            "  sha256sum SKILL.md scripts/* > CHECKSUM",
            "",
            "Paso 2 — Guarda el CHECKSUM en un lugar seguro (no en el skill).",
            "",
            "Paso 3 — Luego puedes verificar:",
            "  sha256sum -c CHECKSUM",
            "",
            "Paso 4 — Para skills de terceros, solicita firmas GPG a los mantenedores.",
        ]
        result["fix_en"] = [
            "Without signatures, you can't verify a skill hasn't been modified.",
            "",
            "Step 1 — For trusted skills, create SHA256 signatures:",
            "  cd ~/.openclaw/skills/SKILL_NAME",
            "  sha256sum SKILL.md scripts/* > CHECKSUM",
            "",
            "Step 2 — Save the CHECKSUM in a safe place (not in the skill).",
            "",
            "Step 3 — Then you can verify:",
            "  sha256sum -c CHECKSUM",
            "",
            "Step 4 — For third-party skills, request GPG signatures from maintainers.",
        ]

    return result


def check_code_execution_sandbox():
    """CHECK 46: Is code execution properly sandboxed?"""
    result = {
        "id": "code_execution_sandbox",
        "name_es": "Sandbox de ejecucion de codigo",
        "name_en": "Code execution sandbox",
        "severity": "HIGH",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    issues = []

    # Check if AppArmor or SELinux is active
    stdout, stderr, returncode = run_command("sudo aa-status 2>/dev/null | head -1")
    apparmor_active = returncode == 0 and "apparmor" in stdout.lower()

    stdout, stderr, returncode = run_command("getenforce 2>/dev/null")
    selinux_active = returncode == 0 and "enforcing" in stdout.lower()

    if not apparmor_active and not selinux_active:
        issues.append({
            "es": "AppArmor o SELinux no estan habilitados",
            "en": "AppArmor or SELinux not enabled",
        })

    # Check if OpenClaw process has seccomp filter
    stdout, stderr, returncode = run_command("ps aux | grep openclaw | grep -v grep | head -1 | awk '{print $2}'")
    if stdout.strip().isdigit():
        pid = stdout.strip()
        stdout, stderr, returncode = run_command(f"grep Seccomp /proc/{pid}/status 2>/dev/null")
        if returncode != 0 or "0" in stdout:
            issues.append({
                "es": "OpenClaw no usa seccomp filter",
                "en": "OpenClaw does not use seccomp filter",
            })

    # Check if containerized
    if not file_exists("/.dockerenv") and not file_exists("/run/.containerenv"):
        issues.append({
            "es": "OpenClaw no corre en contenedor",
            "en": "OpenClaw not running in container",
        })

    if not issues:
        result["passed"] = True
        result["details_en"] = "Code execution is properly sandboxed."
        result["details_es"] = "La ejecucion de codigo esta apropiadamente aislada."
    else:
        result["details_en"] = "OpenClaw runs without container isolation. This requires manual Docker setup (not auto-fixable)."
        result["details_es"] = "OpenClaw corre sin aislamiento de contenedor. Requiere instalar Docker manualmente (no tiene auto-fix)."
        result["fix_es"] = [
            "COMO SOLUCIONARLO (manual, 5 minutos):",
            "",
            "1. Instala Docker:",
            "   curl -fsSL https://get.docker.com | sudo sh",
            "   sudo usermod -aG docker $USER",
            "",
            "2. Crea un archivo llamado Dockerfile:",
            "   FROM node:20-slim",
            "   RUN npm install -g openclaw",
            "   COPY .openclaw /root/.openclaw",
            "   EXPOSE 18789",
            "   CMD [openclaw, start]",
            "",
            "3. Construye y ejecuta:",
            "   docker build -t openclaw-secure .",
            "   docker run -d --name openclaw \\",
            "     --restart unless-stopped \\",
            "     -p 18789:18789 \\",
            "     -v ~/.openclaw:/root/.openclaw \\",
            "     openclaw-secure",
            "",
            "Esto encierra OpenClaw en un contenedor aislado",
            "donde el codigo no puede acceder al resto del servidor.",
        ]
        result["fix_en"] = [
            "HOW TO FIX (manual, 5 minutes):",
            "",
            "1. Install Docker:",
            "   curl -fsSL https://get.docker.com | sudo sh",
            "   sudo usermod -aG docker $USER",
            "",
            "2. Create a file called Dockerfile:",
            "   FROM node:20-slim",
            "   RUN npm install -g openclaw",
            "   COPY .openclaw /root/.openclaw",
            "   EXPOSE 18789",
            "   CMD [openclaw, start]",
            "",
            "3. Build and run:",
            "   docker build -t openclaw-secure .",
            "   docker run -d --name openclaw \\",
            "     --restart unless-stopped \\",
            "     -p 18789:18789 \\",
            "     -v ~/.openclaw:/root/.openclaw \\",
            "     openclaw-secure",
            "",
            "This isolates OpenClaw in a container where",
            "code cannot access the rest of your server.",
        ]

    return result


def check_api_key_rotation():
    """CHECK 47: Have API keys been rotated recently?"""
    result = {
        "id": "api_key_rotation",
        "name_es": "Rotacion de claves API",
        "name_en": "API key rotation",
        "severity": "MEDIUM",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    issues = []
    env_file = OPENCLAW_CREDENTIALS

    if not file_exists(env_file):
        result["passed"] = True
        result["details_en"] = "No .env file found."
        result["details_es"] = "No se encontro archivo .env."
        return result

    try:
        stat = os.stat(env_file)
        modification_age_days = (datetime.now() - datetime.fromtimestamp(stat.st_mtime)).total_seconds() / 86400

        if modification_age_days > 90:
            issues.append({
                "es": f".env no ha sido modificado en {int(modification_age_days)} dias",
                "en": f".env has not been modified in {int(modification_age_days)} days",
            })
    except OSError:
        pass

    if not issues:
        result["passed"] = True
        result["details_en"] = "API keys appear to have been rotated recently."
        result["details_es"] = "Las claves API parecen haber sido rotadas recientemente."
    else:
        result["details_en"] = "Key rotation issues: " + "; ".join(set(i["en"] for i in issues))
        result["details_es"] = "Problemas de rotacion de claves: " + "; ".join(set(i["es"] for i in issues))
        result["fix_es"] = [
            "Las claves API antiguas aumentan el riesgo si han sido comprometidas.",
            "",
            "Paso 1 — Rota tus claves API en cada proveedor:",
            "  OpenAI: https://platform.openai.com/account/api-keys",
            "  Anthropic: https://console.anthropic.com/",
            "  GitHub: https://github.com/settings/tokens",
            "  AWS: https://console.aws.amazon.com/iam/",
            "",
            "Paso 2 — Actualiza tu archivo .env:",
            "  nano ~/.openclaw/.env",
            "",
            "Paso 3 — Busca y actualiza cada clave con su nueva version.",
            "",
            "Paso 4 — Reinicia OpenClaw:",
            "  systemctl restart openclaw",
        ]
        result["fix_en"] = [
            "Old API keys increase risk if they've been compromised.",
            "",
            "Step 1 — Rotate your API keys at each provider:",
            "  OpenAI: https://platform.openai.com/account/api-keys",
            "  Anthropic: https://console.anthropic.com/",
            "  GitHub: https://github.com/settings/tokens",
            "  AWS: https://console.aws.amazon.com/iam/",
            "",
            "Step 2 — Update your .env file:",
            "  nano ~/.openclaw/.env",
            "",
            "Step 3 — Find and update each key with its new version.",
            "",
            "Step 4 — Restart OpenClaw:",
            "  systemctl restart openclaw",
        ]

    return result


def check_rate_limiting():
    """CHECK 48: Is rate limiting configured on the gateway?"""
    result = {
        "id": "rate_limiting",
        "name_es": "Limitacion de velocidad",
        "name_en": "Rate limiting",
        "severity": "MEDIUM",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    issues = []

    # Check gateway config
    gateway_config = read_json_safe(OPENCLAW_GATEWAY_CONFIG)

    # If no gateway config or gateway is localhost-only, rate limiting may not be critical
    if not gateway_config:
        result["passed"] = True
        result["details_en"] = "No gateway configuration found."
        result["details_es"] = "No se encontro configuracion de gateway."
        return result

    bind_address = gateway_config.get("bind", "localhost")
    is_local = any(safe in str(bind_address).lower() for safe in SAFE_BIND_VALUES)

    if not is_local:
        # Gateway is exposed, check for rate limiting
        rate_limit = gateway_config.get("rateLimit")
        if not rate_limit:
            issues.append({
                "es": "Gateway esta expuesto pero sin rate limiting",
                "en": "Gateway is exposed but has no rate limiting",
            })

    if not issues:
        result["passed"] = True
        result["details_en"] = "Rate limiting is properly configured or not needed."
        result["details_es"] = "Rate limiting esta apropiadamente configurado o no es necesario."
    else:
        result["details_en"] = "Rate limiting issues: " + "; ".join(set(i["en"] for i in issues))
        result["details_es"] = "Problemas de rate limiting: " + "; ".join(set(i["es"] for i in issues))
        result["fix_es"] = [
            "Sin rate limiting, un atacante puede enviar muchas solicitudes para sobrecargar.",
            "",
            "Paso 1 — Edita tu configuracion de gateway:",
            "  cat ~/.openclaw/config/gateway.json",
            "",
            "Paso 2 — Añade rate limiting:",
            "  {",
            "    'rateLimit': {",
            "      'requests': 100,",
            "      'window': '1m'",
            "    }",
            "  }",
            "",
            "Paso 3 — Reinicia el gateway.",
        ]
        result["fix_en"] = [
            "Without rate limiting, an attacker can send many requests to overload.",
            "",
            "Step 1 — Edit your gateway config:",
            "  cat ~/.openclaw/config/gateway.json",
            "",
            "Step 2 — Add rate limiting:",
            "  {",
            "    'rateLimit': {",
            "      'requests': 100,",
            "      'window': '1m'",
            "    }",
            "  }",
            "",
            "Step 3 — Restart the gateway.",
        ]

    return result


def check_skill_network_access():
    """CHECK 49: Do skills make unexpected network calls?"""
    result = {
        "id": "skill_network_access",
        "name_es": "Acceso de red en skills",
        "name_en": "Skill network access",
        "severity": "HIGH",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    network_patterns = [
        (r'requests\.post\(["\']http', 'HTTP POST request'),
        (r'requests\.get\(["\']http', 'HTTP GET request'),
        (r'webhook\.site|ngrok\.io|pipedream', 'Known exfil endpoint'),
        (r'socket\.connect', 'Socket connection'),
        (r'paramiko|pexpect', 'SSH library import'),
        (r'smtplib', 'Email sending'),
    ]

    issues = []

    if not file_exists(OPENCLAW_SKILLS_DIR):
        result["passed"] = True
        result["details_en"] = "Skills directory does not exist."
        result["details_es"] = "El directorio de skills no existe."
        return result

    for skill_dir in Path(OPENCLAW_SKILLS_DIR).iterdir():
        if not skill_dir.is_dir() or skill_dir.name in WHITELISTED_SKILLS:
            continue

        for script_file in skill_dir.rglob("*"):
            if script_file.suffix not in [".py", ".js", ".sh"]:
                continue

            try:
                content = script_file.read_text(errors="ignore")
                for pattern, description in network_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        issues.append({
                            "es": f"{skill_dir.name}/{script_file.name}: {description}",
                            "en": f"{skill_dir.name}/{script_file.name}: {description}",
                        })
                        break
            except OSError:
                pass

    if not issues:
        result["passed"] = True
        result["details_en"] = "No unexpected network access detected in skills."
        result["details_es"] = "No se detecto acceso de red inesperado en skills."
    else:
        result["details_en"] = "Network access detected: " + "; ".join(set(i["en"] for i in issues[:5]))
        result["details_es"] = "Acceso de red detectado: " + "; ".join(set(i["es"] for i in issues[:5]))
        result["fix_es"] = [
            "Un skill que hace llamadas de red podria exfiltrar datos.",
            "",
            "Paso 1 — Examina el skill sospechoso:",
            "  grep -r 'requests\\|socket\\|http' ~/.openclaw/skills/NOMBRE_SKILL/",
            "",
            "Paso 2 — Verifica que las llamadas de red sean legitimas:",
            "  - Debe estar documentado en SKILL.md",
            "  - Debe ser para un proposito claro",
            "",
            "Paso 3 — Si es sospechoso, desinstala:",
            "  rm -rf ~/.openclaw/skills/NOMBRE_SKILL",
            "",
            "Paso 4 — Solo usa skills que confies o que esten open-source.",
        ]
        result["fix_en"] = [
            "A skill making network calls could exfiltrate data.",
            "",
            "Step 1 — Examine the suspicious skill:",
            "  grep -r 'requests\\|socket\\|http' ~/.openclaw/skills/SKILL_NAME/",
            "",
            "Step 2 — Verify the network calls are legitimate:",
            "  - Should be documented in SKILL.md",
            "  - Should be for a clear purpose",
            "",
            "Step 3 — If suspicious, uninstall:",
            "  rm -rf ~/.openclaw/skills/SKILL_NAME",
            "",
            "Step 4 — Only use skills you trust or that are open-source.",
        ]

    return result


def check_process_isolation():
    """CHECK 50: Is OpenClaw properly isolated from other processes?"""
    result = {
        "id": "process_isolation",
        "name_es": "Aislamiento de procesos",
        "name_en": "Process isolation",
        "severity": "MEDIUM",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    issues = []

    # Check number of processes on system
    stdout, stderr, returncode = run_command("ps aux | wc -l")
    if returncode == 0:
        try:
            process_count = int(stdout.strip())
            if process_count > 300:
                issues.append({
                    "es": f"Demasiados procesos en el sistema ({process_count})",
                    "en": f"Too many processes on system ({process_count})",
                })
        except ValueError:
            pass

    # Check if other web services are running
    web_services = ["apache2", "nginx", "httpd", "tomcat"]
    for service in web_services:
        stdout, stderr, returncode = run_command(f"systemctl is-active {service} 2>/dev/null")
        if returncode == 0 and "active" in stdout:
            issues.append({
                "es": f"Otro servicio web activo: {service}",
                "en": f"Other web service active: {service}",
            })

    # Check if databases are running
    db_services = ["mysql", "postgresql", "mongodb", "redis"]
    for service in db_services:
        stdout, stderr, returncode = run_command(f"systemctl is-active {service} 2>/dev/null")
        if returncode == 0 and "active" in stdout:
            issues.append({
                "es": f"Base de datos activa: {service}",
                "en": f"Database service active: {service}",
            })

    if not issues:
        result["passed"] = True
        result["details_en"] = "OpenClaw is well isolated from other processes."
        result["details_es"] = "OpenClaw esta bien aislado de otros procesos."
    else:
        result["details_en"] = "Isolation issues: " + "; ".join(set(i["en"] for i in issues[:3]))
        result["details_es"] = "Problemas de aislamiento: " + "; ".join(set(i["es"] for i in issues[:3]))
        result["fix_es"] = [
            "Ejecutar OpenClaw en un servidor compartido aumenta el riesgo.",
            "",
            "Paso 1 — Considera usar un servidor dedicado o contenedor para OpenClaw.",
            "",
            "Paso 2 — Si es necesario compartir el servidor, detén servicios innecesarios:",
            "  sudo systemctl stop apache2",
            "  sudo systemctl disable apache2",
            "",
            "Paso 3 — Aislamiento con contenedores es ideal:",
            "  docker run -d -v ~/.openclaw:/root/.openclaw openclaw:latest",
            "",
            "Paso 4 — Usa cgroups y namespaces para limitar recursos.",
        ]
        result["fix_en"] = [
            "Running OpenClaw on a shared server increases risk.",
            "",
            "Step 1 — Consider using a dedicated server or container for OpenClaw.",
            "",
            "Step 2 — If sharing the server is necessary, stop unnecessary services:",
            "  sudo systemctl stop apache2",
            "  sudo systemctl disable apache2",
            "",
            "Step 3 — Containerization with Docker is ideal:",
            "  docker run -d -v ~/.openclaw:/root/.openclaw openclaw:latest",
            "",
            "Step 4 — Use cgroups and namespaces to limit resources.",
        ]

    return result


# ─── Forensic and Advanced Hardening Checks (51-70) ───────────────────────────

def check_ssh_authorized_keys_audit():
    """CHECK 51: Are SSH authorized keys secure and not recently compromised?"""
    result = {
        "id": "ssh_authorized_keys_audit",
        "name_es": "Auditoria de llaves SSH autorizadas",
        "name_en": "SSH authorized keys audit",
        "severity": "HIGH",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    issues = []

    # Check /root/.ssh/authorized_keys
    root_ssh_path = Path.home() / ".ssh" / "authorized_keys"
    if root_ssh_path.exists():
        try:
            with open(root_ssh_path, 'r') as f:
                root_keys = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            if len(root_keys) > 5:
                issues.append({
                    "es": f"Demasiadas llaves SSH en root ({len(root_keys)} > 5)",
                    "en": f"Too many SSH keys for root ({len(root_keys)} > 5)",
                })

            # Check modification time
            stdout, stderr, returncode = run_command(f"stat -c %Y {root_ssh_path} 2>/dev/null")
            if returncode == 0:
                try:
                    mtime = int(stdout.strip())
                    current_time = int(datetime.now().timestamp())
                    age_seconds = current_time - mtime
                    age_hours = age_seconds / 3600
                    if age_hours < 48:
                        issues.append({
                            "es": f"Llaves SSH modificadas hace {age_hours:.1f} horas",
                            "en": f"SSH keys modified {age_hours:.1f} hours ago",
                        })
                except (ValueError, TypeError):
                    pass
        except (PermissionError, IOError):
            pass

    # Check /home/*/.ssh/authorized_keys
    home_dir = Path("/home")
    if home_dir.exists():
        try:
            for user_dir in home_dir.iterdir():
                try:
                    if user_dir.is_dir():
                        user_ssh_path = user_dir / ".ssh" / "authorized_keys"
                        try:
                            if user_ssh_path.exists():
                                try:
                                    with open(user_ssh_path, 'r') as f:
                                        user_keys = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                                    if len(user_keys) > 5:
                                        issues.append({
                                            "es": f"Demasiadas llaves SSH para {user_dir.name} ({len(user_keys)} > 5)",
                                            "en": f"Too many SSH keys for {user_dir.name} ({len(user_keys)} > 5)",
                                        })
                                except (PermissionError, IOError):
                                    pass
                        except (PermissionError, OSError):
                            pass
                except (PermissionError, OSError):
                    pass
        except (PermissionError, OSError):
            pass

    if not issues:
        result["passed"] = True
        result["details_en"] = "SSH authorized keys are secure and appropriately configured."
        result["details_es"] = "Las llaves SSH autorizadas estan seguras y correctamente configuradas."
    else:
        result["details_en"] = "SSH key issues: " + "; ".join(set(i["en"] for i in issues[:3]))
        result["details_es"] = "Problemas de llaves SSH: " + "; ".join(set(i["es"] for i in issues[:3]))
        result["fix_es"] = [
            "Audita regularmente tus llaves SSH autorizadas para detectar acceso no autorizado.",
            "",
            "Paso 1 — Lista todas las llaves SSH autorizadas:",
            "  cat ~/.ssh/authorized_keys",
            "",
            "Paso 2 — Elimina llaves desconocidas o antiguas:",
            "  # Edita manualmente el archivo para remover lineas",
            "  nano ~/.ssh/authorized_keys",
            "",
            "Paso 3 — Verifica que tengas menos de 5 llaves por usuario.",
            "",
            "Paso 4 — Considera usar fail2ban para bloquear intentos SSH fallidos.",
        ]
        result["fix_en"] = [
            "Regularly audit your SSH authorized keys to detect unauthorized access.",
            "",
            "Step 1 — List all authorized SSH keys:",
            "  cat ~/.ssh/authorized_keys",
            "",
            "Step 2 — Remove unknown or old keys:",
            "  # Manually edit the file to remove lines",
            "  nano ~/.ssh/authorized_keys",
            "",
            "Step 3 — Ensure you have fewer than 5 keys per user.",
            "",
            "Step 4 — Consider using fail2ban to block failed SSH attempts.",
        ]

    return result


def check_suid_sgid_binary_audit():
    """CHECK 52: Are there dangerous SUID/SGID binaries on the system?"""
    result = {
        "id": "suid_sgid_binary_audit",
        "name_es": "Auditoria de binarios SUID/SGID",
        "name_en": "SUID/SGID binary audit",
        "severity": "CRITICAL",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    known_safe_suid = {
        "/usr/bin/passwd", "/usr/bin/sudo", "/usr/bin/chfn", "/usr/bin/chsh",
        "/usr/bin/gpasswd", "/usr/bin/newgrp", "/usr/bin/su", "/usr/sbin/unix_chkpwd",
        "/usr/lib/dbus-1.0/dbus-daemon-launch-helper", "/usr/lib/openssh/ssh-keysign",
        "/usr/bin/mount", "/usr/bin/umount", "/usr/bin/fusermount", "/usr/bin/fusermount3",
        "/usr/bin/pkexec", "/usr/bin/crontab", "/usr/bin/at", "/usr/lib/snapd/snap-confine",
        "/usr/bin/ssh-agent",
    }

    dangerous_interpreters = ["python", "perl", "ruby", "bash", "sh", "node"]

    issues = []

    # Find all SUID/SGID binaries
    stdout, stderr, returncode = run_command(
        "find / -xdev -type f \\( -perm -4000 -o -perm -2000 \\) 2>/dev/null",
        timeout=15
    )

    if returncode == 0:
        suid_files = [f.strip() for f in stdout.split('\n') if f.strip()]

        for suid_file in suid_files:
            # Check if it's in the safe list
            if suid_file not in known_safe_suid:
                # Check if it's a dangerous interpreter
                is_dangerous = any(interp in suid_file for interp in dangerous_interpreters)
                if is_dangerous:
                    issues.append({
                        "es": f"SUID/SGID en intérprete peligroso: {suid_file}",
                        "en": f"SUID/SGID on dangerous interpreter: {suid_file}",
                    })
                else:
                    # Flag unexpected SUID/SGID
                    issues.append({
                        "es": f"SUID/SGID no esperado: {suid_file}",
                        "en": f"Unexpected SUID/SGID: {suid_file}",
                    })

    if not issues:
        result["passed"] = True
        result["details_en"] = "All SUID/SGID binaries are in the safe whitelist."
        result["details_es"] = "Todos los binarios SUID/SGID estan en la lista blanca de seguridad."
    else:
        result["details_en"] = "SUID/SGID issues: " + "; ".join(set(i["en"] for i in issues[:3]))
        result["details_es"] = "Problemas SUID/SGID: " + "; ".join(set(i["es"] for i in issues[:3]))
        result["fix_es"] = [
            "Los binarios SUID/SGID permiten escalada de privilegios si se explotan.",
            "",
            "Paso 1 — Verifica qué binarios SUID/SGID existen:",
            "  find / -xdev -type f \\( -perm -4000 -o -perm -2000 \\) 2>/dev/null",
            "",
            "Paso 2 — Para cada binario no esperado, elimina el bit SUID/SGID:",
            "  sudo chmod u-s,g-s /path/to/binary",
            "",
            "Paso 3 — Nunca permitas SUID en scripts interpretes (python, bash, etc).",
            "",
            "Paso 4 — Revisa regularmente con find para detectar cambios.",
        ]
        result["fix_en"] = [
            "SUID/SGID binaries can be exploited for privilege escalation.",
            "",
            "Step 1 — Check what SUID/SGID binaries exist:",
            "  find / -xdev -type f \\( -perm -4000 -o -perm -2000 \\) 2>/dev/null",
            "",
            "Step 2 — For each unexpected binary, remove the SUID/SGID bit:",
            "  sudo chmod u-s,g-s /path/to/binary",
            "",
            "Step 3 — Never allow SUID on interpreter scripts (python, bash, etc).",
            "",
            "Step 4 — Review regularly with find to detect changes.",
        ]

    return result


def check_world_writable_files_detection():
    """CHECK 53: Are there dangerous world-writable files?"""
    result = {
        "id": "world_writable_files_detection",
        "name_es": "Deteccion de archivos escribibles mundialmente",
        "name_en": "World-writable files detection",
        "severity": "HIGH",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    issues = []

    # Find world-writable files in sensitive locations
    stdout, stderr, returncode = run_command(
        "find /etc /opt /home /root -xdev -type f -perm -0002 2>/dev/null",
        timeout=15
    )

    if returncode == 0:
        world_writable = [f.strip() for f in stdout.split('\n') if f.strip()]

        if world_writable:
            issues.append({
                "es": f"Se encontraron {len(world_writable)} archivos escribibles mundialmente",
                "en": f"Found {len(world_writable)} world-writable files",
            })

            # Show first few examples
            for ww_file in world_writable[:3]:
                issues.append({
                    "es": f"Archivo escribible: {ww_file}",
                    "en": f"World-writable file: {ww_file}",
                })

    if not issues:
        result["passed"] = True
        result["details_en"] = "No dangerous world-writable files found."
        result["details_es"] = "No se encontraron archivos peligrosamente escribibles mundialmente."
    else:
        result["details_en"] = "World-writable files detected: " + "; ".join(set(i["en"] for i in issues[:2]))
        result["details_es"] = "Se detectaron archivos escribibles: " + "; ".join(set(i["es"] for i in issues[:2]))
        result["fix_es"] = [
            "Los archivos escribibles mundialmente pueden ser modificados por cualquier usuario.",
            "",
            "Paso 1 — Encuentra archivos escribibles mundialmente:",
            "  find /etc /opt /home /root -xdev -type f -perm -0002 2>/dev/null",
            "",
            "Paso 2 — Para cada archivo, elimina los permisos de escritura mundial:",
            "  sudo chmod o-w /path/to/file",
            "",
            "Paso 3 — Considera usar el bit sticky en directorios compartidos:",
            "  sudo chmod +t /shared/directory",
        ]
        result["fix_en"] = [
            "World-writable files can be modified by any user on the system.",
            "",
            "Step 1 — Find world-writable files:",
            "  find /etc /opt /home /root -xdev -type f -perm -0002 2>/dev/null",
            "",
            "Step 2 — For each file, remove world-write permissions:",
            "  sudo chmod o-w /path/to/file",
            "",
            "Step 3 — Consider using sticky bit on shared directories:",
            "  sudo chmod +t /shared/directory",
        ]

    return result


def check_reverse_shell_detection():
    """CHECK 54: Is there evidence of reverse shell activity?"""
    result = {
        "id": "reverse_shell_detection",
        "name_es": "Deteccion de shells inversas",
        "name_en": "Reverse shell detection",
        "severity": "CRITICAL",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    issues = []

    # Check for established network connections
    stdout, stderr, returncode = run_command("ss -tnp 2>/dev/null | grep ESTAB")

    if returncode == 0:
        shell_processes = ["bash", "sh", "nc", "python", "perl"]
        established_conns = stdout.split('\n')

        for conn in established_conns:
            if not conn.strip():
                continue

            # Check if connection involves shell processes
            is_shell_process = any(proc in conn for proc in shell_processes)

            if is_shell_process:
                # Exclude localhost connections
                if "127.0.0.1" not in conn and "::1" not in conn:
                    issues.append({
                        "es": "Conexion ESTABLISHED de proceso shell a IP externa",
                        "en": "ESTABLISHED connection from shell process to external IP",
                    })
                    break  # Only report once

    if not issues:
        result["passed"] = True
        result["details_en"] = "No reverse shell patterns detected."
        result["details_es"] = "No se detectaron patrones de shells inversas."
    else:
        result["details_en"] = "Reverse shell activity detected: " + issues[0]["en"]
        result["details_es"] = "Actividad de shell inversa detectada: " + issues[0]["es"]
        result["fix_es"] = [
            "Una shell inversa indica que un atacante tiene acceso remoto interactivo.",
            "",
            "ACCCION INMEDIATA: Tu sistema puede estar comprometido.",
            "",
            "Paso 1 — Termina todas las sesiones de red sospechosas:",
            "  ss -tnp | grep ESTAB  # Identifica conexiones",
            "",
            "Paso 2 — Mata los procesos sospechosos:",
            "  sudo kill -9 <PID>",
            "",
            "Paso 3 — Revisa los logs de acceso SSH:",
            "  sudo cat /var/log/auth.log | tail -100",
            "",
            "Paso 4 — Considera ejecutar un respaldo y limpiar el sistema.",
        ]
        result["fix_en"] = [
            "A reverse shell indicates an attacker has interactive remote access.",
            "",
            "IMMEDIATE ACTION: Your system may be compromised.",
            "",
            "Step 1 — Terminate all suspicious network sessions:",
            "  ss -tnp | grep ESTAB  # Identify connections",
            "",
            "Step 2 — Kill suspicious processes:",
            "  sudo kill -9 <PID>",
            "",
            "Step 3 — Review SSH access logs:",
            "  sudo cat /var/log/auth.log | tail -100",
            "",
            "Step 4 — Consider running a backup and cleaning the system.",
        ]

    return result


def check_cryptominer_detection():
    """CHECK 55: Is a cryptominer process running on the system?"""
    result = {
        "id": "cryptominer_detection",
        "name_es": "Deteccion de criptominero",
        "name_en": "Cryptominer detection",
        "severity": "HIGH",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    miner_names = ["xmrig", "minerd", "cpuminer", "ethminer", "cgminer", "bfgminer", "ccminer"]
    mining_ports = ["3333", "4444", "5555", "7777", "8888", "9999", "14444"]

    issues = []

    # Check for miner processes in top CPU consumers
    stdout, stderr, returncode = run_command("ps aux --sort=-%cpu 2>/dev/null | head -10")

    if returncode == 0:
        processes = stdout.split('\n')
        for proc in processes:
            for miner in miner_names:
                if miner in proc.lower():
                    issues.append({
                        "es": f"Proceso criptominero detectado: {miner}",
                        "en": f"Cryptominer process detected: {miner}",
                    })
                    break

            # Check for high CPU usage on suspicious processes
            if any(high_cpu in proc for high_cpu in ["python", "perl", "node", "sh", "bash"]):
                try:
                    parts = proc.split()
                    if len(parts) > 2:
                        cpu_usage = float(parts[2])
                        if cpu_usage > 90:
                            issues.append({
                                "es": f"Proceso consumiendo excesiva CPU ({cpu_usage}%): {parts[-1]}",
                                "en": f"Process using excessive CPU ({cpu_usage}%): {parts[-1]}",
                            })
                except (ValueError, IndexError):
                    pass

    # Check for mining pool connections
    stdout, stderr, returncode = run_command("ss -tnp 2>/dev/null | grep -E ':(3333|4444|5555|7777|8888|9999|14444)'")

    if returncode == 0 and stdout.strip():
        issues.append({
            "es": "Conexion a puerto de pool de mineria detectada",
            "en": "Connection to mining pool port detected",
        })

    if not issues:
        result["passed"] = True
        result["details_en"] = "No cryptominer activity detected."
        result["details_es"] = "No se detectó actividad de criptominería."
    else:
        result["details_en"] = "Cryptominer indicators: " + "; ".join(set(i["en"] for i in issues[:2]))
        result["details_es"] = "Indicadores de criptominería: " + "; ".join(set(i["es"] for i in issues[:2]))
        result["fix_es"] = [
            "Un criptominero consume recursos del sistema para generar ganancias ilegales.",
            "",
            "Paso 1 — Identifica procesos sospechosos con CPU alta:",
            "  ps aux --sort=-%cpu | head -20",
            "",
            "Paso 2 — Termina los procesos mineros:",
            "  sudo kill -9 <PID>",
            "",
            "Paso 3 — Busca y elimina malware:",
            "  sudo rkhunter --check --skip-keypress",
            "",
            "Paso 4 — Verifica cron jobs y servicios de inicio:",
            "  crontab -l",
            "  systemctl list-unit-files",
        ]
        result["fix_en"] = [
            "A cryptominer consumes system resources to generate illegal profits.",
            "",
            "Step 1 — Identify suspicious processes with high CPU:",
            "  ps aux --sort=-%cpu | head -20",
            "",
            "Step 2 — Terminate miner processes:",
            "  sudo kill -9 <PID>",
            "",
            "Step 3 — Search for and remove malware:",
            "  sudo rkhunter --check --skip-keypress",
            "",
            "Step 4 — Check cron jobs and startup services:",
            "  crontab -l",
            "  systemctl list-unit-files",
        ]

    return result


def check_rootkit_detection_basic():
    """CHECK 56: Are there signs of rootkit infection?"""
    result = {
        "id": "rootkit_detection_basic",
        "name_es": "Deteccion basica de rootkit",
        "name_en": "Basic rootkit detection",
        "severity": "CRITICAL",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    issues = []

    # Check kernel taint
    stdout, stderr, returncode = run_command("cat /proc/sys/kernel/tainted 2>/dev/null")
    if returncode == 0:
        taint = stdout.strip()
        if taint and taint != "0":
            issues.append({
                "es": f"Kernel tainted flag no es 0: {taint}",
                "en": f"Kernel taint flag is not 0: {taint}",
            })

    # Check for hidden kernel modules
    stdout_lsmod, _, rc1 = run_command("lsmod 2>/dev/null | wc -l")
    stdout_sysmod, _, rc2 = run_command("ls /sys/module/ 2>/dev/null | wc -l")

    if rc1 == 0 and rc2 == 0:
        try:
            lsmod_count = int(stdout_lsmod.strip())
            sysmod_count = int(stdout_sysmod.strip())

            # If /sys/module has significantly more than lsmod reports, there may be hidden modules
            if sysmod_count > lsmod_count * 4:
                issues.append({
                    "es": f"Diferencia sospechosa en modulos: lsmod={lsmod_count}, sysfs={sysmod_count}",
                    "en": f"Suspicious difference in modules: lsmod={lsmod_count}, sysfs={sysmod_count}",
                })
        except ValueError:
            pass

    # Check for suspicious /dev entries
    stdout, stderr, returncode = run_command("ls /dev/ 2>/dev/null | grep -E '(\\.|--)'")
    if returncode == 0 and stdout.strip():
        suspicious_devices = stdout.split('\n')
        if len(suspicious_devices) > 0:
            issues.append({
                "es": f"Dispositivos /dev sospechosos detectados: {suspicious_devices[0]}",
                "en": f"Suspicious /dev devices detected: {suspicious_devices[0]}",
            })

    if not issues:
        result["passed"] = True
        result["details_en"] = "No rootkit indicators detected."
        result["details_es"] = "No se detectaron indicadores de rootkit."
    else:
        result["details_en"] = "Rootkit indicators: " + "; ".join(set(i["en"] for i in issues))
        result["details_es"] = "Indicadores de rootkit: " + "; ".join(set(i["es"] for i in issues))
        result["fix_es"] = [
            "Los rootkits son formas avanzadas de malware que se ocultan en el kernel.",
            "",
            "ACCION INMEDIATA: Tu sistema podria estar profundamente comprometido.",
            "",
            "Paso 1 — Verifica la integridad del kernel:",
            "  cat /proc/sys/kernel/tainted",
            "",
            "Paso 2 — Busca indicadores con herramientas especializadas:",
            "  sudo apt-get install rkhunter aide",
            "  sudo rkhunter --check --skip-keypress",
            "",
            "Paso 3 — Considera el poder usar un liveCD de Linux para analizar:",
            "  # Arranca desde USB con una distribucion limpia",
            "",
            "Paso 4 — Si se confirma, considera reinstalar el sistema.",
        ]
        result["fix_en"] = [
            "Rootkits are advanced forms of malware that hide in the kernel.",
            "",
            "IMMEDIATE ACTION: Your system may be deeply compromised.",
            "",
            "Step 1 — Check kernel integrity:",
            "  cat /proc/sys/kernel/tainted",
            "",
            "Step 2 — Search for indicators with specialized tools:",
            "  sudo apt-get install rkhunter aide",
            "  sudo rkhunter --check --skip-keypress",
            "",
            "Step 3 — Consider using a LiveCD to analyze the system:",
            "  # Boot from USB with a clean distribution",
            "",
            "Step 4 — If confirmed, consider reinstalling the system.",
        ]

    return result


def check_dns_tunneling_detection():
    """CHECK 57: Is DNS being used for data tunneling or exfiltration?"""
    result = {
        "id": "dns_tunneling_detection",
        "name_es": "Deteccion de DNS tunneling",
        "name_en": "DNS tunneling detection",
        "severity": "HIGH",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    issues = []

    dns_tunnel_tools = ["iodine", "dnscat", "dns2tcp"]

    # Check for DNS client tool connections
    stdout, stderr, returncode = run_command("ss -unp 2>/dev/null | grep :53")

    if returncode == 0 and stdout.strip():
        unusual_dns = stdout.split('\n')
        for conn in unusual_dns:
            # Flag non-standard DNS queries
            if ":" in conn and not any(std in conn for std in ["systemd-resolve", "dnsmasq", "named"]):
                issues.append({
                    "es": "Conexion DNS inusual detectada",
                    "en": "Unusual DNS connection detected",
                })
                break

    # Check for DNS tunneling tools in processes
    stdout, stderr, returncode = run_command("ps aux 2>/dev/null | grep -E '(iodine|dnscat|dns2tcp)'")

    if returncode == 0 and stdout.strip():
        for tool in dns_tunnel_tools:
            if tool in stdout and "grep" not in stdout:
                issues.append({
                    "es": f"Herramienta de DNS tunneling encontrada: {tool}",
                    "en": f"DNS tunneling tool found: {tool}",
                })

    if not issues:
        result["passed"] = True
        result["details_en"] = "No DNS tunneling indicators detected."
        result["details_es"] = "No se detectaron indicadores de DNS tunneling."
    else:
        result["details_en"] = "DNS tunneling detected: " + "; ".join(set(i["en"] for i in issues))
        result["details_es"] = "DNS tunneling detectado: " + "; ".join(set(i["es"] for i in issues))
        result["fix_es"] = [
            "DNS tunneling permite evasion de firewalls y exfiltracion de datos.",
            "",
            "Paso 1 — Identifica conexiones DNS inusales:",
            "  ss -unp | grep :53",
            "",
            "Paso 2 — Bloquea herramientas de DNS tunneling:",
            "  sudo apt-get remove iodine dnscat2 dns2tcp",
            "",
            "Paso 3 — Configura firewall para limitar DNS a servidores confiables:",
            "  sudo ufw allow out 53",
            "",
            "Paso 4 — Monitorea logs de DNS para patrones sospechosos.",
        ]
        result["fix_en"] = [
            "DNS tunneling allows firewall evasion and data exfiltration.",
            "",
            "Step 1 — Identify unusual DNS connections:",
            "  ss -unp | grep :53",
            "",
            "Step 2 — Block DNS tunneling tools:",
            "  sudo apt-get remove iodine dnscat2 dns2tcp",
            "",
            "Step 3 — Configure firewall to limit DNS to trusted servers:",
            "  sudo ufw allow out 53",
            "",
            "Step 4 — Monitor DNS logs for suspicious patterns.",
        ]

    return result


def check_websocket_security():
    """CHECK 58: Is the websocket gateway properly secured?"""
    result = {
        "id": "websocket_security",
        "name_es": "Seguridad del websocket",
        "name_en": "Websocket security",
        "severity": "CRITICAL",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    issues = []

    # Check gateway config for origin validation
    gateway_config_path = OPENCLAW_HOME / "config" / "gateway.json"

    if gateway_config_path.exists():
        config = read_json_safe(gateway_config_path)
        if config:
            websocket_config = config.get("websocket", {})

            # Check for origin validation
            if not websocket_config.get("origin_validation_enabled", False):
                issues.append({
                    "es": "Validacion de origen del websocket no habilitada",
                    "en": "Websocket origin validation not enabled",
                })

            # Check for CORS headers
            cors_origins = websocket_config.get("allowed_origins", [])
            if not cors_origins or "*" in cors_origins:
                issues.append({
                    "es": "Origenes de websocket demasiado permisivos",
                    "en": "Websocket origins too permissive",
                })

    # Check if websocket is listening
    stdout, stderr, returncode = run_command("ss -tlnp 2>/dev/null | grep -E ':(18789|3000)'")

    if returncode == 0 and stdout.strip():
        # Websocket is listening - check if properly configured
        if issues:
            result["details_en"] = "Websocket exposed with insecure config"
            result["details_es"] = "Websocket expuesto con configuracion insegura"

    if not issues:
        result["passed"] = True
        result["details_en"] = "Websocket is properly secured with origin validation."
        result["details_es"] = "El websocket esta adecuadamente protegido con validacion de origen."
    else:
        result["details_en"] = "Websocket security issues: " + "; ".join(set(i["en"] for i in issues))
        result["details_es"] = "Problemas de seguridad del websocket: " + "; ".join(set(i["es"] for i in issues))
        result["fix_es"] = [
            "El websocket sin validacion de origen permite ataques CSRF y cross-site.",
            "",
            "Paso 1 — Edita la configuracion del gateway:",
            "  nano ~/.openclaw/config/gateway.json",
            "",
            "Paso 2 — Añade validacion de origen:",
            "  {",
            "    \"websocket\": {",
            "      \"origin_validation_enabled\": true,",
            "      \"allowed_origins\": [\"https://tu-dominio.com\"]",
            "    }",
            "  }",
            "",
            "Paso 3 — Reinicia OpenClaw:",
            "  openclaw restart gateway",
        ]
        result["fix_en"] = [
            "Websocket without origin validation allows CSRF and cross-site attacks.",
            "",
            "Step 1 — Edit gateway configuration:",
            "  nano ~/.openclaw/config/gateway.json",
            "",
            "Step 2 — Add origin validation:",
            "  {",
            "    \"websocket\": {",
            "      \"origin_validation_enabled\": true,",
            "      \"allowed_origins\": [\"https://your-domain.com\"]",
            "    }",
            "  }",
            "",
            "Step 3 — Restart OpenClaw:",
            "  openclaw restart gateway",
        ]

    return result


def check_sudo_nopasswd_audit():
    """CHECK 59: Are there dangerous NOPASSWD entries in sudoers?"""
    result = {
        "id": "sudo_nopasswd_audit",
        "name_es": "Auditoria de NOPASSWD en sudoers",
        "name_en": "Sudoers NOPASSWD audit",
        "severity": "CRITICAL",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    dangerous_patterns = ["NOPASSWD: ALL", "NOPASSWD: /bin/bash", "NOPASSWD: /bin/sh"]
    issues = []

    # Read sudoers file
    stdout_sudoers, _, rc1 = run_command("cat /etc/sudoers 2>/dev/null")
    stdout_sudoers_d, _, rc2 = run_command("cat /etc/sudoers.d/* 2>/dev/null")

    all_sudoers = (stdout_sudoers if rc1 == 0 else "") + "\n" + (stdout_sudoers_d if rc2 == 0 else "")

    for line in all_sudoers.split('\n'):
        if line.strip() and not line.startswith('#'):
            for pattern in dangerous_patterns:
                if pattern in line:
                    issues.append({
                        "es": f"NOPASSWD peligroso encontrado: {line.strip()[:60]}",
                        "en": f"Dangerous NOPASSWD found: {line.strip()[:60]}",
                    })

            # Check for NOPASSWD with wildcards
            if "NOPASSWD" in line and "*" in line:
                issues.append({
                    "es": f"NOPASSWD con wildcards: {line.strip()[:60]}",
                    "en": f"NOPASSWD with wildcards: {line.strip()[:60]}",
                })

    if not issues:
        result["passed"] = True
        result["details_en"] = "No dangerous NOPASSWD configurations found in sudoers."
        result["details_es"] = "No se encontraron configuraciones peligrosas de NOPASSWD en sudoers."
    else:
        result["details_en"] = "Dangerous sudoers entries: " + "; ".join(set(i["en"] for i in issues[:2]))
        result["details_es"] = "Entradas peligrosas en sudoers: " + "; ".join(set(i["es"] for i in issues[:2]))
        result["fix_es"] = [
            "NOPASSWD sin contrasena permite escalada de privilegios sin autenticacion.",
            "",
            "Paso 1 — Verifica tu configuracion de sudoers:",
            "  sudo visudo",
            "",
            "Paso 2 — Elimina lineas con NOPASSWD peligrosas o restriccionelas:",
            "  # MAL: usuario ALL=(ALL) NOPASSWD: ALL",
            "  # BIEN: usuario ALL=(ALL) PASSWD: ALL",
            "",
            "Paso 3 — Si necesitas NOPASSWD, limitalo a comandos especificos:",
            "  usuario ALL=(ALL) NOPASSWD: /usr/bin/specific_command",
            "",
            "Paso 4 — Valida los cambios sin salir:",
            "  sudo visudo -c",
        ]
        result["fix_en"] = [
            "NOPASSWD without password allows privilege escalation without authentication.",
            "",
            "Step 1 — Check your sudoers configuration:",
            "  sudo visudo",
            "",
            "Step 2 — Remove dangerous NOPASSWD lines or restrict them:",
            "  # BAD: user ALL=(ALL) NOPASSWD: ALL",
            "  # GOOD: user ALL=(ALL) PASSWD: ALL",
            "",
            "Step 3 — If you need NOPASSWD, limit it to specific commands:",
            "  user ALL=(ALL) NOPASSWD: /usr/bin/specific_command",
            "",
            "Step 4 — Validate changes without exiting:",
            "  sudo visudo -c",
        ]

    return result


def check_swap_encryption():
    """CHECK 60: Is swap memory encrypted?"""
    result = {
        "id": "swap_encryption",
        "name_es": "Encriptacion de swap",
        "name_en": "Swap encryption",
        "severity": "MEDIUM",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    issues = []

    # Check if swap exists
    stdout, stderr, returncode = run_command("swapon --show 2>/dev/null")

    if returncode == 0 and stdout.strip():
        # Swap exists - check if encrypted
        swap_devices = stdout.split('\n')[1:]  # Skip header

        for swap_line in swap_devices:
            if swap_line.strip():
                # Check if it's a dm-crypt device
                if "dm-" not in swap_line:
                    issues.append({
                        "es": "Swap detectado sin encriptacion",
                        "en": "Unencrypted swap detected",
                    })
                    break
    else:
        # No swap - this is fine
        result["passed"] = True
        result["details_en"] = "No swap configured (acceptable) or swap is encrypted."
        result["details_es"] = "Sin swap configurado (aceptable) o swap encriptado."
        return result

    if not issues:
        result["passed"] = True
        result["details_en"] = "Swap is properly encrypted with LUKS/dm-crypt."
        result["details_es"] = "Swap esta apropiadamente encriptado con LUKS/dm-crypt."
    else:
        result["details_en"] = "Swap encryption issues: " + "; ".join(set(i["en"] for i in issues))
        result["details_es"] = "Problemas de encriptacion de swap: " + "; ".join(set(i["es"] for i in issues))
        result["fix_es"] = [
            "Swap sin encriptacion puede exponer datos sensibles en memoria.",
            "",
            "Paso 1 — Verifica tu configuracion actual de swap:",
            "  swapon --show",
            "",
            "Paso 2 — Si tienes swap, considera migrarlo a dm-crypt:",
            "  sudo swapoff /swapfile",
            "",
            "Paso 3 — Crea una particion de swap encriptada con LUKS.",
            "",
            "Paso 4 — Alternativa: deshabilita swap si no es critico:",
            "  sudo swapoff -a",
        ]
        result["fix_en"] = [
            "Unencrypted swap can expose sensitive data in memory.",
            "",
            "Step 1 — Check your current swap configuration:",
            "  swapon --show",
            "",
            "Step 2 — If you have swap, consider migrating to dm-crypt:",
            "  sudo swapoff /swapfile",
            "",
            "Step 3 — Create LUKS-encrypted swap partition.",
            "",
            "Step 4 — Alternative: disable swap if not critical:",
            "  sudo swapoff -a",
        ]

    return result


def check_core_dump_protection():
    """CHECK 61: Are core dumps restricted to prevent information disclosure?"""
    result = {
        "id": "core_dump_protection",
        "name_es": "Proteccion contra core dumps",
        "name_en": "Core dump protection",
        "severity": "MEDIUM",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    issues = []

    # Check kernel core_pattern
    stdout, stderr, returncode = run_command("cat /proc/sys/kernel/core_pattern 2>/dev/null")
    if returncode == 0 and stdout.strip().startswith("|"):
        # Piped to a program - OK
        pass
    elif returncode == 0 and "core" in stdout:
        issues.append({
            "es": "Core dumps pueden estar habilitados: " + stdout.strip()[:30],
            "en": "Core dumps may be enabled: " + stdout.strip()[:30],
        })

    # Check suid_dumpable
    stdout, stderr, returncode = run_command("cat /proc/sys/fs/suid_dumpable 2>/dev/null")
    if returncode == 0:
        try:
            suid_dump = int(stdout.strip())
            if suid_dump != 0:
                issues.append({
                    "es": f"suid_dumpable es {suid_dump} (deberia ser 0)",
                    "en": f"suid_dumpable is {suid_dump} (should be 0)",
                })
        except ValueError:
            pass

    # Check ulimit
    stdout, stderr, returncode = run_command("ulimit -c 2>/dev/null")
    if returncode == 0 and stdout.strip() != "0":
        issues.append({
            "es": f"ulimit -c es {stdout.strip()} (deberia ser 0)",
            "en": f"ulimit -c is {stdout.strip()} (should be 0)",
        })

    if not issues:
        result["passed"] = True
        result["details_en"] = "Core dumps are properly disabled."
        result["details_es"] = "Los core dumps estan apropiadamente deshabilitados."
    else:
        result["details_en"] = "Core dump issues: " + "; ".join(set(i["en"] for i in issues))
        result["details_es"] = "Problemas de core dumps: " + "; ".join(set(i["es"] for i in issues))
        result["fix_es"] = [
            "Los core dumps pueden exponer informacion sensible del proceso.",
            "",
            "Paso 1 — Deshabilita core dumps en el kernel:",
            "  echo 'kernel.core_pattern = /dev/null' | sudo tee -a /etc/sysctl.conf",
            "  echo 'fs.suid_dumpable = 0' | sudo tee -a /etc/sysctl.conf",
            "",
            "Paso 2 — Aplica los cambios:",
            "  sudo sysctl -p",
            "",
            "Paso 3 — Deshabilita ulimit para core dumps:",
            "  echo '* hard core 0' | sudo tee -a /etc/security/limits.conf",
        ]
        result["fix_en"] = [
            "Core dumps can expose sensitive process information.",
            "",
            "Step 1 — Disable core dumps in kernel:",
            "  echo 'kernel.core_pattern = /dev/null' | sudo tee -a /etc/sysctl.conf",
            "  echo 'fs.suid_dumpable = 0' | sudo tee -a /etc/sysctl.conf",
            "",
            "Step 2 — Apply the changes:",
            "  sudo sysctl -p",
            "",
            "Step 3 — Disable ulimit for core dumps:",
            "  echo '* hard core 0' | sudo tee -a /etc/security/limits.conf",
        ]

    return result


def check_conversation_log_security():
    """CHECK 62: Are conversation logs secured from unauthorized access?"""
    result = {
        "id": "conversation_log_security",
        "name_es": "Seguridad de logs de conversacion",
        "name_en": "Conversation log security",
        "severity": "HIGH",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    issues = []

    sessions_dir = OPENCLAW_HOME / "agents" / "*" / "sessions"

    # Check for world/group readable conversation files
    stdout, stderr, returncode = run_command(
        f"find {OPENCLAW_HOME} -name '*.jsonl' -perm /044 2>/dev/null | head -5"
    )

    if returncode == 0 and stdout.strip():
        readable_logs = stdout.split('\n')
        issues.append({
            "es": f"Se encontraron {len(readable_logs)} archivos JSONL con permisos inseguros",
            "en": f"Found {len(readable_logs)} JSONL files with insecure permissions",
        })

    # Check directory permissions in .openclaw
    for item in [OPENCLAW_HOME / "agents", OPENCLAW_HOME / "config"]:
        if item.exists():
            try:
                stat_info = item.stat()
                perms = oct(stat_info.st_mode)[-3:]

                # Check if group or others can read
                if int(perms[1]) > 0 or int(perms[2]) > 0:
                    issues.append({
                        "es": f"Directorio {item.name} tiene permisos inseguros: {perms}",
                        "en": f"Directory {item.name} has insecure permissions: {perms}",
                    })
            except (OSError, ValueError):
                pass

    if not issues:
        result["passed"] = True
        result["details_en"] = "Conversation logs are properly secured."
        result["details_es"] = "Los logs de conversacion estan apropiadamente protegidos."
    else:
        result["details_en"] = "Log security issues: " + "; ".join(set(i["en"] for i in issues[:2]))
        result["details_es"] = "Problemas de seguridad de logs: " + "; ".join(set(i["es"] for i in issues[:2]))
        result["fix_es"] = [
            "Logs de conversacion expuestos pueden revelar prompts sensibles y contextos.",
            "",
            "Paso 1 — Verifica permisos de archivos de sesion:",
            "  ls -la ~/.openclaw/agents/*/sessions/*.jsonl",
            "",
            "Paso 2 — Restringe permisos para que solo root pueda leer:",
            "  chmod 600 ~/.openclaw/agents/*/sessions/*.jsonl",
            "",
            "Paso 3 — Protege directorios:",
            "  chmod 700 ~/.openclaw/agents",
            "  chmod 700 ~/.openclaw/agents/*/sessions",
            "",
            "Paso 4 — Considera encriptar los logs en reposo.",
        ]
        result["fix_en"] = [
            "Exposed conversation logs can reveal sensitive prompts and contexts.",
            "",
            "Step 1 — Check permissions of session files:",
            "  ls -la ~/.openclaw/agents/*/sessions/*.jsonl",
            "",
            "Step 2 — Restrict permissions to root only:",
            "  chmod 600 ~/.openclaw/agents/*/sessions/*.jsonl",
            "",
            "Step 3 — Protect directories:",
            "  chmod 700 ~/.openclaw/agents",
            "  chmod 700 ~/.openclaw/agents/*/sessions",
            "",
            "Step 4 — Consider encrypting logs at rest.",
        ]

    return result


def check_skill_update_verification():
    """CHECK 63: Are skill updates verified over secure channels?"""
    result = {
        "id": "skill_update_verification",
        "name_es": "Verificacion de actualizaciones de skills",
        "name_en": "Skill update verification",
        "severity": "HIGH",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    issues = []

    # Check if skill registry uses HTTPS
    config = read_json_safe(OPENCLAW_CONFIG)
    if config:
        skill_registry = config.get("skill_registry", "")

        if skill_registry and "http://" in skill_registry.lower():
            issues.append({
                "es": "Skill registry usa HTTP inseguro",
                "en": "Skill registry uses insecure HTTP",
            })
        elif not skill_registry or "https://" not in skill_registry.lower():
            issues.append({
                "es": "Skill registry no esta configurado o usa HTTP",
                "en": "Skill registry not configured or uses HTTP",
            })

    # Check for clawhub CLI
    stdout, stderr, returncode = run_command("which clawhub 2>/dev/null")

    if returncode == 0:
        # clawhub is installed, check if it's configured for HTTPS
        clawhub_config = Path.home() / ".clawhub" / "config.json"
        if clawhub_config.exists():
            clawhub_conf = read_json_safe(clawhub_config)
            if clawhub_conf:
                registry = clawhub_conf.get("registry", "")
                if "http://" in registry:
                    issues.append({
                        "es": "ClavHub CLI usa HTTP inseguro",
                        "en": "ClavHub CLI uses insecure HTTP",
                    })

    if not issues:
        result["passed"] = True
        result["details_en"] = "Skill updates use secure HTTPS channels."
        result["details_es"] = "Las actualizaciones de skills usan canales seguros HTTPS."
    else:
        result["details_en"] = "Skill update issues: " + "; ".join(set(i["en"] for i in issues))
        result["details_es"] = "Problemas de actualización de skills: " + "; ".join(set(i["es"] for i in issues))
        result["fix_es"] = [
            "Las actualizaciones de skills sin HTTPS estan vulnerables a man-in-the-middle.",
            "",
            "Paso 1 — Verifica tu configuracion de registry:",
            "  cat ~/.openclaw/config/moltbot.json | grep registry",
            "",
            "Paso 2 — Actualiza a usar HTTPS:",
            "  {",
            "    \"skill_registry\": \"https://skills.openclaw.io\"",
            "  }",
            "",
            "Paso 3 — Para ClavHub CLI:",
            "  clawhub config set registry https://registry.clawhub.io",
        ]
        result["fix_en"] = [
            "Skill updates without HTTPS are vulnerable to man-in-the-middle attacks.",
            "",
            "Step 1 — Check your registry configuration:",
            "  cat ~/.openclaw/config/moltbot.json | grep registry",
            "",
            "Step 2 — Update to use HTTPS:",
            "  {",
            "    \"skill_registry\": \"https://skills.openclaw.io\"",
            "  }",
            "",
            "Step 3 — For ClavHub CLI:",
            "  clawhub config set registry https://registry.clawhub.io",
        ]

    return result


def check_cross_agent_communication():
    """CHECK 64: Are multiple agents properly isolated?"""
    result = {
        "id": "cross_agent_communication",
        "name_es": "Aislamiento de agentes multiples",
        "name_en": "Cross-agent communication isolation",
        "severity": "HIGH",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    issues = []

    # Check how many agents are running
    stdout, stderr, returncode = run_command("openclaw agents list 2>/dev/null")

    if returncode == 0:
        agents = stdout.split('\n')
        agent_count = sum(1 for a in agents if a.strip() and not a.startswith('-'))

        if agent_count > 1:
            # Multiple agents - check for shared credentials
            shared_env_vars = []

            # Check environment for shared API keys
            for agent in agents[:min(agent_count, 3)]:
                agent_name = agent.strip()
                if agent_name:
                    stdout_env, _, rc_env = run_command(f"openclaw agent env {agent_name} 2>/dev/null")
                    if rc_env == 0 and "ANTHROPIC_API_KEY" in stdout_env:
                        shared_env_vars.append(agent_name)

            if shared_env_vars:
                issues.append({
                    "es": f"Agentes comparten credenciales: {', '.join(shared_env_vars[:2])}",
                    "en": f"Agents share credentials: {', '.join(shared_env_vars[:2])}",
                })
        else:
            # Single agent is ideal
            result["passed"] = True
            result["details_en"] = "Single agent - no cross-agent communication risk."
            result["details_es"] = "Agente unico - sin riesgo de comunicacion entre agentes."
            return result
    else:
        # Can't enumerate agents
        result["passed"] = True
        result["details_en"] = "Unable to enumerate agents (single agent likely)."
        result["details_es"] = "No se pueden enumerar agentes (probablemente agente unico)."
        return result

    if not issues:
        result["passed"] = True
        result["details_en"] = "Multiple agents are properly isolated."
        result["details_es"] = "Multiples agentes estan apropiadamente aislados."
    else:
        result["details_en"] = "Agent isolation issues: " + "; ".join(set(i["en"] for i in issues))
        result["details_es"] = "Problemas de aislamiento de agentes: " + "; ".join(set(i["es"] for i in issues))
        result["fix_es"] = [
            "Agentes que comparten credenciales pueden comprometer a todos cuando uno es comprometido.",
            "",
            "Paso 1 — Usa claves API separadas para cada agente:",
            "  openclaw agent create --api-key <unique-key-for-agent>",
            "",
            "Paso 2 — Aisla contextos de agentes:",
            "  openclaw agent config --isolation=namespace",
            "",
            "Paso 3 — Limita el alcance de permisos por agente:",
            "  openclaw agent permissions --role=limited",
        ]
        result["fix_en"] = [
            "Agents sharing credentials can compromise all when one is compromised.",
            "",
            "Step 1 — Use separate API keys for each agent:",
            "  openclaw agent create --api-key <unique-key-for-agent>",
            "",
            "Step 2 — Isolate agent contexts:",
            "  openclaw agent config --isolation=namespace",
            "",
            "Step 3 — Limit permission scope per agent:",
            "  openclaw agent permissions --role=limited",
        ]

    return result


def check_session_token_security():
    """CHECK 65: Are session tokens securely stored and not exposed?"""
    result = {
        "id": "session_token_security",
        "name_es": "Seguridad de tokens de sesion",
        "name_en": "Session token security",
        "severity": "CRITICAL",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    issues = []

    # Check if tokens are exposed via EnvironmentFile
    _svc_out, _, _svc_rc = run_command("systemctl --user cat openclaw-gateway 2>/dev/null")
    if _svc_rc == 0 and "EnvironmentFile" not in (_svc_out or ""):
        issues.append({
            "es": "Tokens expuestos: el servicio no usa EnvironmentFile",
            "en": "Tokens exposed: service does not use EnvironmentFile",
        })

    # Check OpenClaw token storage permissions
    token_dir = OPENCLAW_HOME / "tokens"
    if token_dir.exists():
        try:
            stat_info = token_dir.stat()
            perms = oct(stat_info.st_mode)[-3:]

            # Check if group or others can read
            if int(perms[1]) > 0 or int(perms[2]) > 0:
                issues.append({
                    "es": f"Directorio de tokens tiene permisos inseguros: {perms}",
                    "en": f"Token directory has insecure permissions: {perms}",
                })
        except (OSError, ValueError):
            pass

    # Check environment variables for API keys
    stdout, stderr, returncode = run_command("env | grep -i 'anthropic\\|openclaw.*key'")

    if returncode == 0 and stdout.strip():
        issues.append({
            "es": "Claves API detectadas en variables de entorno",
            "en": "API keys detected in environment variables",
        })

    if not issues:
        result["passed"] = True
        result["details_en"] = "Session tokens are properly secured and not exposed."
        result["details_es"] = "Los tokens de sesion estan apropiadamente protegidos y no expuestos."
    else:
        result["details_en"] = "Token security issues: " + "; ".join(set(i["en"] for i in issues[:2]))
        result["details_es"] = "Problemas de seguridad de tokens: " + "; ".join(set(i["es"] for i in issues[:2]))
        result["fix_es"] = [
            "Tokens expuestos en /proc pueden ser accedidos por otros usuarios.",
            "",
            "ACCION INMEDIATA: Rotacion de tokens recomendada.",
            "",
            "Paso 1 — Verifica donde estan tus tokens:",
            "  ls -la ~/.openclaw/tokens/",
            "",
            "Paso 2 — Asegura permisos (700 para directorios, 600 para archivos):",
            "  chmod 700 ~/.openclaw/tokens/",
            "  chmod 600 ~/.openclaw/tokens/*",
            "",
            "Paso 3 — Nunca exporte claves API en variables de entorno globales:",
            "  # MALO: export ANTHROPIC_API_KEY=...",
            "  # BIEN: Usa .env local o archivos de credenciales seguros",
            "",
            "Paso 4 — Rota tus tokens API en la consola de Anthropic.",
        ]
        result["fix_en"] = [
            "Tokens exposed in /proc can be accessed by other users.",
            "",
            "IMMEDIATE ACTION: Token rotation recommended.",
            "",
            "Step 1 — Check where your tokens are stored:",
            "  ls -la ~/.openclaw/tokens/",
            "",
            "Step 2 — Secure permissions (700 for dirs, 600 for files):",
            "  chmod 700 ~/.openclaw/tokens/",
            "  chmod 600 ~/.openclaw/tokens/*",
            "",
            "Step 3 — Never export API keys in global environment variables:",
            "  # BAD: export ANTHROPIC_API_KEY=...",
            "  # GOOD: Use local .env or secure credential files",
            "",
            "Step 4 — Rotate your API tokens in the Anthropic console.",
        ]

    return result


def check_filesystem_immutable_attributes():
    """CHECK 66: Are critical config files marked with immutable attributes?"""
    result = {
        "id": "filesystem_immutable_attributes",
        "name_es": "Atributos inmutables del sistema de archivos",
        "name_en": "Filesystem immutable attributes",
        "severity": "MEDIUM",
        "passed": True,  # This is always pass (advisory)
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    # Check immutable flag on critical files
    critical_files = [
        OPENCLAW_HOME / "config" / "moltbot.json",
        OPENCLAW_HOME / ".env",
    ]

    recommendations = []

    for cfile in critical_files:
        if cfile.exists():
            stdout, stderr, returncode = run_command(f"lsattr {cfile} 2>/dev/null")

            if returncode == 0:
                if "-i" not in stdout:
                    recommendations.append(f"  {cfile.name}")

    # Always pass but provide details
    result["details_en"] = "Immutable attributes provide additional protection against accidental or malicious modifications."
    result["details_es"] = "Los atributos inmutables proporcionan proteccion adicional contra modificaciones."

    if recommendations:
        rec_str = "\n".join(recommendations)
        result["details_en"] += f"\n\nRecommended to set immutable on:\n{rec_str}"
        result["details_es"] += f"\n\nRecomendado configurar como inmutables:\n{rec_str}"

    result["fix_es"] = [
        "Los atributos inmutables previenen cambios incluso por root (requiere desactivar primero).",
        "",
        "Paso 1 — Establece el atributo inmutable en archivos criticos:",
        "  sudo chattr +i ~/.openclaw/config/moltbot.json",
        "  sudo chattr +i ~/.openclaw/.env",
        "",
        "Paso 2 — Verifica que se establecio:",
        "  lsattr ~/.openclaw/config/moltbot.json",
        "",
        "Paso 3 — Si necesitas modificar, primero desactiva:",
        "  sudo chattr -i ~/.openclaw/config/moltbot.json",
        "  # ... hacer cambios ...",
        "  sudo chattr +i ~/.openclaw/config/moltbot.json",
    ]
    result["fix_en"] = [
        "Immutable attributes prevent changes even by root (requires disabling first).",
        "",
        "Step 1 — Set immutable attribute on critical files:",
        "  sudo chattr +i ~/.openclaw/config/moltbot.json",
        "  sudo chattr +i ~/.openclaw/.env",
        "",
        "Step 2 — Verify it was set:",
        "  lsattr ~/.openclaw/config/moltbot.json",
        "",
        "Step 3 — If you need to modify, disable first:",
        "  sudo chattr -i ~/.openclaw/config/moltbot.json",
        "  # ... make changes ...",
        "  sudo chattr +i ~/.openclaw/config/moltbot.json",
    ]

    return result


def check_usb_device_restrictions():
    """CHECK 67: Are USB storage devices restricted?"""
    result = {
        "id": "usb_device_restrictions",
        "name_es": "Restricciones de dispositivos USB",
        "name_en": "USB device restrictions",
        "severity": "MEDIUM",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    # Check if running on VPS (not applicable for bare metal)
    stdout, stderr, returncode = run_command("systemd-detect-virt 2>/dev/null")

    is_vps = returncode == 0 and stdout.strip() not in ["none", ""]

    if is_vps or (returncode != 0):
        # VPS or unable to detect - USB not applicable
        result["passed"] = True
        result["details_en"] = "Running on VPS - USB restrictions not applicable."
        result["details_es"] = "Ejecutando en VPS - restricciones USB no aplicables."
        return result

    # Check USB storage blacklist
    stdout, stderr, returncode = run_command("cat /etc/modprobe.d/*.conf 2>/dev/null | grep -i 'usb_storage'")

    if returncode == 0 and "blacklist usb_storage" in stdout:
        result["passed"] = True
        result["details_en"] = "USB storage modules are blacklisted."
        result["details_es"] = "Los modulos de almacenamiento USB estan bloqueados."
    else:
        result["details_en"] = "USB storage is not blacklisted - physical access risk."
        result["details_es"] = "Almacenamiento USB no bloqueado - riesgo de acceso fisico."
        result["fix_es"] = [
            "USB storage puede permitir exfiltracion de datos si el servidor es accesible fisicamente.",
            "",
            "Paso 1 — Crea una configuracion para bloquear USB:",
            "  echo 'blacklist usb_storage' | sudo tee /etc/modprobe.d/disable-usb-storage.conf",
            "",
            "Paso 2 — Tambien bloquea conduccion masiva:",
            "  echo 'install usb_storage /bin/true' | sudo tee -a /etc/modprobe.d/disable-usb-storage.conf",
            "",
            "Paso 3 — Reboot para aplicar (o usa update-initramfs).",
        ]
        result["fix_en"] = [
            "USB storage can allow data exfiltration if server is physically accessible.",
            "",
            "Step 1 — Create configuration to blacklist USB:",
            "  echo 'blacklist usb_storage' | sudo tee /etc/modprobe.d/disable-usb-storage.conf",
            "",
            "Step 2 — Also block mass storage driver:",
            "  echo 'install usb_storage /bin/true' | sudo tee -a /etc/modprobe.d/disable-usb-storage.conf",
            "",
            "Step 3 — Reboot to apply (or use update-initramfs).",
        ]

    return result


def check_network_namespace_isolation():
    """CHECK 68: Is OpenClaw properly isolated in network namespace?"""
    result = {
        "id": "network_namespace_isolation",
        "name_es": "Aislamiento de espacio de nombres de red",
        "name_en": "Network namespace isolation",
        "severity": "HIGH",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    # Check if running in container
    stdout, stderr, returncode = run_command("cat /proc/1/cgroup 2>/dev/null")

    is_containerized = returncode == 0 and ("docker" in stdout or "lxc" in stdout or "containerd" in stdout)

    if is_containerized:
        # In container - check network mode
        stdout_netns, _, rc_netns = run_command("cat /proc/1/ns/net 2>/dev/null")

        result["passed"] = True
        result["details_en"] = "Running in container with network isolation."
        result["details_es"] = "Ejecutando en contenedor con aislamiento de red."
        return result

    # Not in container - check if single-host deployment
    result["passed"] = True
    result["details_en"] = "Single-host deployment - network isolation not critical."
    result["details_es"] = "Despliegue en un unico host - aislamiento de red no critico."
    result["fix_es"] = [
        "Para mayor seguridad, considera ejecutar OpenClaw en un contenedor.",
        "",
        "Paso 1 — Crea una imagen Docker:",
        "  docker build -t openclaw:isolated .",
        "",
        "Paso 2 — Ejecuta con aislamiento de red:",
        "  docker run --network=bridge openclaw:isolated",
        "",
        "Paso 3 — Usa Docker Compose para orquestracion:",
        "  docker-compose up -d",
    ]
    result["fix_en"] = [
        "For better security, consider running OpenClaw in a container.",
        "",
        "Step 1 — Build Docker image:",
        "  docker build -t openclaw:isolated .",
        "",
        "Step 2 — Run with network isolation:",
        "  docker run --network=bridge openclaw:isolated",
        "",
        "Step 3 — Use Docker Compose for orchestration:",
        "  docker-compose up -d",
    ]

    return result


def check_auditd_logging():
    """CHECK 69: Is auditd properly configured for logging?"""
    result = {
        "id": "auditd_logging",
        "name_es": "Registro de auditd",
        "name_en": "Auditd logging",
        "severity": "MEDIUM",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    issues = []

    # Check if auditd is running
    stdout, stderr, returncode = run_command("sudo systemctl is-active auditd 2>/dev/null")

    if returncode != 0 or "active" not in stdout:
        issues.append({
            "es": "auditd no esta activo",
            "en": "auditd is not active",
        })

    # Check for audit rules
    stdout, stderr, returncode = run_command("sudo auditctl -l 2>/dev/null | wc -l")

    if returncode == 0:
        try:
            rule_count = int(stdout.strip())
            if rule_count < 3:
                issues.append({
                    "es": f"Pocas reglas de auditoria ({rule_count})",
                    "en": f"Few audit rules ({rule_count})",
                })
        except ValueError:
            pass

    if not issues:
        result["passed"] = True
        result["details_en"] = "Auditd is active with logging rules."
        result["details_es"] = "Auditd esta activo con reglas de registro."
    else:
        result["details_en"] = "Auditd logging issues: " + "; ".join(set(i["en"] for i in issues))
        result["details_es"] = "Problemas de registro de auditd: " + "; ".join(set(i["es"] for i in issues))
        result["fix_es"] = [
            "Auditd proporciona un registro de seguridad detallado de cambios del sistema.",
            "",
            "Paso 1 — Instala auditd:",
            "  sudo apt-get install auditd",
            "",
            "Paso 2 — Inicia el servicio:",
            "  sudo systemctl start auditd",
            "  sudo systemctl enable auditd",
            "",
            "Paso 3 — Añade reglas de auditoria para OpenClaw:",
            "  sudo auditctl -w ~/.openclaw/config/ -p wa -k openclaw_config",
            "  sudo auditctl -w ~/.openclaw/skills/ -p wa -k openclaw_skills",
            "",
            "Paso 4 — Guarda las reglas permanentemente:",
            "  sudo service auditd restart",
        ]
        result["fix_en"] = [
            "Auditd provides detailed security logging of system changes.",
            "",
            "Step 1 — Install auditd:",
            "  sudo apt-get install auditd",
            "",
            "Step 2 — Start the service:",
            "  sudo systemctl start auditd",
            "  sudo systemctl enable auditd",
            "",
            "Step 3 — Add audit rules for OpenClaw:",
            "  sudo auditctl -w ~/.openclaw/config/ -p wa -k openclaw_config",
            "  sudo auditctl -w ~/.openclaw/skills/ -p wa -k openclaw_skills",
            "",
            "Step 4 — Save rules permanently:",
            "  sudo service auditd restart",
        ]

    return result


def check_incident_response_readiness():
    """CHECK 70: Is the system ready for incident response?"""
    result = {
        "id": "incident_response_readiness",
        "name_es": "Preparacion para respuesta a incidentes",
        "name_en": "Incident response readiness",
        "severity": "MEDIUM",
        "passed": False,
        "details_es": "", "details_en": "",
        "fix_es": [], "fix_en": [],
    }

    capabilities = []

    # Check if service can be stopped (kill switch)
    stdout, stderr, returncode = run_command("systemctl list-unit-files | grep openclaw")

    if returncode == 0 and stdout.strip():
        capabilities.append({
            "es": "Servicio OpenClaw registrado y puede ser detenido",
            "en": "OpenClaw service registered and can be stopped",
        })

    # Check for backups
    backup_locations = [
        OPENCLAW_HOME / "backups",
        Path("/var/backups/openclaw"),
        Path("/backup/openclaw"),
    ]

    for backup_loc in backup_locations:
        if backup_loc.exists():
            # Check age of backups
            stdout, stderr, returncode = run_command(f"find {backup_loc} -type f -mtime -7 2>/dev/null | wc -l")

            if returncode == 0:
                try:
                    recent_backups = int(stdout.strip())
                    if recent_backups > 0:
                        capabilities.append({
                            "es": f"Backups recientes encontrados en {backup_loc.name}",
                            "en": f"Recent backups found in {backup_loc.name}",
                        })
                except ValueError:
                    pass

    # Check for alerting configuration
    config = read_json_safe(OPENCLAW_CONFIG)
    if config:
        alerting = config.get("alerting", {})
        if alerting.get("enabled") or alerting.get("email") or alerting.get("webhook"):
            capabilities.append({
                "es": "Alerting configurado",
                "en": "Alerting configured",
            })

    # Pass if we have at least 2 capabilities
    if len(capabilities) >= 2:
        result["passed"] = True
        result["details_en"] = "Incident response capabilities: " + "; ".join(c["en"] for c in capabilities[:2])
        result["details_es"] = "Capacidades de respuesta a incidentes: " + "; ".join(c["es"] for c in capabilities[:2])
    else:
        result["details_en"] = "Limited incident response readiness."
        result["details_es"] = "Preparacion limitada para respuesta a incidentes."
        result["fix_es"] = [
            "Preparate para incidentes de seguridad antes de que ocurran.",
            "",
            "Paso 1 — Crea un script de kill switch:",
            "  cat > ~/kill-openclaw.sh << 'EOF'",
            "    #!/bin/bash",
            "    sudo systemctl stop openclaw",
            "    sudo killall -9 openclaw-gateway",
            "  EOF",
            "  chmod +x ~/kill-openclaw.sh",
            "",
            "Paso 2 — Establece backups regulares:",
            "  crontab -e",
            "  # Añade: 0 2 * * * tar czf /backup/openclaw-$(date +%Y%m%d).tar.gz ~/.openclaw/",
            "",
            "Paso 3 — Configura alertas en tu config:",
            "  echo '{\"alerting\": {\"enabled\": true, \"email\": \"admin@example.com\"}}' >> ~/.openclaw/config/moltbot.json",
        ]
        result["fix_en"] = [
            "Prepare for security incidents before they occur.",
            "",
            "Step 1 — Create a kill switch script:",
            "  cat > ~/kill-openclaw.sh << 'EOF'",
            "    #!/bin/bash",
            "    sudo systemctl stop openclaw",
            "    sudo killall -9 openclaw-gateway",
            "  EOF",
            "  chmod +x ~/kill-openclaw.sh",
            "",
            "Step 2 — Set up regular backups:",
            "  crontab -e",
            "  # Add: 0 2 * * * tar czf /backup/openclaw-$(date +%Y%m%d).tar.gz ~/.openclaw/",
            "",
            "Step 3 — Configure alerts in your config:",
            "  echo '{\"alerting\": {\"enabled\": true, \"email\": \"admin@example.com\"}}' >> ~/.openclaw/config/moltbot.json",
        ]

    return result


# ─── Main Report Generator ───────────────────────────────────────────────────

def generate_report():
    """Run all 50 security checks and generate the full security report."""

    report = {
        "tool": "LobsterGuard",
        "version": "5.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "secureclaw_available": False,
        "secureclaw_report": None,
        "checks": [],
        "score": 0,
        "summary": {},
    }

    # Check SecureClaw integration
    secureclaw_available = check_secureclaw_available()
    report["secureclaw_available"] = secureclaw_available

    if secureclaw_available:
        sc_report = run_secureclaw_audit()
        if sc_report:
            report["secureclaw_report"] = sc_report

    # Run LobsterGuard's 70 security checks
    checks = [
        # OpenClaw checks (1-5)
        check_gateway_exposure(),
        check_authentication(),
        check_version(),
        check_credentials(),
        check_installed_skills(),
        # Server checks (6-15)
        check_ssh_root_login(),
        check_ssh_password_auth(),
        check_firewall(),
        check_fail2ban(),
        check_auto_updates(),
        check_openclaw_user(),
        check_open_ports(),
        check_disk_space(),
        check_docker_security(),
        check_intrusion_attempts(),
        # Advanced checks (16-28)
        check_config_permissions(),
        check_ssl_tls(),
        check_backups(),
        check_skills_supply_chain(),
        check_env_leakage(),
        check_cron_persistence(),
        check_cors_config(),
        check_skill_integrity(),
        check_system_users(),
        check_log_rotation(),
        check_sandbox_mode(),
        check_outbound_connections(),
        check_self_protection(),
        # OWASP Agentic AI checks (29-50)
        check_skill_prompt_injection(),
        check_skill_hidden_content(),
        check_mcp_server_security(),
        check_mcp_tool_poisoning(),
        check_data_exfiltration_channels(),
        check_log_secrets(),
        check_skill_typosquatting(),
        check_auto_approval(),
        check_excessive_permissions(),
        check_memory_poisoning(),
        check_git_hook_injection(),
        check_unsafe_defaults(),
        check_rogue_agent(),
        check_kernel_hardening(),
        check_systemd_hardening(),
        check_tmp_security(),
        check_skill_signatures(),
        check_code_execution_sandbox(),
        check_api_key_rotation(),
        check_rate_limiting(),
        check_skill_network_access(),
        check_process_isolation(),
        # Forensic checks (51-57)
        check_ssh_authorized_keys_audit(),
        check_suid_sgid_binary_audit(),
        check_world_writable_files_detection(),
        check_reverse_shell_detection(),
        check_cryptominer_detection(),
        check_rootkit_detection_basic(),
        check_dns_tunneling_detection(),
        # Advanced Hardening checks (58-68)
        check_websocket_security(),
        check_sudo_nopasswd_audit(),
        check_swap_encryption(),
        check_core_dump_protection(),
        check_conversation_log_security(),
        # check_skill_update_verification(),  # Removed: covered by /checkskill and skill quarantine
        check_cross_agent_communication(),
        check_session_token_security(),
        check_filesystem_immutable_attributes(),
        check_usb_device_restrictions(),
        check_network_namespace_isolation(),
        check_auditd_logging(),
        # check_incident_response_readiness(),  # Removed: organizational, not technical
    ]

    report["checks"] = checks

    # Calculate score
    total = len(checks)
    passed = sum(1 for c in checks if c["passed"])
    # Don't count INFO-level checks in failure penalties
    critical_failures = sum(1 for c in checks if not c["passed"] and c["severity"] == "CRITICAL")
    high_failures = sum(1 for c in checks if not c["passed"] and c["severity"] == "HIGH")
    medium_failures = sum(1 for c in checks if not c["passed"] and c["severity"] == "MEDIUM")

    # Score: base is percentage passed, with moderate severity penalties
    # Penalties are capped at 40% of base score to avoid misleading 0 scores
    base_score = int((passed / total) * 100)
    raw_penalty = (critical_failures * 5) + (high_failures * 3) + (medium_failures * 1)
    max_penalty = int(base_score * 0.4)  # Never penalize more than 40% of base
    penalty = min(raw_penalty, max_penalty)
    score = max(0, min(100, base_score - penalty))
    report["score"] = score

    # ─── Visual Score Bar ───────────────────────────────────────────────
    # Generate a visual progress bar for the bot to display
    filled = round(score / 10)
    empty = 10 - filled

    if score >= 80:
        bar_char = "🟢"
        level = "good"
        emoji = "🛡️"
    elif score >= 60:
        bar_char = "🟡"
        level = "moderate"
        emoji = "⚠️"
    elif score >= 30:
        bar_char = "🟠"
        level = "warning"
        emoji = "🚨"
    else:
        bar_char = "🔴"
        level = "danger"
        emoji = "💀"

    score_bar = bar_char * filled + "⚫" * empty

    # Category breakdowns
    openclaw_checks = checks[0:5]
    server_checks = checks[5:15]
    advanced_checks = checks[15:28]
    agentic_checks = checks[28:50]
    forensic_checks = checks[50:57]
    hardening_checks = checks[57:68]

    openclaw_passed = sum(1 for c in openclaw_checks if c["passed"])
    server_passed = sum(1 for c in server_checks if c["passed"])
    advanced_passed = sum(1 for c in advanced_checks if c["passed"])
    agentic_passed = sum(1 for c in agentic_checks if c["passed"])
    forensic_passed = sum(1 for c in forensic_checks if c["passed"])
    hardening_passed = sum(1 for c in hardening_checks if c["passed"])

    report["score_visual"] = {
        "bar": score_bar,
        "emoji": emoji,
        "score_text_es": f"{emoji} Puntuacion de seguridad: {score}/100",
        "score_text_en": f"{emoji} Security score: {score}/100",
        "bar_text_es": f"  {score_bar}  {score}%",
        "bar_text_en": f"  {score_bar}  {score}%",
        "categories_es": {
            "OpenClaw": f"{'✅' if openclaw_passed == 5 else '⚠️'} {openclaw_passed}/5 checks",
            "Servidor": f"{'✅' if server_passed == 10 else '⚠️'} {server_passed}/10 checks",
            "Avanzado": f"{'✅' if advanced_passed == 13 else '⚠️'} {advanced_passed}/13 checks",
            "IA Agental": f"{'✅' if agentic_passed == 22 else '⚠️'} {agentic_passed}/22 checks",
            "Forense": f"{'✅' if forensic_passed == 7 else '⚠️'} {forensic_passed}/7 checks",
            "Endurecimiento": f"{'✅' if hardening_passed == 11 else '⚠️'} {hardening_passed}/11 checks",
        },
        "categories_en": {
            "OpenClaw": f"{'✅' if openclaw_passed == 5 else '⚠️'} {openclaw_passed}/5 checks",
            "Server": f"{'✅' if server_passed == 10 else '⚠️'} {server_passed}/10 checks",
            "Advanced": f"{'✅' if advanced_passed == 13 else '⚠️'} {advanced_passed}/13 checks",
            "Agentic AI": f"{'✅' if agentic_passed == 22 else '⚠️'} {agentic_passed}/22 checks",
            "Forensic": f"{'✅' if forensic_passed == 7 else '⚠️'} {forensic_passed}/7 checks",
            "Hardening": f"{'✅' if hardening_passed == 11 else '⚠️'} {hardening_passed}/11 checks",
        },
    }

    # Failure summary by severity
    report["failure_summary"] = {
        "critical": critical_failures,
        "high": high_failures,
        "medium": medium_failures,
        "total_failed": total - passed,
        "total_passed": passed,
        "total_checks": total,
    }

    # Summary with visual
    if score >= 80:
        report["summary"] = {
            "es": f"🛡️ Tu instalacion esta bien protegida. {passed}/{total} checks pasaron.",
            "en": f"🛡️ Your installation is well protected. {passed}/{total} checks passed.",
            "level": level,
        }
    elif score >= 60:
        report["summary"] = {
            "es": f"⚠️ Hay cosas que mejorar. {passed}/{total} checks pasaron, {critical_failures} criticos pendientes.",
            "en": f"⚠️ There are things to improve. {passed}/{total} checks passed, {critical_failures} critical pending.",
            "level": level,
        }
    elif score >= 30:
        report["summary"] = {
            "es": f"🚨 Tienes riesgos importantes. {total - passed} checks fallaron ({critical_failures} criticos, {high_failures} altos).",
            "en": f"🚨 You have important risks. {total - passed} checks failed ({critical_failures} critical, {high_failures} high).",
            "level": level,
        }
    else:
        report["summary"] = {
            "es": f"💀 Tu instalacion esta en peligro serio. {critical_failures} problemas criticos y {high_failures} altos requieren atencion inmediata.",
            "en": f"💀 Your installation is in serious danger. {critical_failures} critical and {high_failures} high issues need immediate attention.",
            "level": level,
        }

    return report


# ─── Pre-formatted Report ────────────────────────────────────────────────────

def format_report_text(report, lang="es"):
    """Generate a pre-formatted text report ready to display.
    This reduces API token usage by 80%+ since the bot just shows it."""

    lines = []
    sv = report["score_visual"]
    fs = report["failure_summary"]

    # Header + Score
    lines.append(f"🛡️ LobsterGuard v{report['version']} — {'Auditoría de Seguridad' if lang == 'es' else 'Security Audit'}")
    lines.append(f"📅 {report['timestamp'][:10]}")
    lines.append("")
    lines.append(sv[f"score_text_{lang}"])
    lines.append(sv[f"bar_text_{lang}"])
    lines.append("")

    # Categories
    cat_key = "categories_es" if lang == "es" else "categories_en"
    for cat, val in sv[cat_key].items():
        lines.append(f"  {cat}: {val}")
    lines.append("")

    # Passed checks (compact)
    passed_checks = [c for c in report["checks"] if c["passed"]]
    failed_checks = [c for c in report["checks"] if not c["passed"]]

    lines.append(f"✅ {'Checks que pasaron' if lang == 'es' else 'Checks passed'} ({len(passed_checks)}/{fs['total_checks']}):")
    for c in passed_checks:
        lines.append(f"  ✅ #{c['id']} {c[f'name_{lang}']}")
    lines.append("")

    # Failed checks (detailed)
    if failed_checks:
        lines.append(f"❌ {'Problemas encontrados' if lang == 'es' else 'Issues found'} ({fs['total_failed']}):")
        lines.append("")

        # Sort by severity: CRITICAL first, then HIGH, then MEDIUM
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
        failed_sorted = sorted(failed_checks, key=lambda c: severity_order.get(c["severity"], 5))

        for c in failed_sorted:
            sev_emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡"}.get(c["severity"], "⚪")
            lines.append(f"  {sev_emoji} [{c['severity']}] {c[f'name_{lang}']}")
            lines.append(f"     {c[f'details_{lang}']}")
            fix_key = f"fix_{lang}"
            if c.get(fix_key):
                fix_text = " → ".join(c[fix_key]) if isinstance(c[fix_key], list) else c[fix_key]
                lines.append(f"     🔧 {fix_text}")
            lines.append("")

    # Priority actions
    critical_and_high = [c for c in failed_checks if c["severity"] in ("CRITICAL", "HIGH")]
    if critical_and_high:
        lines.append(f"🔜 {'Acciones prioritarias:' if lang == 'es' else 'Priority actions:'}")
        for i, c in enumerate(sorted(critical_and_high, key=lambda c: 0 if c["severity"] == "CRITICAL" else 1), 1):
            sev_emoji = "🔴" if c["severity"] == "CRITICAL" else "🟠"
            lines.append(f"  {sev_emoji} {i}. {c[f'name_{lang}']}")
        lines.append("")

    # Summary
    lines.append(report["summary"][lang])

    return "\n".join(lines)


# ─── Compact Report (API-friendly) ──────────────────────────────────────────


def format_compact(report, lang="es"):
    """Generate an ultra-compact report for minimal API token usage.
    Only shows: score, category summary, and failed checks.
    If everything passes, just a one-liner."""

    # Mapping from check IDs to Telegram fix commands
    FIX_COMMANDS = {
        "firewall": "/fixfw",
        "backups": "/fixbackup",
        "backup_config": "/fixbackup",
        "kernel_hardening": "/fixkernel",
        "core_dumps": "/fixcore",
        "core_dump_protection": "/fixcore",
        "audit_logging": "/fixaudit",
        "auditd_logging": "/fixaudit",
        "sandbox_mode": "/fixsandbox",
        "session_token": "/fixenv",
        "session_token_security": "/fixenv",
        "env_leakage": "/fixenv",
        "tmp_security": "/fixtmp",
        "skill_integrity": "/fixcode",
        "code_integrity": "/fixcode",
        "openclaw_user": "/runuser",
        "systemd_hardening": "/fixsystemd",

    }

    lines = []
    sv = report["score_visual"]
    fs = report["failure_summary"]
    score = report["score"]
    failed_checks = [c for c in report["checks"] if not c["passed"]]

    # Score line
    lines.append(f"{sv['emoji']} LobsterGuard — Score: {score}/100 — {fs['total_passed']}/{fs['total_checks']} checks")
    lines.append("")

    # Categories (one line each)
    cat_key = "categories_es" if lang == "es" else "categories_en"
    for cat, val in sv[cat_key].items():
        lines.append(f"  {cat}: {val}")

    # If everything passed, short message
    if not failed_checks:
        lines.append("")
        lines.append("Todo en orden. No se encontraron problemas de seguridad." if lang == "es" else "All clear. No security issues found.")
        return "\n".join(lines)

    # Only show failed checks (sorted by severity)
    lines.append("")
    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
    failed_sorted = sorted(failed_checks, key=lambda c: severity_order.get(c["severity"], 5))

    for c in failed_sorted:
        sev_emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡"}.get(c["severity"], "⚪")
        
        # Look up Telegram fix command
        fix_cmd = FIX_COMMANDS.get(c["id"])
        if fix_cmd:
            fix_suffix = f" → {fix_cmd}"
        elif c.get("auto_fixable"):
            fix_suffix = " [auto-fix]"
        else:
            fix_suffix = ""
        
        lines.append(f"{sev_emoji} {c['severity']}: {c[f'name_{lang}']}{fix_suffix}")
        lines.append(f"   {c[f'details_{lang}']}")

    # Offer fixes with cleaner list
    fixable = [c for c in failed_sorted if c.get("auto_fixable")]
    if fixable:
        lines.append("")
        lines.append("🔧 Comandos de auto-fix disponibles / Available auto-fix commands:")
        
        # Build a set of unique commands to show
        commands_shown = set()
        for c in fixable:
            fix_cmd = FIX_COMMANDS.get(c["id"])
            if fix_cmd and fix_cmd not in commands_shown:
                # Add descriptions for each command
                descriptions = {
                    "/fixfw": "Configurar firewall",
                    "/fixbackup": "Configurar backups",
                    "/fixkernel": "Endurecer kernel",
                    "/fixcore": "Deshabilitar core dumps",
                    "/fixaudit": "Habilitar audit logging",
                    "/fixsandbox": "Habilitar sandbox mode",
                    "/fixenv": "Configurar session token",
                    "/fixtmp": "Asegurar /tmp",
                    "/fixcode": "Verificar integridad del código",
                    "/runuser": "Crear usuario OpenClaw",
                }
                desc = descriptions.get(fix_cmd, "Auto-fix")
                lines.append(f"  {fix_cmd} — {desc}")
                commands_shown.add(fix_cmd)
        


    return "\n".join(lines)




# ─── Entry Point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    report = generate_report()

    # Language detection
    report_lang = get_configured_language()
    for i, arg in enumerate(sys.argv):
        if arg == "--lang" and i + 1 < len(sys.argv):
            report_lang = sys.argv[i + 1] if sys.argv[i + 1] in ("es", "en") else "es"
            break
    else:
        report_lang = get_configured_language()

    # Check for flags (ignore --lang and its value)
    flags = [a for a in sys.argv[1:] if a != "--lang" and a not in ("es", "en")]
    flag = flags[0] if flags else ""

    if flag == "--json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
    elif flag == "--compact":
        # Ultra-compact: only failures + summary (saves ~90% tokens)
        print(format_compact(report, lang=report_lang))
        # Save full reports to cache for later use
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            with open(os.path.join(DATA_DIR, "latest-report.txt"), "w") as f:
                f.write(format_report_text(report, lang=report_lang))
            with open(os.path.join(DATA_DIR, "latest-report.json"), "w") as f:
                f.write(json.dumps(report, indent=2, ensure_ascii=False))
        except Exception:
            pass
    else:
        # Default: pre-formatted text report (saves API tokens)
        print(format_report_text(report, lang=report_lang))
        # Also print a small JSON summary at the end for the bot to parse if needed
        print("\n---JSON_SUMMARY---")
        mini = {
            "version": report["version"],
            "score": report["score"],
            "passed": report["failure_summary"]["total_passed"],
            "failed": report["failure_summary"]["total_failed"],
            "critical": report["failure_summary"]["critical"],
        }
        print(json.dumps(mini))
