#!/usr/bin/env python3
"""
Extract and analyze all LOINC codes from a FHIR Questionnaire.

This script recursively extracts all LOINC codes from a FHIR Questionnaire JSON file,
categorizes them by type (question codes vs answer codes), and provides detailed
information about where each code is used. Optionally validates codes against the
LOINC database.

Usage:
    python extract_loinc_codes.py questionnaire.json
    python extract_loinc_codes.py questionnaire.json --output codes.json
    python extract_loinc_codes.py questionnaire.json --format table
    python extract_loinc_codes.py questionnaire.json --validate
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Optional
from collections import defaultdict


def extract_loinc_codes(item: dict, codes_dict: Dict, path: str = "") -> None:
    """
    Recursively extract LOINC codes from questionnaire items.

    Args:
        item: Questionnaire item to process
        codes_dict: Dictionary to store extracted codes
        path: Current path in the questionnaire hierarchy
    """
    link_id = item.get('linkId', 'unknown')
    current_path = f"{path}/{link_id}" if path else link_id

    # Extract question codes from the 'code' array
    if 'code' in item:
        for code in item['code']:
            if code.get('system') == 'http://loinc.org' and 'code' in code:
                loinc_code = code['code']
                display = code.get('display', 'No display text')

                if loinc_code not in codes_dict:
                    codes_dict[loinc_code] = {
                        'locations': [],
                        'display': display,
                        'type': 'question'
                    }
                codes_dict[loinc_code]['locations'].append(current_path)

    # Extract answer option codes from answerOption array
    if 'answerOption' in item:
        for answer in item['answerOption']:
            if 'valueCoding' in answer:
                coding = answer['valueCoding']
                if coding.get('system') == 'http://loinc.org' and 'code' in coding:
                    loinc_code = coding['code']
                    display = coding.get('display', 'No display text')

                    if loinc_code not in codes_dict:
                        codes_dict[loinc_code] = {
                            'locations': [],
                            'display': display,
                            'type': 'answer'
                        }
                    codes_dict[loinc_code]['locations'].append(f"{current_path} (answer)")

    # Extract codes from answerValueSet (if present)
    if 'answerValueSet' in item:
        valueset_url = item['answerValueSet']
        # Note: This doesn't extract actual codes, just notes the ValueSet reference
        # Could be enhanced to fetch and expand ValueSets

    # Recursively process nested items
    if 'item' in item:
        for child in item['item']:
            extract_loinc_codes(child, codes_dict, current_path)


def load_questionnaire(file_path: Path) -> Optional[dict]:
    """
    Load and parse a FHIR Questionnaire JSON file.

    Args:
        file_path: Path to the questionnaire file

    Returns:
        Parsed questionnaire dictionary or None on error
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            questionnaire = json.load(f)

        # Basic validation
        if questionnaire.get('resourceType') != 'Questionnaire':
            print(f"Warning: Resource type is '{questionnaire.get('resourceType')}', expected 'Questionnaire'",
                  file=sys.stderr)

        return questionnaire

    except FileNotFoundError:
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error loading questionnaire: {e}", file=sys.stderr)
        return None


def extract_all_codes(questionnaire: dict) -> Dict[str, dict]:
    """
    Extract all LOINC codes from a questionnaire.

    Args:
        questionnaire: Parsed questionnaire dictionary

    Returns:
        Dictionary of LOINC codes with metadata
    """
    codes = {}

    if 'item' in questionnaire:
        for item in questionnaire['item']:
            extract_loinc_codes(item, codes)

    return codes


def format_table_output(codes: Dict[str, dict]) -> str:
    """Format codes as a readable table."""
    if not codes:
        return "No LOINC codes found in questionnaire."

    # Separate by type
    question_codes = {k: v for k, v in sorted(codes.items()) if v['type'] == 'question'}
    answer_codes = {k: v for k, v in sorted(codes.items()) if v['type'] == 'answer'}

    output = []
    output.append("=" * 80)
    output.append("LOINC CODES FOUND IN QUESTIONNAIRE")
    output.append("=" * 80)
    output.append(f"\nTotal unique LOINC codes: {len(codes)}")
    output.append(f"  Question codes: {len(question_codes)}")
    output.append(f"  Answer codes: {len(answer_codes)}")

    if question_codes:
        output.append("\n" + "=" * 80)
        output.append("QUESTION CODES")
        output.append("=" * 80)
        for code, info in question_codes.items():
            output.append(f"\n{code}: {info['display']}")
            output.append(f"  Used in: {', '.join(info['locations'])}")

    if answer_codes:
        output.append("\n" + "=" * 80)
        output.append("ANSWER CODES")
        output.append("=" * 80)

        # Group by unique code
        unique_answer_codes = {}
        for code, info in answer_codes.items():
            if code not in unique_answer_codes:
                unique_answer_codes[code] = {
                    'display': info['display'],
                    'locations': info['locations']
                }

        for code, info in sorted(unique_answer_codes.items()):
            output.append(f"\n{code}: {info['display']}")
            if len(info['locations']) > 1:
                output.append(f"  Used in {len(info['locations'])} locations")

    output.append("\n")
    return "\n".join(output)


