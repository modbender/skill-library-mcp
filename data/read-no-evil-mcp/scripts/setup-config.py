#!/usr/bin/env python3
"""
Flag-driven configuration manager for read-no-evil-mcp.

Creates and manages config.yaml files for the read-no-evil-mcp server.
Zero dependencies — uses only Python stdlib (3.8+).
Designed for invocation by LLM agents (no interactive prompts).

Usage:
    setup-config.py create [--threshold 0.5] [--force]
    setup-config.py add --email USER@DOMAIN --host IMAP_HOST [--smtp-host SMTP_HOST] ...
    setup-config.py remove <account_id>
    setup-config.py list
    setup-config.py show
"""

import argparse
import os
import re
import sys
import tempfile


# --- Constants ---

DEFAULT_CONFIG = os.path.join(
    os.environ.get("XDG_CONFIG_HOME", os.path.join(os.path.expanduser("~"), ".config")),
    "read-no-evil-mcp",
    "config.yaml",
)

ACCOUNT_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


# --- YAML serializer ---

def dump_yaml(config):
    """Serialize config dict to YAML string."""
    lines = []
    _dump_dict(lines, config, indent=0)
    return "\n".join(lines) + "\n"


def _dump_dict(lines, d, indent):
    prefix = "  " * indent
    for key, val in d.items():
        if isinstance(val, dict):
            lines.append(f"{prefix}{key}:")
            _dump_dict(lines, val, indent + 1)
        elif isinstance(val, list):
            lines.append(f"{prefix}{key}:")
            _dump_list(lines, val, indent + 1)
        else:
            lines.append(f"{prefix}{key}: {_format_scalar(val)}")


def _dump_list(lines, lst, indent):
    prefix = "  " * indent
    for item in lst:
        if isinstance(item, dict):
            keys = list(item.items())
            first_key, first_val = keys[0]
            if isinstance(first_val, (dict, list)):
                lines.append(f"{prefix}- {first_key}:")
                if isinstance(first_val, dict):
                    _dump_dict(lines, first_val, indent + 2)
                else:
                    _dump_list(lines, first_val, indent + 2)
            else:
                lines.append(f"{prefix}- {first_key}: {_format_scalar(first_val)}")
            for key, val in keys[1:]:
                if isinstance(val, dict):
                    lines.append(f"{prefix}  {key}:")
                    _dump_dict(lines, val, indent + 2)
                elif isinstance(val, list):
                    lines.append(f"{prefix}  {key}:")
                    _dump_list(lines, val, indent + 2)
                else:
                    lines.append(f"{prefix}  {key}: {_format_scalar(val)}")
        else:
            lines.append(f"{prefix}- {_format_scalar(item)}")


def _format_scalar(val):
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, int):
        return str(val)
    if isinstance(val, float):
        return str(val)
    if isinstance(val, str):
        return _quote_string(val)
    if val is None:
        return "null"
    return str(val)


def _quote_string(s):
    """Quote strings that need it, leave simple ones bare."""
    if not s:
        return '""'
    needs_quote = False
    if s.strip() != s:
        needs_quote = True
    if s.lower() in ("true", "false", "null", "yes", "no", "on", "off"):
        needs_quote = True
    special = set(":#{}[]!&*?,|>'\"@`")
    if any(c in special for c in s):
        needs_quote = True
    try:
        float(s)
        needs_quote = True
    except ValueError:
        pass
    if needs_quote:
        escaped = s.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return s


# --- YAML parser ---

def load_yaml(text):
    """Parse YAML text (as produced by dump_yaml) into a dict."""
    lines = _prepare_lines(text)
    if not lines:
        return {}
    result, _ = _parse_block(lines, 0, 0)
    return result if isinstance(result, dict) else {}


def _prepare_lines(text):
    """Strip comments and blank lines, return list of (indent, content) tuples."""
    result = []
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip())
        result.append((indent, stripped))
    return result


def _parse_block(lines, pos, base_indent):
    """Parse a block at a given indent level. Returns (value, next_pos)."""
    if pos >= len(lines):
        return {}, pos

    indent, content = lines[pos]

    if content.startswith("- "):
        return _parse_list_block(lines, pos, base_indent)
    else:
        return _parse_dict_block(lines, pos, base_indent)


