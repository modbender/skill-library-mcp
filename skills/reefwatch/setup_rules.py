#!/usr/bin/env python3
"""
ReefWatch Rule Setup 🪸
Downloads and configures initial YARA and Sigma rulesets.
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
RULES_DIR = SCRIPT_DIR / "rules"

# Rule sources
YARA_SOURCES = [
    {
        "name": "signature-base",
        "description": "Florian Roth's signature base (webshells, exploits, malware)",
        "url": "https://github.com/Neo23x0/signature-base.git",
        "tag": "v1.2",  # Pin to known-good release tag
        "paths": [
            "yara/gen_webshells.yar",
            "yara/gen_webshells_ext_vars.yar",
            "yara/gen_crimson_rat.yar",
            "yara/gen_rats_malware_indicators.yar",
            "yara/gen_crypto_mining.yar",
            "yara/gen_xmrig_miner.yar",
            "yara/gen_mal_scripts.yar",
            "yara/gen_powershell_empire.yar",
            "yara/gen_mimikatz.yar",
            "yara/gen_metasploit_payloads.yar",
            "yara/gen_cobaltstrike.yar",
            "yara/gen_invoke_thehash.yar",
            "yara/gen_p0wnshell.yar",
        ],
    },
    {
        "name": "yara-rules-community",
        "description": "YARA community rules",
        "url": "https://github.com/Yara-Rules/rules.git",
        "tag": "20240726",  # Pin to known-good release tag
        "paths": [
            "malware/RANSOM_WannaCry.yar",
            "malware/MALW_Eicar.yar",
            "crypto/crypto_mining.yar",
            "cve_rules/",
        ],
    },
]

SIGMA_SOURCES = [
    {
        "name": "sigma-rules",
        "description": "SigmaHQ official rules",
        "url": "https://github.com/SigmaHQ/sigma.git",
        "tag": "r2024-11-25",  # Pin to known-good release tag
        "paths": [
            # Linux authentication & brute force
            "rules/linux/auditd/lnx_auditd_susp_cmds.yml",
            "rules/linux/auditd/lnx_auditd_cred_dump.yml",
            "rules/linux/builtin/auth/lnx_auth_ssh_brute_force.yml",
            "rules/linux/builtin/auth/lnx_auth_pam_config_mod.yml",
            # Linux persistence
            "rules/linux/builtin/lnx_shell_crontab_mod.yml",
            "rules/linux/builtin/lnx_systemd_service_creation.yml",
            "rules/linux/builtin/lnx_at_command.yml",
            # Linux privilege escalation
            "rules/linux/auditd/lnx_auditd_setuid_setgid.yml",
            "rules/linux/builtin/lnx_sudo_cve_2019_14287.yml",
            # Linux lateral movement / reconnaissance
            "rules/linux/builtin/lnx_nmap_scanning.yml",
            "rules/linux/builtin/lnx_network_enum.yml",
            # macOS specifics
            "rules/macos/",
            # General process creation
            "rules/linux/process_creation/proc_creation_lnx_base64_decode.yml",
            "rules/linux/process_creation/proc_creation_lnx_curl_download.yml",
            "rules/linux/process_creation/proc_creation_lnx_wget_download.yml",
            "rules/linux/process_creation/proc_creation_lnx_reverse_shell.yml",
            "rules/linux/process_creation/proc_creation_lnx_python_reverse_shell.yml",
            "rules/linux/process_creation/proc_creation_lnx_nc_reverse_shell.yml",
        ],
    },
]

# Known malicious IPs (sample set - should be updated regularly)
INITIAL_IOC_BLOCKLIST = """# ReefWatch IOC Blocklist
# Updated: auto-generated at setup
# Format: one IP per line
# Sources: abuse.ch, emergingthreats, community reports

