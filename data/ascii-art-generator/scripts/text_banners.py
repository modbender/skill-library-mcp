#!/usr/bin/env python3
"""
Text Banners for ASCII Art Generator

Provides functions for creating decorative text headers and banners
using ASCII and Unicode characters.
"""

def create_banner(text, style='simple', width=None):
    """
    Create a decorative banner with text.
    
    Args:
        text: Text to display in banner
        style: Banner style ('simple', 'double', 'rounded', 'fancy', 'block')
        width: Optional width (auto if None)
    
    Returns:
        ASCII art banner as a string
    """
    if width is None:
        width = len(text) + 4
    
    # Define border characters based on style
    if style == 'simple':
        tl, tr, bl, br, h, v = '┌', '┐', '└', '┘', '─', '│'
    elif style == 'double':
        tl, tr, bl, br, h, v = '╔', '╗', '╚', '╝', '═', '║'
    elif style == 'rounded':
        tl, tr, bl, br, h, v = '╭', '╮', '╰', '╯', '─', '│'
    elif style == 'fancy':
        tl, tr, bl, br, h, v = '╔', '╗', '╚', '╝', '═', '║'
    elif style == 'block':
        tl, tr, bl, br, h, v = '█', '█', '█', '█', '█', '█'
    else:
        tl, tr, bl, br, h, v = '┌', '┐', '└', '┘', '─', '│'
    
    # Calculate padding
    padding = max(0, width - len(text) - 2)
    left_pad = padding // 2
    right_pad = padding - left_pad
    
    # Create banner
    top = tl + (h * (width - 2)) + tr + '\n'
    middle = v + ' ' * left_pad + text + ' ' * right_pad + v + '\n'
    bottom = bl + (h * (width - 2)) + br
    
    if style == 'fancy':
        # Add extra decorative elements
        top = '✨' + top[1:-1] + '✨\n'
        bottom = '✨' + bottom[1:-1] + '✨\n'
    
    return top + middle + bottom

