#!/usr/bin/env python3
"""Radicale server management operations."""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Optional, List

# Default paths
DEFAULT_CONFIG_PATHS = [
    Path("/etc/radicale/config"),
    Path.home() / ".config" / "radicale" / "config",
]

DEFAULT_STORAGE_PATH = "/var/lib/radicale/collections"
DEFAULT_USERS_PATH = "/etc/radicale/users"


def print_result(success: bool, message: str, data: Optional[Dict] = None):
    """Print result in consistent format."""
    result = {"success": success, "message": message}
    if data:
        result["data"] = data
    print(json.dumps(result, indent=2, default=str))


def find_config() -> Optional[Path]:
    """Find Radicale config file."""
    # Check environment variable
    if os.environ.get("RADICALE_CONFIG"):
        path = Path(os.environ["RADICALE_CONFIG"])
        if path.exists():
            return path

    # Check default paths
    for path in DEFAULT_CONFIG_PATHS:
        if path.exists():
            return path

    return None


def parse_config(config_path: Path) -> Dict:
    """Parse Radicale INI config file."""
    import configparser

    config = configparser.ConfigParser()
    config.read(config_path)

    result = {}
    for section in config.sections():
        result[section] = dict(config[section])

    return result


def cmd_status(args):
    """Check Radicale server status."""
    data = {}

    # Check if config exists
    config_path = find_config()
    if config_path:
        data["config_path"] = str(config_path)
    else:
        data["config_path"] = None
        data["config_warning"] = "No config file found"

    # Check if service is running (systemd)
    try:
        result = subprocess.run(
            ["systemctl", "status", "radicale"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            data["service_status"] = "running"
            # Extract active state
            for line in result.stdout.split("\n"):
                if "Active:" in line:
                    data["service_active"] = line.split("Active:")[1].strip()
                    break
        else:
            data["service_status"] = "stopped or not installed"
    except FileNotFoundError:
        data["service_status"] = "systemd not available"
    except subprocess.TimeoutExpired:
        data["service_status"] = "timeout checking service"
    except Exception as e:
        data["service_status"] = f"error: {e}"

    # Check if process is running (non-systemd)
    if data.get("service_status") != "running":
        try:
            result = subprocess.run(
                ["pgrep", "-f", "radicale"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                data["process_running"] = True
                data["pids"] = result.stdout.strip().split("\n")
        except Exception:
            pass

    # Check storage
    config = parse_config(config_path) if config_path else {}
    storage_path = config.get("storage", {}).get("filesystem_folder", DEFAULT_STORAGE_PATH)
    storage = Path(storage_path)

    if storage.exists():
        data["storage_path"] = str(storage)
        # Count collections
        try:
            collections = list(storage.glob("*/*"))
            data["collection_count"] = len([c for c in collections if c.is_dir()])
        except Exception:
            pass
    else:
        data["storage_path"] = str(storage)
        data["storage_exists"] = False

    # Check users file
    auth_type = config.get("auth", {}).get("type", "none")
    data["auth_type"] = auth_type

    if auth_type == "htpasswd":
        users_path = config.get("auth", {}).get("htpasswd_filename", DEFAULT_USERS_PATH)
        if Path(users_path).exists():
            data["users_file"] = users_path
            try:
                with open(users_path) as f:
                    data["user_count"] = len([l for l in f if l.strip() and not l.startswith("#")])
            except Exception:
                pass
        else:
            data["users_file"] = users_path
            data["users_file_exists"] = False

    print_result(True, "Radicale status", data)


def cmd_config_show(args):
    """Show Radicale configuration."""
    config_path = find_config()

    if not config_path:
        print_result(False, "No Radicale config file found")
        return

    config = parse_config(config_path)
    print_result(True, f"Config from {config_path}", {"config": config, "path": str(config_path)})


def cmd_config_validate(args):
    """Validate Radicale configuration."""
    config_path = find_config()

    if not config_path:
        print_result(False, "No Radicale config file found")
        return

    issues = []
    warnings = []
    config = parse_config(config_path)

    # Check auth
    auth_type = config.get("auth", {}).get("type", "denyall")
    if auth_type == "none":
        issues.append("Authentication is disabled (auth.type=none) - anyone can access!")
    elif auth_type == "denyall":
        warnings.append("Authentication is denyall - no users can log in")

    # Check if htpasswd file exists for htpasswd auth
    if auth_type == "htpasswd":
        users_file = config.get("auth", {}).get("htpasswd_filename", DEFAULT_USERS_PATH)
        if not Path(users_file).exists():
            issues.append(f"htpasswd file not found: {users_file}")

    # Check storage
    storage_path = config.get("storage", {}).get("filesystem_folder", DEFAULT_STORAGE_PATH)
    storage = Path(storage_path)
    if not storage.exists():
        warnings.append(f"Storage path does not exist: {storage_path}")
    else:
        # Check permissions
        if not os.access(storage, os.W_OK):
            issues.append(f"No write permission on storage: {storage_path}")

    # Check SSL
    server_config = config.get("server", {})
    hosts = server_config.get("hosts", "localhost:5232")

    if server_config.get("ssl") == "True":
        cert = server_config.get("certificate", "/etc/ssl/radicale.cert.pem")
        key = server_config.get("key", "/etc/ssl/radicale.key.pem")
        if not Path(cert).exists():
            issues.append(f"SSL certificate not found: {cert}")
        if not Path(key).exists():
            issues.append(f"SSL key not found: {key}")
    else:
        # Check if bound to public interface without SSL
        if "0.0.0.0" in hosts or "::" in hosts:
            warnings.append("Server bound to all interfaces without SSL - traffic is unencrypted!")

    result = {
        "config_path": str(config_path),
        "issues": issues,
        "warnings": warnings,
        "valid": len(issues) == 0,
    }

    if issues or warnings:
        print_result(result["valid"], "Configuration has issues", result)
    else:
        print_result(True, "Configuration is valid", result)


def cmd_users_list(args):
    """List Radicale users from htpasswd file."""
    config_path = find_config()

    if not config_path:
        # Try to find users file directly
        users_path = Path(args.users_file or DEFAULT_USERS_PATH)
    else:
        config = parse_config(config_path)
        auth_type = config.get("auth", {}).get("type", "none")

        if auth_type != "htpasswd":
            print_result(False, f"Auth type is '{auth_type}', not htpasswd")
            return

        users_path = Path(config.get("auth", {}).get("htpasswd_filename", DEFAULT_USERS_PATH))

    if not users_path.exists():
        print_result(False, f"Users file not found: {users_path}")
        return

    users = []
    with open(users_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                parts = line.split(":", 1)
                if len(parts) == 2:
                    users.append(
                        {
                            "username": parts[0],
                            "has_password": True,
                        }
                    )

    print_result(True, f"Found {len(users)} user(s)", {"users": users, "file": str(users_path)})


def cmd_users_add(args):
    """Add a user to htpasswd file."""
    config_path = find_config()

    if config_path:
        config = parse_config(config_path)
        users_path = Path(config.get("auth", {}).get("htpasswd_filename", DEFAULT_USERS_PATH))
    else:
        users_path = Path(args.users_file or DEFAULT_USERS_PATH)

    # Check if htpasswd command exists
    try:
        subprocess.run(["htpasswd", "--help"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print_result(False, "htpasswd command not found. Install apache2-utils or httpd-tools")
        return

    # Build htpasswd command
    cmd = ["htpasswd"]

    if args.encryption:
        if args.encryption == "sha512":
            cmd.append("-5")
        elif args.encryption == "sha256":
            cmd.append("-s")
        elif args.encryption == "bcrypt":
            cmd.append("-B")
        elif args.encryption == "md5":
            cmd.append("-m")
        elif args.encryption == "plain":
            # Will add manually
            pass

    # Create file if doesn't exist
    if not users_path.exists():
        cmd.append("-c")

    cmd.extend([str(users_path), args.username])

    try:
        # Run htpasswd interactively (will prompt for password)
        result = subprocess.run(cmd)
        if result.returncode == 0:
            print_result(True, f"User '{args.username}' added to {users_path}")
        else:
            print_result(False, f"Failed to add user: htpasswd returned {result.returncode}")
    except Exception as e:
        print_result(False, f"Failed to add user: {e}")


def cmd_users_remove(args):
    """Remove a user from htpasswd file."""
    config_path = find_config()

    if config_path:
        config = parse_config(config_path)
        users_path = Path(config.get("auth", {}).get("htpasswd_filename", DEFAULT_USERS_PATH))
    else:
        users_path = Path(args.users_file or DEFAULT_USERS_PATH)

    if not users_path.exists():
        print_result(False, f"Users file not found: {users_path}")
        return

    # Read existing users
    lines = []
    found = False
    with open(users_path) as f:
        for line in f:
            if line.strip().startswith(args.username + ":"):
                found = True
            else:
                lines.append(line)

    if not found:
        print_result(False, f"User '{args.username}' not found")
        return

    # Write back
    with open(users_path, "w") as f:
        f.writelines(lines)

    print_result(True, f"User '{args.username}' removed")


def cmd_storage_verify(args):
    """Verify Radicale storage integrity."""
    config_path = find_config()

    if config_path:
        config = parse_config(config_path)
        storage_path = Path(config.get("storage", {}).get("filesystem_folder", DEFAULT_STORAGE_PATH))
    else:
        storage_path = Path(args.storage_path or DEFAULT_STORAGE_PATH)

    if not storage_path.exists():
        print_result(False, f"Storage path not found: {storage_path}")
        return

    # Run radicale --verify-storage if available
    try:
        result = subprocess.run(
            ["python3", "-m", "radicale", "--verify-storage"],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode == 0:
            print_result(True, "Storage verified", {"output": result.stdout})
        else:
            print_result(False, "Storage verification failed", {"output": result.stdout, "error": result.stderr})
    except FileNotFoundError:
        print_result(False, "Radicale not installed")
    except subprocess.TimeoutExpired:
        print_result(False, "Storage verification timed out")
    except Exception as e:
        print_result(False, f"Failed to verify storage: {e}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Radicale server management")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Status
    subparsers.add_parser("status", help="Check Radicale status")

    # Config
    config_parser = subparsers.add_parser("config", help="Configuration management")
    config_sub = config_parser.add_subparsers(dest="config_command", required=True)
    config_sub.add_parser("show", help="Show configuration")
    config_sub.add_parser("validate", help="Validate configuration")

    # Users
    users_parser = subparsers.add_parser("users", help="User management")
    users_sub = users_parser.add_subparsers(dest="users_command", required=True)

    users_list = users_sub.add_parser("list", help="List users")
    users_list.add_argument("--users-file", help="Custom users file path")

    users_add = users_sub.add_parser("add", help="Add user")
    users_add.add_argument("--username", required=True, help="Username")
    users_add.add_argument("--encryption", choices=["sha512", "sha256", "bcrypt", "md5", "plain"],
                          default="sha512", help="Password encryption")
    users_add.add_argument("--users-file", help="Custom users file path")

    users_remove = users_sub.add_parser("remove", help="Remove user")
    users_remove.add_argument("--username", required=True, help="Username")
    users_remove.add_argument("--users-file", help="Custom users file path")

    # Storage
    storage_parser = subparsers.add_parser("storage", help="Storage management")
    storage_sub = storage_parser.add_subparsers(dest="storage_command", required=True)
    storage_verify = storage_sub.add_parser("verify", help="Verify storage")
    storage_verify.add_argument("--storage-path", help="Custom storage path")

    args = parser.parse_args()

    # Dispatch
    if args.command == "config":
        globals()[f"cmd_config_{args.config_command}"](args)
    elif args.command == "users":
        globals()[f"cmd_users_{args.users_command}"](args)
    elif args.command == "storage":
        globals()[f"cmd_storage_{args.storage_command}"](args)
    else:
        globals()[f"cmd_{args.command}"](args)


if __name__ == "__main__":
    main()
