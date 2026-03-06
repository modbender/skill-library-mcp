#!/usr/bin/env python3
"""GitHub Release Workflow CLI"""
import argparse
import subprocess
import sys
from pathlib import Path


def run(cmd: str, check: bool = True) -> None:
    """Run shell command"""
    print(f"→ {cmd}")
    result = subprocess.run(cmd, shell=True, check=check)
    if result.returncode != 0:
        sys.exit(result.returncode)


def cmd_init(args) -> None:
    """Initialize git repository"""
    if Path(".git").exists():
        print("Git repository already exists")
        return
    
    run("git init")
    run('git config user.name "Steven"')
    run('git config user.email "steven@example.com"')


def cmd_release(args) -> None:
    """Create a new release"""
    version = args.version
    
    print(f"Creating release {version}...")
    
    # Stage
    run("git add .")
    
    # Commit
    run(f'git commit -m "release: {version}"')
    
    # Tag
    run(f'git tag -a {version} -m "Version {version}"')
    
    # Push
    run("git push")
    run(f"git push origin {version}")
    
    print(f"✅ Release {version} complete!")


def cmd_status(args) -> None:
    """Show git status"""
    run("git status")


def cmd_log(args) -> None:
    """Show commit log"""
    run(f"git log --oneline -n {args.count}")


def main():
    parser = argparse.ArgumentParser(description="GitHub Release Workflow")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # init
    subparsers.add_parser("init", help="Initialize git repository")
    
    # release
    rel_parser = subparsers.add_parser("release", help="Create release")
    rel_parser.add_argument("version", help="Version (e.g., v1.0.0)")
    
    # status
    subparsers.add_parser("status", help="Show git status")
    
    # log
    log_parser = subparsers.add_parser("log", help="Show commit log")
    log_parser.add_argument("-n", "--count", type=int, default=10)
    
    args = parser.parse_args()
    
    if args.command == "init":
        cmd_init(args)
    elif args.command == "release":
        cmd_release(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "log":
        cmd_log(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
