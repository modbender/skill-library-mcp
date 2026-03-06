#!/usr/bin/env python3
"""
Create reusable CodeSystem and ValueSet resources (opt-in).

This script generates custom CodeSystem and ValueSet resources in the Welshare
namespace for use cases where reusable codes across multiple questionnaires are
explicitly desired.

NOTE: For most custom answer lists, prefer inline answerOption with system-less
valueCoding directly in the questionnaire. Only use this script when the user
explicitly requests reusable codes that can be shared across questionnaires.

URL Base: http://codes.welshare.app
All resources created by this script use the Welshare URL base for consistency.

Usage:
    python create_custom_codesystem.py --id routine-preference --category brainhealth --title "Routine Preference Scale" --codes "prefer-routines:Prefer routines,sometimes-new:Sometimes seek new challenges"
    python create_custom_codesystem.py --interactive
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


def sanitize_id(text: str) -> str:
    """Convert text to a valid FHIR id (lowercase, hyphens, alphanumeric)."""
    # Convert to lowercase
    text = text.lower()
    # Replace spaces and underscores with hyphens
    text = re.sub(r'[\s_]+', '-', text)
    # Remove any non-alphanumeric characters except hyphens and dots
    text = re.sub(r'[^a-z0-9\-.]', '', text)
    # Remove leading/trailing hyphens
    text = text.strip('-')
    # Limit to 64 characters
    return text[:64]


def sanitize_code(text: str) -> str:
    """Convert text to a valid code (lowercase, hyphens, alphanumeric)."""
    # Similar to id but more restrictive
    text = text.lower()
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'[^a-z0-9\-]', '', text)
    text = text.strip('-')
    return text


def create_codesystem(
    id: str,
    category: str,
    title: str,
    description: str,
    concepts: List[Tuple[str, str]],
    publisher: str = "Welshare",
    experimental: bool = False
) -> Dict:
    """
    Create a CodeSystem resource.

    Uses the Welshare URL base: http://codes.welshare.app for consistency
    across reusable code systems.

    Args:
        id: CodeSystem identifier (e.g., "routine-preference")
        category: Category/domain (e.g., "brainhealth")
        title: Human-readable title
        description: Description of the code system
        concepts: List of (code, display) tuples
        publisher: Organization name
        experimental: Whether this is experimental

    Returns:
        CodeSystem resource as dict
    """
    today = datetime.now().strftime("%Y-%m-%d")

    # Create name from title (CamelCase, no spaces)
    name = ''.join(word.capitalize() for word in title.split())
    name = re.sub(r'[^A-Za-z0-9]', '', name)

    # URL base: http://codes.welshare.app
    codesystem = {
        "resourceType": "CodeSystem",
        "id": id,
        "url": f"http://codes.welshare.app/CodeSystem/{category}/{id}.json",
        "version": "1.0.0",
        "name": name,
        "title": title,
        "status": "active",
        "experimental": experimental,
        "date": today,
        "publisher": publisher,
        "description": description,
        "content": "complete",
        "concept": [
            {
                "code": code,
                "display": display
            }
            for code, display in concepts
        ]
    }

    return codesystem


def create_valueset(
    codesystem_id: str,
    category: str,
    title: str,
    description: str = None
) -> Dict:
    """
    Create a ValueSet resource that references a CodeSystem.

    Uses the Welshare URL base: http://codes.welshare.app for consistency
    across reusable value sets.

    Args:
        codesystem_id: ID of the CodeSystem to reference
        category: Category/domain (same as CodeSystem)
        title: Human-readable title (usually same as CodeSystem)
        description: Optional description

    Returns:
        ValueSet resource as dict
    """
    valueset_id = f"vs-{codesystem_id}"
    # URL base: http://codes.welshare.app
    codesystem_url = f"http://codes.welshare.app/CodeSystem/{category}/{codesystem_id}.json"

    valueset = {
        "resourceType": "ValueSet",
        "id": valueset_id,
        "url": f"http://codes.welshare.app/ValueSet/{category}/{codesystem_id}.json",
        "status": "active",
        "compose": {
            "include": [
                {
                    "system": codesystem_url
                }
            ]
        }
    }

    if title:
        valueset["title"] = f"ValueSet - {title}"

    if description:
        valueset["description"] = description

    return valueset


def parse_codes_string(codes_str: str) -> List[Tuple[str, str]]:
    """
    Parse codes from string format.

    Format: "code1:Display 1,code2:Display 2,code3:Display 3"

    Returns:
        List of (code, display) tuples
    """
    concepts = []
    for pair in codes_str.split(','):
        pair = pair.strip()
        if ':' not in pair:
            print(f"Warning: Invalid code format '{pair}'. Expected 'code:display'", file=sys.stderr)
            continue

        code, display = pair.split(':', 1)
        code = code.strip()
        display = display.strip()

        if not code or not display:
            print(f"Warning: Empty code or display in '{pair}'", file=sys.stderr)
            continue

        concepts.append((code, display))

    return concepts


def interactive_mode() -> Tuple[str, str, str, str, List[Tuple[str, str]]]:
    """
    Interactive mode to gather input from user.

    Returns:
        Tuple of (id, category, title, description, concepts)
    """
    print("\n=== Create Reusable CodeSystem & ValueSet ===")
    print("Note: For simple custom answer lists, consider using inline answerOption")
    print("      with system-less valueCoding instead (simpler, no external resources).\n")

    # Get title first (most natural)
    title = input("Title (e.g., 'Routine Preference Scale'): ").strip()
    if not title:
        print("Error: Title is required", file=sys.stderr)
        sys.exit(1)

    # Suggest ID based on title
    suggested_id = sanitize_id(title)
    id_input = input(f"ID [default: {suggested_id}]: ").strip()
    id = id_input if id_input else suggested_id

    # Category
    category = input("Category/domain (e.g., 'brainhealth', 'social'): ").strip()
    if not category:
        print("Error: Category is required", file=sys.stderr)
        sys.exit(1)
    category = sanitize_id(category)

    # Description
    description = input("Description: ").strip()
    if not description:
        description = f"Custom code system for {title.lower()}"

    # Concepts
    print("\nEnter concepts (codes and displays). Press Enter with empty code to finish.")
    concepts = []
    idx = 1

    while True:
        print(f"\nConcept {idx}:")
        code = input("  Code (or Enter to finish): ").strip()
        if not code:
            break

        # Suggest sanitized version
        suggested_code = sanitize_code(code)
        if code != suggested_code:
            confirm = input(f"  Use sanitized code '{suggested_code}'? [Y/n]: ").strip().lower()
            if confirm != 'n':
                code = suggested_code

        display = input("  Display text: ").strip()
        if not display:
            print("  Warning: Display text is required. Skipping this concept.")
            continue

        concepts.append((code, display))
        idx += 1

    if not concepts:
        print("\nError: At least one concept is required", file=sys.stderr)
        sys.exit(1)

    return id, category, title, description, concepts


def main():
    parser = argparse.ArgumentParser(
        description="Create reusable CodeSystem and ValueSet resources (opt-in for cross-questionnaire code sharing)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
NOTE: For most custom answer lists, prefer inline answerOption with system-less
      valueCoding. Only use this script when reusable codes are explicitly needed.

Examples:
  # Interactive mode
  python create_custom_codesystem.py --interactive

  # Command-line mode
  python create_custom_codesystem.py \\
    --id routine-preference \\
    --category brainhealth \\
    --title "Routine Preference Scale" \\
    --description "Scale for assessing preference for routines" \\
    --codes "prefer-routines:Prefer routines,sometimes-new:Sometimes seek new challenges,frequently-new:Frequently seek new challenges"

  # Output to specific directory
  python create_custom_codesystem.py --interactive --output ./custom-codes/

  # Mark as experimental
  python create_custom_codesystem.py --interactive --experimental
        """
    )

    parser.add_argument("--interactive", "-i", action="store_true",
                       help="Interactive mode - prompt for all values")
    parser.add_argument("--id", help="CodeSystem ID (e.g., 'routine-preference')")
    parser.add_argument("--category", help="Category/domain (e.g., 'brainhealth')")
    parser.add_argument("--title", help="Human-readable title")
    parser.add_argument("--description", help="Description of the code system")
    parser.add_argument("--codes", help="Comma-separated codes in format 'code1:Display 1,code2:Display 2'")
    parser.add_argument("--publisher", default="Welshare", help="Publisher name (default: Welshare)")
    parser.add_argument("--experimental", action="store_true", help="Mark as experimental")
    parser.add_argument("--output", "-o", type=Path, default=".",
                       help="Output directory (default: current directory)")

    args = parser.parse_args()

    # Gather input
    if args.interactive:
        id, category, title, description, concepts = interactive_mode()
        experimental = args.experimental
        publisher = args.publisher
    else:
        # Validate required arguments
        if not all([args.id, args.category, args.title, args.codes]):
            parser.error("Non-interactive mode requires --id, --category, --title, and --codes")

        id = args.id
        category = args.category
        title = args.title
        description = args.description if args.description else f"Custom code system for {title.lower()}"
        concepts = parse_codes_string(args.codes)
        experimental = args.experimental
        publisher = args.publisher

        if not concepts:
            print("Error: No valid concepts provided", file=sys.stderr)
            sys.exit(1)

    # Create resources
    codesystem = create_codesystem(
        id=id,
        category=category,
        title=title,
        description=description,
        concepts=concepts,
        publisher=publisher,
        experimental=experimental
    )

    valueset = create_valueset(
        codesystem_id=id,
        category=category,
        title=title,
        description=f"ValueSet containing all codes from {title}"
    )

    # Ensure output directory exists
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write files
    codesystem_file = output_dir / f"CodeSystem-{id}.json"
    valueset_file = output_dir / f"ValueSet-vs-{id}.json"

    with open(codesystem_file, 'w') as f:
        json.dump(codesystem, f, indent=2)

    with open(valueset_file, 'w') as f:
        json.dump(valueset, f, indent=2)

    # Success message
    print(f"\n✅ Successfully created reusable code system!\n")
    print(f"CodeSystem: {codesystem_file}")
    print(f"  URL: {codesystem['url']}")
    print(f"  Concepts: {len(concepts)}")
    print(f"\nValueSet: {valueset_file}")
    print(f"  URL: {valueset['url']}")
    print(f"\n📋 Usage in Questionnaire (with ValueSet reference):")
    print(f'   "answerValueSet": "{valueset["url"]}"')
    print(f"\n   Or with inline coding (add system to each valueCoding):")
    print(f'   "answerOption": [')
    print(f'     {{"valueCoding": {{')
    print(f'       "system": "{codesystem["url"]}",')
    print(f'       "code": "{concepts[0][0]}",')
    print(f'       "display": "{concepts[0][1]}"')
    print(f'     }}}}')
    print(f'   ]')
    print(f"\n💡 Tip: For simpler use cases, consider inline answerOption without system:"
          f'\n   {{"valueCoding": {{"code": "{concepts[0][0]}", "display": "{concepts[0][1]}"}}}}')
    print(f"   This avoids external resource dependencies.")


if __name__ == "__main__":
    main()