def format_summary_output(codes: Dict[str, dict]) -> str:
    """Format a concise summary of codes."""
    question_codes = [k for k, v in codes.items() if v['type'] == 'question']
    answer_codes = [k for k, v in codes.items() if v['type'] == 'answer']

    output = []
    output.append(f"Total LOINC codes: {len(codes)}")
    output.append(f"Question codes ({len(question_codes)}): {', '.join(sorted(question_codes)) if question_codes else 'None'}")
    output.append(f"Answer codes ({len(answer_codes)}): {', '.join(sorted(set(answer_codes))) if answer_codes else 'None'}")

    return "\n".join(output)


def format_json_output(codes: Dict[str, dict]) -> str:
    """Format codes as JSON."""
    question_codes = {k: v for k, v in sorted(codes.items()) if v['type'] == 'question'}
    answer_codes = {k: v for k, v in sorted(codes.items()) if v['type'] == 'answer'}

    output = {
        'total': len(codes),
        'question_codes': question_codes,
        'answer_codes': answer_codes,
        'all_codes': sorted(codes.keys())
    }

    return json.dumps(output, indent=2)


def validate_codes(codes: Dict[str, dict]) -> None:
    """
    Validate LOINC codes using search_loinc.py.

    Note: This requires the search_loinc module to be available.
    """
    try:
        # Import the search_loinc module
        sys.path.insert(0, str(Path(__file__).parent))
        from search_loinc import search_loinc

        print("\n" + "=" * 80)
        print("VALIDATING LOINC CODES")
        print("=" * 80)

        for code in sorted(codes.keys()):
            # Search for exact code
            results = search_loinc(code, limit=1)

            if results and results[0]['code'] == code:
                status = "✓ VALID"
                official_display = results[0]['display']

                if codes[code]['display'] != official_display:
                    print(f"{code}: {status}")
                    print(f"  Current: {codes[code]['display']}")
                    print(f"  Official: {official_display}")
                else:
                    print(f"{code}: {status} - {official_display}")
            else:
                print(f"{code}: ✗ NOT FOUND")
                print(f"  Display: {codes[code]['display']}")

        print("\n")

    except ImportError:
        print("Warning: Could not import search_loinc module. Skipping validation.", file=sys.stderr)
    except Exception as e:
        print(f"Warning: Validation failed: {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Extract and analyze LOINC codes from FHIR Questionnaires",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract and display as table
  python extract_loinc_codes.py questionnaire.json

  # Save to JSON file
  python extract_loinc_codes.py questionnaire.json --output codes.json

  # Show summary only
  python extract_loinc_codes.py questionnaire.json --format summary

  # Validate codes against LOINC database
  python extract_loinc_codes.py questionnaire.json --validate
        """
    )

    parser.add_argument(
        "questionnaire",
        type=Path,
        help="Path to FHIR Questionnaire JSON file"
    )

    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output file path (default: print to stdout)"
    )

    parser.add_argument(
        "-f", "--format",
        choices=["table", "json", "summary"],
        default="table",
        help="Output format (default: table)"
    )

    parser.add_argument(
        "-v", "--validate",
        action="store_true",
        help="Validate codes against LOINC database (requires network access)"
    )

    args = parser.parse_args()

    # Load questionnaire
    questionnaire = load_questionnaire(args.questionnaire)
    if questionnaire is None:
        sys.exit(1)

    # Extract codes
    codes = extract_all_codes(questionnaire)

    if not codes:
        print("No LOINC codes found in questionnaire.", file=sys.stderr)
        sys.exit(0)

    # Format output
    if args.format == "table":
        output = format_table_output(codes)
    elif args.format == "json":
        output = format_json_output(codes)
    elif args.format == "summary":
        output = format_summary_output(codes)
    else:
        output = format_json_output(codes)

    # Write or print output
    if args.output:
        try:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Extracted codes saved to: {args.output}")
        except Exception as e:
            print(f"Error writing output file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(output)

    # Validate if requested
    if args.validate:
        validate_codes(codes)


if __name__ == '__main__':
    main()
