#!/usr/bin/env python3
"""
ASCII table formatter for Telegram with smart column sizing and text wrapping.

USAGE:
    ascii-table <<'EOF'
    Name|Value
    Price|$500
    EOF

    cat data.txt | ascii-table
    echo -e 'A|B\\n1|2' | ascii-table --mobile

OPTIONS:
    --desktop, -d   Unicode box chars, 58 char width (DEFAULT)
    --mobile, -m    ASCII chars (+|-), 48 char width
    --width, -w N   Override width

DESIGN: Stdin-only input. CLI args for row data are intentionally not supported
to avoid shell injection risks — shell parses arguments before scripts run,
which can execute backticks or expand variables in untrusted data.
"""
import sys
import textwrap
import argparse

# Box-drawing character sets
UNICODE_CHARS = {
    'top_left': '┌', 'top_right': '┐', 'bottom_left': '└', 'bottom_right': '┘',
    'horizontal': '─', 'vertical': '│',
    'top_tee': '┬', 'bottom_tee': '┴', 'left_tee': '├', 'right_tee': '┤',
    'cross': '┼'
}

ASCII_CHARS = {
    'top_left': '+', 'top_right': '+', 'bottom_left': '+', 'bottom_right': '+',
    'horizontal': '-', 'vertical': '|',
    'top_tee': '+', 'bottom_tee': '+', 'left_tee': '+', 'right_tee': '+',
    'cross': '+'
}

# Default widths
DEFAULT_DESKTOP_WIDTH = 58
DEFAULT_MOBILE_WIDTH = 48


def make_table(rows, max_width=58, mobile=False):
    """Generate ASCII/Unicode box table with smart column widths and wrapping.
    
    Args:
        rows: List of strings, each with pipe-separated columns ("col1|col2|col3")
        max_width: Maximum total width of table in characters
        mobile: If True, use ASCII chars (+|-|) instead of Unicode box drawing
    
    Returns:
        Formatted table as string
    """
    if not rows:
        return ""
    
    chars = ASCII_CHARS if mobile else UNICODE_CHARS
    
    # Parse all rows into columns
    parsed = [row.split('|') for row in rows]
    num_cols = max(len(r) for r in parsed)
    
    # Pad rows to same number of columns
    for r in parsed:
        while len(r) < num_cols:
            r.append('')
        # Strip whitespace from each cell
        for i in range(len(r)):
            r[i] = r[i].strip()
    
    # Calculate ideal width per column (longest content in each)
    ideal_widths = []
    for col in range(num_cols):
        max_len = max(len(r[col]) for r in parsed)
        ideal_widths.append(max(max_len, 1))  # Minimum 1 char
    
    # Calculate available space for content
    # Structure: │ content │ content │ = 1 + (content + 3) * num_cols
    # Each col needs: space + content + space + border = content + 3
    border_overhead = 1 + (3 * num_cols)
    available = max_width - border_overhead
    
    if available < num_cols:
        # Table too narrow, force minimum
        available = num_cols * 3
    
    total_ideal = sum(ideal_widths)
    
    if total_ideal <= available:
        # Everything fits - use ideal widths
        col_widths = ideal_widths[:]
    else:
        # Need to compress - distribute proportionally with minimum
        min_col_width = 3
        col_widths = []
        
        for ideal in ideal_widths:
            # Proportional share, but at least minimum
            share = max(min_col_width, int(available * ideal / total_ideal))
            col_widths.append(share)
        
        # Adjust to fit exactly within available space
        while sum(col_widths) > available:
            # Shrink the largest column
            max_idx = col_widths.index(max(col_widths))
            if col_widths[max_idx] > min_col_width:
                col_widths[max_idx] -= 1
            else:
                break  # Can't shrink further
        
        while sum(col_widths) < available:
            # Grow columns that are under their ideal
            grew = False
            for i, (w, ideal) in enumerate(zip(col_widths, ideal_widths)):
                if w < ideal and sum(col_widths) < available:
                    col_widths[i] += 1
                    grew = True
            if not grew:
                break
    
    lines = []
    
    # Top border
    top = chars['top_left']
    for i, w in enumerate(col_widths):
        top += chars['horizontal'] * (w + 2)
        top += chars['top_tee'] if i < len(col_widths) - 1 else chars['top_right']
    lines.append(top)
    
    def add_row(cells, add_separator=False):
        """Add a data row, wrapping text as needed."""
        # Wrap each cell's content to fit column width
        wrapped_cols = []
        for i, cell in enumerate(cells):
            wrapped = textwrap.wrap(cell, width=col_widths[i]) or ['']
            wrapped_cols.append(wrapped)
        
        # Find max lines needed for this row
        max_lines = max(len(w) for w in wrapped_cols)
        
        # Pad each column to same number of lines
        for w in wrapped_cols:
            while len(w) < max_lines:
                w.append('')
        
        # Output each line of the row
        for line_idx in range(max_lines):
            row_str = chars['vertical']
            for col_idx, w in enumerate(wrapped_cols):
                content = w[line_idx]
                row_str += f" {content:<{col_widths[col_idx]}} {chars['vertical']}"
            lines.append(row_str)
        
        # Add separator between rows (not after last row)
        if add_separator:
            sep = chars['left_tee']
            for i, w in enumerate(col_widths):
                sep += chars['horizontal'] * (w + 2)
                sep += chars['cross'] if i < len(col_widths) - 1 else chars['right_tee']
            lines.append(sep)
    
    # Add all data rows
    for i, row in enumerate(parsed):
        is_last = (i == len(parsed) - 1)
        add_row(row, add_separator=(not is_last))
    
    # Bottom border
    bottom = chars['bottom_left']
    for i, w in enumerate(col_widths):
        bottom += chars['horizontal'] * (w + 2)
        bottom += chars['bottom_tee'] if i < len(col_widths) - 1 else chars['bottom_right']
    lines.append(bottom)
    
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='ASCII/Unicode table formatter for Telegram (stdin-only input)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
USAGE:
    ascii-table <<'EOF'
    Name|Value
    Price|$500
    EOF

    cat data.txt | ascii-table
    echo -e 'A|B\\n1|2' | ascii-table --mobile

Stdin-only input eliminates shell injection risks.
Quoted heredoc ('EOF') passes all data through literally.
'''
    )
    
    parser.add_argument(
        '--desktop', '-d',
        action='store_true',
        default=True,
        help=f'Desktop mode: Unicode box chars, {DEFAULT_DESKTOP_WIDTH} char width (default)'
    )
    parser.add_argument(
        '--mobile', '-m',
        action='store_true',
        help=f'Mobile mode: ASCII chars (+|-), {DEFAULT_MOBILE_WIDTH} char width'
    )
    parser.add_argument(
        '--width', '-w',
        type=int,
        default=None,
        help='Override default width'
    )
    
    args = parser.parse_args()
    
    # Check if stdin has data
    if sys.stdin.isatty():
        parser.error('No input provided. Pipe data or use heredoc:\n\n'
                     '    ascii-table <<\'EOF\'\n'
                     '    Name|Value\n'
                     '    Row1|Data1\n'
                     '    EOF\n')
    
    # Determine mode and width
    mobile = args.mobile
    if args.width:
        width = args.width
    else:
        width = DEFAULT_MOBILE_WIDTH if mobile else DEFAULT_DESKTOP_WIDTH
    
    # Read rows from stdin
    rows = [line.rstrip('\n\r') for line in sys.stdin if line.strip()]
    
    if not rows:
        parser.error('No rows provided in stdin')
    
    print(make_table(rows, max_width=width, mobile=mobile))


if __name__ == '__main__':
    main()
