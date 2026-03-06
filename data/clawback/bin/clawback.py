#!/usr/bin/env python3
"""
ClawBack CLI Wrapper - Entry point for the OpenClaw skill
ROBUST VERSION: Handles different execution contexts
"""

import os
import sys
import subprocess

def find_skill_dir():
    """Find the skill directory regardless of execution context."""
    # Try multiple approaches to find the skill directory
    
    # Approach 1: Relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(script_dir)
    
    # Check if this looks like a skill directory
    if os.path.exists(os.path.join(skill_dir, "SKILL.md")):
        return skill_dir
    
    # Approach 2: Check environment variable
    if "OPENCLAW_SKILL_DIR" in os.environ:
        skill_dir = os.environ["OPENCLAW_SKILL_DIR"]
        if os.path.exists(os.path.join(skill_dir, "SKILL.md")):
            return skill_dir
    
    # Approach 3: Check current working directory
    cwd = os.getcwd()
    if os.path.exists(os.path.join(cwd, "SKILL.md")):
        return cwd
    
    # Approach 4: Check parent of current directory
    parent_dir = os.path.dirname(cwd)
    if os.path.exists(os.path.join(parent_dir, "SKILL.md")):
        return parent_dir
    
    # If all else fails, return the script's parent directory
    return skill_dir

def main():
    # Find the skill directory
    skill_dir = find_skill_dir()
    
    # Check if virtual environment exists
    venv_python = os.path.join(skill_dir, "venv", "bin", "python")
    
    if os.path.exists(venv_python):
        # Use the virtual environment Python
        cmd = [venv_python, "-m", "clawback.cli"] + sys.argv[1:]
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)
    else:
        # Try to use the installed package
        try:
            # Add src directory to path
            src_dir = os.path.join(skill_dir, "src")
            sys.path.insert(0, src_dir)
            
            from clawback.cli import main as cli_main
            cli_main()
        except ImportError as e:
            print(f"Error: {e}", file=sys.stderr)
            print("\nVirtual environment not found and clawback not installed.", file=sys.stderr)
            print("\nPlease run:", file=sys.stderr)
            print(f"  cd {skill_dir}", file=sys.stderr)
            print("  ./setup.sh", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()