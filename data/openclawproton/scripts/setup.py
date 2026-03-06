"""Setup commands for the Protonmail skill.

Handles Bridge systemd service, credential writing, and himalaya config generation.

Usage:
    python3 setup.py install
    python3 setup.py configure --email ... --display-name ...
    python3 setup.py verify
"""

import json
import os
import shutil
import socket
import stat
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
CONFIG_DIR = SKILL_DIR / "config"

REQUIRED_BINS = ["himalaya"]
LINUXBREW_BIN = "/home/linuxbrew/.linuxbrew/bin"


def _print_step(number, title):
    print(f"\n{'='*60}")
    print(f"  Step {number}: {title}")
    print(f"{'='*60}\n")


def _backup_if_exists(path):
    """Back up existing file to .bak before overwriting."""
    if path.exists():
        backup = path.with_suffix(path.suffix + ".bak")
        shutil.copy2(path, backup)
        print(f"  Backed up existing file to {backup}")
        return True
    return False


def _export_bridge_cert(cert_path, imap_port=1143):
    """Export Bridge's self-signed TLS cert via openssl s_client."""
    try:
        result = subprocess.run(
            ["openssl", "s_client", "-starttls", "imap",
             "-connect", f"127.0.0.1:{imap_port}"],
            input=b"", capture_output=True, timeout=10,
        )
        output = result.stdout.decode()
        start = output.find("-----BEGIN CERTIFICATE-----")
        end = output.find("-----END CERTIFICATE-----")
        if start == -1 or end == -1:
            print("  WARNING: Could not extract Bridge TLS certificate")
            return
        pem = output[start:end + len("-----END CERTIFICATE-----")] + "\n"
        cert_path.write_text(pem)
        print(f"  Exported Bridge TLS cert to {cert_path}")
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"  WARNING: Could not export Bridge cert: {e}")


def detect_binary_paths():
    """Find required binaries. Tries $PATH, then Linuxbrew fallback."""
    bins = {}
    missing = []

    for name in REQUIRED_BINS:
        path = shutil.which(name)
        if path:
            bins[name] = path
            continue

        linuxbrew_path = os.path.join(LINUXBREW_BIN, name)
        if os.path.isfile(linuxbrew_path) and os.access(linuxbrew_path, os.X_OK):
            bins[name] = linuxbrew_path
            continue

        missing.append(name)

    if missing:
        print(f"Error: Required binaries not found: {', '.join(missing)}", file=sys.stderr)
        print("Install with: brew install " + " ".join(missing), file=sys.stderr)
        sys.exit(1)

    return bins


def write_auth_file(password):
    """Write Bridge password to config/auth (chmod 600)."""
    auth_path = CONFIG_DIR / "auth"
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    _backup_if_exists(auth_path)
    auth_path.write_text(password + "\n")
    os.chmod(auth_path, stat.S_IRUSR | stat.S_IWUSR)
    print(f"  Wrote {auth_path} (permissions: 600)")
    return auth_path


def _validate_toml_string(value, field_name):
    """Reject values that could inject arbitrary TOML when interpolated into
    a double-quoted string. Characters like ", \, newlines, and control chars
    would let an attacker break out of the string and inject new keys —
    e.g. overriding backend.auth.command to run arbitrary shell commands."""
    dangerous = {'"', '\\', '\n', '\r', '\t'}
    found = [ch for ch in value if ch in dangerous or ord(ch) < 32]
    if found:
        labels = {'"': 'double quote', '\\': 'backslash', '\n': 'newline',
                  '\r': 'carriage return', '\t': 'tab'}
        names = [labels.get(ch, f"U+{ord(ch):04X}") for ch in found]
        print(f"Error: {field_name} contains invalid characters: {', '.join(set(names))}", file=sys.stderr)
        sys.exit(1)


def generate_himalaya_config(email, display_name, auth_path, imap_port=1143, smtp_port=1025):
    """Generate config/himalaya.toml for IMAP/SMTP via Bridge.

    IMAP uses start-tls with the exported Bridge cert. SMTP uses no encryption
    because Bridge's cert has CA:TRUE which rustls-webpki (himalaya's SMTP TLS
    library) rejects. Localhost-only, so this is safe.
    """
    _validate_toml_string(email, "--email")
    _validate_toml_string(display_name, "--display-name")

    config_path = CONFIG_DIR / "himalaya.toml"
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    _backup_if_exists(config_path)

    abs_auth = str(auth_path.resolve())
    _validate_toml_string(abs_auth, "auth path")

    cert_path = CONFIG_DIR / "bridge-cert.pem"
    _export_bridge_cert(cert_path, imap_port)
    abs_cert = str(cert_path.resolve())
    _validate_toml_string(abs_cert, "cert path")

    content = f"""[accounts.protonmail]
default = true
email = "{email}"
display-name = "{display_name}"

backend.type = "imap"
backend.host = "127.0.0.1"
backend.port = {imap_port}
backend.encryption.type = "start-tls"
backend.encryption.cert = "{abs_cert}"
backend.login = "{email}"
backend.auth.type = "password"
backend.auth.command = "cat {abs_auth}"

message.send.backend.type = "smtp"
message.send.backend.host = "127.0.0.1"
message.send.backend.port = {smtp_port}
message.send.backend.encryption.type = "none"
message.send.backend.login = "{email}"
message.send.backend.auth.type = "password"
message.send.backend.auth.command = "cat {abs_auth}"
message.send.save-copy = true
"""
    config_path.write_text(content)
    print(f"  Wrote {config_path}")
    return config_path


