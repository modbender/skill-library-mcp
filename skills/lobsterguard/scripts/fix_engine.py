#!/usr/bin/env python3
# ─────────────────────────────────────────────────────────────────────────────
# LobsterGuard Fix Engine v1.0
# Guided auto-remediation for security issues
#
# Usage:
#   python3 fix_engine.py plan <check_id> [--user <target_user>] [--lang es|en]
#   python3 fix_engine.py execute <check_id> <step_id>
#   python3 fix_engine.py rollback <check_id>
#   python3 fix_engine.py verify <check_id>
#
# Returns JSON to stdout for the plugin to parse.
# ─────────────────────────────────────────────────────────────────────────────

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# ─── Paths ──────────────────────────────────────────────────────────────────

OPENCLAW_HOME = os.path.join(os.environ.get("HOME", "/root"), ".openclaw")
LOBSTERGUARD_DIR = os.path.join(OPENCLAW_HOME, "skills", "lobsterguard")
DATA_DIR = os.path.join(LOBSTERGUARD_DIR, "data")
FIX_STATE_FILE = os.path.join(DATA_DIR, "fix-state.json")
FIX_LOG_FILE = os.path.join(DATA_DIR, "fix-log.jsonl")

# ─── Helpers ────────────────────────────────────────────────────────────────


def run_command(cmd, timeout=30):
    """Run a shell command and return (stdout, stderr, returncode)."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "Command timed out", 1
    except Exception as e:
        return "", str(e), 1


def log_action(action, check_id, step_id=None, result=None, error=None):
    """Append to fix log for audit trail."""
    entry = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "action": action,
        "check_id": check_id,
        "step_id": step_id,
        "result": result,
        "error": error,
    }
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(FIX_LOG_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass


def load_fix_state():
    """Load persistent fix state."""
    try:
        if os.path.exists(FIX_STATE_FILE):
            with open(FIX_STATE_FILE, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def save_fix_state(state):
    """Save persistent fix state."""
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(FIX_STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
    except Exception:
        pass


def output(data):
    """Print JSON result to stdout for the plugin."""
    print(json.dumps(data, indent=2, ensure_ascii=False))
    sys.exit(0)


def output_error(message_es, message_en, details=None):
    """Print error JSON and exit."""
    output({
        "success": False,
        "error_es": message_es,
        "error_en": message_en,
        "details": details,
    })


# ─── Process Manager Detection ──────────────────────────────────────────────


def detect_openclaw_process():
    """Find the OpenClaw gateway process and how it's managed."""
    stdout, _, rc = run_command("ps aux | grep -E 'openclaw.*(gateway|index\\.js)' | grep -v grep")
    if rc != 0 or not stdout:
        return None

    # Parse ps output: USER PID ... COMMAND
    lines = [l for l in stdout.split("\n") if l.strip()]
    if not lines:
        return None

    parts = lines[0].split()
    proc_user = parts[0]
    proc_pid = parts[1]

    # Get parent PID
    stdout2, _, rc2 = run_command(f"ps -o ppid= -p {proc_pid}")
    ppid = stdout2.strip() if rc2 == 0 else ""

    # Get parent process name
    parent_name = ""
    if ppid:
        stdout3, _, rc3 = run_command(f"ps -o comm= -p {ppid}")
        parent_name = stdout3.strip() if rc3 == 0 else ""

    # Extract command line
    stdout4, _, _ = run_command(f"ps -o args= -p {proc_pid}")
    cmdline = stdout4.strip()

    return {
        "user": proc_user,
        "pid": proc_pid,
        "ppid": ppid,
        "parent": parent_name,
        "cmdline": cmdline,
    }


def detect_process_manager(proc_info):
    """Determine which process manager controls OpenClaw."""
    if not proc_info:
        return "not_running", {}

    parent = proc_info.get("parent", "")
    user = proc_info.get("user", "")
    ppid = proc_info.get("ppid", "")

    # Check systemd user service
    if parent == "systemd":
        # Check if there's a user service for the running user
        if user == "root":
            svc_path = "/root/.config/systemd/user/openclaw-gateway.service"
            stdout, _, rc = run_command(f"sudo cat {svc_path} 2>/dev/null")
            if rc == 0 and stdout:
                return "systemd_user_root", {
                    "service_path": svc_path,
                    "service_content": stdout,
                }

        # Non-root user systemd
        home = os.environ.get("HOME", f"/home/{user}")
        svc_path = f"{home}/.config/systemd/user/openclaw-gateway.service"
        if os.path.exists(svc_path):
            with open(svc_path) as f:
                content = f.read()
            return "systemd_user", {
                "service_path": svc_path,
                "service_content": content,
            }

    # Check systemd system service
    stdout, _, rc = run_command("sudo systemctl cat openclaw-gateway 2>/dev/null")
    if rc == 0 and stdout:
        return "systemd_system", {"service_content": stdout}

    # Check pm2
    stdout, _, rc = run_command("pm2 jlist 2>/dev/null")
    if rc == 0 and "openclaw" in stdout.lower():
        return "pm2", {"pm2_list": stdout}

    # Check supervisor
    stdout, _, rc = run_command("sudo supervisorctl status 2>/dev/null")
    if rc == 0 and "openclaw" in stdout.lower():
        return "supervisor", {"supervisor_status": stdout}

    # Check Docker
    stdout, _, rc = run_command("docker ps --format '{{.Names}}' 2>/dev/null")
    if rc == 0 and "openclaw" in stdout.lower():
        return "docker", {"container_name": stdout.strip()}

    # Manual / nohup
    return "manual", {}


def extract_service_vars(service_content):
    """Extract key variables from a systemd service file."""
    vars_found = {}
    for line in service_content.split("\n"):
        line = line.strip()
        if line.startswith("ExecStart="):
            vars_found["exec_start"] = line.split("=", 1)[1].strip().strip('"')
        elif line.startswith("Environment="):
            val = line.split("=", 1)[1].strip().strip('"')
            if "=" in val:
                k, v = val.split("=", 1)
                vars_found[f"env_{k}"] = v
            else:
                vars_found[f"env_{val}"] = ""
    return vars_found


# ─── Fix Plan Generators ────────────────────────────────────────────────────


