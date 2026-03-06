#!/usr/bin/env python3
"""
Analyze Sui Move source coverage with precise uncovered code detection.

Usage:
    python3 analyze_source.py --module <module_name> [--path <package_path>]

This script uses PTY to capture colored output from `sui move coverage source`.
"""

import os
import pty
import sys
import re
import json
import argparse
from dataclasses import dataclass, field
from typing import List, Optional

# ANSI patterns (with \x1b escape)
ANSI_CODE = re.compile(r'\x1b\[[\d;]*m')
RED_PATTERN = re.compile(r'\x1b\[1?;?31m')
GREEN_PATTERN = re.compile(r'\x1b\[32m')
RESET_PATTERN = re.compile(r'\x1b\[0m|\x1b\[39m')


def run_coverage_with_pty(module_name: str, package_path: str = '.') -> str:
    """Run sui move coverage source with PTY to preserve colors."""
    master, slave = pty.openpty()
    pid = os.fork()
    
    if pid == 0:
        # Child process
        os.close(master)
        os.setsid()
        os.dup2(slave, 0)
        os.dup2(slave, 1) 
        os.dup2(slave, 2)
        os.close(slave)
        os.chdir(package_path)
        os.execvp('sui', ['sui', 'move', 'coverage', 'source', '--module', module_name])
    else:
        # Parent process
        os.close(slave)
        output = b''
        while True:
            try:
                data = os.read(master, 4096)
                if not data:
                    break
                output += data
            except OSError:
                break
        os.close(master)
        os.waitpid(pid, 0)
        return output.decode('utf-8', errors='replace')


@dataclass
class UncoveredSegment:
    line_num: int
    full_line: str
    uncovered_text: str
    context_before: str
    context_after: str


def parse_colored_output(output: str) -> List[UncoveredSegment]:
    """Parse colored output to find uncovered (red) segments."""
    uncovered = []
    lines = output.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        # Skip notes and empty lines
        if line.startswith('[NOTE]') or line.startswith('[['):
            continue
        if not line.strip():
            continue
            
        # Find red segments in this line
        # Pattern: text before red, red content, text after red
        
        # Remove all ANSI codes to get clean line
        clean_line = ANSI_CODE.sub('', line)
        
        # Find red sections
        # Split by color codes and track current color
        parts = re.split(r'(\x1b\[[\d;]*m)', line)
        
        current_color = None
        position = 0
        red_segments = []
        
        for part in parts:
            if RED_PATTERN.match(part):
                current_color = 'red'
            elif GREEN_PATTERN.match(part):
                current_color = 'green'
            elif RESET_PATTERN.match(part):
                current_color = None
            elif part and not part.startswith('\x1b'):
                # This is actual text
                if current_color == 'red' and part.strip():
                    # Find position in clean line
                    start = clean_line.find(part, position)
                    if start >= 0:
                        # Get context (chars before and after)
                        ctx_start = max(0, start - 20)
                        ctx_end = min(len(clean_line), start + len(part) + 20)
                        
                        before = clean_line[ctx_start:start]
                        after = clean_line[start + len(part):ctx_end]
                        
                        red_segments.append({
                            'text': part,
                            'before': before,
                            'after': after,
                        })
                        position = start + len(part)
        
        for seg in red_segments:
            uncovered.append(UncoveredSegment(
                line_num=line_num,
                full_line=clean_line.strip(),
                uncovered_text=seg['text'],
                context_before=seg['before'],
                context_after=seg['after'],
            ))
    
    return uncovered


def group_by_function(uncovered: List[UncoveredSegment], source_lines: List[str]) -> dict:
    """Group uncovered segments by function."""
    functions = {}
    current_func = None
    
    # Find function boundaries
    func_pattern = re.compile(r'(?:public\s+)?fun\s+(\w+)')
    
    func_starts = {}
    for i, line in enumerate(source_lines, 1):
        match = func_pattern.search(line)
        if match:
            func_starts[i] = match.group(1)
    
    # Assign each uncovered segment to a function
    sorted_funcs = sorted(func_starts.items())
    
    for seg in uncovered:
        func_name = None
        for start_line, name in reversed(sorted_funcs):
            if seg.line_num >= start_line:
                func_name = name
                break
        
        if func_name:
            if func_name not in functions:
                functions[func_name] = []
            functions[func_name].append(seg)
    
    return functions