# Common C2 infrastructure (examples - update with threat feeds)
# Add your own IOCs or connect to a threat feed
"""


def _write_restricted(path: Path, content: str):
    """Write a file with 0o600 permissions (owner-only read/write)."""
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(str(path), flags, 0o600)
    try:
        os.write(fd, content.encode())
    finally:
        os.close(fd)


def run_cmd(cmd: list[str], cwd: str = None) -> bool:
    try:
        subprocess.run(
            cmd,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
            timeout=120,
        )
        return True
    except Exception as e:
        print(f"  ⚠ Command failed: {' '.join(cmd[:3])}... → {e}")
        return False


def download_rules(sources: list[dict], target_dir: Path, rule_type: str):
    """Clone repos and copy specific rule files."""
    target_dir.mkdir(parents=True, exist_ok=True)

    for source in sources:
        print(f"\n📦 Downloading {source['name']}...")
        print(f"   {source['description']}")

        with tempfile.TemporaryDirectory() as tmpdir:
            # Shallow clone pinned to tag/branch for reproducibility
            clone_cmd = ["git", "clone", "--depth=1", "--single-branch"]
            tag = source.get("tag")
            if tag:
                clone_cmd += ["--branch", tag]
            clone_cmd += [source["url"], tmpdir]
            if not run_cmd(clone_cmd):
                print(f"  ❌ Failed to clone {source['name']}, skipping")
                continue

            # Verify commit SHA if pinned (tags can be moved by repo owners)
            expected_sha = source.get("commit_sha")
            if expected_sha:
                result = subprocess.run(
                    ["git", "-C", tmpdir, "rev-parse", "HEAD"],
                    capture_output=True, text=True, timeout=10,
                )
                actual_sha = result.stdout.strip()
                if actual_sha != expected_sha:
                    print(
                        f"  ❌ SHA mismatch for {source['name']}: "
                        f"expected {expected_sha[:12]}, got {actual_sha[:12]}"
                    )
                    continue

            copied = 0
            for rel_path in source["paths"]:
                src = Path(tmpdir) / rel_path
                if src.is_dir():
                    # Copy entire directory
                    dest = target_dir / src.name
                    if dest.exists():
                        shutil.rmtree(dest)
                    exts = (
                        (".yar", ".yara")
                        if rule_type == "yara"
                        else (".yml", ".yaml")
                    )
                    dest.mkdir(parents=True, exist_ok=True)
                    for f in src.rglob("*"):
                        if f.is_file() and f.suffix in exts:
                            shutil.copy2(f, dest / f.name)
                            copied += 1
                elif src.is_file():
                    shutil.copy2(src, target_dir / src.name)
                    copied += 1
                else:
                    # Try glob
                    parent = Path(tmpdir) / Path(rel_path).parent
                    if parent.exists():
                        for f in parent.glob(Path(rel_path).name):
                            if f.is_file():
                                shutil.copy2(f, target_dir / f.name)
                                copied += 1

            print(f"  ✅ Copied {copied} rule files from {source['name']}")


def setup_custom_rules():
    """Create default custom rules directory with IOC blocklist."""
    custom_dir = RULES_DIR / "custom"
    custom_dir.mkdir(parents=True, exist_ok=True)

    ioc_file = custom_dir / "ioc_blocklist.txt"
    if not ioc_file.exists():
        _write_restricted(ioc_file, INITIAL_IOC_BLOCKLIST)
        print("  ✅ Created IOC blocklist template")

    # Create a basic brute-force sigma rule specific to OpenClaw hosts
    openclaw_rules = custom_dir / "openclaw_specific.yml"
    if not openclaw_rules.exists():
        _write_restricted(openclaw_rules,
            """title: OpenClaw Configuration Tampering
id: reef-001
status: stable
level: critical
description: Detects modifications to critical OpenClaw configuration files from unexpected processes
detection:
  keywords:
    - "openclaw.json"
    - "HEARTBEAT.md"
    - "IDENTITY.md"
    - "SOUL.md"
  selection:
    - "modified"
    - "changed"
    - "written"
  condition: keywords and selection
logsource:
  category: file_change
  product: linux

---