def _parse_dict_block(lines, pos, base_indent):
    """Parse a dict block."""
    result = {}
    while pos < len(lines):
        indent, content = lines[pos]
        if indent < base_indent:
            break
        if indent > base_indent:
            break
        if content.startswith("- "):
            break

        key, val_str = _split_key_value(content)
        if val_str is not None:
            result[key] = _parse_scalar(val_str)
            pos += 1
        else:
            # Block value — peek at next line to determine type
            if pos + 1 < len(lines) and lines[pos + 1][0] > indent:
                child, pos = _parse_block(lines, pos + 1, lines[pos + 1][0])
                result[key] = child
            else:
                result[key] = None
                pos += 1
    return result, pos


def _parse_list_block(lines, pos, base_indent):
    """Parse a list block."""
    result = []
    while pos < len(lines):
        indent, content = lines[pos]
        if indent < base_indent:
            break
        if indent > base_indent:
            break
        if not content.startswith("- "):
            break

        item_content = content[2:]
        key, val_str = _split_key_value(item_content)

        if key is not None and val_str is not None:
            # - key: value — start of a dict item
            item = {key: _parse_scalar(val_str)}
            pos += 1
            # Collect remaining keys at indent + 2
            child_indent = base_indent + 2
            while pos < len(lines) and lines[pos][0] >= child_indent:
                if lines[pos][0] > child_indent and not lines[pos][1].startswith("- "):
                    break
                if lines[pos][0] < child_indent:
                    break
                ci, cc = lines[pos]
                if cc.startswith("- "):
                    break
                k2, v2 = _split_key_value(cc)
                if k2 is not None and v2 is not None:
                    item[k2] = _parse_scalar(v2)
                    pos += 1
                elif k2 is not None:
                    # Nested block
                    if pos + 1 < len(lines) and lines[pos + 1][0] > ci:
                        child, pos = _parse_block(lines, pos + 1, lines[pos + 1][0])
                        item[k2] = child
                    else:
                        item[k2] = None
                        pos += 1
                else:
                    break
            result.append(item)
        elif key is not None and val_str is None:
            # - key:  (block value follows)
            if pos + 1 < len(lines) and lines[pos + 1][0] > base_indent:
                child, pos_next = _parse_block(lines, pos + 1, lines[pos + 1][0])
                result.append({key: child})
                pos = pos_next
            else:
                result.append({key: None})
                pos += 1
        else:
            result.append(_parse_scalar(item_content))
            pos += 1
    return result, pos


def _split_key_value(content):
    """Split 'key: value' or 'key:' line. Returns (key, value_str) or (key, None) or (None, None)."""
    # Handle quoted keys (unlikely in our format but be safe)
    if content.startswith('"'):
        end = content.find('"', 1)
        if end == -1:
            return None, None
        key = content[1:end]
        rest = content[end + 1:]
        if rest.startswith(":"):
            val = rest[1:].strip()
            return key, val if val else None
        return None, None

    colon_pos = content.find(":")
    if colon_pos == -1:
        return None, None

    key = content[:colon_pos]
    rest = content[colon_pos + 1:]

    if not rest:
        return key, None
    if rest[0] == " ":
        val = rest[1:].strip() if len(rest) > 1 else ""
        return key, val if val else None
    # Colon in the middle of a word, not a key separator
    return None, None


def _parse_scalar(s):
    """Parse a scalar string into a Python value."""
    s = s.strip()
    if not s:
        return ""

    # Quoted string
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        inner = s[1:-1]
        return inner.replace('\\"', '"').replace("\\\\", "\\")

    low = s.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    if low == "null":
        return None

    # Integer
    try:
        return int(s)
    except ValueError:
        pass

    # Float
    try:
        return float(s)
    except ValueError:
        pass

    return s


# --- Config I/O ---