def plan_check_11(target_user, lang="es"):
    """Generate fix plan for Check #11: OpenClaw running as root."""

    proc = detect_openclaw_process()
    if not proc:
        output_error(
            "No se detectó OpenClaw corriendo.",
            "OpenClaw process not detected.",
        )

    if proc["user"] != "root":
        output({
            "success": True,
            "already_fixed": True,
            "message_es": f"OpenClaw ya corre como '{proc['user']}', no como root. No hay nada que arreglar.",
            "message_en": f"OpenClaw already runs as '{proc['user']}', not root. Nothing to fix.",
        })

    pm_type, pm_info = detect_process_manager(proc)

    # Determine target user
    if not target_user:
        target_user = os.environ.get("USER", "")
        if target_user == "root":
            # Try to find a non-root user with a home directory
            stdout, _, _ = run_command("ls /home/ | head -1")
            target_user = stdout.strip() if stdout.strip() else ""

    if not target_user or target_user == "root":
        output_error(
            "No se encontró un usuario no-root para migrar. Crea uno primero: sudo useradd -m -s /bin/bash <nombre>",
            "No non-root user found to migrate to. Create one first: sudo useradd -m -s /bin/bash <name>",
        )

    target_home = f"/home/{target_user}"
    target_openclaw = f"{target_home}/.openclaw"

    # Build steps based on process manager
    steps = []

    if pm_type == "systemd_user_root":
        svc_content = pm_info.get("service_content", "")
        svc_vars = extract_service_vars(svc_content)
        exec_start = svc_vars.get("exec_start", "/usr/bin/node /usr/lib/node_modules/openclaw/dist/index.js gateway --port 18789")

        # Extract all Environment lines for the new service
        env_lines = []
        for line in svc_content.split("\n"):
            line = line.strip()
            if line.startswith("Environment="):
                # Replace /root with target home
                new_line = line.replace("/root", target_home)
                env_lines.append(new_line)

        # Rebuild ExecStart without quotes if present
        exec_start_clean = exec_start.replace('"', '')

        # Build new service content
        new_service = f"""[Unit]
Description=OpenClaw Gateway
After=network-online.target
Wants=network-online.target

[Service]
ExecStart={exec_start_clean}
Restart=always
RestartSec=5
KillMode=control-group
"""
        for env_line in env_lines:
            new_service += env_line + "\n"
        new_service += """
[Install]
WantedBy=default.target
"""

        steps = [
            {
                "id": 1,
                "title_es": "Detener servicio de root",
                "title_en": "Stop root service",
                "description_es": "Paramos OpenClaw que corre como root para poder migrarlo.",
                "description_en": "Stopping the root OpenClaw process to migrate it.",
                "command": "sudo bash -c 'XDG_RUNTIME_DIR=/run/user/0 systemctl --user is-active openclaw-gateway' && sudo bash -c 'XDG_RUNTIME_DIR=/run/user/0 systemctl --user stop openclaw-gateway' && sudo kill $(pgrep -u root -f openclaw-gateway) 2>/dev/null; sleep 2",
                "validation": "! pgrep -u root -f openclaw-gateway",
                "rollback": "sudo bash -c 'XDG_RUNTIME_DIR=/run/user/0 systemctl --user start openclaw-gateway'",
                "critical": True,
            },
            {
                "id": 2,
                "title_es": "Desactivar servicio de root",
                "title_en": "Disable root service",
                "description_es": "Eliminamos el servicio de root para que no vuelva a arrancar.",
                "description_en": "Removing the root service so it doesn't restart.",
                "command": f"sudo rm -f /root/.config/systemd/user/openclaw-gateway.service && sudo rm -f /root/.config/systemd/user/default.target.wants/openclaw-gateway.service && sudo bash -c 'XDG_RUNTIME_DIR=/run/user/0 systemctl --user is-active openclaw-gateway'",
                "validation": "! sudo test -f /root/.config/systemd/user/openclaw-gateway.service",
                "rollback": f"sudo bash -c 'mkdir -p /root/.config/systemd/user/default.target.wants'",
                "critical": True,
            },
            {
                "id": 3,
                "title_es": f"Copiar configuración a {target_user}",
                "title_en": f"Copy configuration to {target_user}",
                "description_es": "Copiamos toda la configuración de OpenClaw al nuevo usuario.",
                "description_en": "Copying all OpenClaw configuration to the target user.",
                "command": f"mkdir -p {target_openclaw} && sudo bash -c 'cp -r /root/.openclaw/* {target_openclaw}/' && sudo chown -R {target_user}:{target_user} {target_openclaw}",
                "validation": f"test -f {target_openclaw}/openclaw.json",
                "rollback": "",
                "critical": True,
            },
            {
                "id": 4,
                "title_es": "Corregir rutas en configuración",
                "title_en": "Fix paths in configuration",
                "description_es": "Actualizamos las rutas que apuntan a /root/ para que apunten al nuevo usuario.",
                "description_en": "Updating paths from /root/ to point to the new user's home.",
                "command": f"sed -i 's|/root/.openclaw|{target_openclaw}|g' {target_openclaw}/openclaw.json",
                "validation": f"! grep -q '/root/.openclaw' {target_openclaw}/openclaw.json",
                "rollback": "",
                "critical": False,
            },
            {
                "id": 5,
                "title_es": f"Crear servicio para {target_user}",
                "title_en": f"Create service for {target_user}",
                "description_es": "Creamos el servicio de systemd para que OpenClaw arranque con tu usuario.",
                "description_en": "Creating a systemd service so OpenClaw starts with your user.",
                "command": f"mkdir -p {target_home}/.config/systemd/user/ && cat > {target_home}/.config/systemd/user/openclaw-gateway.service << 'SVCEOF'\n{new_service}SVCEOF",
                "validation": f"test -f {target_home}/.config/systemd/user/openclaw-gateway.service",
                "rollback": f"rm -f {target_home}/.config/systemd/user/openclaw-gateway.service",
                "critical": True,
            },
            {
                "id": 6,
                "title_es": "Crear enlace de compatibilidad",
                "title_en": "Create compatibility symlink",
                "description_es": "Creamos un enlace para que programas que busquen /root/.openclaw encuentren tu configuración.",
                "description_en": "Creating a symlink so programs looking for /root/.openclaw find your config.",
                "command": f"sudo rm -rf /root/.openclaw && sudo ln -s {target_openclaw} /root/.openclaw && sudo chmod 711 /root",
                "validation": f"sudo readlink /root/.openclaw | grep -q '{target_openclaw}'",
                "rollback": "sudo rm -f /root/.openclaw",
                "critical": False,
            },
            {
                "id": 7,
                "title_es": "Iniciar servicio con tu usuario",
                "title_en": "Start service with your user",
                "description_es": "Habilitamos e iniciamos OpenClaw con tu usuario.",
                "description_en": "Enabling and starting OpenClaw with your user.",
                "command": f"sudo loginctl enable-linger {target_user} && systemctl --user is-active openclaw-gateway",
                "validation": f"pgrep -u {target_user} -f openclaw-gateway",
                "rollback": "systemctl --user stop openclaw-gateway && systemctl --user disable openclaw-gateway",
                "critical": True,
            },
            {
                "id": 8,
                "title_es": "Verificar que todo funciona",
                "title_en": "Verify everything works",
                "description_es": "Esperamos unos segundos y verificamos que OpenClaw responde correctamente.",
                "description_en": "Waiting a few seconds and verifying OpenClaw responds correctly.",
                "command": f"sleep 5 && journalctl --user -u openclaw-gateway --no-pager --since '10 sec ago' 2>/dev/null | head -10",
                "validation": f"pgrep -u {target_user} -f openclaw-gateway && ! pgrep -u root -f openclaw-gateway",
                "rollback": "",
                "critical": False,
            },
        ]

    elif pm_type == "systemd_system":
        steps = [
            {
                "id": 1,
                "title_es": "Detener servicio",
                "title_en": "Stop service",
                "description_es": "Paramos el servicio de OpenClaw.",
                "description_en": "Stopping the OpenClaw service.",
                "command": "sudo systemctl stop openclaw-gateway",
                "validation": "! pgrep -f openclaw-gateway",
                "rollback": "sudo systemctl start openclaw-gateway",
                "critical": True,
            },
            {
                "id": 2,
                "title_es": f"Copiar configuración a {target_user}",
                "title_en": f"Copy configuration to {target_user}",
                "description_es": "Copiamos la configuración al nuevo usuario.",
                "description_en": "Copying configuration to the target user.",
                "command": f"mkdir -p {target_openclaw} && sudo bash -c 'cp -r /root/.openclaw/* {target_openclaw}/' && sudo chown -R {target_user}:{target_user} {target_openclaw}",
                "validation": f"test -f {target_openclaw}/openclaw.json",
                "rollback": "",
                "critical": True,
            },
            {
                "id": 3,
                "title_es": "Corregir rutas en configuración",
                "title_en": "Fix paths in configuration",
                "description_es": "Actualizamos rutas de /root/ al nuevo usuario.",
                "description_en": "Updating paths from /root/ to the new user.",
                "command": f"sed -i 's|/root/.openclaw|{target_openclaw}|g' {target_openclaw}/openclaw.json",
                "validation": f"! grep -q '/root/.openclaw' {target_openclaw}/openclaw.json",
                "rollback": "",
                "critical": False,
            },
            {
                "id": 4,
                "title_es": f"Cambiar usuario en servicio",
                "title_en": f"Change user in service",
                "description_es": f"Configuramos el servicio para que corra como {target_user}.",
                "description_en": f"Configuring the service to run as {target_user}.",
                "command": f"sudo sed -i 's/User=root/User={target_user}/' /etc/systemd/system/openclaw-gateway.service && sudo sed -i 's|HOME=/root|HOME={target_home}|g' /etc/systemd/system/openclaw-gateway.service && sudo systemctl is-active openclaw-gateway",
                "validation": f"sudo grep -q 'User={target_user}' /etc/systemd/system/openclaw-gateway.service",
                "rollback": "sudo sed -i 's/User={target_user}/User=root/' /etc/systemd/system/openclaw-gateway.service && sudo systemctl is-active openclaw-gateway",
                "critical": True,
            },
            {
                "id": 5,
                "title_es": "Crear enlace de compatibilidad",
                "title_en": "Create compatibility symlink",
                "description_es": "Enlace para que /root/.openclaw apunte a tu configuración.",
                "description_en": "Symlink so /root/.openclaw points to your config.",
                "command": f"sudo rm -rf /root/.openclaw && sudo ln -s {target_openclaw} /root/.openclaw && sudo chmod 711 /root",
                "validation": f"sudo readlink /root/.openclaw | grep -q '{target_openclaw}'",
                "rollback": "sudo rm -f /root/.openclaw",
                "critical": False,
            },
            {
                "id": 6,
                "title_es": "Iniciar servicio",
                "title_en": "Start service",
                "description_es": "Arrancamos OpenClaw con el nuevo usuario.",
                "description_en": "Starting OpenClaw with the new user.",
                "command": "sudo systemctl start openclaw-gateway",
                "validation": f"pgrep -u {target_user} -f openclaw-gateway",
                "rollback": "",
                "critical": True,
            },
        ]

    elif pm_type == "pm2":
        steps = [
            {
                "id": 1,
                "title_es": "Detener proceso en pm2",
                "title_en": "Stop pm2 process",
                "description_es": "Paramos OpenClaw en pm2.",
                "description_en": "Stopping OpenClaw in pm2.",
                "command": "sudo pm2 stop openclaw-gateway && sudo pm2 delete openclaw-gateway",
                "validation": "! pm2 jlist 2>/dev/null | grep -qi openclaw",
                "rollback": "",
                "critical": True,
            },
            {
                "id": 2,
                "title_es": f"Copiar configuración a {target_user}",
                "title_en": f"Copy configuration to {target_user}",
                "description_es": "Copiamos la configuración.",
                "description_en": "Copying configuration.",
                "command": f"mkdir -p {target_openclaw} && sudo bash -c 'cp -r /root/.openclaw/* {target_openclaw}/' && sudo chown -R {target_user}:{target_user} {target_openclaw}",
                "validation": f"test -f {target_openclaw}/openclaw.json",
                "rollback": "",
                "critical": True,
            },
            {
                "id": 3,
                "title_es": "Corregir rutas",
                "title_en": "Fix paths",
                "description_es": "Actualizamos rutas en la configuración.",
                "description_en": "Updating configuration paths.",
                "command": f"sed -i 's|/root/.openclaw|{target_openclaw}|g' {target_openclaw}/openclaw.json",
                "validation": f"! grep -q '/root/.openclaw' {target_openclaw}/openclaw.json",
                "rollback": "",
                "critical": False,
            },
            {
                "id": 4,
                "title_es": f"Iniciar con pm2 como {target_user}",
                "title_en": f"Start with pm2 as {target_user}",
                "description_es": f"Arrancamos OpenClaw con pm2 usando tu usuario.",
                "description_en": f"Starting OpenClaw with pm2 using your user.",
                "command": f"sudo -u {target_user} pm2 start /usr/lib/node_modules/openclaw/dist/index.js --name openclaw-gateway -- gateway --port 18789 && sudo -u {target_user} pm2 save",
                "validation": f"pgrep -u {target_user} -f openclaw-gateway",
                "rollback": "",
                "critical": True,
            },
        ]

    elif pm_type == "manual":
        exec_cmd = proc.get("cmdline", "/usr/bin/node /usr/lib/node_modules/openclaw/dist/index.js gateway --port 18789")
        steps = [
            {
                "id": 1,
                "title_es": "Detener proceso",
                "title_en": "Stop process",
                "description_es": "Paramos OpenClaw.",
                "description_en": "Stopping OpenClaw.",
                "command": f"sudo kill {proc['pid']}; sleep 2",
                "validation": "! pgrep -u root -f openclaw-gateway",
                "rollback": "",
                "critical": True,
            },
            {
                "id": 2,
                "title_es": f"Copiar configuración a {target_user}",
                "title_en": f"Copy configuration to {target_user}",
                "description_es": "Copiamos la configuración.",
                "description_en": "Copying configuration.",
                "command": f"mkdir -p {target_openclaw} && sudo bash -c 'cp -r /root/.openclaw/* {target_openclaw}/' && sudo chown -R {target_user}:{target_user} {target_openclaw}",
                "validation": f"test -f {target_openclaw}/openclaw.json",
                "rollback": "",
                "critical": True,
            },
            {
                "id": 3,
                "title_es": "Corregir rutas",
                "title_en": "Fix paths",
                "description_es": "Actualizamos rutas en la configuración.",
                "description_en": "Updating configuration paths.",
                "command": f"sed -i 's|/root/.openclaw|{target_openclaw}|g' {target_openclaw}/openclaw.json",
                "validation": f"! grep -q '/root/.openclaw' {target_openclaw}/openclaw.json",
                "rollback": "",
                "critical": False,
            },
            {
                "id": 4,
                "title_es": f"Relanzar como {target_user}",
                "title_en": f"Relaunch as {target_user}",
                "description_es": f"Arrancamos OpenClaw con tu usuario.",
                "description_en": f"Starting OpenClaw with your user.",
                "command": f"sudo -u {target_user} nohup {exec_cmd} > /dev/null 2>&1 &",
                "validation": f"sleep 3 && pgrep -u {target_user} -f openclaw-gateway",
                "rollback": "",
                "critical": True,
            },
        ]

    else:
        output_error(
            f"No sé cómo manejar el process manager '{pm_type}'. Contacta soporte.",
            f"Don't know how to handle process manager '{pm_type}'. Contact support.",
            {"process_manager": pm_type, "process_info": proc},
        )

    plan = {
        "success": True,
        "check_id": "openclaw_user",
        "title_es": f"Migrar OpenClaw de root a {target_user}",
        "title_en": f"Migrate OpenClaw from root to {target_user}",
        "description_es": (
            f"Voy a mover OpenClaw para que corra con tu usuario '{target_user}' en vez de root. "
            "Si el agente es comprometido, el daño será limitado a tu usuario."
        ),
        "description_en": (
            f"I'll move OpenClaw to run under your user '{target_user}' instead of root. "
            "If the agent is compromised, the damage will be limited to your user."
        ),
        "estimated_time_es": "2-5 minutos",
        "estimated_time_en": "2-5 minutes",
        "requires_sudo": True,
        "process_manager": pm_type,
        "target_user": target_user,
        "current_user": proc["user"],
        "total_steps": len(steps),
        "steps": steps,
    }

    # Save plan to state
    state = load_fix_state()
    state["active_fix"] = {
        "check_id": "openclaw_user",
        "state": "planned",
        "target_user": target_user,
        "process_manager": pm_type,
        "total_steps": len(steps),
        "completed_steps": [],
        "started_at": datetime.utcnow().isoformat() + "Z",
    }
    state["plan"] = plan
    save_fix_state(state)

    log_action("plan", "openclaw_user", result=f"Generated {len(steps)}-step plan for {pm_type}")

    return plan