title: SSH Brute Force Detection
id: reef-002
status: stable
level: high
description: Detects multiple failed SSH authentication attempts
detection:
  keywords:
    - "Failed password"
    - "authentication failure"
    - "Invalid user"
    - "Connection closed by authenticating user"
  condition: keywords
logsource:
  category: auth
  product: linux

---

title: Suspicious Crontab Modification
id: reef-003
status: stable
level: high
description: Detects crontab modifications that could indicate persistence
detection:
  keywords:
    - "CRON"
    - "crontab"
    - "REPLACE"
    - "EDIT"
  selection:
    - "root"
    - "www-data"
    - "nobody"
  condition: keywords and selection
logsource:
  category: syslog
  product: linux

---

title: Reverse Shell Detection
id: reef-004
status: stable
level: critical
description: Detects common reverse shell patterns in logs
detection:
  keywords:
    - "/bin/bash -i"
    - "/bin/sh -i"
    - "bash -c 'bash -i"
    - "python -c 'import socket"
    - "python3 -c 'import socket"
    - "perl -e 'use Socket"
    - "ruby -rsocket"
    - "nc -e /bin"
    - "ncat -e /bin"
    - "mkfifo /tmp"
  condition: keywords
logsource:
  category: process_creation
  product: linux

---

title: Privilege Escalation Attempt
id: reef-005
status: stable
level: high
description: Detects sudo abuse and privilege escalation attempts
detection:
  keywords:
    - "sudo:"
    - "COMMAND="
  selection:
    - "NOT allowed"
    - "3 incorrect password attempts"
    - "authentication failure"
    - "account is not allowed"
  condition: keywords and selection
logsource:
  category: auth
  product: linux
"""
        )
        print("  ✅ Created OpenClaw-specific detection rules (Sigma format)")

    # Create sample JSON rules for CustomRulesEngine
    json_rule_file = custom_dir / "suspicious_file_changes.json"
    if not json_rule_file.exists():
        import json
        sample_rules = [
            {
                "name": "Suspicious script in /tmp",
                "description": "Detects script files created or modified in /tmp",
                "source_type": "file_change",
                "conditions": {"path": "/tmp/"},
                "severity": "HIGH",
            },
            {
                "name": "SSH key modification",
                "description": "Detects changes to SSH authorized_keys",
                "source_type": "file_change",
                "conditions": {"path": "authorized_keys"},
                "severity": "CRITICAL",
            },
        ]
        _write_restricted(json_rule_file, json.dumps(sample_rules, indent=2))
        print("  ✅ Created sample custom rules (JSON format)")


def create_sample_yara_rules():
    """Create some basic YARA rules in case git clone fails."""
    yara_dir = RULES_DIR / "yara"
    yara_dir.mkdir(parents=True, exist_ok=True)

    fallback = yara_dir / "reefwatch_basics.yar"
    if not fallback.exists():
        _write_restricted(fallback,
            """
rule ReefWatch_CryptoMiner_Strings
{
    meta:
        description = "Detects common crypto miner strings"
        author = "ReefWatch"
        severity = "HIGH"

    strings:
        $s1 = "stratum+tcp://" ascii
        $s2 = "stratum+ssl://" ascii
        $s3 = "xmrig" ascii nocase
        $s4 = "cpuminer" ascii nocase
        $s5 = "minerd" ascii nocase
        $s6 = "cryptonight" ascii nocase
        $s7 = "hashrate" ascii nocase
        $s8 = "mining_pool" ascii nocase

    condition:
        any of them
}

rule ReefWatch_WebShell_Generic
{
    meta:
        description = "Detects common webshell patterns"
        author = "ReefWatch"
        severity = "CRITICAL"

    strings:
        $php1 = "<?php eval(" ascii
        $php2 = "<?php assert(" ascii
        $php3 = "<?php system(" ascii
        $php4 = "base64_decode(gzinflate(" ascii
        $py1 = "exec(compile(" ascii
        $py2 = "__import__('os').system" ascii
        $sh1 = "bash -i >& /dev/tcp/" ascii
        $sh2 = "nc -e /bin/sh" ascii

    condition:
        any of them
}