def write_config_json(email, display_name, bins, imap_port=1143, smtp_port=1025):
    """Write config/config.json with runtime settings."""
    config_path = CONFIG_DIR / "config.json"
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    if config_path.exists():
        _backup_if_exists(config_path)

    himalaya_config_path = str((CONFIG_DIR / "himalaya.toml").resolve())

    config = {
        "account_email": email,
        "display_name": display_name,
        "imap_host": "127.0.0.1",
        "imap_port": imap_port,
        "smtp_host": "127.0.0.1",
        "smtp_port": smtp_port,
        "bins": bins,
        "himalaya_config": himalaya_config_path,
    }

    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
        f.write("\n")

    print(f"  Wrote {config_path}")
    return config


def _find_bridge_binary():
    """Locate protonmail-bridge: $PATH, Linuxbrew, then common apt locations."""
    path = shutil.which("protonmail-bridge")
    if path:
        return path

    linuxbrew_path = os.path.join(LINUXBREW_BIN, "protonmail-bridge")
    if os.path.isfile(linuxbrew_path) and os.access(linuxbrew_path, os.X_OK):
        return linuxbrew_path

    for candidate in ["/usr/bin/protonmail-bridge", "/usr/local/bin/protonmail-bridge"]:
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate

    return None


def create_systemd_service():
    """Create and start a systemd user service for Bridge."""
    bridge_bin = _find_bridge_binary()
    if not bridge_bin:
        print("Error: protonmail-bridge binary not found.", file=sys.stderr)
        print("Install it first:", file=sys.stderr)
        print("  1. Download from https://proton.me/bridge/install", file=sys.stderr)
        print("  2. sudo apt install ./protonmail-bridge_*.deb", file=sys.stderr)
        sys.exit(1)

    print(f"  Found protonmail-bridge: {bridge_bin}")

    service_dir = Path.home() / ".config" / "systemd" / "user"
    service_dir.mkdir(parents=True, exist_ok=True)
    service_path = service_dir / "protonmail-bridge.service"

    _backup_if_exists(service_path)

    content = f"""[Unit]
Description=Proton Bridge
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart={bridge_bin} --noninteractive
Restart=on-failure
RestartSec=10
Environment=PATH=/usr/local/bin:/usr/bin:/bin
Environment=DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/%U/bus

[Install]
WantedBy=default.target
"""
    service_path.write_text(content)
    print(f"  Wrote {service_path}")

    for cmd, desc in [
        (["systemctl", "--user", "daemon-reload"], "Reloading systemd"),
        (["systemctl", "--user", "enable", "protonmail-bridge.service"], "Enabling service"),
        (["systemctl", "--user", "start", "protonmail-bridge.service"], "Starting service"),
    ]:
        print(f"  {desc}...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  Warning: {' '.join(cmd)} failed: {result.stderr.strip()}", file=sys.stderr)


def verify(config):
    """Check Bridge service, ports, and himalaya connectivity."""
    results = {
        "service_active": False,
        "imap_port_open": False,
        "smtp_port_open": False,
        "himalaya_connect": False,
    }

    print("  Checking systemd service...")
    svc_result = subprocess.run(
        ["systemctl", "--user", "is-active", "protonmail-bridge.service"],
        capture_output=True, text=True
    )
    if svc_result.stdout.strip() == "active":
        results["service_active"] = True
        print("  [ok] protonmail-bridge service is active")
    else:
        print("  [fail] protonmail-bridge service is not active")
        print("    Fix: systemctl --user start protonmail-bridge")

    imap_port = config.get("imap_port", 1143)
    smtp_port = config.get("smtp_port", 1025)

    for port, name in [(imap_port, "imap_port_open"), (smtp_port, "smtp_port_open")]:
        print(f"  Checking port {port}...")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect(("127.0.0.1", port))
            sock.close()
            results[name] = True
            print(f"  [ok] Port {port} is listening")
        except (socket.timeout, ConnectionRefusedError, OSError):
            print(f"  [fail] Port {port} is not responding")
            print(f"    Fix: Ensure Bridge is running and logged in")

    himalaya_bin = config.get("bins", {}).get("himalaya")
    himalaya_config = config.get("himalaya_config")

    if himalaya_bin and himalaya_config:
        print("  Checking himalaya connectivity...")
        him_result = subprocess.run(
            [himalaya_bin, "--config", himalaya_config, "envelope", "list", "--page-size", "1"],
            capture_output=True, text=True, timeout=15
        )
        if him_result.returncode == 0:
            results["himalaya_connect"] = True
            print("  [ok] himalaya can connect to Proton Bridge")
        else:
            print(f"  [fail] himalaya connection failed: {him_result.stderr.strip()[:200]}")
            print("    Fix: Check Bridge password in config/auth and Bridge login status")
    else:
        print("  [skip] himalaya binary or config path not found in config.json")

    return results