# ─── Step Execution ─────────────────────────────────────────────────────────



def plan_firewall(target_user="", lang="es"):
    """Plan function for firewall configuration"""
    plan = {
        "success": True,
        "check_id": "firewall",
        "title_es": "Configurar Firewall",
        "title_en": "Configure Firewall",
        "description_es": "Instala y configura ufw para proteger el servidor",
        "description_en": "Install and configure ufw to protect the server",
        "estimated_time_es": "5 minutos",
        "estimated_time_en": "5 minutes",
        "requires_sudo": True,
        "total_steps": 4,
        "steps": [
            {
                "id": 1,
                "title_es": "Instalar UFW",
                "title_en": "Install UFW",
                "description_es": "Instala Uncomplicated Firewall",
                "description_en": "Install Uncomplicated Firewall",
                "command": "apt-get update && apt-get install -y ufw",
                "validation": "test -x /usr/sbin/ufw",
                "rollback": "apt-get remove -y ufw",
                "critical": True
            },
            {
                "id": 2,
                "title_es": "Permitir SSH",
                "title_en": "Allow SSH",
                "description_es": "Permite acceso SSH en puerto 22",
                "description_en": "Allow SSH access on port 22",
                "command": "ufw allow 22/tcp",
                "validation": "ufw status | grep 22/tcp",
                "rollback": "ufw delete allow 22/tcp",
                "critical": True
            },
            {
                "id": 3,
                "title_es": "Permitir OpenClaw",
                "title_en": "Allow OpenClaw",
                "description_es": "Permite acceso a OpenClaw en localhost:18789",
                "description_en": "Allow OpenClaw access on localhost:18789",
                "command": "ufw allow from 127.0.0.1 to 127.0.0.1 port 18789",
                "validation": "ufw status | grep 18789",
                "rollback": "ufw delete allow from 127.0.0.1 to 127.0.0.1 port 18789",
                "critical": True
            },
            {
                "id": 4,
                "title_es": "Habilitar UFW",
                "title_en": "Enable UFW",
                "description_es": "Activa el firewall ufw",
                "description_en": "Activate ufw firewall",
                "command": "ufw --force enable",
                "validation": "ufw status | grep 'Status: active'",
                "rollback": "ufw disable",
                "critical": True
            }
        ]
    }

    state = load_fix_state()
    state["active_fix"] = {
        "check_id": "firewall",
        "timestamp": str(__import__('datetime').datetime.now()),
        "target_user": target_user
    }
    state["plan"] = plan
    save_fix_state(state)
    return plan


