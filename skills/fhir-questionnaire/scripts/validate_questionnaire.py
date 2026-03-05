#!/usr/bin/env python3
"""
Validate FHIR Questionnaire resources against JSON Schema.

This script validates FHIR Questionnaire JSON files against the schema defined in
references/schema/questionnaire.schema.json. It performs both schema validation and
additional semantic checks.

Source of Truth: The definitive schema is located at references/schema/questionnaire.schema.json

Usage:
    python validate_questionnaire.py questionnaire.json
    python validate_questionnaire.py questionnaire.json --verbose
    python validate_questionnaire.py questionnaire.json --schema-only
"""

# Standard imports
import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

try:
    import jsonschema
    from jsonschema import Draft7Validator, ValidationError
except ImportError:
    print("Error: jsonschema library not found. Install it with: pip install jsonschema", file=sys.stderr)
    sys.exit(1)


class QuestionnaireValidator:
    """Validates FHIR Questionnaire resources against JSON Schema and semantic rules."""

    def __init__(self, schema: Dict[str, Any], verbose: bool = False):
        self.schema = schema
        self.verbose = verbose
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.validator = Draft7Validator(schema)

    def validate(self, data: Dict[str, Any], schema_only: bool = False) -> Tuple[bool, List[str], List[str]]:
        """
        Validate a FHIR Questionnaire resource.

        Args:
            data: Questionnaire data to validate
            schema_only: If True, only perform schema validation (skip semantic checks)

        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []

        # Perform JSON Schema validation
        schema_errors = list(self.validator.iter_errors(data))
        for error in schema_errors:
            # Format error message with path
            path = ".".join(str(p) for p in error.path) if error.path else "root"
            self.errors.append(f"{path}: {error.message}")

        # If schema_only mode or schema validation failed, return early
        if schema_only or schema_errors:
            return len(self.errors) == 0, self.errors, self.warnings

        # Additional semantic validations
        self._check_linkid_uniqueness(data)
        self._check_enable_when_references(data)
        self._check_common_issues(data)

        return len(self.errors) == 0, self.errors, self.warnings

    def _check_linkid_uniqueness(self, data: Dict[str, Any]):
        """Check that all linkIds are unique across the questionnaire."""
        link_ids: Set[str] = set()
        duplicates: Set[str] = set()

        def collect_link_ids(items: List[Dict], path: str = ""):
            for idx, item in enumerate(items):
                if "linkId" in item:
                    link_id = item["linkId"]
                    if link_id in link_ids:
                        duplicates.add(link_id)
                    link_ids.add(link_id)

                # Recurse into nested items
                if "item" in item:
                    collect_link_ids(item["item"], f"{path}.item[{idx}]")

        if "item" in data:
            collect_link_ids(data["item"])

        for dup in duplicates:
            self.errors.append(f"Duplicate linkId: '{dup}' (linkIds must be unique across the entire questionnaire)")

    def _check_enable_when_references(self, data: Dict[str, Any]):
        """Check that enableWhen references point to valid linkIds."""
        link_ids: Set[str] = set()

        # First, collect all linkIds
        def collect_link_ids(items: List[Dict]):
            for item in items:
                if "linkId" in item:
                    link_ids.add(item["linkId"])
                if "item" in item:
                    collect_link_ids(item["item"])

        if "item" in data:
            collect_link_ids(data["item"])

        # Then check enableWhen references
        def check_references(items: List[Dict], path: str = "item"):
            for idx, item in enumerate(items):
                item_path = f"{path}[{idx}]"

                if "enableWhen" in item:
                    for ew_idx, enable_when in enumerate(item["enableWhen"]):
                        if "question" in enable_when:
                            ref_link_id = enable_when["question"]
                            if ref_link_id not in link_ids:
                                self.errors.append(
                                    f"{item_path}.enableWhen[{ew_idx}]: "
                                    f"References non-existent linkId '{ref_link_id}'"
                                )

                if "item" in item:
                    check_references(item["item"], f"{item_path}.item")

        if "item" in data:
            check_references(data["item"])

    def _check_common_issues(self, data: Dict[str, Any]):
        """Check for common issues and best practices."""
        # Check for url (recommended for published questionnaires)
        if data.get("status") in ["active", "retired"] and "url" not in data:
            self.warnings.append("Published questionnaires should have a 'url' field")

        # Check for version
        if "url" in data and "version" not in data:
            self.warnings.append("Questionnaires with a URL should have a 'version' field")

        # Check for title or name
        if "title" not in data and "name" not in data:
            self.warnings.append("Questionnaire should have a 'title' or 'name' field")

        # Check for text in items (for user display)
        def check_items_text(items: List[Dict], path: str = "item"):
            for idx, item in enumerate(items):
                item_path = f"{path}[{idx}]"
                if "text" not in item and item.get("type") != "display":
                    self.warnings.append(
                        f"{item_path}: Missing 'text' field (recommended for user display)"
                    )

                # Check choice/open-choice items have answer options
                if item.get("type") in ["choice", "open-choice"]:
                    if "answerOption" not in item and "answerValueSet" not in item:
                        self.warnings.append(
                            f"{item_path}: Choice/open-choice items should have 'answerOption' or 'answerValueSet'"
                        )

                if "item" in item:
                    check_items_text(item["item"], f"{item_path}.item")

        if "item" in data:
            check_items_text(data["item"])


def load_questionnaire(file_path: Path) -> Dict[str, Any]:
    """Load questionnaire from JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {file_path}: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)


