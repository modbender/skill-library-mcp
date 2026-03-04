#!/usr/bin/env python3
"""
converter.py — Main CLI entry point for Python to Go conversion.

Usage:
  python-to-go-converter convert <input.py> [--output <output.go>] [--verbose]

This script reads a Python source file, converts it to Go code, and writes
the result to the specified output file or stdout.

Exit codes:
  0 on success
  1 on general error
  2 if input file not found
  3 if conversion error (unsupported feature)
  4 if Go output cannot be written
  5 if Go compilation check fails (optional)
"""

import argparse
import ast
import json
import os
import subprocess
import sys

# Add scripts directory to path to import siblings
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)

from ast_parser import parse as parse_ir
from go_generator import GoGenerator
from import_handler import collect_imports_from_ast, get_required_go_imports

REFERENCES_DIR = os.path.join(SCRIPTS_DIR, '..', 'references')
ERROR_CODES_PATH = os.path.join(REFERENCES_DIR, 'error_codes.json')

with open(ERROR_CODES_PATH, 'r') as f:
    ERROR_CODES = json.load(f)


def error_exit(code_id: str, **format_args):
    err = ERROR_CODES.get(code_id, {"message": "Unknown error"})
    msg = err["message"].format(**format_args)
    print(f"Error {code_id}: {msg}", file=sys.stderr)
    sys.exit(int(code_id[1:]))


def main():
    parser = argparse.ArgumentParser(description="Convert Python code to Go")
    parser.add_argument("command", choices=["convert"], help="Command to execute")
    parser.add_argument("input", help="Input Python file")
    parser.add_argument("--output", "-o", help="Output Go file (default: stdout)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose diagnostics")
    parser.add_argument("--check", action="store_true", help="Check generated code with go vet (requires go)")
    args = parser.parse_args()

    if args.command != "convert":
        parser.error("Only 'convert' command is supported")

    # Check input file
    if not os.path.isfile(args.input):
        error_exit("E005", path=args.input)

    # Read source
    try:
        with open(args.input, 'r') as f:
            source = f.read()
    except IOError as e:
        error_exit("E005", path=args.input)

    # Parse source to AST (for imports)
    try:
        ast_tree = ast.parse(source)
    except SyntaxError as e:
        print(f"Syntax error: {e}", file=sys.stderr)
        sys.exit(3)

    # Collect required imports
    py_modules = collect_imports_from_ast(ast_tree)
    go_imports = get_required_go_imports(py_modules)
    if args.verbose:
        print(f"Detected Python imports: {sorted(py_modules)}", file=sys.stderr)
        print(f"Resolved Go imports: {sorted(go_imports)}", file=sys.stderr)

    # Parse to IR
    try:
        ir = parse_ir(source)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(3)

    # Check for unsupported features in IR
    for stmt in ir:
        if stmt.get('type') == 'unsupported':
            feature = stmt.get('feature', 'unknown')
            print(f"Warning: Unsupported feature '{feature}' will be skipped", file=sys.stderr)

    # Generate Go code
    generator = GoGenerator(ir, required_imports=go_imports)
    go_code = generator.generate()

    # Optionally, add a comment with source file info
    header = f"// Automatically converted from {os.path.basename(args.input)} by python-to-go-converter\n"
    go_code = header + go_code

    # Output
    output_dest = args.output
    try:
        if output_dest:
            with open(output_dest, 'w') as f:
                f.write(go_code)
            if args.verbose:
                print(f"Wrote Go code to {output_dest}", file=sys.stderr)
        else:
            print(go_code)
    except IOError as e:
        error_exit("E004", path=output_dest or "stdout")

    # Optional go vet check
    if args.check:
        # Write to temp file if not already file, or use file directly
        check_path = output_dest if output_dest else None
        if not check_path:
            import tempfile
            tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.go', delete=False)
            tmp.write(go_code)
            tmp.close()
            check_path = tmp.name
        try:
            result = subprocess.run(['go', 'vet', check_path], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"go vet failed:\n{result.stdout}\n{result.stderr}", file=sys.stderr)
                # Not exit, just warning
            else:
                print("go vet passed", file=sys.stderr)
        except FileNotFoundError:
            print("go command not found, skipping vet", file=sys.stderr)
        finally:
            if not output_dest and 'tmp' in locals():
                os.unlink(tmp.name)

    # Success
    sys.exit(0)


if __name__ == "__main__":
    main()