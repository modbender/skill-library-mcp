#!/usr/bin/env python3
"""
Basic Shapes for ASCII Art Generator

Provides functions for creating geometric shapes, borders, and patterns
using ASCII and Unicode characters.
"""

def create_box(width=20, height=10, style='single'):
    """
    Create a box with specified dimensions and border style.
    
    Args:
        width: Width of the box (excluding borders)
        height: Height of the box (excluding borders)
        style: Border style ('single', 'double', 'rounded', 'thick')
    
    Returns:
        ASCII art box as a string
    """
    # Define border characters based on style
    if style == 'single':
        tl, tr, bl, br, h, v = '┌', '┐', '└', '┘', '─', '│'
    elif style == 'double':
        tl, tr, bl, br, h, v = '╔', '╗', '╚', '╝', '═', '║'
    elif style == 'rounded':
        tl, tr, bl, br, h, v = '╭', '╮', '╰', '╯', '─', '│'
    elif style == 'thick':
        tl, tr, bl, br, h, v = '┏', '┓', '┗', '┛', '━', '┃'
    else:
        tl, tr, bl, br, h, v = '┌', '┐', '└', '┘', '─', '│'
    
    # Create top border
    top = tl + (h * width) + tr + '\n'
    
    # Create middle rows
    middle = (v + ' ' * width + v + '\n') * (height - 2)
    
    # Create bottom border
    bottom = bl + (h * width) + br
    
    return top + middle + bottom

def create_circle(radius=5, filled=False):
    """
    Create a circle approximation using ASCII characters.
    
    Args:
        radius: Radius of the circle
        filled: Whether to fill the circle
    
    Returns:
        ASCII art circle as a string
    """
    result = []
    chars = '·◦○◌◯◎⦿' if filled else '·◦○◌◯◎⦿'
    
    for y in range(-radius, radius + 1):
        row = ''
        for x in range(-radius, radius + 1):
            distance = (x**2 + y**2) ** 0.5
            
            if filled:
                if distance <= radius:
                    # Gradient fill based on distance from center
                    if distance <= radius * 0.3:
                        row += '⦿'
                    elif distance <= radius * 0.6:
                        row += '◎'
                    elif distance <= radius * 0.9:
                        row += '◯'
                    else:
                        row += '○'
                else:
                    row += ' '
            else:
                # Outline only
                if abs(distance - radius) < 0.5:
                    row += '○'
                else:
                    row += ' '
        result.append(row)
    
    return '\n'.join(result)

def create_tree(height=10):
    """
    Create a simple tree using ASCII characters.
    
    Args:
        height: Height of the tree
    
    Returns:
        ASCII art tree as a string
    """
    result = []
    
    # Create leaves (triangle shape)
    for i in range(1, height - 2):
        spaces = ' ' * (height - i - -2)
        leaves = '▲' * (2 * i - 1)
        result.append(spaces + leaves)
    
    # Create trunk
    trunk_width = max(1, height // 6)
    trunk_spaces = ' ' * (height - trunk_width // 2 - 1)
    trunk = '█' * trunk_width
    
    for _ in range(2):
        result.append(trunk_spaces + trunk)
    
    return '\n'.join(result)

def create_heart(size=5):
    """
    Create a heart shape using ASCII characters.
    
    Args:
        size: Size of the heart
    
    Returns:
        ASCII art heart as a string
    """
    # Heart shape algorithm
    result = []
    for y in range(size, -size, -1):
        row = ''
        for x in range(-size, size + 1):
            # Heart equation: (x^2 + y^2 - 1)^3 - x^2 * y^3 <= 0
            equation = (x**2 + y**2 - 1)**3 - x**2 * y**3
            if equation <= 0:
                row += '❤'
            else:
                row += ' '
        result.append(row)
    
    return '\n'.join(result)

def create_pattern(pattern_type='grid', width=20, height=10):
    """
    Create repeating patterns.
    
    Args:
        pattern_type: Type of pattern ('grid', 'dots', 'waves', 'checker')
        width: Width of pattern
        height: Height of pattern
    
    Returns:
        Pattern as ASCII art
    """
    patterns = {
        'grid': ['+--', '|  '],
        'dots': ['∙∙ ', ' ∙∙'],
        'waves': ['~~ ', ' ~~'],
        'checker': ['██ ', ' ██'],
        'diagonal': ['// ', ' //'],
        'cross': ['++ ', ' ++']
    }
    
    if pattern_type not in patterns:
        pattern_type = 'grid'
    
    pattern = patterns[pattern_type]
    pattern_width = len(pattern[0])
    pattern_height = len(pattern)
    
    result = []
    for y in range(height):
        row = ''
        for x in range(width):
            row += pattern[y % pattern_height][x % pattern_width]
        result.append(row)
    
    return '\n'.join(result)

def create_progress_bar(percentage=50, width=20, style='block'):
    """
    Create a progress bar.
    
    Args:
        percentage: Progress percentage (0-100)
        width: Width of progress bar
        style: Style ('block', 'arrow', 'gradient')
    
    Returns:
        Progress bar as ASCII art
    """
    filled_width = int(width * percentage / 100)
    empty_width = width - filled_width
    
    if style == 'block':
        filled = '█' * filled_width
        empty = '░' * empty_width
    elif style == 'arrow':
        filled = '▶' * filled_width
        empty = '·' * empty_width
    elif style == 'gradient':
        gradient = '█▓▒░'
        filled = ''
        for i in range(filled_width):
            filled += gradient[min(i, len(gradient)-1)]
        empty = ' ' * empty_width
    else:
        filled = '█' * filled_width
        empty = '░' * empty_width
    
    return f'[{filled}{empty}] {percentage}%'

if __name__ == "__main__":
    # Test the functions
    print("Box (single border):")
    print(create_box(15, 6, 'single'))
    print("\n" + "="*40 + "\n")
    
    print("Circle (outline):")
    print(create_circle(5, False))
    print("\n" + "="*40 + "\n")
    
    print("Tree:")
    print(create_tree(8))
    print("\n" + "="*40 + "\n")
    
    print("Heart:")
    print(create_heart(4))
    print("\n" + "="*40 + "\n")
    
    print("Pattern (checker):")
    print(create_pattern('checker', -20, 6))
    print("\n" + "="*40 + "\n")
    
    print("Progress Bar:")
    print(create_progress_bar(75, 25, 'gradient'))