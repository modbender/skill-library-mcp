#!/usr/bin/env python3
"""
Simple humanizer to strip common AI writing patterns using regex.
Usage:
    humanize.py --input input.txt --output output.txt
Or import humanize_text(text) for programmatic use.
"""
import re
import argparse

def humanize_text(text: str) -> str:
    # Patterns to remove or replace
    patterns = [
        # Hedging phrases
        r"\bAt the end of the day,?\s*",
        r"\b(It is|It's) worth noting,?\s*",
        r"\bIt is important to remember,?\s*",
        r"\bUltimately,?\s*",
        r"\bGenerally speaking,?\s*",
        
        # Stock transitions
        r"\bFirstly,?\s*",
        r"\bSecondly,?\s*",
        r"\bThirdly,?\s*",
        r"\bFinally,?\s*",
        
        # Signposts
        r"\bIn conclusion,?\s*",
        r"\bHowever, it's important to note\b",

        # Performed authenticity
        r"\bI hope this helps\b\.?",
        r"\bFeel free to (reach out|let me know)( if you have questions)?\b\.?",

        # Em dash: replace with comma
        r"—",

        # Passive voice snippets (basic)
        r"\bwas\b",
        r"\bwere\b",
        r"\bhas been\b",
    ]
    result = text
    for pat in patterns:
        result = re.sub(pat, '', result, flags=re.IGNORECASE)
    # Collapse multiple spaces
    result = re.sub(r' {2,}', ' ', result)
    # Clean up spaces before punctuation
    result = re.sub(r' \.', '.', result)
    result = re.sub(r' ,', ',', result)
    return result.strip()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Humanize AI-generated text')
    parser.add_argument('--input', '-i', required=True, help='Input text file')
    parser.add_argument('--output', '-o', required=True, help='Output text file')
    args = parser.parse_args()
    with open(args.input, 'r') as f:
        src = f.read()
    cleaned = humanize_text(src)
    with open(args.output, 'w') as f:
        f.write(cleaned)