rule ReefWatch_Reverse_Shell
{
    meta:
        description = "Detects reverse shell payloads"
        author = "ReefWatch"
        severity = "CRITICAL"

    strings:
        $bash = "/bin/bash -i >& /dev/tcp/" ascii
        $sh = "/bin/sh -i >& /dev/tcp/" ascii
        $python = "import socket,subprocess,os;s=socket.socket" ascii
        $perl = "use Socket;$i=" ascii
        $ruby = "TCPSocket.open" ascii
        $nc1 = "nc -e /bin/sh" ascii
        $nc2 = "nc -e /bin/bash" ascii
        $mkfifo = "mkfifo /tmp/f;cat /tmp/f|/bin" ascii

    condition:
        any of them
}

rule ReefWatch_Ransomware_Note
{
    meta:
        description = "Detects common ransomware note patterns"
        author = "ReefWatch"
        severity = "CRITICAL"

    strings:
        $r1 = "Your files have been encrypted" ascii nocase
        $r2 = "send bitcoin to" ascii nocase
        $r3 = "decrypt your files" ascii nocase
        $r4 = "pay the ransom" ascii nocase
        $r5 = ".onion" ascii
        $r6 = "tor browser" ascii nocase

    condition:
        2 of them
}

rule ReefWatch_Suspicious_Script
{
    meta:
        description = "Detects suspicious script patterns"
        author = "ReefWatch"
        severity = "MEDIUM"

    strings:
        $s1 = "curl http" ascii
        $s2 = "| bash" ascii
        $s3 = "| sh" ascii
        $s4 = "wget -O- http" ascii
        $s5 = "chmod 777" ascii
        $s6 = "chmod +x /tmp" ascii

    condition:
        2 of them
}
"""
        )
        print("  ✅ Created fallback YARA rules")


def main():
    parser = argparse.ArgumentParser(description="ReefWatch Rule Setup 🪸")
    parser.add_argument("--update", action="store_true", help="Update existing rules")
    parser.add_argument(
        "--skip-download", action="store_true", help="Skip Git downloads, use fallbacks"
    )
    args = parser.parse_args()

    print("🪸 ReefWatch Rule Setup")
    print("=" * 40)

    # Check git
    has_git = shutil.which("git") is not None
    if not has_git:
        print("⚠ git not found. Will use built-in fallback rules.")
        args.skip_download = True

    # YARA rules
    print("\n📋 YARA Rules")
    print("-" * 30)
    if not args.skip_download:
        download_rules(YARA_SOURCES, RULES_DIR / "yara", "yara")
    create_sample_yara_rules()

    # Sigma rules
    print("\n📋 Sigma Rules")
    print("-" * 30)
    if not args.skip_download:
        download_rules(SIGMA_SOURCES, RULES_DIR / "sigma", "sigma")

    # Custom rules
    print("\n📋 Custom Rules")
    print("-" * 30)
    setup_custom_rules()

    # Summary
    yara_count = len(list((RULES_DIR / "yara").rglob("*.yar"))) + len(
        list((RULES_DIR / "yara").rglob("*.yara"))
    )
    sigma_count = len(list((RULES_DIR / "sigma").rglob("*.yml"))) + len(
        list((RULES_DIR / "sigma").rglob("*.yaml"))
    )
    custom_count = (
        len(list((RULES_DIR / "custom").rglob("*.json")))
        + len(list((RULES_DIR / "custom").rglob("*.yml")))
    )

    print("\n" + "=" * 40)
    print("✅ Setup complete!")
    print(f"   YARA rules:   {yara_count}")
    print(f"   Sigma rules:  {sigma_count}")
    print(f"   Custom rules: {custom_count}")
    print(f"   Rules dir:    {RULES_DIR}")
    print("=" * 40)


if __name__ == "__main__":
    main()