def load_config(path):
    """Load and parse config file. Returns dict."""
    try:
        with open(path) as f:
            return load_yaml(f.read())
    except FileNotFoundError:
        print(f"Error: Config file not found: {path}", file=sys.stderr)
        print("Run 'setup-config.py create' to create one.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Cannot parse config file: {path}", file=sys.stderr)
        print(f"  {e}", file=sys.stderr)
        print("Fix it manually or run 'setup-config.py create' to start fresh.", file=sys.stderr)
        sys.exit(1)


def write_config(path, config):
    """Write config dict to YAML file. Creates parent dirs. Uses atomic write."""
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    text = dump_yaml(config)
    fd, tmp_path = tempfile.mkstemp(dir=parent, suffix=".yaml.tmp")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(text)
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


# --- Helpers ---

def suggest_account_id(email, existing_ids):
    """Suggest account ID from email address."""
    local = email.split("@")[0]
    candidate = re.sub(r"[^a-z0-9-]", "", local.lower())
    if not candidate:
        candidate = "default"
    if candidate not in existing_ids:
        return candidate
    for i in range(2, 100):
        if f"{candidate}{i}" not in existing_ids:
            return f"{candidate}{i}"
    return candidate


def build_account(args, existing_ids):
    """Build an account dict from CLI flags. Validates and errors on missing fields."""
    email = args.email

    if "@" not in email or "." not in email.split("@")[-1]:
        print(f"Error: Invalid email address: {email}", file=sys.stderr)
        sys.exit(1)

    account_id = args.id if args.id else suggest_account_id(email, existing_ids)
    account_id = account_id.lower()

    if account_id in existing_ids:
        print(f"Error: Account '{account_id}' already exists.", file=sys.stderr)
        sys.exit(1)
    if not ACCOUNT_ID_RE.match(account_id):
        print("Error: Account ID must be lowercase alphanumeric with hyphens only.", file=sys.stderr)
        sys.exit(1)

    # SMTP is only required when --send is enabled
    if args.send and not args.smtp_host:
        print("Error: --smtp-host is required when --send is enabled.", file=sys.stderr)
        sys.exit(1)

    account = {"id": account_id, "type": "imap"}
    account["host"] = args.host
    account["port"] = args.port
    account["ssl"] = not args.no_ssl
    account["username"] = email

    if args.smtp_host:
        account["smtp_host"] = args.smtp_host
        account["smtp_port"] = args.smtp_port
        account["smtp_ssl"] = args.smtp_ssl

    # Permissions (read is always on)
    account["permissions"] = {
        "read": True,
        "send": args.send,
        "delete": args.delete,
        "move": args.move,
    }

    if args.threshold is not None:
        account["protection"] = {"threshold": args.threshold}

    return account


