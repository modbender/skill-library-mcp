#!/usr/bin/env python3
"""Config helper for mediator - safely manages YAML config."""

import argparse
import os
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Installing PyYAML...")
    os.system(f"{sys.executable} -m pip install -q pyyaml")
    import yaml

CONFIG_FILE = Path.home() / ".clawdbot" / "mediator.yaml"


def load_config():
    if not CONFIG_FILE.exists():
        return {"mediator": {"contacts": []}}
    with open(CONFIG_FILE) as f:
        return yaml.safe_load(f) or {"mediator": {"contacts": []}}


def save_config(config):
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


def cmd_add(args):
    config = load_config()
    
    if "contacts" not in config.get("mediator", {}):
        config.setdefault("mediator", {})["contacts"] = []
    
    # Check if contact already exists
    contacts = config["mediator"]["contacts"]
    for c in contacts:
        if c.get("name", "").lower() == args.name.lower():
            print(f"Contact '{args.name}' already exists. Remove first to update.")
            sys.exit(1)
    
    # Build contact entry
    contact = {
        "name": args.name,
        "channels": args.channels.split(","),
        "mode": args.mode,
        "summarize": args.summarize,
        "respond": args.respond,
    }
    
    if args.email:
        contact["email"] = args.email
    if args.phone:
        contact["phone"] = args.phone
    
    contacts.append(contact)
    save_config(config)


def cmd_remove(args):
    config = load_config()
    contacts = config.get("mediator", {}).get("contacts", [])
    
    original_len = len(contacts)
    contacts = [c for c in contacts if c.get("name", "").lower() != args.name.lower()]
    
    if len(contacts) == original_len:
        print(f"Contact '{args.name}' not found.")
        sys.exit(1)
    
    config["mediator"]["contacts"] = contacts
    save_config(config)


def cmd_list(args):
    config = load_config()
    contacts = config.get("mediator", {}).get("contacts", [])
    
    if not contacts:
        print("No contacts configured.")
        print("Add one with: mediator.sh add <name> --email <addr> --channels email,imessage")
        return
    
    print(f"Configured contacts ({len(contacts)}):")
    print("")
    for c in contacts:
        name = c.get("name", "Unknown")
        email = c.get("email", "-")
        phone = c.get("phone", "-")
        channels = ", ".join(c.get("channels", []))
        mode = c.get("mode", "intercept")
        summarize = c.get("summarize", "facts-only")
        
        print(f"  {name}")
        print(f"    Email: {email}")
        print(f"    Phone: {phone}")
        print(f"    Channels: {channels}")
        print(f"    Mode: {mode} | Summarize: {summarize}")
        print("")


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    
    # Add command
    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("--name", required=True)
    add_parser.add_argument("--email", default="")
    add_parser.add_argument("--phone", default="")
    add_parser.add_argument("--channels", default="email")
    add_parser.add_argument("--mode", default="intercept")
    add_parser.add_argument("--summarize", default="facts-only")
    add_parser.add_argument("--respond", default="draft")
    
    # Remove command
    remove_parser = subparsers.add_parser("remove")
    remove_parser.add_argument("--name", required=True)
    
    # List command
    subparsers.add_parser("list")
    
    args = parser.parse_args()
    
    if args.command == "add":
        cmd_add(args)
    elif args.command == "remove":
        cmd_remove(args)
    elif args.command == "list":
        cmd_list(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
