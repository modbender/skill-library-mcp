#!/usr/bin/env python3
"""
Create a new bot configuration (controller config or script config).

Usage:
    # List available controller templates
    python create.py --list-controllers

    # List available scripts
    python create.py --list-scripts

    # List existing configs
    python create.py --list-configs

    # Create a controller config (shows template interactively)
    python create.py controller my_config --template market_making
"""

import argparse
import asyncio
import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from hbot_client import client


async def list_controllers():
    """List available controller templates."""
    async with client() as c:
        controllers = await c.controllers.list_controllers()

        print("Available Controller Templates:")
        print("-" * 50)

        if isinstance(controllers, dict):
            # Controllers organized by type
            for ctrl_type, names in controllers.items():
                if names:
                    print(f"\n  {ctrl_type}:")
                    for name in names:
                        print(f"    - {name}")
        elif isinstance(controllers, list):
            for ctrl in controllers:
                print(f"  {ctrl}")


async def list_scripts():
    """List available scripts."""
    async with client() as c:
        scripts = await c.scripts.list_scripts()

        print("Available Scripts:")
        print("-" * 50)
        for script in scripts:
            if isinstance(script, dict):
                name = script.get("name", script.get("id", str(script)))
                print(f"  {name}")
            else:
                print(f"  {script}")


async def list_configs():
    """List existing controller configs."""
    async with client() as c:
        configs = await c.controllers.list_controller_configs()

        print("Existing Configurations:")
        print("-" * 60)

        if not configs:
            print("  No configurations found")
            return

        print(f"  {'NAME':25} {'CONTROLLER':20} {'TYPE':15}")
        print("  " + "-" * 55)

        for cfg in configs:
            if isinstance(cfg, dict):
                name = cfg.get("id", cfg.get("name", "?"))
                controller = cfg.get("controller_name", cfg.get("controller", "?"))
                ctrl_type = cfg.get("controller_type", "?")
                print(f"  {name:25} {controller:20} {ctrl_type:15}")
            else:
                print(f"  {cfg}")


async def create_controller_config(name: str, template: str = None):
    """Create a controller configuration."""
    async with client() as c:
        if not template:
            print("Error: --template is required")
            print("\nList available templates with: python create.py --list-controllers")
            return

        # Get config template to show required fields
        try:
            # Try to get the config template for the controller
            controllers = await c.controllers.list_controllers()

            # Find the controller type
            ctrl_type = None
            if isinstance(controllers, dict):
                for ctype, names in controllers.items():
                    if template in names:
                        ctrl_type = ctype
                        break

            if ctrl_type:
                print(f"\nCreating config '{name}' from template '{template}' ({ctrl_type})")
                print("\nNote: Use the API directly or edit the YAML file to set parameters:")
                print(f"  Config path: conf/controllers/{name}.yml")
            else:
                print(f"Controller template '{template}' not found")
                return

        except Exception as e:
            print(f"Error: {e}")


def main():
    parser = argparse.ArgumentParser(description="Create bot configurations")
    parser.add_argument("type", nargs="?", choices=["controller", "script"], help="Config type")
    parser.add_argument("name", nargs="?", help="Config name")
    parser.add_argument("--list-controllers", action="store_true", help="List controller templates")
    parser.add_argument("--list-scripts", action="store_true", help="List available scripts")
    parser.add_argument("--list-configs", action="store_true", help="List existing configs")
    parser.add_argument("--template", help="Controller template name")
    args = parser.parse_args()

    try:
        if args.list_controllers:
            asyncio.run(list_controllers())
        elif args.list_scripts:
            asyncio.run(list_scripts())
        elif args.list_configs:
            asyncio.run(list_configs())
        elif args.type == "controller" and args.name:
            asyncio.run(create_controller_config(args.name, template=args.template))
        else:
            parser.print_help()
            print("\nExamples:")
            print("  python create.py --list-controllers      # List available templates")
            print("  python create.py --list-configs          # List existing configs")
            print("  python create.py controller my_config --template market_making")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
