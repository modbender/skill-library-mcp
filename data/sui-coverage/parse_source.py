#!/usr/bin/env python3
"""
Parse Sui Move source coverage output (ANSI colors) to identify uncovered code.

Usage:
    sui move coverage source --module <name> 2>&1 | python3 parse_source.py

Forces color output even when piped:
    script -q /dev/null sui move coverage source --module <name> | python3 parse_source.py
"""

import re
import sys
import json
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

# ANSI color code patterns
ANSI_PATTERN = re.compile(r'\x1b\[(\d+)m')
GREEN_CODE = '32'
RED_CODE = '31'
YELLOW_CODE = '33'
RESET_CODE = '39'

@dataclass
class CodeSegment:
    text: str
    covered: Optional[bool]  # True=green, False=red, None=no color/neutral


@dataclass 
class LineAnalysis:
    line_num: int
    raw_text: str
    segments: List[CodeSegment] = field(default_factory=list)
    has_uncovered: bool = False
    uncovered_text: List[str] = field(default_factory=list)


def parse_ansi_line(line: str) -> List[CodeSegment]:
    """Parse a line with ANSI codes into segments."""
    segments = []
    current_color = None  # None=neutral, True=green, False=red
    
    # Split by ANSI codes
    parts = ANSI_PATTERN.split(line)
    
    i = 0
    current_text = ""
    
    while i < len(parts):
        part = parts[i]
        
        # Check if this is a color code
        if part == GREEN_CODE:
            if current_text:
                segments.append(CodeSegment(text=current_text, covered=current_color))
                current_text = ""
            current_color = True
        elif part == RED_CODE:
            if current_text:
                segments.append(CodeSegment(text=current_text, covered=current_color))
                current_text = ""
            current_color = False
        elif part == YELLOW_CODE:
            if current_text:
                segments.append(CodeSegment(text=current_text, covered=current_color))
                current_text = ""
            current_color = None  # Yellow = partial/neutral
        elif part in (RESET_CODE, '0', '39'):
            if current_text:
                segments.append(CodeSegment(text=current_text, covered=current_color))
                current_text = ""
            current_color = None
        else:
            # Regular text
            current_text += part
        
        i += 1
    
    # Don't forget remaining text
    if current_text:
        segments.append(CodeSegment(text=current_text, covered=current_color))
    
    return segments


def analyze_coverage(input_text: str) -> dict:
    """Analyze source coverage and return structured data."""
    lines = input_text.split('\n')
    
    results = {
        'lines': [],
        'uncovered_summary': [],
        'stats': {
            'total_lines': 0,
            'lines_with_uncovered': 0,
            'fully_covered_lines': 0,
        }
    }
    
    for line_num, line in enumerate(lines, 1):
        if not line.strip():
            continue
            
        segments = parse_ansi_line(line)
        
        # Check for uncovered (red) segments
        uncovered_texts = [seg.text for seg in segments if seg.covered == False and seg.text.strip()]
        has_uncovered = len(uncovered_texts) > 0
        
        # Check if any covered code
        has_covered = any(seg.covered == True for seg in segments)
        
        if has_covered or has_uncovered:
            results['stats']['total_lines'] += 1
            
            if has_uncovered:
                results['stats']['lines_with_uncovered'] += 1
                
                # Get clean line text (remove ANSI codes)
                clean_line = ANSI_PATTERN.sub('', line)
                
                line_analysis = {
                    'line': line_num,
                    'code': clean_line.strip(),
                    'uncovered_parts': uncovered_texts,
                }
                results['uncovered_summary'].append(line_analysis)
            else:
                results['stats']['fully_covered_lines'] += 1
    
    return results


def print_report(results: dict):
    """Print human-readable coverage report."""
    stats = results['stats']
    
    print("=" * 70)
    print("SOURCE COVERAGE ANALYSIS")
    print("=" * 70)
    
    total = stats['total_lines']
    covered = stats['fully_covered_lines']
    uncovered = stats['lines_with_uncovered']
    
    if total > 0:
        print(f"\nLines with executable code: {total}")
        print(f"Fully covered lines:        {covered} ({100*covered//total}%)")
        print(f"Lines with uncovered code:  {uncovered} ({100*uncovered//total}%)")
    
    if results['uncovered_summary']:
        print("\n" + "-" * 70)
        print("UNCOVERED CODE (RED SECTIONS)")
        print("-" * 70)
        
        for item in results['uncovered_summary']:
            print(f"\n📍 Line {item['line']}:")
            print(f"   {item['code']}")
            print(f"   🔴 Uncovered: {item['uncovered_parts']}")
    
    print("\n" + "=" * 70)


def print_json(results: dict):
    """Print JSON output."""
    print(json.dumps(results, indent=2))


def main():
    # Check for --help
    if '--help' in sys.argv or '-h' in sys.argv:
        print(__doc__)
        print("\nOptions:")
        print("  --json    Output as JSON")
        print("  --help    Show this help")
        sys.exit(0)
    
    # Read from stdin or show usage
    if sys.stdin.isatty():
        print("Usage: sui move coverage source --module <name> 2>&1 | python3 parse_source.py")
        print("\nTo preserve colors when piping, use one of:")
        print("  script -q /dev/null sui move coverage source --module <name> | python3 parse_source.py")
        print("  unbuffer sui move coverage source --module <name> | python3 parse_source.py")
        sys.exit(1)
    
    input_text = sys.stdin.read()
    
    # Check if we got any ANSI codes
    if '\x1b[' not in input_text and '[32m' not in input_text:
        print("Warning: No ANSI color codes detected in input.", file=sys.stderr)
        print("The coverage output may have lost colors during piping.", file=sys.stderr)
        print("Try: script -q /dev/null sui move coverage source --module <name> | python3 parse_source.py", file=sys.stderr)
    
    results = analyze_coverage(input_text)
    
    if '--json' in sys.argv:
        print_json(results)
    else:
        print_report(results)


if __name__ == '__main__':
    main()