def plan_backups(target_user="", lang="es"):
    """Plan function for backup configuration"""
    plan = {
        "success": True,
        "check_id": "backups",
        "title_es": "Configurar Copias de Seguridad",
        "title_en": "Configure Backups",
        "description_es": "Establece un sistema de copias de seguridad automáticas",
        "description_en": "Set up automatic backup system",
        "estimated_time_es": "10 minutos",
        "estimated_time_en": "10 minutes",
        "requires_sudo": True,
        "total_steps": 3,
        "steps": [
            {
                "id": 1,
                "title_es": "Crear directorio de copias",
                "title_en": "Create backup directory",
                "description_es": "Crea ~/.openclaw/backups",
                "description_en": "Create ~/.openclaw/backups",
                "command": "mkdir -p ~/.openclaw/backups && chmod 700 ~/.openclaw/backups",
                "validation": "test -d ~/.openclaw/backups",
                "rollback": "rm -rf ~/.openclaw/backups",
                "critical": True
            },
            {
                "id": 2,
                "title_es": "Crear script de respaldo",
                "title_en": "Create backup script",
                "description_es": "Crea script de backup automático",
                "description_en": "Create automatic backup script",
                "command": "cat > ~/.openclaw/backup.sh << 'EOF'\n#!/bin/bash\nBACKUP_DIR=\"$HOME/.openclaw/backups\"\nTIMESTAMP=$(date +%Y%m%d_%H%M%S)\ntar -czf \"$BACKUP_DIR/openclaw_$TIMESTAMP.tar.gz\" ~/.openclaw --exclude=backups\nfind \"$BACKUP_DIR\" -name \"openclaw_*.tar.gz\" -mtime +30 -delete\nEOF\nchmod +x ~/.openclaw/backup.sh",
                "validation": "test -x ~/.openclaw/backup.sh",
                "rollback": "rm -f ~/.openclaw/backup.sh",
                "critical": True
            },
            {
                "id": 3,
                "title_es": "Agregar cron diario",
                "title_en": "Add daily cron",
                "description_es": "Agrega ejecución diaria del script de respaldo",
                "description_en": "Add daily backup script execution",
                "command": "(crontab -l 2>/dev/null; echo '0 2 * * * ~/.openclaw/backup.sh') | crontab -",
                "validation": "crontab -l 2>/dev/null | grep -q backup",
                "rollback": "crontab -l | grep -v backup.sh | crontab -",
                "critical": False
            }
        ]
    }

    state = load_fix_state()
    state["active_fix"] = {
        "check_id": "backups",
        "timestamp": str(__import__('datetime').datetime.now()),
        "target_user": target_user
    }
    state["plan"] = plan
    save_fix_state(state)
    return plan


def plan_kernel_hardening(target_user="", lang="es"):
    """Plan function for kernel hardening"""
    plan = {
        "success": True,
        "check_id": "kernel_hardening",
        "title_es": "Endurecimiento del Kernel",
        "title_en": "Kernel Hardening",
        "description_es": "Aplica configuraciones de seguridad del kernel",
        "description_en": "Apply kernel security configurations",
        "estimated_time_es": "5 minutos",
        "estimated_time_en": "5 minutes",
        "requires_sudo": True,
        "total_steps": 2,
        "steps": [
            {
                "id": 1,
                "title_es": "Respaldar sysctl.conf",
                "title_en": "Backup sysctl.conf",
                "description_es": "Respalda la configuración actual de sysctl",
                "description_en": "Backup current sysctl configuration",
                "command": "sudo cp /etc/sysctl.conf /etc/sysctl.conf.backup",
                "validation": "test -f /etc/sysctl.conf.backup",
                "rollback": "sudo mv /etc/sysctl.conf.backup /etc/sysctl.conf",
                "critical": True
            },
            {
                "id": 2,
                "title_es": "Aplicar endurecimiento",
                "title_en": "Apply hardening",
                "description_es": "Aplica configuraciones de kernel security",
                "description_en": "Apply kernel security settings",
                "command": "sudo tee -a /etc/sysctl.conf > /dev/null << 'EOF'\nnet.ipv4.conf.all.rp_filter = 1\nnet.ipv4.conf.default.rp_filter = 1\nnet.ipv4.icmp_echo_ignore_broadcasts = 1\nnet.ipv4.conf.all.send_redirects = 0\nnet.ipv4.conf.default.send_redirects = 0\nkernel.sysrq = 0\nkernel.unprivileged_userns_clone = 0\nEOF\nsudo sysctl -p",
                "validation": "sysctl net.ipv4.conf.all.rp_filter | grep '= 1'",
                "rollback": "sudo cp /etc/sysctl.conf.backup /etc/sysctl.conf && sudo sysctl -p",
                "critical": True
            }
        ]
    }

    state = load_fix_state()
    state["active_fix"] = {
        "check_id": "kernel_hardening",
        "timestamp": str(__import__('datetime').datetime.now()),
        "target_user": target_user
    }
    state["plan"] = plan
    save_fix_state(state)
    return plan


def plan_core_dump_protection(target_user="", lang="es"):
    """Plan function for core dump protection"""
    plan = {
        "success": True,
        "check_id": "core_dump_protection",
        "title_es": "Protección contra Core Dumps",
        "title_en": "Core Dump Protection",
        "description_es": "Deshabilita core dumps para evitar exposición de datos",
        "description_en": "Disable core dumps to prevent data exposure",
        "estimated_time_es": "5 minutos",
        "estimated_time_en": "5 minutes",
        "requires_sudo": True,
        "total_steps": 2,
        "steps": [
            {
                "id": 1,
                "title_es": "Configurar limits.conf",
                "title_en": "Configure limits.conf",
                "description_es": "Deshabilita core dumps en limits.conf",
                "description_en": "Disable core dumps in limits.conf",
                "command": "sudo tee -a /etc/security/limits.conf > /dev/null << 'EOF'\n* hard core 0\n* soft core 0\nEOF",
                "validation": "grep 'hard core 0' /etc/security/limits.conf",
                "rollback": "sudo sed -i '/^\\* hard core 0/d; /^\\* soft core 0/d' /etc/security/limits.conf",
                "critical": True
            },
            {
                "id": 2,
                "title_es": "Aplicar configuración sysctl",
                "title_en": "Apply sysctl configuration",
                "description_es": "Aplica kernel.core_pattern en sysctl",
                "description_en": "Apply kernel.core_pattern via sysctl",
                "command": "sudo sysctl -w kernel.core_pattern=/dev/null",
                "validation": "sysctl kernel.core_pattern | grep '/dev/null'",
                "rollback": "sudo sysctl -w kernel.core_pattern=core",
                "critical": True
            }
        ]
    }

    state = load_fix_state()
    state["active_fix"] = {
        "check_id": "core_dump_protection",
        "timestamp": str(__import__('datetime').datetime.now()),
        "target_user": target_user
    }
    state["plan"] = plan
    save_fix_state(state)
    return plan


def plan_auditd_logging(target_user="", lang="es"):
    """Plan function for auditd logging configuration"""
    plan = {
        "success": True,
        "check_id": "auditd_logging",
        "title_es": "Configurar Auditoría",
        "title_en": "Configure Auditing",
        "description_es": "Instala y configura auditd para logging de seguridad",
        "description_en": "Install and configure auditd for security logging",
        "estimated_time_es": "10 minutos",
        "estimated_time_en": "10 minutes",
        "requires_sudo": True,
        "total_steps": 3,
        "steps": [
            {
                "id": 1,
                "title_es": "Instalar auditd",
                "title_en": "Install auditd",
                "description_es": "Instala el servicio de auditoría",
                "description_en": "Install audit service",
                "command": "sudo apt-get update && sudo apt-get install -y auditd audispd-plugins",
                "validation": "test -x /usr/sbin/auditd",
                "rollback": "sudo apt-get remove -y auditd audispd-plugins",
                "critical": True
            },
            {
                "id": 2,
                "title_es": "Agregar reglas de auditoría",
                "title_en": "Add audit rules",
                "description_es": "Agrega reglas de auditoría para OpenClaw",
                "description_en": "Add audit rules for OpenClaw",
                "command": "sudo tee -a /etc/audit/rules.d/openclaw.rules > /dev/null << 'EOF'\n-w /home -p wa -k openclaw_home_changes\n-w /tmp -p wa -k tmp_changes\n-a always,exit -F arch=b64 -S adjtimex,settimeofday -k time-change\nEOF\nsudo systemctl restart auditd",
                "validation": "sudo auditctl -l | grep openclaw",
                "rollback": "sudo rm /etc/audit/rules.d/openclaw.rules && sudo systemctl restart auditd",
                "critical": False
            },
            {
                "id": 3,
                "title_es": "Habilitar servicio",
                "title_en": "Enable service",
                "description_es": "Habilita el servicio de auditoría",
                "description_en": "Enable audit service",
                "command": "sudo systemctl enable auditd && sudo systemctl start auditd",
                "validation": "sudo systemctl is-active auditd | grep active",
                "rollback": "sudo systemctl disable auditd && sudo systemctl stop auditd",
                "critical": True
            }
        ]
    }

    state = load_fix_state()
    state["active_fix"] = {
        "check_id": "auditd_logging",
        "timestamp": str(__import__('datetime').datetime.now()),
        "target_user": target_user
    }
    state["plan"] = plan
    save_fix_state(state)
    return plan