def print_report(uncovered: List[UncoveredSegment], module_name: str):
    """Print human-readable report."""
    print("=" * 70)
    print(f"SOURCE COVERAGE ANALYSIS: {module_name}")
    print("=" * 70)
    
    if not uncovered:
        print("\n✅ All code is covered!")
        return
    
    print(f"\n🔴 Found {len(uncovered)} uncovered code segment(s)")
    print("-" * 70)
    
    # Group by line
    by_line = {}
    for seg in uncovered:
        if seg.line_num not in by_line:
            by_line[seg.line_num] = {
                'full_line': seg.full_line,
                'segments': []
            }
        by_line[seg.line_num]['segments'].append(seg)
    
    for line_num in sorted(by_line.keys()):
        info = by_line[line_num]
        print(f"\n📍 Line {line_num}:")
        print(f"   {info['full_line']}")
        
        for seg in info['segments']:
            # Show the uncovered part with markers
            print(f"   └─ 🔴 Uncovered: \"{seg.uncovered_text}\"")
            if seg.context_before or seg.context_after:
                ctx = f"...{seg.context_before}[{seg.uncovered_text}]{seg.context_after}..."
                print(f"      Context: {ctx}")
    
    print("\n" + "=" * 70)
    
    # Summary of what to test
    print("\n💡 SUGGESTIONS:")
    print("-" * 70)
    
    # Identify patterns
    assertions = [s for s in uncovered if 'assert!' in s.uncovered_text]
    func_names = [s for s in uncovered if s.uncovered_text.isidentifier()]
    
    if assertions:
        print("\n🧪 Test assertion failure paths:")
        for seg in assertions:
            print(f"   - Line {seg.line_num}: {seg.uncovered_text}")
            print(f"     → Write a test where this assertion FAILS")
    
    if func_names:
        print("\n🧪 Call these uncovered functions:")
        for seg in func_names:
            print(f"   - {seg.uncovered_text}()")
    
    print()


def print_json(uncovered: List[UncoveredSegment]):
    """Print JSON output."""
    data = {
        'uncovered_count': len(uncovered),
        'uncovered': [
            {
                'line': s.line_num,
                'full_line': s.full_line,
                'uncovered_text': s.uncovered_text,
                'context_before': s.context_before,
                'context_after': s.context_after,
            }
            for s in uncovered
        ]
    }
    print(json.dumps(data, indent=2))


def generate_markdown(uncovered: List[UncoveredSegment], module_name: str) -> str:
    """Generate markdown report."""
    lines = []
    lines.append(f"# Coverage Report: {module_name}")
    lines.append("")
    
    if not uncovered:
        lines.append("✅ **All code is covered!**")
        return '\n'.join(lines)
    
    lines.append(f"🔴 **Found {len(uncovered)} uncovered code segment(s)**")
    lines.append("")
    
    # Group by line
    by_line = {}
    for seg in uncovered:
        if seg.line_num not in by_line:
            by_line[seg.line_num] = {
                'full_line': seg.full_line,
                'segments': []
            }
        by_line[seg.line_num]['segments'].append(seg)
    
    lines.append("## Uncovered Code")
    lines.append("")
    
    for line_num in sorted(by_line.keys()):
        info = by_line[line_num]
        lines.append(f"### Line {line_num}")
        lines.append("")
        lines.append("```move")
        lines.append(info['full_line'])
        lines.append("```")
        lines.append("")
        
        for seg in info['segments']:
            lines.append(f"- ❌ **Uncovered:** `{seg.uncovered_text}`")
        lines.append("")
    
    # Suggestions
    lines.append("## Suggestions")
    lines.append("")
    
    assertions = [s for s in uncovered if 'assert!' in s.uncovered_text]
    func_names = [s for s in uncovered if re.match(r'^[a-z_][a-z0-9_]*$', s.uncovered_text) and len(s.uncovered_text) > 1]
    
    if assertions:
        lines.append("### Test Assertion Failure Paths")
        lines.append("")
        for seg in assertions:
            lines.append(f"- [ ] Line {seg.line_num}: `{seg.uncovered_text}`")
            lines.append(f"  - Write a test where this assertion **fails**")
        lines.append("")
    
    if func_names:
        lines.append("### Call Uncovered Functions")
        lines.append("")
        seen = set()
        for seg in func_names:
            if seg.uncovered_text not in seen:
                seen.add(seg.uncovered_text)
                lines.append(f"- [ ] `{seg.uncovered_text}()`")
        lines.append("")
    
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Analyze Sui Move source coverage')
    parser.add_argument('--module', '-m', required=True, help='Module name to analyze')
    parser.add_argument('--path', '-p', default='.', help='Package path (default: current dir)')
    parser.add_argument('--json', '-j', action='store_true', help='Output as JSON')
    parser.add_argument('--markdown', '--md', action='store_true', help='Output as Markdown')
    parser.add_argument('--output', '-o', help='Output file path (e.g., coverage.md)')
    args = parser.parse_args()
    
    # Run coverage command with PTY
    print(f"Running: sui move coverage source --module {args.module}", file=sys.stderr)
    output = run_coverage_with_pty(args.module, args.path)
    
    # Parse the colored output
    uncovered = parse_colored_output(output)
    
    # Generate output
    if args.json:
        result = json.dumps({
            'uncovered_count': len(uncovered),
            'uncovered': [
                {
                    'line': s.line_num,
                    'full_line': s.full_line,
                    'uncovered_text': s.uncovered_text,
                }
                for s in uncovered
            ]
        }, indent=2)
    elif args.markdown or (args.output and args.output.endswith('.md')):
        result = generate_markdown(uncovered, args.module)
    else:
        # Default: print to console
        print_report(uncovered, args.module)
        return
    
    # Output to file or stdout
    if args.output:
        with open(args.output, 'w') as f:
            f.write(result)
        print(f"Report saved to: {args.output}", file=sys.stderr)
    else:
        print(result)


if __name__ == '__main__':
    main()
