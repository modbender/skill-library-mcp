#!/usr/bin/env python3
"""
Dependency Update Checker - CLI tool to check for outdated dependencies
"""

import argparse
import json
import os
import subprocess
import sys
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

def detect_package_managers(path: str = ".") -> Dict[str, str]:
    """Detect which package managers are relevant based on files in directory."""
    path = os.path.abspath(path)
    managers = {}
    
    # Check for npm/package.json
    package_json = os.path.join(path, "package.json")
    if os.path.exists(package_json):
        managers["npm"] = package_json
    
    # Check for pip/requirements.txt
    requirements_txt = os.path.join(path, "requirements.txt")
    if os.path.exists(requirements_txt):
        managers["pip"] = requirements_txt
    
    # Check for Pipfile
    pipfile = os.path.join(path, "Pipfile")
    if os.path.exists(pipfile):
        managers["pip"] = pipfile
    
    # Check for poetry/pyproject.toml
    pyproject_toml = os.path.join(path, "pyproject.toml")
    if os.path.exists(pyproject_toml):
        # Check if it's a poetry project
        try:
            with open(pyproject_toml, "r") as f:
                content = f.read()
                if "tool.poetry" in content:
                    managers["poetry"] = pyproject_toml
        except:
            pass
    
    return managers

def check_command_exists(cmd: str) -> bool:
    """Check if a command exists in PATH."""
    try:
        subprocess.run(["which", cmd], capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def run_command(cmd: List[str], timeout: int = 30, cwd: str = ".") -> Dict[str, Any]:
    """Run a command and return standardized result."""
    start_time = time.time()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd
        )
        elapsed = time.time() - start_time
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "elapsed_time": elapsed
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Command timed out after {timeout} seconds",
            "elapsed_time": time.time() - start_time
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "elapsed_time": time.time() - start_time
        }

def parse_npm_outdated(output: str) -> List[Dict[str, str]]:
    """Parse npm outdated output."""
    try:
        # Try to parse as JSON first
        data = json.loads(output)
        outdated = []
        for package, info in data.items():
            outdated.append({
                "package": package,
                "current": info.get("current", ""),
                "wanted": info.get("wanted", ""),
                "latest": info.get("latest", ""),
                "type": info.get("type", "dependencies")
            })
        return outdated
    except json.JSONDecodeError:
        # Fallback to text parsing
        outdated = []
        lines = output.strip().split("\n")
        if len(lines) > 1:
            # Skip header line
            for line in lines[1:]:
                parts = line.split()
                if len(parts) >= 4:
                    outdated.append({
                        "package": parts[0],
                        "current": parts[1],
                        "wanted": parts[2],
                        "latest": parts[3],
                        "type": "unknown"
                    })
        return outdated

def parse_pip_outdated(output: str) -> List[Dict[str, str]]:
    """Parse pip list --outdated output."""
    try:
        # Try to parse as JSON first
        data = json.loads(output)
        outdated = []
        for item in data:
            outdated.append({
                "package": item.get("name", ""),
                "current": item.get("version", ""),
                "latest": item.get("latest_version", "")
            })
        return outdated
    except json.JSONDecodeError:
        # Parse text output
        outdated = []
        lines = output.strip().split("\n")
        if len(lines) > 2:
            # Skip header lines
            for line in lines[2:]:
                parts = line.split()
                if len(parts) >= 3:
                    outdated.append({
                        "package": parts[0],
                        "current": parts[1],
                        "latest": parts[2]
                    })
        return outdated

def parse_poetry_outdated(output: str) -> List[Dict[str, str]]:
    """Parse poetry show --outdated output."""
    outdated = []
    lines = output.strip().split("\n")
    for line in lines:
        parts = line.split()
        if len(parts) >= 3 and parts[0] and not parts[0].startswith("-"):
            outdated.append({
                "package": parts[0],
                "current": parts[1],
                "latest": parts[2]
            })
    return outdated