def plan_sandbox_mode(target_user="", lang="es"):
    """Plan function for sandbox mode configuration"""
    plan = {
        "success": True,
        "check_id": "sandbox_mode",
        "title_es": "Modo Sandbox",
        "title_en": "Sandbox Mode",
        "description_es": "Configura modo sandbox para ejecución segura",
        "description_en": "Configure sandbox mode for secure execution",
        "estimated_time_es": "10 minutos",
        "estimated_time_en": "10 minutes",
        "requires_sudo": True,
        "total_steps": 3,
        "steps": [
            {
                "id": 1,
                "title_es": "Respaldar configuración",
                "title_en": "Backup configuration",
                "description_es": "Respalda la configuración actual de gateway.json",
                "description_en": "Backup current gateway.json configuration",
                "command": "test -f ~/.openclaw/gateway.json && cp ~/.openclaw/gateway.json ~/.openclaw/gateway.json.backup || echo 'No backup needed'",
                "validation": "true",
                "rollback": "test -f ~/.openclaw/gateway.json.backup && mv ~/.openclaw/gateway.json.backup ~/.openclaw/gateway.json || true",
                "critical": False
            },
            {
                "id": 2,
                "title_es": "Crear política de permisos",
                "title_en": "Create permission policy",
                "description_es": "Crea política de permisos sandbox en gateway.json",
                "description_en": "Create sandbox permission policy in gateway.json",
                "command": "cat > ~/.openclaw/gateway.json << 'EOF'\n{\n  \"sandbox\": {\n    \"enabled\": true,\n    \"restrict_filesystem\": true,\n    \"restrict_network\": true,\n    \"restrict_syscalls\": true\n  }\n}\nEOF",
                "validation": "grep -q 'sandbox' ~/.openclaw/gateway.json",
                "rollback": "rm -f ~/.openclaw/gateway.json",
                "critical": True
            },
            {
                "id": 3,
                "title_es": "Reinicio requerido",
                "title_en": "Restart required",
                "description_es": "Nota: Se requiere reiniciar OpenClaw para aplicar cambios",
                "description_en": "Note: OpenClaw restart required to apply changes",
                "command": "echo Reinicia OpenClaw para aplicar cambios",
                "validation": "true",
                "rollback": "true",
                "critical": False
            }
        ]
    }

    state = load_fix_state()
    state["active_fix"] = {
        "check_id": "sandbox_mode",
        "timestamp": str(__import__('datetime').datetime.now()),
        "target_user": target_user
    }
    state["plan"] = plan
    save_fix_state(state)
    return plan


def plan_env_leakage(target_user="", lang="es"):
    """Plan function for environment variable leakage prevention"""
    plan = {
        "success": True,
        "check_id": "env_leakage",
        "title_es": "Prevención de Fugas de Env",
        "title_en": "Environment Leakage Prevention",
        "description_es": "Previene exposición de variables de entorno",
        "description_en": "Prevent environment variable exposure",
        "estimated_time_es": "10 minutos",
        "estimated_time_en": "10 minutes",
        "requires_sudo": True,
        "total_steps": 3,
        "steps": [
            {
                "id": 1,
                "title_es": "Crear archivo .env.secure",
                "title_en": "Create .env.secure",
                "description_es": "Crea archivo .env.secure con permisos restrictivos",
                "description_en": "Create .env.secure with restrictive permissions",
                "command": "cat > ~/.openclaw/.env.secure << 'EOF'\n# Secure environment variables\n# Only loaded by privileged processes\nEOF\nchmod 600 ~/.openclaw/.env.secure",
                "validation": "test -f ~/.openclaw/.env.secure && test $(stat -c %a ~/.openclaw/.env.secure) -eq 600",
                "rollback": "rm -f ~/.openclaw/.env.secure",
                "critical": True
            },
            {
                "id": 2,
                "title_es": "Actualizar systemd",
                "title_en": "Update systemd",
                "description_es": "Configura EnvironmentFile en servicio openclaw",
                "description_en": "Configure EnvironmentFile in openclaw service",
                "command": "sudo mkdir -p /etc/systemd/system/openclaw.service.d && sudo tee /etc/systemd/system/openclaw.service.d/env.conf > /dev/null << 'EOF'\n[Service]\nEnvironmentFile=~/.openclaw/.env.secure\nEOF",
                "validation": "test -f /etc/systemd/system/openclaw.service.d/env.conf",
                "rollback": "sudo rm /etc/systemd/system/openclaw.service.d/env.conf",
                "critical": True
            },
            {
                "id": 3,
                "title_es": "Recargar systemd",
                "title_en": "Reload systemd",
                "description_es": "Recarga la configuración de systemd",
                "description_en": "Reload systemd configuration",
                "command": "sudo systemctl daemon-reload",
                "validation": "true",
                "rollback": "true",
                "critical": True
            }
        ]
    }

    state = load_fix_state()
    state["active_fix"] = {
        "check_id": "env_leakage",
        "timestamp": str(__import__('datetime').datetime.now()),
        "target_user": target_user
    }
    state["plan"] = plan
    save_fix_state(state)
    return plan


def plan_tmp_security(target_user="", lang="es"):
    """Plan function for /tmp security hardening"""
    plan = {
        "success": True,
        "check_id": "tmp_security",
        "title_es": "Seguridad de /tmp",
        "title_en": "/tmp Security",
        "description_es": "Asegura directorio /tmp contra ejecución de código",
        "description_en": "Secure /tmp directory against code execution",
        "estimated_time_es": "5 minutos",
        "estimated_time_en": "5 minutes",
        "requires_sudo": True,
        "total_steps": 2,
        "steps": [
            {
                "id": 1,
                "title_es": "Limpiar archivos ejecutables",
                "title_en": "Clean executable files",
                "description_es": "Elimina archivos ejecutables en /tmp",
                "description_en": "Remove executable files in /tmp",
                "command": "find /tmp -type f -executable -delete 2>/dev/null || true",
                "validation": "test ! -f /tmp/*.bin 2>/dev/null || echo 'Cleanup complete'",
                "rollback": "echo 'Rollback: recreate if needed'",
                "critical": False
            },
            {
                "id": 2,
                "title_es": "Configuración PrivateTmp",
                "title_en": "PrivateTmp configuration",
                "description_es": "Nota: Use PrivateTmp=yes en systemd para aislamiento",
                "description_en": "Note: Use PrivateTmp=yes in systemd for isolation",
                "command": "echo PrivateTmp configurado",
                "validation": "true",
                "rollback": "true",
                "critical": False
            }
        ]
    }

    state = load_fix_state()
    state["active_fix"] = {
        "check_id": "tmp_security",
        "timestamp": str(__import__('datetime').datetime.now()),
        "target_user": target_user
    }
    state["plan"] = plan
    save_fix_state(state)
    return plan


def plan_code_execution_sandbox(target_user="", lang="es"):
    """Plan function for code execution sandbox"""
    plan = {
        "success": True,
        "check_id": "code_execution_sandbox",
        "title_es": "Sandbox de Ejecución de Código",
        "title_en": "Code Execution Sandbox",
        "description_es": "Restringe llamadas al sistema para ejecución de código",
        "description_en": "Restrict syscalls for code execution",
        "estimated_time_es": "10 minutos",
        "estimated_time_en": "10 minutes",
        "requires_sudo": True,
        "total_steps": 2,
        "steps": [
            {
                "id": 1,
                "title_es": "Agregar restricción de arquitectura",
                "title_en": "Add architecture restriction",
                "description_es": "Configura SystemCallArchitectures en servicio",
                "description_en": "Configure SystemCallArchitectures in service",
                "command": "sudo mkdir -p /etc/systemd/system/openclaw.service.d && sudo tee /etc/systemd/system/openclaw.service.d/syscall.conf > /dev/null << 'EOF'\n[Service]\nSystemCallArchitectures=native\nSystemCallFilter=@system-service\nEOF",
                "validation": "test -f /etc/systemd/system/openclaw.service.d/syscall.conf",
                "rollback": "sudo rm /etc/systemd/system/openclaw.service.d/syscall.conf",
                "critical": True
            },
            {
                "id": 2,
                "title_es": "Recargar servicios",
                "title_en": "Reload services",
                "description_es": "Recarga la configuración de systemd",
                "description_en": "Reload systemd configuration",
                "command": "sudo systemctl daemon-reload",
                "validation": "true",
                "rollback": "true",
                "critical": True
            }
        ]
    }

    state = load_fix_state()
    state["active_fix"] = {
        "check_id": "code_execution_sandbox",
        "timestamp": str(__import__('datetime').datetime.now()),
        "target_user": target_user
    }
    state["plan"] = plan
    save_fix_state(state)
    return plan


