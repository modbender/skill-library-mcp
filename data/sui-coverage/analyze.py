#!/usr/bin/env python3
"""
Sui Move Coverage Analyzer

Parses LCOV format output from `sui move coverage lcov` and identifies
uncovered code sections to help write more comprehensive tests.
"""

import argparse
import json
import os
import sys
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class BranchInfo:
    line: int
    block: int
    branch: int
    taken: bool
    count: int  # -1 means never taken


@dataclass
class FunctionInfo:
    name: str
    line: int
    call_count: int


@dataclass
class FileCoverage:
    path: str
    functions: list[FunctionInfo] = field(default_factory=list)
    line_hits: dict[int, int] = field(default_factory=dict)  # line -> hit count
    branches: list[BranchInfo] = field(default_factory=list)
    # Summary stats
    functions_found: int = 0
    functions_hit: int = 0
    lines_found: int = 0
    lines_hit: int = 0
    branches_found: int = 0
    branches_hit: int = 0


def parse_lcov(lcov_path: str) -> list[FileCoverage]:
    """Parse LCOV file and return coverage data per source file."""
    files = []
    current = None
    fn_lines = {}  # name -> line number
    fn_counts = {}  # name -> call count (for current file)

    with open(lcov_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            if line.startswith('SF:'):
                # New source file
                current = FileCoverage(path=line[3:])
                fn_lines = {}
                fn_counts = {}
            elif line.startswith('FN:'):
                # Function definition: FN:line,name
                parts = line[3:].split(',', 1)
                if len(parts) == 2:
                    fn_line, fn_name = int(parts[0]), parts[1]
                    fn_lines[fn_name] = fn_line
            elif line.startswith('FNDA:'):
                # Function execution: FNDA:count,name
                parts = line[5:].split(',', 1)
                if len(parts) == 2 and current:
                    count, name = int(parts[0]), parts[1]
                    fn_counts[name] = count
            elif line.startswith('DA:'):
                # Line data: DA:line,count
                parts = line[3:].split(',')
                if len(parts) == 2 and current:
                    ln, count = int(parts[0]), int(parts[1])
                    current.line_hits[ln] = count
            elif line.startswith('BRDA:'):
                # Branch data: BRDA:line,block,branch,count
                parts = line[5:].split(',')
                if len(parts) == 4 and current:
                    ln, block, branch = int(parts[0]), int(parts[1]), int(parts[2])
                    count_str = parts[3]
                    if count_str == '-':
                        count = -1
                        taken = False
                    else:
                        count = int(count_str)
                        taken = count > 0
                    current.branches.append(BranchInfo(line=ln, block=block, branch=branch, taken=taken, count=count))
            elif line.startswith('FNF:'):
                if current:
                    current.functions_found = int(line[4:])
            elif line.startswith('FNH:'):
                if current:
                    current.functions_hit = int(line[4:])
            elif line.startswith('LF:'):
                if current:
                    current.lines_found = int(line[3:])
            elif line.startswith('LH:'):
                if current:
                    current.lines_hit = int(line[3:])
            elif line.startswith('BRF:'):
                if current:
                    current.branches_found = int(line[4:])
            elif line.startswith('BRH:'):
                if current:
                    current.branches_hit = int(line[4:])
            elif line == 'end_of_record':
                if current:
                    # Finalize functions for this file
                    for name, fn_line in fn_lines.items():
                        count = fn_counts.get(name, 0)
                        current.functions.append(FunctionInfo(name=name, line=fn_line, call_count=count))
                    files.append(current)
                    current = None
                    fn_lines = {}
                    fn_counts = {}

    # Handle file without end_of_record
    if current:
        for name, fn_line in fn_lines.items():
            count = fn_counts.get(name, 0)
            current.functions.append(FunctionInfo(name=name, line=fn_line, call_count=count))
        files.append(current)

    return files


def get_uncovered_lines(coverage: FileCoverage) -> list[int]:
    """Return list of lines with 0 hit count."""
    return sorted([ln for ln, count in coverage.line_hits.items() if count == 0])


def get_untaken_branches(coverage: FileCoverage) -> list[dict]:
    """Return branches that were never taken."""
    return [
        {'line': b.line, 'block': b.block, 'branch': b.branch}
        for b in coverage.branches if not b.taken
    ]


def get_uncalled_functions(coverage: FileCoverage) -> list[dict]:
    """Return functions that were never called."""
    return [
        {'name': f.name, 'line': f.line}
        for f in coverage.functions if f.call_count == 0
    ]


def read_source_lines(source_path: str) -> dict[int, str]:
    """Read source file and return line number -> content mapping."""
    lines = {}
    try:
        with open(source_path, 'r') as f:
            for i, line in enumerate(f, 1):
                lines[i] = line.rstrip()
    except Exception:
        pass
    return lines


def generate_suggestions(coverage: FileCoverage, source_lines: Optional[dict] = None) -> list[dict]:
    """Generate actionable suggestions for improving coverage."""
    suggestions = []

    # Uncalled functions
    for f in coverage.functions:
        if f.call_count == 0:
            suggestion = {
                'type': 'uncalled_function',
                'priority': 'high',
                'function': f.name,
                'line': f.line,
                'action': f'Write a test that calls `{f.name}()`'
            }
            if source_lines and f.line in source_lines:
                suggestion['source'] = source_lines[f.line]
            suggestions.append(suggestion)

    # Untaken branches (grouped by line)
    branch_lines = {}
    for b in coverage.branches:
        if not b.taken:
            if b.line not in branch_lines:
                branch_lines[b.line] = []
            branch_lines[b.line].append(b)

    for line, branches in branch_lines.items():
        suggestion = {
            'type': 'untaken_branch',
            'priority': 'medium',
            'line': line,
            'branches': len(branches),
            'action': f'Add test case to cover alternate branch at line {line}'
        }
        if source_lines and line in source_lines:
            suggestion['source'] = source_lines[line]
        suggestions.append(suggestion)

    # Uncovered lines (grouped into ranges)
    uncovered = get_uncovered_lines(coverage)
    if uncovered:
        ranges = []
        start = end = uncovered[0]
        for ln in uncovered[1:]:
            if ln == end + 1:
                end = ln
            else:
                ranges.append((start, end))
                start = end = ln
        ranges.append((start, end))

        for start, end in ranges:
            if start == end:
                line_desc = f'line {start}'
            else:
                line_desc = f'lines {start}-{end}'
            suggestion = {
                'type': 'uncovered_lines',
                'priority': 'low',
                'start_line': start,
                'end_line': end,
                'action': f'Write test to execute {line_desc}'
            }
            if source_lines:
                snippet = []
                for ln in range(start, min(end + 1, start + 5)):
                    if ln in source_lines:
                        snippet.append(f'{ln}: {source_lines[ln]}')
                if snippet:
                    suggestion['source_snippet'] = snippet
            suggestions.append(suggestion)

    return suggestions


def analyze(lcov_path: str, source_dir: Optional[str] = None) -> dict:
    """Main analysis function."""
    files = parse_lcov(lcov_path)

    results = {
        'summary': {
            'total_files': len(files),
            'total_functions_found': sum(f.functions_found for f in files),
            'total_functions_hit': sum(f.functions_hit for f in files),
            'total_lines_found': sum(f.lines_found for f in files),
            'total_lines_hit': sum(f.lines_hit for f in files),
            'total_branches_found': sum(f.branches_found for f in files),
            'total_branches_hit': sum(f.branches_hit for f in files),
        },
        'files': []
    }

    # Calculate percentages
    s = results['summary']
    s['function_coverage'] = f"{s['total_functions_hit']}/{s['total_functions_found']}" if s['total_functions_found'] else "N/A"
    s['line_coverage'] = f"{s['total_lines_hit']}/{s['total_lines_found']}" if s['total_lines_found'] else "N/A"
    s['branch_coverage'] = f"{s['total_branches_hit']}/{s['total_branches_found']}" if s['total_branches_found'] else "N/A"

    if s['total_lines_found']:
        s['line_coverage_pct'] = round(100 * s['total_lines_hit'] / s['total_lines_found'], 1)
    if s['total_branches_found']:
        s['branch_coverage_pct'] = round(100 * s['total_branches_hit'] / s['total_branches_found'], 1)

    for cov in files:
        source_lines = None
        if source_dir:
            # Try to find source file
            basename = os.path.basename(cov.path)
            source_path = os.path.join(source_dir, basename)
            if os.path.exists(source_path):
                source_lines = read_source_lines(source_path)
            elif os.path.exists(cov.path):
                source_lines = read_source_lines(cov.path)

        file_result = {
            'path': cov.path,
            'coverage': {
                'functions': f"{cov.functions_hit}/{cov.functions_found}",
                'lines': f"{cov.lines_hit}/{cov.lines_found}",
                'branches': f"{cov.branches_hit}/{cov.branches_found}",
            },
            'uncovered_lines': get_uncovered_lines(cov),
            'untaken_branches': get_untaken_branches(cov),
            'uncalled_functions': get_uncalled_functions(cov),
            'suggestions': generate_suggestions(cov, source_lines),
        }
        results['files'].append(file_result)

    return results


def print_human_readable(results: dict):
    """Print results in a human-readable format."""
    s = results['summary']
    print("=" * 60)
    print("SUI MOVE COVERAGE ANALYSIS")
    print("=" * 60)
    print(f"\nFiles analyzed: {s['total_files']}")
    print(f"Function coverage: {s['function_coverage']}")
    print(f"Line coverage: {s['line_coverage']} ({s.get('line_coverage_pct', 'N/A')}%)")
    print(f"Branch coverage: {s['branch_coverage']} ({s.get('branch_coverage_pct', 'N/A')}%)")

    for file_data in results['files']:
        print(f"\n{'─' * 60}")
        print(f"📄 {file_data['path']}")
        print(f"   Lines: {file_data['coverage']['lines']}, "
              f"Branches: {file_data['coverage']['branches']}, "
              f"Functions: {file_data['coverage']['functions']}")

        if file_data['uncalled_functions']:
            print("\n   ⚠️  Uncalled functions:")
            for f in file_data['uncalled_functions']:
                print(f"      - {f['name']} (line {f['line']})")

        if file_data['untaken_branches']:
            print("\n   ⚠️  Untaken branches:")
            lines = set(b['line'] for b in file_data['untaken_branches'])
            for ln in sorted(lines):
                count = sum(1 for b in file_data['untaken_branches'] if b['line'] == ln)
                print(f"      - Line {ln}: {count} branch(es) not taken")

        if file_data['uncovered_lines']:
            print(f"\n   ⚠️  Uncovered lines: {file_data['uncovered_lines']}")

        if file_data['suggestions']:
            print("\n   💡 Suggestions:")
            for i, sug in enumerate(file_data['suggestions'], 1):
                priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(sug['priority'], '⚪')
                print(f"      {i}. {priority_emoji} {sug['action']}")
                if 'source' in sug:
                    print(f"         └─ {sug['source'][:80]}...")
                if 'source_snippet' in sug:
                    for snippet_line in sug['source_snippet'][:3]:
                        print(f"         │ {snippet_line[:70]}")

    print("\n" + "=" * 60)


def filter_results(results: dict, path_filter: str = None, issues_only: bool = False) -> dict:
    """Filter results by path pattern and/or issues only."""
    filtered_files = []
    
    for file_data in results['files']:
        # Path filter
        if path_filter and path_filter not in file_data['path']:
            continue
        
        # Issues only filter
        if issues_only:
            has_issues = (
                file_data['uncovered_lines'] or 
                file_data['untaken_branches'] or 
                file_data['uncalled_functions']
            )
            if not has_issues:
                continue
        
        filtered_files.append(file_data)
    
    # Recalculate summary for filtered files
    filtered_results = {
        'summary': {
            'total_files': len(filtered_files),
            'total_functions_found': sum(
                int(f['coverage']['functions'].split('/')[1]) for f in filtered_files
            ),
            'total_functions_hit': sum(
                int(f['coverage']['functions'].split('/')[0]) for f in filtered_files
            ),
            'total_lines_found': sum(
                int(f['coverage']['lines'].split('/')[1]) for f in filtered_files
            ),
            'total_lines_hit': sum(
                int(f['coverage']['lines'].split('/')[0]) for f in filtered_files
            ),
            'total_branches_found': sum(
                int(f['coverage']['branches'].split('/')[1]) for f in filtered_files
            ),
            'total_branches_hit': sum(
                int(f['coverage']['branches'].split('/')[0]) for f in filtered_files
            ),
        },
        'files': filtered_files
    }
    
    s = filtered_results['summary']
    s['function_coverage'] = f"{s['total_functions_hit']}/{s['total_functions_found']}"
    s['line_coverage'] = f"{s['total_lines_hit']}/{s['total_lines_found']}"
    s['branch_coverage'] = f"{s['total_branches_hit']}/{s['total_branches_found']}"
    
    if s['total_lines_found']:
        s['line_coverage_pct'] = round(100 * s['total_lines_hit'] / s['total_lines_found'], 1)
    if s['total_branches_found']:
        s['branch_coverage_pct'] = round(100 * s['total_branches_hit'] / s['total_branches_found'], 1)
    
    return filtered_results


def main():
    parser = argparse.ArgumentParser(description='Analyze Sui Move test coverage')
    parser.add_argument('lcov_file', help='Path to lcov.info file')
    parser.add_argument('--source-dir', '-s', help='Directory containing Move source files')
    parser.add_argument('--json', '-j', action='store_true', help='Output as JSON')
    parser.add_argument('--filter', '-f', help='Only show files matching this path pattern')
    parser.add_argument('--issues-only', '-i', action='store_true', help='Only show files with coverage issues')
    args = parser.parse_args()

    if not os.path.exists(args.lcov_file):
        print(f"Error: File not found: {args.lcov_file}", file=sys.stderr)
        sys.exit(1)

    results = analyze(args.lcov_file, args.source_dir)
    
    # Apply filters
    if args.filter or args.issues_only:
        results = filter_results(results, args.filter, args.issues_only)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print_human_readable(results)


if __name__ == '__main__':
    main()
