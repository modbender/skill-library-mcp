#!/usr/bin/env python3
"""
Validate SRT file format
"""

import argparse
import re
import sys
from typing import List, Tuple


def validate_srt(filepath: str) -> Tuple[bool, List[str]]:
    """
    Validate SRT file format.
    Returns (is_valid, list_of_errors)
    """
    errors = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return False, [f"Cannot read file: {e}"]
    
    # Split by double newline
    blocks = re.split(r'\n\s*\n', content.strip())
    
    expected_index = 1
    
    for i, block in enumerate(blocks, 1):
        lines = block.strip().split('\n')
        
        # Check minimum lines
        if len(lines) < 3:
            errors.append(f"Block {i}: Too few lines (expected at least 3, got {len(lines)})")
            continue
        
        # Check index
        try:
            index = int(lines[0].strip())
            if index != expected_index:
                errors.append(f"Block {i}: Index mismatch (expected {expected_index}, got {index})")
            expected_index += 1
        except ValueError:
            errors.append(f"Block {i}: Invalid index '{lines[0]}'")
            continue
        
        # Check timecode format
        timecode_pattern = r'^(\d{2}:\d{2}:\d{2},\d{3})\s+--\u003e\s+(\d{2}:\d{2}:\d{2},\d{3})$'
        match = re.match(timecode_pattern, lines[1].strip())
        if not match:
            errors.append(f"Block {i}: Invalid timecode format '{lines[1]}'")
        else:
            # Validate time ranges
            start_time = match.group(1)
            end_time = match.group(2)
            
            def time_to_ms(t: str) -> int:
                h, m, s = t.split(':')
                s, ms = s.split(',')
                return int(h) * 3600000 + int(m) * 60000 + int(s) * 1000 + int(ms)
            
            start_ms = time_to_ms(start_time)
            end_ms = time_to_ms(end_time)
            
            if end_ms <= start_ms:
                errors.append(f"Block {i}: End time must be after start time")
        
        # Check subtitle text (at least one line)
        if len(lines) < 3 or not lines[2].strip():
            errors.append(f"Block {i}: Missing subtitle text")
    
    is_valid = len(errors) == 0
    return is_valid, errors


def main():
    parser = argparse.ArgumentParser(description='Validate SRT subtitle file format')
    parser.add_argument('file', help='SRT file to validate')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed output')
    
    args = parser.parse_args()
    
    is_valid, errors = validate_srt(args.file)
    
    if is_valid:
        print(f"✓ {args.file} is valid SRT format")
        sys.exit(0)
    else:
        print(f"✗ {args.file} has {len(errors)} error(s):")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)


if __name__ == '__main__':
    main()