def load_schema(schema_path: Path = None) -> Dict[str, Any]:
    """Load the JSON Schema for validation."""
    if schema_path is None:
        # Try to find schema relative to script location
        script_dir = Path(__file__).parent
        schema_path = script_dir.parent / "references" / "schema" / "questionnaire.schema.json"

    try:
        with open(schema_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Schema file not found at {schema_path}", file=sys.stderr)
        print("Please ensure references/schema/questionnaire.schema.json exists", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in schema file: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Validate FHIR Questionnaire resources against JSON Schema",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full validation (schema + semantic checks)
  python validate_questionnaire.py questionnaire.json

  # Verbose output
  python validate_questionnaire.py questionnaire.json --verbose

  # Schema validation only (skip semantic checks)
  python validate_questionnaire.py questionnaire.json --schema-only

  # Use custom schema file
  python validate_questionnaire.py questionnaire.json --schema custom-schema.json
        """
    )

    parser.add_argument("file", type=Path, help="Path to FHIR Questionnaire JSON file")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Show detailed validation output")
    parser.add_argument("--schema-only", action="store_true",
                       help="Only perform JSON Schema validation (skip semantic checks)")
    parser.add_argument("--schema", type=Path,
                       help="Path to custom schema file (default: references/schema/questionnaire.schema.json)")

    args = parser.parse_args()

    # Load schema
    schema = load_schema(args.schema)

    # Load questionnaire
    data = load_questionnaire(args.file)

    # Validate
    validator = QuestionnaireValidator(schema, verbose=args.verbose)
    is_valid, errors, warnings = validator.validate(data, schema_only=args.schema_only)

    # Output results
    if args.verbose or not is_valid:
        print(f"\nValidating: {args.file}")
        print("=" * 80)

    if errors:
        print("\nERRORS:")
        for error in errors:
            print(f"  ❌ {error}")

    if warnings:
        print("\nWARNINGS:")
        for warning in warnings:
            print(f"  ⚠️  {warning}")

    if is_valid:
        print(f"\n✅ Questionnaire is valid!")
        if warnings:
            print(f"   ({len(warnings)} warning(s))")
        sys.exit(0)
    else:
        print(f"\n❌ Questionnaire is invalid ({len(errors)} error(s))")
        sys.exit(1)


if __name__ == "__main__":
    main()
