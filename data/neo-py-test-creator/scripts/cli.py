#!/usr/bin/env python3
"""
Command-line interface for py-test-creator skill.

This module provides the main entry point for the CLI tool that generates
pytest unit tests from Python source files.
"""

import argparse
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.parser import PythonParser
from scripts.generator import TestGenerator


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate pytest unit tests from Python code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s mymodule.py
  %(prog)s mymodule.py --output test_mymodule.py
  %(prog)s mymodule.py --verbose
  %(prog)s mymodule.py --coverage
"""
    )

    parser.add_argument(
        "input_file",
        help="Path to the Python file to generate tests for"
    )

    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: test_<input filename>)"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Include coverage hints in generated tests"
    )

    parser.add_argument(
        "--strict",
        action="store_true",
        help="Enable strict mode (fail on warnings)"
    )

    parser.add_argument(
        "--config",
        help="Path to configuration file"
    )

    return parser.parse_args()


def generate_output_filename(input_path: str, output_path: str = None) -> str:
    """Generate the output filename based on input and optional override."""
    input_file = Path(input_path)
    if output_path:
        return output_path

    # Default: test_<filename>.py
    return f"test_{input_file.name}"


def main():
    """Main entry point for the CLI."""
    args = parse_arguments()

    # Validate input file exists
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file '{args.input_file}' does not exist", file=sys.stderr)
        sys.exit(1)

    if not input_path.is_file():
        print(f"Error: '{args.input_file}' is not a file", file=sys.stderr)
        sys.exit(1)

    try:
        # Read the input Python file
        if args.verbose:
            print(f"Reading file: {args.input_file}")

        with open(input_path, 'r', encoding='utf-8') as f:
            source_code = f.read()

        # Parse the Python code
        if args.verbose:
            print("Parsing Python AST...")

        parser = PythonParser(source_code, filename=input_path.name)
        functions = parser.parse()

        if args.verbose:
            print(f"Found {len(functions)} function(s) to generate tests for")

        # Generate tests
        if args.verbose:
            print("Generating pytest code...")

        generator = TestGenerator(
            functions=functions,
            module_name=input_path.stem,
            coverage=args.coverage,
            strict=args.strict
        )
        test_code = generator.generate()

        # Determine output filename
        output_filename = generate_output_filename(args.input_file, args.output)
        output_path = Path(output_filename)

        # Write output file
        if args.verbose:
            print(f"Writing test file: {output_path}")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(test_code)

        if args.verbose:
            print(f"Successfully generated {len(test_code.splitlines())} lines of test code")
            print(f"Output written to: {output_path}")

        # Success
        sys.exit(0)

    except SyntaxError as e:
        print(f"Syntax error in input file: {e}", file=sys.stderr)
        sys.exit(2)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
