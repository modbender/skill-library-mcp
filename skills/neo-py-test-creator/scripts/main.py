#!/usr/bin/env python3
"""
Main entry point for py-test-creator skill.

This module serves as the primary interface for the test generation skill.
It can be called directly or via the CLI module.
"""

import sys
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from scripts.parser import PythonParser
from scripts.generator import TestGenerator


def generate_tests(
    input_path: str,
    output_path: Optional[str] = None,
    verbose: bool = False,
    coverage: bool = False,
    strict: bool = False
) -> str:
    """
    Generate pytest tests from a Python file.

    Args:
        input_path: Path to the input Python file
        output_path: Optional output file path (auto-generated if None)
        verbose: Whether to print progress messages
        coverage: Include coverage hints in output
        strict: Enable strict mode

    Returns:
        Generated test code as a string

    Raises:
        FileNotFoundError: If input file doesn't exist
        SyntaxError: If input file has invalid Python syntax
        Exception: For other errors during parsing or generation
    """
    input_file = Path(input_path)

    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if verbose:
        print(f"Reading: {input_path}", file=sys.stderr)

    # Read source code
    with open(input_file, 'r', encoding='utf-8') as f:
        source_code = f.read()

    if verbose:
        print("Parsing Python AST...", file=sys.stderr)

    # Parse functions
    parser = PythonParser(source_code, filename=input_file.name)
    functions = parser.parse()

    if verbose:
        print(f"Found {len(functions)} function(s)", file=sys.stderr)

    if not functions:
        print("Warning: No functions found to test", file=sys.stderr)

    if verbose:
        print("Generating test code...", file=sys.stderr)

    # Generate tests
    generator = TestGenerator(
        functions=functions,
        module_name=input_file.stem,
        coverage=coverage,
        strict=strict
    )
    test_code = generator.generate()

    if verbose:
        lines = test_code.count('\n') + 1
        print(f"Generated {lines} lines of test code", file=sys.stderr)

    return test_code


def main():
    """Command-line entry point."""
    # Import CLI args parsing here to avoid circular imports
    from scripts.cli import parse_arguments

    args = parse_arguments()

    try:
        test_code = generate_tests(
            input_path=args.input_file,
            output_path=args.output,
            verbose=args.verbose,
            coverage=args.coverage,
            strict=args.strict
        )

        # Determine output path
        if args.output:
            output_path = args.output
        else:
            input_file = Path(args.input_file)
            output_path = f"test_{input_file.name}"

        # Write output
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(test_code)

        if args.verbose:
            print(f"Wrote: {output_path}", file=sys.stderr)

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