def create_header(text, level=1, align='center'):
    """
    Create a text header with different levels.
    
    Args:
        text: Header text
        level: Header level (1-3)
        align: Alignment ('left', 'center', 'right')
    
    Returns:
        ASCII art header as a string
    """
    if level == 1:
        # Level 1: Double underline
        underline = '═' * (len(text) + 4)
        if align == 'center':
            return f"  {text}\n{underline}"
        elif align == 'left':
            return f"{text}\n{'═' * len(text)}"
        else:  # right
            spaces = ' ' * (len(underline) - len(text) - 2)
            return f"{spaces}{text}\n{underline}"
    
    elif level == 2:
        # Level 2: Single underline
        underline = '─' * (len(text) + 2)
        if align == 'center':
            return f" {text}\n{underline}"
        elif align == 'left':
            return f"{text}\n{'─' * len(text)}"
        else:  # right
            spaces = ' ' * (len(underline) - len(text) - 1)
            return f"{spaces}{text}\n{underline}"
    
    else:  # level 3
        # Level 3: Bracketed
        if align == 'center':
            spaces = ' ' * ((len(text) + 2) // 2)
            return f"{spaces}[ {text} ]"
        elif align == 'left':
            return f"[ {text} ]"
        else:  # right
            spaces = ' ' * (len(text) + 1)
            return f"{spaces}[ {text} ]"

def create_centered_text(text, width=60, border=False):
    """
    Create centered text with optional border.
    
    Args:
        text: Text to center
        width: Total width
        border: Whether to add border
    
    Returns:
        Centered text as ASCII art
    """
    lines = text.split('\n')
    result = []
    
    for line in lines:
        if len(line) >= width:
            result.append(line)
        else:
            padding = width - len(line)
            left_pad = padding // 2
            right_pad = padding - left_pad
            
            if border:
                centered = '│' + ' ' * left_pad + line + ' ' * right_pad + '│'
            else:
                centered = ' ' * left_pad + line + ' ' * right_pad
            result.append(centered)
    
    if border:
        border_line = '┌' + '─' * (width - 2) + '┐'
        result.insert(0, border_line)
        result.append('└' + '─' * (width - 2) + '┘')
    
    return '\n'.join(result)

def create_quote(text, author=None, width=50):
    """
    Create a formatted quote.
    
    Args:
        text: Quote text
        author: Optional author
        width: Maximum width
    
    Returns:
        Formatted quote as ASCII art
    """
    # Wrap text
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        if len(' '.join(current_line + [word])) <= width:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    # Build quote
    result = []
    result.append('  ┌' + '─' * (width + 2) + '┐')
    
    for i, line in enumerate(lines):
        if i == 0:
            result.append('  │  "' + line.ljust(width) + '  │')
        else:
            result.append('  │   ' + line.ljust(width) + '  │')
    
    result.append('  │' + ' ' * (width + 4) + '│')
    
    if author:
        author_line = f"  — {author}"
        padding = width + 6 - len(author_line)
        result.append('  │' + ' ' * padding + author_line + '  │')
    
    result.append('  └' + '─' * (width + 2) + '┘')
    
    return '\n'.join(result)

def create_progress_header(step, total, title, width=40):
    """
    Create a header with progress indicator.
    
    Args:
        step: Current step (1-based)
        total: Total steps
        title: Step title
        width: Header width
    
    Returns:
        Progress header as ASCII art
    """
    progress = int((step / total) * (width - 10))
    progress_bar = '█' * progress + '░' * (width - 10 - progress)
    
    header = f"Step {step}/{total}: {title}"
    padding = width - len(header) - 2
    
    if padding > 0:
        left_pad = padding // 2
        right_pad = padding - left_pad
        header = ' ' * left_pad + header + ' ' * right_pad
    
    result = []
    result.append('╔' + '═' * (width - 2) + '╗')
    result.append('║' + header + '║')
    result.append('║' + ' ' * (width - 2) + '║')
    result.append('║  [' + progress_bar + f'] {step}/{total} ║')
    result.append('╚' + '═' * (width - 2) + '╝')
    
    return '\n'.join(result)

def create_warning_box(text, width=50):
    """
    Create a warning/alert box.
    
    Args:
        text: Warning text
        width: Box width
    
    Returns:
        Warning box as ASCII art
    """
    lines = []
    words = text.split()
    current_line = []
    
    for word in words:
        if len(' '.join(current_line + [word])) <= width - 4:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    result = []
    result.append('╔' + '═' * (width - 2) + '╗')
    result.append('║ ⚠  WARNING' + ' ' * (width - 13) + '║')
    result.append('║' + '═' * (width - 2) + '║')
    
    for line in lines:
        padding = width - len(line) - III
        left_pad = 2
        right_pad = padding - left_pad
        result.append('║' + ' ' * left_pad + line + ' ' * right_pad + '║')
    
    result.append('╚' + '═' * (width - 2) + '╝')
    
    return '\n'.join(result)

if __name__ == "__main__":
    # Test the functions
    print("Simple Banner:")
    print(create_banner("Hello World", 'simple'))
    print("\n" + "="*50 + "\n")
    
    print("Fancy Banner:")
    print(create_banner("Important Notice", 'fancy', 30))
    print("\n" + "="*50 + "\n")
    
    print("Header Level 1:")
    print(create_header("Main Title", 1, 'center'))
    print("\n" + "="*50 + "\n")
    
    print("Centered Text with Border:")
    print(create_centered_text("This text is centered\nwith multiple lines", 40, True))
    print("\n" + "="*50 + "\n")
    
    print("Quote:")
    print(create_quote("The only way to do great work is to love what you do.", "Steve Jobs", 40))
    print("\n" + "="*50 + "\n")
    
    print("Progress Header:")
    print(create_progress_header(3, 5, "Processing Data", 50))
    print("\n" + "="*50 + "\n")
    
    print("Warning Box:")
    print(create_warning_box("This action cannot be undone. Please proceed with caution.", 50))