#!/usr/bin/env python3
"""
Token Optimizer CLI
Command-line interface for OpenClaw token optimization.
"""

import sys
import json
import argparse
from pathlib import Path

from src import __version__


def main():
    parser = argparse.ArgumentParser(
        prog='token-optimizer',
        description='Reduce OpenClaw AI costs by 97%',
        epilog='For more info: https://github.com/smartpeopleconnected/openclaw-token-optimizer'
    )

    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Disable colored output'
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Analyze command
    subparsers.add_parser(
        'analyze',
        help='Analyze current configuration and show optimization opportunities'
    )

    # Optimize command
    optimize_parser = subparsers.add_parser(
        'optimize',
        help='Apply token optimizations'
    )
    optimize_parser.add_argument(
        '--mode',
        choices=['full', 'routing', 'heartbeat', 'caching', 'limits'],
        default='full',
        help='Optimization mode (default: full)'
    )
    optimize_parser.add_argument(
        '--apply',
        action='store_true',
        help='Apply changes (default is dry-run preview)'
    )

    # Verify command
    subparsers.add_parser(
        'verify',
        help='Verify optimization setup and show estimated savings'
    )

    # Setup heartbeat command
    heartbeat_parser = subparsers.add_parser(
        'setup-heartbeat',
        help='Configure heartbeat provider (ollama, lmstudio, groq, none)'
    )
    heartbeat_parser.add_argument(
        '--provider',
        choices=['ollama', 'lmstudio', 'groq', 'none'],
        default='ollama',
        help='Heartbeat provider (default: ollama)'
    )
    heartbeat_parser.add_argument(
        '--model',
        default=None,
        help='Model name for heartbeat (default: provider-specific)'
    )
    heartbeat_parser.add_argument(
        '--fallback',
        choices=['ollama', 'lmstudio', 'groq', 'none'],
        default=None,
        help='Fallback provider if primary is unavailable'
    )
    heartbeat_parser.add_argument(
        '--apply',
        action='store_true',
        help='Apply changes (default is dry-run preview)'
    )

    # Rollback command
    rollback_parser = subparsers.add_parser(
        'rollback',
        help='Restore a previous configuration backup'
    )
    rollback_parser.add_argument(
        '--list',
        action='store_true',
        dest='list_backups',
        help='List available backups'
    )
    rollback_parser.add_argument(
        '--to',
        dest='backup_file',
        default=None,
        help='Restore a specific backup file'
    )

    # Health command
    subparsers.add_parser(
        'health',
        help='Quick system health check'
    )

    # Version command
    subparsers.add_parser(
        'version',
        help='Show version information'
    )

    args = parser.parse_args()

    # Apply --no-color globally
    if args.no_color:
        import src.colors
        src.colors.NO_COLOR = True

    if args.command == 'analyze':
        from src.analyzer import main as analyze_main
        return analyze_main()

    elif args.command == 'optimize':
        from src.optimizer import TokenOptimizer
        dry_run = not args.apply
        if dry_run:
            from src.colors import Colors, colorize
            print(colorize("[DRY-RUN] Preview mode. Use --apply to make changes.\n", Colors.YELLOW))
        optimizer = TokenOptimizer(dry_run=dry_run)
        optimizer.optimize_mode(args.mode)
        return 0

    elif args.command == 'verify':
        from src.verify import main as verify_main
        return verify_main()

    elif args.command == 'setup-heartbeat':
        from src.optimizer import TokenOptimizer
        from src.colors import Colors, colorize
        dry_run = not args.apply
        if dry_run:
            print(colorize("[DRY-RUN] Preview mode. Use --apply to make changes.\n", Colors.YELLOW))
        optimizer = TokenOptimizer(dry_run=dry_run)
        optimizer.setup_heartbeat_provider(
            provider=args.provider,
            model=args.model,
            fallback=args.fallback
        )
        config = optimizer.load_config()
        config = optimizer.apply_heartbeat(
            config,
            provider=args.provider,
            model=args.model,
            fallback=args.fallback
        )
        optimizer.save_config(config)
        return 0

    elif args.command == 'rollback':
        from src.optimizer import TokenOptimizer
        from src.colors import Colors, colorize
        optimizer = TokenOptimizer()

        if args.list_backups:
            backups = optimizer.list_backups()
            if not backups:
                print(colorize("[INFO] No backups found", Colors.YELLOW))
            else:
                print(colorize(f"[INFO] {len(backups)} backup(s) found:\n", Colors.CYAN))
                for b in backups:
                    size_kb = b.stat().st_size / 1024
                    print(f"  {b.name}  ({size_kb:.1f} KB)")
                print(colorize(f"\nRestore with: token-optimizer rollback --to <filename>", Colors.CYAN))
            return 0

        if args.backup_file:
            backup_path = optimizer.backup_dir / args.backup_file
            if not backup_path.exists():
                # Try as absolute path
                backup_path = Path(args.backup_file)
            success = optimizer.restore_backup(backup_path)
            return 0 if success else 1

        print(colorize("[ERROR] Use --list to see backups or --to <file> to restore", Colors.RED))
        return 1

    elif args.command == 'health':
        from src.colors import Colors, colorize
        from src.optimizer import resolve_heartbeat_provider, check_heartbeat_provider

        print(colorize("\n=== Token Optimizer - Health Check ===\n", Colors.BOLD + Colors.CYAN))

        openclaw_dir = Path.home() / '.openclaw'
        config_path = openclaw_dir / 'openclaw.json'
        checks_passed = 0
        checks_total = 0

        # 1. Config exists
        checks_total += 1
        if config_path.exists():
            print(colorize("[PASS] Config file exists", Colors.GREEN))
            checks_passed += 1
        else:
            print(colorize("[FAIL] Config file not found", Colors.RED))
            print(colorize("  Run: token-optimizer optimize", Colors.CYAN))

        # 2. Valid JSON
        config = {}
        checks_total += 1
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                print(colorize("[PASS] Config is valid JSON", Colors.GREEN))
                checks_passed += 1
            except (json.JSONDecodeError, IOError):
                print(colorize("[FAIL] Config is not valid JSON", Colors.RED))
        else:
            print(colorize("[SKIP] Config not found, skipping JSON check", Colors.YELLOW))

        # 3. Provider reachable
        checks_total += 1
        provider = resolve_heartbeat_provider(config)
        if provider == "none":
            print(colorize("[SKIP] Heartbeat disabled (provider: none)", Colors.YELLOW))
            checks_passed += 1
        elif check_heartbeat_provider(provider):
            print(colorize(f"[PASS] Heartbeat provider '{provider}' is reachable", Colors.GREEN))
            checks_passed += 1
        else:
            print(colorize(f"[FAIL] Heartbeat provider '{provider}' is not reachable", Colors.RED))

        # 4. Workspace lean
        checks_total += 1
        workspace_dir = openclaw_dir / 'workspace'
        if workspace_dir.exists():
            total_size = sum(f.stat().st_size for f in workspace_dir.iterdir() if f.is_file())
            size_kb = total_size / 1024
            if size_kb < 15:
                print(colorize(f"[PASS] Workspace is lean ({size_kb:.1f} KB)", Colors.GREEN))
                checks_passed += 1
            else:
                print(colorize(f"[WARN] Workspace is large ({size_kb:.1f} KB, target <15 KB)", Colors.YELLOW))
        else:
            print(colorize("[SKIP] No workspace directory found", Colors.YELLOW))
            checks_passed += 1

        # 5. Budget active
        checks_total += 1
        budgets = config.get('budgets', {})
        if budgets.get('daily') or budgets.get('monthly'):
            print(colorize(f"[PASS] Budget controls active (daily: ${budgets.get('daily', 'n/a')}, monthly: ${budgets.get('monthly', 'n/a')})", Colors.GREEN))
            checks_passed += 1
        else:
            print(colorize("[FAIL] No budget controls configured", Colors.RED))

        # Summary
        print(colorize(f"\n{checks_passed}/{checks_total} checks passed", Colors.BOLD))
        return 0 if checks_passed == checks_total else 1

    elif args.command == 'version':
        print(f"Token Optimizer v{__version__}")
        print("Reduce OpenClaw AI costs by 97%")
        return 0

    else:
        parser.print_help()
        return 0


if __name__ == '__main__':
    sys.exit(main())