def check_npm(path: str, timeout: int) -> Dict[str, Any]:
    """Check npm dependencies."""
    result = {
        "manager": "npm",
        "success": False,
        "outdated": [],
        "error": None
    }
    
    if not check_command_exists("npm"):
        result["error"] = "npm not found in PATH"
        return result
    
    # Try JSON output first
    cmd_result = run_command(["npm", "outdated", "--json"], timeout=timeout, cwd=path)
    if cmd_result["success"]:
        result["success"] = True
        result["outdated"] = parse_npm_outdated(cmd_result["stdout"])
    else:
        # Fallback to text output
        cmd_result = run_command(["npm", "outdated"], timeout=timeout, cwd=path)
        if cmd_result["success"]:
            result["success"] = True
            result["outdated"] = parse_npm_outdated(cmd_result["stdout"])
        else:
            result["error"] = cmd_result.get("error", cmd_result.get("stderr", "Unknown error"))
    
    return result

def check_pip(path: str, timeout: int) -> Dict[str, Any]:
    """Check pip dependencies."""
    result = {
        "manager": "pip",
        "success": False,
        "outdated": [],
        "error": None
    }
    
    if not check_command_exists("pip"):
        result["error"] = "pip not found in PATH"
        return result
    
    # Try JSON output
    cmd_result = run_command(["pip", "list", "--outdated", "--format=json"], timeout=timeout, cwd=path)
    if cmd_result["success"]:
        result["success"] = True
        result["outdated"] = parse_pip_outdated(cmd_result["stdout"])
    else:
        # Fallback to text output
        cmd_result = run_command(["pip", "list", "--outdated"], timeout=timeout, cwd=path)
        if cmd_result["success"]:
            result["success"] = True
            result["outdated"] = parse_pip_outdated(cmd_result["stdout"])
        else:
            result["error"] = cmd_result.get("error", cmd_result.get("stderr", "Unknown error"))
    
    return result

def check_poetry(path: str, timeout: int) -> Dict[str, Any]:
    """Check poetry dependencies."""
    result = {
        "manager": "poetry",
        "success": False,
        "outdated": [],
        "error": None
    }
    
    if not check_command_exists("poetry"):
        result["error"] = "poetry not found in PATH"
        return result
    
    cmd_result = run_command(["poetry", "show", "--outdated", "--no-ansi"], timeout=timeout, cwd=path)
    if cmd_result["success"]:
        result["success"] = True
        result["outdated"] = parse_poetry_outdated(cmd_result["stdout"])
    else:
        result["error"] = cmd_result.get("error", cmd_result.get("stderr", "Unknown error"))
    
    return result

def format_table(data: List[Dict[str, Any]]) -> str:
    """Format outdated packages as a table."""
    if not data:
        return "No outdated dependencies found."
    
    # Determine columns based on data
    if "wanted" in data[0]:
        # npm format
        headers = ["Package", "Current", "Wanted", "Latest", "Type"]
        rows = []
        for item in data:
            rows.append([
                item.get("package", ""),
                item.get("current", ""),
                item.get("wanted", ""),
                item.get("latest", ""),
                item.get("type", "")
            ])
    else:
        # pip/poetry format
        headers = ["Package", "Current", "Latest"]
        rows = []
        for item in data:
            rows.append([
                item.get("package", ""),
                item.get("current", ""),
                item.get("latest", "")
            ])
    
    # Simple table formatting
    col_widths = [max(len(str(h)), max(len(str(r[i])) for r in rows)) for i, h in enumerate(headers)]
    
    # Build table
    lines = []
    # Header
    header = "┌" + "─".join("─" * (w + 2) for w in col_widths) + "┐"
    header = header.replace("─┬", "┬").replace("┬─", "┬")
    lines.append(header)
    
    header_row = "│ " + " │ ".join(h.ljust(w) for h, w in zip(headers, col_widths)) + " │"
    lines.append(header_row)
    
    separator = "├" + "─".join("─" * (w + 2) for w in col_widths) + "┤"
    separator = separator.replace("─┼", "┼").replace("┼─", "┼")
    lines.append(separator)
    
    # Rows
    for row in rows:
        row_str = "│ " + " │ ".join(str(cell).ljust(w) for cell, w in zip(row, col_widths)) + " │"
        lines.append(row_str)
    
    # Footer
    footer = "└" + "─".join("─" * (w + 2) for w in col_widths) + "┘"
    footer = footer.replace("─┴", "┴").replace("┴─", "┴")
    lines.append(footer)
    
    return "\n".join(lines)

