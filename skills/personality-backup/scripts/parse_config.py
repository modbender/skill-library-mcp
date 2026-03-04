#!/usr/bin/env python3
"""Parse backup config JSON and output shell variable assignments."""
import json, sys, os

config_file = sys.argv[1]
with open(config_file) as f:
    c = json.load(f)

# Read password
pw_file = c.get("password_file", "")
password = ""
if pw_file and os.path.isfile(pw_file):
    with open(pw_file) as f:
        field = c.get("password_field", "Password")
        if field:
            for line in f:
                if line.startswith(f"{field}:"):
                    password = line.split(":", 1)[1].strip()
                    break
        else:
            password = f.read().strip()

# SMTP password
email_cfg = c.get("email", {})
smtp_pass = email_cfg.get("smtp_pass", "")
if not smtp_pass:
    env_var = email_cfg.get("smtp_pass_env", "")
    if env_var:
        smtp_pass = os.environ.get(env_var, "")

workspace = c.get("workspace", os.path.expanduser("~/.openclaw/workspace"))
excludes = ",".join(c.get("project_excludes", ["node_modules", ".git", "__pycache__", "*.mp4", "*.mp3", "*.wav"]))
pfiles = ",".join(c.get("personality_files", ["SOUL.md", "IDENTITY.md", "USER.md", "AGENTS.md", "MEMORY.md", "TOOLS.md"]))

def sh_escape(s):
    return s.replace("'", "'\\''")

pairs = {
    "CFG_PASSWORD": password,
    "CFG_WORKSPACE": workspace,
    "CFG_SECRETS_DIR": c.get("secrets_dir", os.path.expanduser("~/.openclaw/secrets")),
    "CFG_CONFIG_FILE": c.get("config_file", os.path.expanduser("~/.openclaw/openclaw.json")),
    "CFG_DELIVERY": c.get("delivery", "local"),
    "CFG_EMAIL_TO": email_cfg.get("to", ""),
    "CFG_EMAIL_FROM": email_cfg.get("from", ""),
    "CFG_SMTP_HOST": email_cfg.get("smtp_host", ""),
    "CFG_SMTP_PORT": str(email_cfg.get("smtp_port", 465)),
    "CFG_SMTP_USER": email_cfg.get("smtp_user", ""),
    "CFG_SMTP_PASS": smtp_pass,
    "CFG_LOCAL_DIR": c.get("local", {}).get("dir", "/tmp/backups"),
    "CFG_AGENT_NAME": c.get("agent_name", "Agent"),
    "CFG_AGENT_EMOJI": c.get("agent_emoji", ""),
    "CFG_PERSONALITY_FILES": pfiles,
    "CFG_PROJECT_EXCLUDES": excludes,
    "CFG_BACKUP_MEMORY": str(c.get("backup_memory", True)).lower(),
    "CFG_BACKUP_SECRETS": str(c.get("backup_secrets", True)).lower(),
    "CFG_BACKUP_CONFIG": str(c.get("backup_config", True)).lower(),
    "CFG_BACKUP_PROJECTS": str(c.get("backup_projects", True)).lower(),
    "CFG_BACKUP_SCRIPTS": str(c.get("backup_scripts", True)).lower(),
    "CFG_GENERATE_RESTORE": str(c.get("generate_restore_guide", True)).lower(),
}

for k, v in pairs.items():
    print(f"{k}='{sh_escape(v)}'")