def create_env_file(config_path, account_ids):
    """Create .env file with password placeholders. Preserves existing values."""
    env_path = os.path.join(os.path.dirname(config_path), ".env")

    existing_vars = {}
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, val = line.partition("=")
                    existing_vars[key.strip()] = val.strip()

    new_lines = [
        "# read-no-evil-mcp credentials",
        "# !! Keep this file secret — do not commit to version control !!",
    ]
    for aid in account_ids:
        var_name = f"RNOE_ACCOUNT_{aid.upper()}_PASSWORD"
        val = existing_vars.get(var_name, "your-app-password-here")
        new_lines.append(f"{var_name}={val}")

    parent = os.path.dirname(env_path)
    fd, tmp_path = tempfile.mkstemp(dir=parent, suffix=".env.tmp")
    try:
        with os.fdopen(fd, "w") as f:
            f.write("\n".join(new_lines) + "\n")
        os.replace(tmp_path, env_path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise

    os.chmod(env_path, 0o600)
    print(f"Created .env: {env_path}")


# --- Subcommands ---

def cmd_create(args):
    """Create a new config file."""
    if os.path.exists(args.config) and not args.force:
        print(f"Error: Config file already exists: {args.config}", file=sys.stderr)
        print("Use --force to overwrite.", file=sys.stderr)
        sys.exit(1)

    config = {
        "protection": {"threshold": args.threshold},
        "accounts": [],
    }

    write_config(args.config, config)
    print(f"Config created: {args.config}")


def cmd_add(args):
    """Add an account to existing config."""
    config = load_config(args.config)
    accounts = config.get("accounts") or []
    existing_ids = {a.get("id", "") for a in accounts}

    account = build_account(args, existing_ids)
    accounts.append(account)
    config["accounts"] = accounts

    write_config(args.config, config)

    env_var = f"RNOE_ACCOUNT_{account['id'].upper()}_PASSWORD"
    print(f"Account '{account['id']}' added to: {args.config}")
    print(f"Set password env var: {env_var}")

    if args.create_env:
        account_ids = [a["id"] for a in accounts]
        create_env_file(args.config, account_ids)


def cmd_remove(args):
    """Remove an account by ID."""
    config = load_config(args.config)
    accounts = config.get("accounts") or []
    original_len = len(accounts)
    new_accounts = [a for a in accounts if a.get("id") != args.account_id]

    if len(new_accounts) == original_len:
        print(f"Error: No account with ID '{args.account_id}'", file=sys.stderr)
        sys.exit(1)

    config["accounts"] = new_accounts
    write_config(args.config, config)
    print(f"Account '{args.account_id}' removed from config.")


def cmd_list(args):
    """List configured accounts."""
    config = load_config(args.config)
    accounts = config.get("accounts") or []
    if not accounts:
        print("No accounts configured.")
        return
    print(f"Accounts in {args.config}:")
    for a in accounts:
        host = a.get("host", "?")
        user = a.get("username", "?")
        print(f"  {a.get('id', '?'):12s} {user:30s} {host}")


def cmd_show(args):
    """Print the raw config file contents."""
    try:
        with open(args.config) as f:
            print(f.read(), end="")
    except FileNotFoundError:
        print(f"Error: Config file not found: {args.config}", file=sys.stderr)
        sys.exit(1)


# --- Main ---

def main():
    parser = argparse.ArgumentParser(
        description="Manage read-no-evil-mcp configuration (flag-driven, no interactive prompts)"
    )
    parser.add_argument(
        "--config", default=DEFAULT_CONFIG, help="Config file path"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # create
    create_parser = subparsers.add_parser("create", help="Create config skeleton")
    create_parser.add_argument("--threshold", type=float, default=0.5, help="Global protection threshold (default: 0.5)")
    create_parser.add_argument("--force", action="store_true", help="Overwrite existing config")

    # add
    add_parser = subparsers.add_parser("add", help="Add an account")
    add_parser.add_argument("--email", required=True, help="Email address (required)")
    add_parser.add_argument("--id", default=None, help="Account ID (auto-generated from email if omitted)")
    add_parser.add_argument("--host", required=True, help="IMAP host (required)")
    add_parser.add_argument("--port", type=int, default=993, help="IMAP port (default: 993)")
    add_parser.add_argument("--smtp-host", default=None, help="SMTP host (required when --send is used)")
    add_parser.add_argument("--smtp-port", type=int, default=587, help="SMTP port (default: 587)")
    add_parser.add_argument("--no-ssl", action="store_true", default=False, help="Disable IMAP SSL")
    add_parser.add_argument("--smtp-ssl", action="store_true", default=False, help="Enable SMTP SSL")
    add_parser.add_argument("--send", action="store_true", default=False, help="Allow sending emails")
    add_parser.add_argument("--delete", action="store_true", default=False, help="Allow deleting emails")
    add_parser.add_argument("--move", action="store_true", default=False, help="Allow moving emails")
    add_parser.add_argument("--threshold", type=float, default=None, help="Per-account protection threshold")
    add_parser.add_argument("--create-env", action="store_true", default=False, help="Create .env with password placeholders")

    # remove
    remove_parser = subparsers.add_parser("remove", help="Remove an account")
    remove_parser.add_argument("account_id", help="Account ID to remove")

    # list / show
    subparsers.add_parser("list", help="List configured accounts")
    subparsers.add_parser("show", help="Print full config")

    args = parser.parse_args()

    commands = {
        "create": cmd_create,
        "add": cmd_add,
        "remove": cmd_remove,
        "list": cmd_list,
        "show": cmd_show,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