def run_check(args):
    """Execute the dependency check."""
    path = os.path.abspath(args.path)
    
    if not os.path.exists(path):
        return {
            "status": "error",
            "error": f"Path does not exist: {path}"
        }
    
    # Detect package managers
    detected = detect_package_managers(path)
    
    if not detected and not args.manager:
        return {
            "status": "error",
            "error": "No package manager files found and no manager specified"
        }
    
    # Determine which managers to check
    managers_to_check = []
    if args.manager:
        for m in args.manager:
            if m in ["npm", "pip", "poetry"]:
                managers_to_check.append(m)
    else:
        managers_to_check = list(detected.keys())
    
    if not managers_to_check:
        return {
            "status": "error",
            "error": "No valid package managers to check"
        }
    
    # Run checks
    results = {}
    errors = []
    
    print(f"Checking dependencies in {path}...")
    
    for manager in managers_to_check:
        print(f"[{'✓' if manager in detected else '⚠'}] Checking {manager}...")
        
        if manager == "npm":
            result = check_npm(path, args.timeout)
        elif manager == "pip":
            result = check_pip(path, args.timeout)
        elif manager == "poetry":
            result = check_poetry(path, args.timeout)
        else:
            continue
        
        if result["success"]:
            results[manager] = {
                "outdated": result["outdated"],
                "count": len(result["outdated"])
            }
        else:
            errors.append(f"{manager}: {result.get('error', 'Unknown error')}")
            if not args.ignore_errors:
                results[manager] = {"error": result.get("error", "Unknown error")}
    
    # Prepare output
    output = {
        "status": "success" if results else "error",
        "path": path,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "results": results,
        "errors": errors
    }
    
    # Format output
    if args.format == "json":
        return output
    else:
        # Human-readable output
        lines = []
        lines.append(f"Dependency check for: {path}")
        lines.append(f"Time: {output['timestamp']}")
        lines.append("")
        
        for manager, data in results.items():
            lines.append(f"=== {manager.upper()} ===")
            if "error" in data:
                lines.append(f"Error: {data['error']}")
            elif data.get("outdated"):
                lines.append(format_table(data["outdated"]))
                lines.append(f"Total outdated: {data['count']}")
            else:
                lines.append("✓ All dependencies are up to date")
            lines.append("")
        
        if errors:
            lines.append("=== ERRORS ===")
            for error in errors:
                lines.append(f"⚠ {error}")
        
        output["formatted"] = "\n".join(lines)
        return output

def main():
    parser = argparse.ArgumentParser(
        description="Check for outdated dependencies across multiple package managers."
    )
    parser.add_argument(
        "command",
        choices=["check", "help"],
        help="Command to execute"
    )
    
    # Arguments for 'check'
    parser.add_argument(
        "--manager",
        action="append",
        choices=["npm", "pip", "poetry"],
        help="Package manager(s) to check (can specify multiple)"
    )
    parser.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        help="Output format"
    )
    parser.add_argument(
        "--path",
        default=".",
        help="Path to project directory"
    )
    parser.add_argument(
        "--ignore-errors",
        action="store_true",
        help="Continue checking other managers if one fails"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Timeout in seconds for each package manager check"
    )
    
    args = parser.parse_args()
    
    if args.command == "check":
        result = run_check(args)
        if args.format == "json":
            print(json.dumps(result, indent=2))
        else:
            if "formatted" in result:
                print(result["formatted"])
            else:
                print(json.dumps(result, indent=2))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()