# -- CLI commands --

def cmd_setup_install(args):
    """Create Bridge systemd service."""
    _print_step(1, "Create Proton Bridge systemd service")
    create_systemd_service()

    print("\n" + "="*60)
    print("  Bridge service installed. Next steps:")
    print("="*60)
    print()
    print("  1. Log into Bridge:")
    print("     protonmail-bridge --cli")
    print("     > login")
    print()
    print("  2. Get the Bridge password:")
    print("     > info")
    print("     (NOT your Proton password — it's a generated string)")
    print()
    print("  3. Set the Bridge password in OpenClaw:")
    print("     /secret set PROTON_BRIDGE_PASSWORD")
    print()
    print("  4. Configure the skill:")
    print('     python3 setup.py configure --email you@proton.me --display-name "Your Name"')
    print()


def cmd_setup_configure(args):
    """Write auth, himalaya config, and config.json. Password from $PROTON_BRIDGE_PASSWORD."""
    password = os.environ.get("PROTON_BRIDGE_PASSWORD")
    if not password:
        print("Error: $PROTON_BRIDGE_PASSWORD environment variable is not set.", file=sys.stderr)
        print("Set it with: /secret set PROTON_BRIDGE_PASSWORD", file=sys.stderr)
        print("The Bridge password comes from: protonmail-bridge --cli > info", file=sys.stderr)
        sys.exit(1)

    _print_step(1, "Write credentials")
    auth_path = write_auth_file(password)

    _print_step(2, "Detect binaries")
    bins = detect_binary_paths()
    for name, path in bins.items():
        print(f"  {name}: {path}")

    _print_step(3, "Generate himalaya config")
    generate_himalaya_config(
        args.email, args.display_name, auth_path,
        imap_port=args.imap_port, smtp_port=args.smtp_port
    )

    _print_step(4, "Write config.json")
    config = write_config_json(
        args.email, args.display_name, bins,
        imap_port=args.imap_port, smtp_port=args.smtp_port
    )

    _print_step(5, "Verify connectivity")
    results = verify(config)

    all_passed = all(results.values())
    output = {
        "status": "ok" if all_passed else "partial",
        "config_written": str(CONFIG_DIR / "config.json"),
        "verification": results,
    }
    print(json.dumps(output, indent=2))


def cmd_setup_verify(args):
    """Check Bridge connectivity against current config."""
    config_path = CONFIG_DIR / "config.json"
    if not config_path.exists():
        print(f"Error: config not found at {config_path}", file=sys.stderr)
        print("Run setup configure first.", file=sys.stderr)
        sys.exit(1)

    with open(config_path) as f:
        config = json.load(f)

    results = verify(config)
    all_passed = all(results.values())

    output = {
        "status": "ok" if all_passed else "partial",
        "verification": results,
    }
    print(json.dumps(output, indent=2))


def build_parser():
    import argparse

    parser = argparse.ArgumentParser(description="Protonmail skill setup")
    subparsers = parser.add_subparsers(dest="command", help="Setup command")

    sub_install = subparsers.add_parser("install", help="Create Bridge systemd service")
    sub_install.set_defaults(func=cmd_setup_install)

    sub_configure = subparsers.add_parser("configure", help="Write all config files")
    sub_configure.add_argument("--email", required=True, help="Proton email address")
    sub_configure.add_argument("--display-name", required=True, help="Display name for outgoing mail")
    sub_configure.add_argument("--imap-port", type=int, default=1143, help="Bridge IMAP port (default: 1143)")
    sub_configure.add_argument("--smtp-port", type=int, default=1025, help="Bridge SMTP port (default: 1025)")
    sub_configure.set_defaults(func=cmd_setup_configure)

    sub_verify = subparsers.add_parser("verify", help="Check Bridge connectivity")
    sub_verify.set_defaults(func=cmd_setup_verify)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
