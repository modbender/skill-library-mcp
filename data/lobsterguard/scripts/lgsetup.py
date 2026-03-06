#!/usr/bin/env python3
"""
LobsterGuard Setup Assistant
Verifies and configures the installation
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from telegram_utils import get_telegram_config, send_telegram

# Configuration

BOT_TOKEN, CHAT_ID = get_telegram_config()
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
OPENCLAW_DIR = os.path.expanduser("~/.openclaw")
QUARANTINE_DIR = os.path.join(OPENCLAW_DIR, "quarantine")

# Emoji and formatting
PASS_MARK = "✅"
FAIL_MARK = "❌"
DIVIDER = "━━━━━━━━━━━━━━━━━━━━━"


def run_command(cmd, shell=False):
    """Run a command and return (success, output)"""
    try:
        if shell:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        else:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "", "Command timeout"
    except Exception as e:
        return False, "", str(e)


def check_openclaw_running():
    """Check if openclaw-gateway is running"""
    success, output, _ = run_command("pgrep -f 'openclaw-gateway' > /dev/null 2>&1", shell=True)
    if success:
        return True, "OpenClaw está ejecutándose / OpenClaw is running"
    else:
        return False, "OpenClaw no está ejecutándose / OpenClaw is not running"


def check_directories_exist():
    """Check if required OpenClaw directories exist"""
    required_dirs = [
        OPENCLAW_DIR,
        os.path.join(OPENCLAW_DIR, "skills"),
        os.path.join(OPENCLAW_DIR, "plugins")
    ]
    
    missing = []
    for dir_path in required_dirs:
        if not os.path.isdir(dir_path):
            missing.append(dir_path)
    
    if not missing:
        return True, "Directorios de OpenClaw encontrados / OpenClaw directories found"
    else:
        missing_str = ", ".join([os.path.basename(d) for d in missing])
        return False, f"Directorios faltantes / Missing directories: {missing_str}"


def check_core_scripts():
    """Check if core scripts exist in SCRIPT_DIR"""
    required_scripts = [
        "check.py",
        "fix_engine.py",
        "skill_scanner.py",
        "autoscan.py",
        "quarantine_watcher.py"
    ]
    
    missing = []
    for script in required_scripts:
        script_path = os.path.join(SCRIPT_DIR, script)
        if not os.path.isfile(script_path):
            missing.append(script)
    
    if not missing:
        return True, f"Scripts principales presentes ({len(required_scripts)}/{len(required_scripts)}) / Core scripts present ({len(required_scripts)}/{len(required_scripts)})"
    else:
        missing_str = ", ".join(missing)
        return False, f"Scripts faltantes / Missing scripts: {missing_str}"


def check_extension_synced():
    """Check if extension/dist/index.js exists"""
    ext_path = os.path.join(OPENCLAW_DIR, "extensions", "lobsterguard-shield", "dist", "index.js")
    
    if os.path.isfile(ext_path):
        return True, "Extensión sincronizada / Extension synced"
    else:
        return False, "Extensión no encontrada / Extension not found"


def check_quarantine_folder():
    """Check/create quarantine folder"""
    try:
        if os.path.isdir(QUARANTINE_DIR):
            return True, "Carpeta de cuarentena lista / Quarantine folder ready"
        else:
            os.makedirs(QUARANTINE_DIR, mode=0o755, exist_ok=True)
            return True, "Carpeta de cuarentena creada / Quarantine folder created"
    except Exception as e:
        return False, f"Error creando carpeta / Error creating folder: {str(e)}"


def check_systemd_services():
    """Check if systemd services are loaded"""
    success, output, _ = run_command("systemctl --user list-unit-files | grep lobsterguard", shell=True)
    
    required_services = ["lobsterguard-autoscan.timer", "lobsterguard-quarantine.service"]
    
    if not output:
        missing_str = ", ".join(required_services)
        return False, f"Servicios faltantes / Missing services: {missing_str}"
    
    missing = []
    for service in required_services:
        if service not in output:
            missing.append(service)
    
    if not missing:
        return True, "Servicios systemd configurados / Systemd services configured"
    else:
        missing_str = ", ".join(missing)
        return False, f"Servicios faltantes / Missing services: {missing_str}"


def check_blacklist_file():
    """Check if skill blacklist file exists, create if missing"""
    data_dir = os.path.join(BASE_DIR, "data")
    blacklist_path = os.path.join(data_dir, "skill_blacklist.json")
    
    if os.path.isfile(blacklist_path):
        return True, "Lista negra de skills cargada / Skill blacklist loaded"
    else:
        try:
            os.makedirs(data_dir, exist_ok=True)
            with open(blacklist_path, "w") as f:
                json.dump({"blacklisted_skills": [], "updated": ""}, f, indent=2)
            return True, "Lista negra creada / Blacklist created"
        except Exception:
            return False, "No se pudo crear lista negra / Could not create blacklist"


def check_initial_scan():
    """Run initial scan and extract score"""
    check_script = os.path.join(SCRIPT_DIR, "check.py")
    
    if not os.path.isfile(check_script):
        return False, "Error ejecutando escaneo / Error running scan"
    
    try:
        result = subprocess.run(
            ["python3", "-W", "ignore", check_script, "--compact"],
            capture_output=True, text=True, timeout=300
        )
        output = result.stdout
        
        import re
        score_match = re.search(r'Score:\s*(\d+)/100', output)
        checks_match = re.search(r'(\d+/\d+)\s*checks', output)
        
        if score_match:
            score = score_match.group(1)
            checks = checks_match.group(1) if checks_match else "?"
            return True, f"Score actual / Current score: {score}/100 — {checks} checks"
        
        return True, "Escaneo completado / Scan completed"
    except subprocess.TimeoutExpired:
        return False, "Timeout ejecutando escaneo / Scan timeout"
    except Exception as e:
        return False, f"Error ejecutando escaneo / Error running scan"


def format_output(results, telegram_mode=False):
    """Format check results"""
    lines = []
    
    if telegram_mode:
        lines.append("🛡 LobsterGuard Setup")
        lines.append("")
    else:
        lines.append("LobsterGuard Setup Assistant")
        lines.append("=" * 50)
        lines.append("")
    
    passed_count = 0
    total_count = len(results)
    
    for passed, message in results:
        if passed:
            passed_count += 1
            mark = PASS_MARK if telegram_mode else "[✓]"
        else:
            mark = FAIL_MARK if telegram_mode else "[✗]"
        
        lines.append(f"{mark} {message}")
    
    lines.append("")
    lines.append(DIVIDER if telegram_mode else "-" * 50)
    lines.append(f"Resultado / Result: {passed_count}/{total_count} checks passed")
    lines.append("")
    
    lines.append("Comandos disponibles / Available commands:")
    lines.append("/scan /fixlist /checkskill /lgsetup /cleanup")
    lines.append("")
    
    lines.append("Carpeta cuarentena / Quarantine folder:")
    lines.append(QUARANTINE_DIR + "/")
    
    return "\n".join(lines)


def main():
    """Run all checks and display results"""
    # Parse arguments
    telegram_mode = "--telegram" in sys.argv
    
    # Run all checks
    results = [
        check_openclaw_running(),
        check_directories_exist(),
        check_core_scripts(),
        check_extension_synced(),
        check_quarantine_folder(),
        check_systemd_services(),
        check_blacklist_file(),
        check_initial_scan()
    ]
    
    # Format and print output
    output = format_output(results, telegram_mode=telegram_mode)
    print(output)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
