#!/usr/bin/env python3
"""Process emails through the rule-based pipeline.

Usage:
    python3 scripts/fetch_mail.py --config c.yaml | python3 scripts/process_mail.py --rules-file rules.yaml
    python3 scripts/process_mail.py --input messages.json --rules '[...]'
    python3 scripts/process_mail.py --input messages.json --config config.yaml --account work --format cli

Output: JSON (default) or CLI summary to stdout.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from lib.account_manager import AccountManager
from lib.defaults import resolve_config_path
from lib.models import EmailMessage
from lib.processor import EmailProcessor


def main() -> None:
    parser = argparse.ArgumentParser(description="Process emails through rule pipeline")

    parser.add_argument("--account", default="",
                        help="Account name (loads per-account + global rules from config)")
    parser.add_argument("--input", default="",
                        help="JSON file with messages (or reads stdin)")
    parser.add_argument("--rules", default="",
                        help="JSON string of rules array")
    parser.add_argument("--rules-file", default="",
                        help="YAML/JSON file with rules")
    parser.add_argument("--config", default="",
                        help="YAML config file (reads rules from 'rules' key or per-account)")
    parser.add_argument("--format", choices=["json", "cli"], default="json",
                        help="Output format (default: json)")

    args = parser.parse_args()
    args.config = resolve_config_path(args.config)

    # Load messages
    if args.input:
        with open(args.input) as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)

    if isinstance(data, dict) and "messages" in data:
        msg_dicts = data["messages"]
    elif isinstance(data, list):
        msg_dicts = data
    else:
        _error("Expected JSON array or object with 'messages' key")
        return

    messages = [EmailMessage.from_dict(d) for d in msg_dicts]

    # Load rules
    rules_config: list[dict] = []
    if args.rules:
        try:
            rules_config = json.loads(args.rules)
        except json.JSONDecodeError as exc:
            _error(f"Invalid --rules JSON: {exc}")
    elif args.rules_file:
        try:
            with open(args.rules_file) as f:
                if args.rules_file.endswith((".yaml", ".yml")):
                    import yaml
                    loaded = yaml.safe_load(f) or {}
                else:
                    loaded = json.load(f)
                if isinstance(loaded, list):
                    rules_config = loaded
                elif isinstance(loaded, dict):
                    rules_config = loaded.get("rules", loaded.get("processing_rules", []))
        except Exception as exc:
            _error(f"Failed to load rules file: {exc}")
    elif args.config:
        try:
            mgr = AccountManager.from_yaml(args.config)
            if args.account:
                rules_config = mgr.get_rules(args.account)
            else:
                rules_config = mgr.get_rules()
        except Exception as exc:
            _error(f"Failed to load config: {exc}")

    if not rules_config:
        _error("No processing rules provided. Use --rules, --rules-file, or --config.")

    # Process
    processor = EmailProcessor.from_config(rules_config)
    results = processor.process_batch(messages)

    if args.format == "cli":
        matched = sum(len(r.matched_rules) for r in results)
        print(f"  Processed {len(results)} messages, {matched} rules matched")
        print()
        for r in results:
            subj = r.message.subject[:50] or "(no subject)"
            acct = f"[{r.message.account}] " if r.message.account else ""
            if r.matched_rules:
                rules_str = ", ".join(r.matched_rules)
                actions_str = ", ".join(r.actions_taken) if r.actions_taken else ""
                print(f"  {acct}{subj}")
                print(f"    Rules:   {rules_str}")
                if actions_str:
                    print(f"    Actions: {actions_str}")
                if r.tags:
                    print(f"    Tags:    {', '.join(r.tags)}")
                if r.move_to:
                    print(f"    Move to: {r.move_to}")
            else:
                print(f"  {acct}{subj}  (no match)")
        print()
    else:
        output = {
            "messages_processed": len(results),
            "rules_matched": sum(len(r.matched_rules) for r in results),
            "results": [r.to_dict() for r in results],
        }
        json.dump(output, sys.stdout, indent=2)
        print()


def _error(msg: str) -> None:
    json.dump({"error": msg}, sys.stderr)
    print(file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