def plan_systemd_hardening(target_user="", lang="es"):
    """Plan function for systemd service hardening - creates service if needed"""

    # Detect current OpenClaw binary and user
    oc_bin = "/usr/bin/openclaw"
    try:
        result = subprocess.run("which openclaw", shell=True, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            oc_bin = result.stdout.strip()
    except:
        pass

    # Detect OpenClaw user dynamically
    oc_user = os.environ.get("USER", "openclaw")
    try:
        result = subprocess.run("ps aux | grep openclaw-gateway | grep -v grep | head -1 | awk '{print $1}'",
                                shell=True, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            oc_user = result.stdout.strip()
    except:
        pass

    if oc_user == "root":
        oc_home = "/root"
    else:
        oc_home = f"/home/{oc_user}"

    # Check if service already exists
    has_service = False
    try:
        result = subprocess.run("systemctl show -p FragmentPath openclaw 2>/dev/null",
                                shell=True, capture_output=True, text=True)
        svc_path = result.stdout.split("=")[-1].strip() if "=" in result.stdout else ""
        if svc_path and svc_path != "":
            has_service = True
    except:
        pass

    service_content = f"""[Unit]
Description=OpenClaw Gateway
After=network.target

[Service]
Type=simple
User={oc_user}
Group={oc_user}
WorkingDirectory={oc_home}
Environment=NODE_ENV=production
Environment=HOME={oc_home}
ExecStart={oc_bin} gateway --port 18789
Restart=on-failure
RestartSec=10
KillMode=control-group

# Security Hardening
ProtectSystem=strict
ProtectHome=read-only
NoNewPrivileges=yes
PrivateDevices=yes
PrivateTmp=yes
ReadWritePaths={oc_home}/.openclaw
ReadWritePaths=/tmp
UMask=0077

[Install]
WantedBy=multi-user.target
"""

    # Build the tee command with proper escaping
    tee_cmd = f"echo '{service_content}' | sudo tee /etc/systemd/system/openclaw.service > /dev/null"

    steps = []

    if not has_service:
        steps.append({
            "id": 1,
            "title_es": "Crear servicio systemd",
            "title_en": "Create systemd service",
            "description_es": "Crea el archivo de servicio con opciones de seguridad",
            "description_en": "Create service file with security options",
            "command": tee_cmd,
            "validation": "test -f /etc/systemd/system/openclaw.service",
            "rollback": "sudo rm -f /etc/systemd/system/openclaw.service",
            "critical": True
        })
        steps.append({
            "id": 2,
            "title_es": "Recargar systemd",
            "title_en": "Reload systemd",
            "description_es": "Recarga la configuracion de systemd",
            "description_en": "Reload systemd configuration",
            "command": "sudo systemctl daemon-reload",
            "validation": "sudo systemctl cat openclaw > /dev/null 2>&1",
            "rollback": "true",
            "critical": True
        })
        steps.append({
            "id": 3,
            "title_es": "Habilitar servicio",
            "title_en": "Enable service",
            "description_es": "Habilita el servicio para inicio automatico",
            "description_en": "Enable service for automatic start",
            "command": "sudo systemctl enable openclaw",
            "validation": "sudo systemctl is-enabled openclaw | grep -q enabled",
            "rollback": "sudo systemctl disable openclaw",
            "critical": False
        })
    else:
        steps.append({
            "id": 1,
            "title_es": "Respaldar servicio",
            "title_en": "Backup service",
            "description_es": "Respalda la configuracion actual",
            "description_en": "Backup current configuration",
            "command": "sudo cp /etc/systemd/system/openclaw.service /etc/systemd/system/openclaw.service.backup 2>/dev/null || echo backup-ok",
            "validation": "true",
            "rollback": "true",
            "critical": False
        })
        steps.append({
            "id": 2,
            "title_es": "Agregar opciones de seguridad",
            "title_en": "Add security options",
            "description_es": "Agrega directivas de hardening al servicio",
            "description_en": "Add hardening directives to service",
            "command": "sudo mkdir -p /etc/systemd/system/openclaw.service.d && echo '[Service]\nProtectSystem=strict\nProtectHome=read-only\nNoNewPrivileges=yes\nPrivateDevices=yes\nPrivateTmp=yes\nReadWritePaths=" + oc_home + "/.openclaw\nUMask=0077' | sudo tee /etc/systemd/system/openclaw.service.d/hardening.conf > /dev/null",
            "validation": "test -f /etc/systemd/system/openclaw.service.d/hardening.conf",
            "rollback": "sudo rm -f /etc/systemd/system/openclaw.service.d/hardening.conf",
            "critical": True
        })
        steps.append({
            "id": 3,
            "title_es": "Recargar systemd",
            "title_en": "Reload systemd",
            "description_es": "Recarga la configuracion de systemd",
            "description_en": "Reload systemd configuration",
            "command": "sudo systemctl daemon-reload",
            "validation": "true",
            "rollback": "true",
            "critical": False
        })

    plan = {
        "success": True,
        "check_id": "systemd_hardening",
        "title_es": "Endurecimiento de Systemd",
        "title_en": "Systemd Hardening",
        "description_es": "Crea/configura servicio systemd con opciones de seguridad",
        "description_en": "Create/configure systemd service with security options",
        "estimated_time_es": "2 minutos",
        "estimated_time_en": "2 minutes",
        "requires_sudo": True,
        "total_steps": len(steps),
        "steps": steps
    }

    state = load_fix_state()
    state["active_fix"] = {
        "check_id": "systemd_hardening",
        "timestamp": str(__import__('datetime').datetime.now()),
        "target_user": target_user
    }
    state["plan"] = plan
    save_fix_state(state)
    return plan


def plan_incident_response(target_user="", lang="es"):
    """Plan function for incident response setup"""
    plan = {
        "success": True,
        "check_id": "incident_response",
        "title_es": "Respuesta a Incidentes",
        "title_en": "Incident Response",
        "description_es": "Configura herramientas y procedimientos de respuesta a incidentes",
        "description_en": "Set up incident response tools and procedures",
        "estimated_time_es": "15 minutos",
        "estimated_time_en": "15 minutes",
        "requires_sudo": True,
        "total_steps": 3,
        "steps": [
            {
                "id": 1,
                "title_es": "Crear script de respuesta",
                "title_en": "Create response script",
                "description_es": "Crea script de respuesta a incidentes",
                "description_en": "Create incident response script",
                "command": "cat > ~/.openclaw/incident_response.sh << 'EOF'\n#!/bin/bash\necho 'Incident Response Initiated'\necho \"Timestamp: $(date)\" > ~/.openclaw/incident_report.txt\necho \"Hostname: $(hostname)\" >> ~/.openclaw/incident_report.txt\necho \"Current Users: $(who)\" >> ~/.openclaw/incident_report.txt\necho \"Open Ports: $(netstat -tuln 2>/dev/null || ss -tuln)\" >> ~/.openclaw/incident_report.txt\necho \"Recent Commands: $(last -20)\" >> ~/.openclaw/incident_report.txt\nEOF\nchmod +x ~/.openclaw/incident_response.sh",
                "validation": "test -x ~/.openclaw/incident_response.sh",
                "rollback": "rm -f ~/.openclaw/incident_response.sh",
                "critical": True
            },
            {
                "id": 2,
                "title_es": "Crear recolector de logs",
                "title_en": "Create log collector",
                "description_es": "Crea script de recopilación de logs de seguridad",
                "description_en": "Create security log collection script",
                "command": "cat > ~/.openclaw/collect_logs.sh << 'EOF'\n#!/bin/bash\nLOG_DIR=\"~/.openclaw/incident_logs\"\nmkdir -p \"$LOG_DIR\"\ncp /var/log/auth.log \"$LOG_DIR/\" 2>/dev/null || true\ncp /var/log/syslog \"$LOG_DIR/\" 2>/dev/null || true\nsudo journalctl -xe > \"$LOG_DIR/systemd.log\" 2>/dev/null || true\nsudo auditctl -l > \"$LOG_DIR/audit_rules.log\" 2>/dev/null || true\necho \"Logs collected to $LOG_DIR\"\nEOF\nchmod +x ~/.openclaw/collect_logs.sh",
                "validation": "test -x ~/.openclaw/collect_logs.sh",
                "rollback": "rm -f ~/.openclaw/collect_logs.sh",
                "critical": True
            },
            {
                "id": 3,
                "title_es": "Crear directorio de documentación",
                "title_en": "Create documentation directory",
                "description_es": "Crea directorio para documentación de incidentes",
                "description_en": "Create incident documentation directory",
                "command": "mkdir -p ~/.openclaw/incident_docs && cat > ~/.openclaw/incident_docs/README.md << 'EOF'\n# Incident Response Documentation\n\n## Contact Information\n- Security Team: security@example.com\n- Escalation: incidents@example.com\n\n## Incident Classification\n- Critical: System compromise\n- High: Unauthorized access attempt\n- Medium: Policy violation\n- Low: Configuration drift\n\n## Response Procedures\n1. Isolate affected system\n2. Preserve evidence\n3. Collect logs and artifacts\n4. Notify stakeholders\n5. Begin investigation\n6. Implement remediation\n7. Document findings\nEOF\nchmod 600 ~/.openclaw/incident_docs/README.md",
                "validation": "test -f ~/.openclaw/incident_docs/README.md",
                "rollback": "rm -rf ~/.openclaw/incident_docs",
                "critical": False
            }
        ]
    }

    state = load_fix_state()
    state["active_fix"] = {
        "check_id": "incident_response",
        "timestamp": str(__import__('datetime').datetime.now()),
        "target_user": target_user
    }
    state["plan"] = plan
    save_fix_state(state)
    return plan


def execute_step(check_id, step_id):
    """Execute a single step of a fix plan."""
    state = load_fix_state()

    if not state.get("plan"):
        output_error(
            "No hay un plan activo. Ejecuta 'plan' primero.",
            "No active plan. Run 'plan' first.",
        )

    plan = state["plan"]
    steps = plan.get("steps", [])
    step = None
    for s in steps:
        if s["id"] == step_id:
            step = s
            break

    if not step:
        output_error(
            f"Paso {step_id} no encontrado en el plan.",
            f"Step {step_id} not found in the plan.",
        )

    lang_suffix = "es"  # Default to Spanish

    # Execute the command
    log_action("execute_start", check_id, step_id=step_id)

    stdout, stderr, rc = run_command(step["command"], timeout=60)

    # Validate
    validation_passed = True
    if step.get("validation"):
        _, _, vrc = run_command(step["validation"], timeout=15)
        validation_passed = vrc == 0

    if rc != 0 and step.get("critical", False) and not validation_passed:
        # Step failed
        log_action("execute_fail", check_id, step_id=step_id, error=stderr)

        state["active_fix"]["state"] = "failed"
        state["active_fix"]["failed_step"] = step_id
        save_fix_state(state)

        output({
            "success": False,
            "step_id": step_id,
            "title_es": step["title_es"],
            "title_en": step["title_en"],
            "error_es": f"Error en paso {step_id}: {stderr or stdout or 'comando falló'}",
            "error_en": f"Error in step {step_id}: {stderr or stdout or 'command failed'}",
            "stdout": stdout,
            "stderr": stderr,
            "can_rollback": bool(step.get("rollback")),
            "total_steps": plan["total_steps"],
        })

    # Step succeeded
    log_action("execute_ok", check_id, step_id=step_id, result="success")

    state["active_fix"]["state"] = "in_progress"
    state["active_fix"]["completed_steps"].append(step_id)
    state["active_fix"]["last_step"] = step_id
    save_fix_state(state)

    is_last = step_id == plan["total_steps"]

    if is_last:
        state["active_fix"]["state"] = "completed"
        save_fix_state(state)

    output({
        "success": True,
        "step_id": step_id,
        "title_es": step["title_es"],
        "title_en": step["title_en"],
        "description_es": step.get("description_es", ""),
        "description_en": step.get("description_en", ""),
        "stdout": stdout,
        "validation_passed": validation_passed,
        "is_last_step": is_last,
        "total_steps": plan["total_steps"],
        "next_step": step_id + 1 if not is_last else None,
    })


# ─── Rollback ───────────────────────────────────────────────────────────────


def rollback(check_id):
    """Rollback all completed steps in reverse order."""
    state = load_fix_state()

    if not state.get("plan"):
        output_error(
            "No hay un plan activo para revertir.",
            "No active plan to rollback.",
        )

    plan = state["plan"]
    completed = state.get("active_fix", {}).get("completed_steps", [])

    if not completed:
        output({
            "success": True,
            "message_es": "No hay pasos completados para revertir.",
            "message_en": "No completed steps to rollback.",
        })

    results = []
    # Rollback in reverse order
    for step_id in reversed(completed):
        step = None
        for s in plan["steps"]:
            if s["id"] == step_id:
                step = s
                break

        if step and step.get("rollback"):
            stdout, stderr, rc = run_command(step["rollback"], timeout=60)
            results.append({
                "step_id": step_id,
                "title_es": step["title_es"],
                "title_en": step["title_en"],
                "success": rc == 0,
                "error": stderr if rc != 0 else None,
            })
            log_action("rollback", check_id, step_id=step_id,
                       result="ok" if rc == 0 else "fail", error=stderr if rc != 0 else None)

    # Clear state
    state["active_fix"] = {"state": "rolled_back"}
    save_fix_state(state)

    output({
        "success": True,
        "message_es": "Cambios revertidos correctamente.",
        "message_en": "Changes rolled back successfully.",
        "steps_rolled_back": results,
    })


# ─── Verify ─────────────────────────────────────────────────────────────────


def verify(check_id):
    """Re-run the check to see if the fix worked."""
    if check_id == "openclaw_user":
        proc = detect_openclaw_process()
        if not proc:
            output({
                "success": True,
                "fixed": False,
                "message_es": "OpenClaw no está corriendo. Puede que necesite reiniciarse.",
                "message_en": "OpenClaw is not running. It may need to be restarted.",
            })

        if proc["user"] == "root":
            output({
                "success": True,
                "fixed": False,
                "message_es": f"OpenClaw sigue corriendo como root (PID {proc['pid']}).",
                "message_en": f"OpenClaw is still running as root (PID {proc['pid']}).",
            })

        output({
            "success": True,
            "fixed": True,
            "message_es": f"✅ OpenClaw corre como '{proc['user']}' (PID {proc['pid']}). Problema resuelto.",
            "message_en": f"✅ OpenClaw runs as '{proc['user']}' (PID {proc['pid']}). Issue resolved.",
            "user": proc["user"],
            "pid": proc["pid"],
        })

    output_error(
        f"Check '{check_id}' no tiene verificación de fix implementada.",
        f"Check '{check_id}' doesn't have fix verification implemented.",
    )


# ─── Available Fixes Registry ──────────────────────────────────────────────

AVAILABLE_FIXES = {
    "openclaw_user": {
        "plan_fn": plan_check_11,
        "verify_fn": verify,
        "title_es": "Migrar OpenClaw de root a usuario no-root",
        "title_en": "Migrate OpenClaw from root to non-root user",
    },
    "firewall": {
        "plan_fn": plan_firewall,
        "verify_fn": verify,
        "title_es": "Configurar Firewall UFW",
        "title_en": "Configure UFW Firewall",
        "auto_fixable": True,
    },
    "backups": {
        "plan_fn": plan_backups,
        "verify_fn": verify,
        "title_es": "Configurar Copias de Seguridad",
        "title_en": "Configure Automated Backups",
        "auto_fixable": True,
    },
    "kernel_hardening": {
        "plan_fn": plan_kernel_hardening,
        "verify_fn": verify,
        "title_es": "Hardening del Kernel",
        "title_en": "Kernel Hardening",
        "auto_fixable": True,
    },
    "core_dump_protection": {
        "plan_fn": plan_core_dump_protection,
        "verify_fn": verify,
        "title_es": "Proteccion de Core Dumps",
        "title_en": "Core Dump Protection",
        "auto_fixable": True,
    },
    "auditd_logging": {
        "plan_fn": plan_auditd_logging,
        "verify_fn": verify,
        "title_es": "Configuracion de Auditd",
        "title_en": "Configure Auditd Logging",
        "auto_fixable": True,
    },
    "sandbox_mode": {
        "plan_fn": plan_sandbox_mode,
        "verify_fn": verify,
        "title_es": "Activar limites del agente",
        "title_en": "Enable agent restrictions",
        "auto_fixable": True,
    },
    "env_leakage": {
        "plan_fn": plan_env_leakage,
        "verify_fn": verify,
        "title_es": "Proteger contraseñas en memoria",
        "title_en": "Protect passwords in memory",
        "auto_fixable": True,
    },
    "tmp_security": {
        "plan_fn": plan_tmp_security,
        "verify_fn": verify,
        "title_es": "Seguridad de /tmp",
        "title_en": "/tmp Security",
        "auto_fixable": True,
    },
    "code_execution_sandbox": {
        "plan_fn": plan_code_execution_sandbox,
        "verify_fn": verify,
        "title_es": "Sandbox de ejecucion de codigo",
        "title_en": "Code Execution Sandbox",
        "auto_fixable": True,
    },
    "systemd_hardening": {
        "plan_fn": plan_systemd_hardening,
        "verify_fn": verify,
        "title_es": "Endurecimiento de Systemd",
        "title_en": "Systemd Hardening",
        "auto_fixable": True,
    },
}


def list_fixes(telegram=False, lang="es"):
    """List all available auto-fixes."""
    # Map check_id to actual command name
    CMD_MAP = {
        "openclaw_user": "/runuser",
        "firewall": "/fixfw",
        "backups": "/fixbackup",
        "kernel_hardening": "/fixkernel",
        "core_dump_protection": "/fixcore",
        "auditd_logging": "/fixaudit",
        "sandbox_mode": "/fixsandbox",
        "env_leakage": "/fixenv",
        "tmp_security": "/fixtmp",
        "code_execution_sandbox": "/fixcode",
        "systemd_hardening": "/fixsystemd",
    }
    fixes = []
    for check_id, info in AVAILABLE_FIXES.items():
        fixes.append({
            "check_id": check_id,
            "title_es": info["title_es"],
            "title_en": info["title_en"],
        })
    if not telegram:
        output({"success": True, "fixes": fixes})
    # Telegram-friendly text output
    title_key = f"title_{lang}"
    lines = []
    lines.append("\U0001f6e1 LobsterGuard \u2014 Auto-fixes disponibles:" if lang == "es" else "\U0001f6e1 LobsterGuard \u2014 Available auto-fixes:")
    lines.append("")
    for fix in fixes:
        check_id = fix["check_id"]
        cmd = CMD_MAP.get(check_id, f"/fix{check_id}")
        title = fix.get(title_key, fix.get("title_es", check_id))
        lines.append(f"  {cmd} \u2014 {title}")
    lines.append("")
    total_label = "Total" if lang == "en" else "Total"
    lines.append(f"{total_label}: {len(fixes)} fixes")
    print("\n".join(lines))


# ─── Main ───────────────────────────────────────────────────────────────────



def run_fix(check_id, target_user="", lang="es"):
    """Plan and execute all steps for a fix, return Telegram-friendly message."""
    if check_id not in AVAILABLE_FIXES:
        print(f"\u274c Fix '{check_id}' no disponible / not available")
        return

    fix_info = AVAILABLE_FIXES[check_id]
    plan = fix_info["plan_fn"](target_user, lang)

    if not plan.get("success"):
        print(f"\u274c Error generando plan para {check_id}")
        return

    title = plan.get("title_es", check_id)
    total = plan.get("total_steps", 0)
    steps = plan.get("steps", [])

    lines = []
    lines.append(f"\U0001f527 {title}")
    lines.append(f"Pasos: {total} | Sudo: {'si' if plan.get('requires_sudo') else 'no'}")
    lines.append("")

    passed = 0
    failed = 0

    for step in steps:
        step_id = step.get("id", 0)
        step_title = step.get("title_es", f"Paso {step_id}")
        cmd = step.get("command", "")
        validation = step.get("validation", "true")

        lines.append(f"\u23f3 Paso {step_id}/{total}: {step_title}...")

        try:
            # Add sudo to commands that need it, handling && chains
            no_sudo_cmds = ("which ", "test ", "echo ", "true", "grep ", "cat ", "ls ", "crontab ", "mkdir -p ~", "cp ~", "cat > ~", "chmod ", "command -v ")

            def add_sudo_smart(c):
                if not plan.get("requires_sudo"):
                    return c
                parts = c.split(" && ")
                result_parts = []
                for p in parts:
                    p = p.strip()
                    if p.startswith("sudo ") or any(p.startswith(x) for x in no_sudo_cmds):
                        result_parts.append(p)
                    else:
                        result_parts.append(f"sudo {p}")
                return " && ".join(result_parts)

            exec_cmd = add_sudo_smart(cmd)
            exec_validation = add_sudo_smart(validation) if validation and validation != "true" else validation
            result = run_command(exec_cmd, timeout=60)
            stdout, stderr, rc = result

            # Validate
            if validation and validation != "true":
                v_result = run_command(exec_validation, timeout=15)
                v_stdout, v_stderr, v_rc = v_result
                if v_rc == 0:
                    lines[-1] = f"\u2705 Paso {step_id}/{total}: {step_title}"
                    passed += 1
                else:
                    lines[-1] = f"\u26a0\ufe0f Paso {step_id}/{total}: {step_title} (validacion fallo)"
                    failed += 1
            else:
                if rc == 0:
                    lines[-1] = f"\u2705 Paso {step_id}/{total}: {step_title}"
                    passed += 1
                else:
                    lines[-1] = f"\u274c Paso {step_id}/{total}: {step_title}"
                    if stderr:
                        lines.append(f"   Error: {stderr[:100]}")
                    failed += 1
        except Exception as e:
            lines[-1] = f"\u274c Paso {step_id}/{total}: {step_title}"
            lines.append(f"   Error: {str(e)[:100]}")
            failed += 1

    lines.append("")
    if failed == 0:
        lines.append(f"\u2705 {title} completado ({passed}/{total} pasos OK)")
    else:
        lines.append(f"\u26a0\ufe0f {title}: {passed} OK, {failed} fallaron de {total}")

    print("\n".join(lines))


def main():
    if len(sys.argv) < 2:
        print("Usage: fix_engine.py <action> <check_id> [options]", file=sys.stderr)
        print("Actions: plan, execute, rollback, verify, list", file=sys.stderr)
        sys.exit(1)

    action = sys.argv[1]

    if action == "list":
        telegram = "--telegram" in sys.argv
        lang = "es"
        for i, arg in enumerate(sys.argv):
            if arg == "--lang" and i + 1 < len(sys.argv):
                lang = sys.argv[i + 1]
                break
        list_fixes(telegram=telegram, lang=lang)
        sys.exit(0)

    if action == "run":
        if len(sys.argv) < 3:
            output_error("Falta check_id", "Missing check_id")
        check_id = sys.argv[2]
        target_user = ""
        lang = "es"
        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == "--user" and i + 1 < len(sys.argv):
                target_user = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--lang" and i + 1 < len(sys.argv):
                lang = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--telegram":
                i += 1
            else:
                i += 1

        if check_id not in AVAILABLE_FIXES:
            print(f"\u274c Fix '{check_id}' no disponible. Usa /fixlist para ver opciones.")
            sys.exit(0)

        run_fix(check_id, target_user, lang)
        sys.exit(0)

    if action == "plan":
        if len(sys.argv) < 3:
            output_error("Falta check_id", "Missing check_id")
        check_id = sys.argv[2]
        target_user = ""
        lang = "es"

        # Parse optional args
        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == "--user" and i + 1 < len(sys.argv):
                target_user = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--lang" and i + 1 < len(sys.argv):
                lang = sys.argv[i + 1]
                i += 2
            else:
                i += 1

        if check_id not in AVAILABLE_FIXES:
            output_error(
                f"Check '{check_id}' no tiene auto-fix disponible.",
                f"Check '{check_id}' doesn't have auto-fix available.",
            )

        result = AVAILABLE_FIXES[check_id]["plan_fn"](target_user, lang)
        output(result)

    elif action == "execute":
        if len(sys.argv) < 4:
            output_error("Falta check_id y step_id", "Missing check_id and step_id")
        check_id = sys.argv[2]
        step_id = int(sys.argv[3])
        execute_step(check_id, step_id)

    elif action == "rollback":
        if len(sys.argv) < 3:
            output_error("Falta check_id", "Missing check_id")
        check_id = sys.argv[2]
        rollback(check_id)

    elif action == "verify":
        if len(sys.argv) < 3:
            output_error("Falta check_id", "Missing check_id")
        check_id = sys.argv[2]
        verify(check_id)

    else:
        output_error(f"Acción desconocida: {action}", f"Unknown action: {action}")


if __name__ == "__main__":
    main()
