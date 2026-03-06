#!/usr/bin/env python3
"""
Email Content Sanitization Script

Sanitizes email content by stripping dangerous elements, extracting only
the newest message, and detecting prompt injection patterns.

Usage:
    python sanitize_content.py --input "email.txt" --output "safe.txt"
    python sanitize_content.py --text "raw email content" --json
"""

import argparse
import base64
import html
import json
import quopri
import re
import sys
from pathlib import Path
from typing import Optional


# Prompt injection patterns to detect
INJECTION_PATTERNS = [
    # Direct overrides
    (r'ignore\s+(all\s+)?previous\s+instructions?', 'critical', 'Direct instruction override'),
    (r'forget\s+(everything|all|what)', 'critical', 'Memory wipe attempt'),
    (r'disregard\s+(the\s+)?(above|previous)', 'critical', 'Instruction disregard'),
    (r'new\s+(task|instruction|objective)', 'high', 'Task hijacking'),
    
    # System role impersonation
    (r'\[system\]|\[admin\]|\[root\]', 'critical', 'Role impersonation'),
    (r'<\/?system>|<\/?admin>', 'critical', 'XML role tags'),
    (r'SYSTEM\s*:', 'high', 'System prefix'),
    
    # Prompt structure manipulation
    (r'</?(assistant|user|human)(_response)?>', 'critical', 'Prompt structure manipulation'),
    (r'```\s*system|```\s*admin', 'high', 'Code block exploitation'),
    
    # Override keywords
    (r'\b(override|bypass|disable)\s+(security|filter|check)', 'critical', 'Security bypass'),
    (r'admin\s+override', 'critical', 'Admin override claim'),
    (r'jailbreak|prompt\s*injection', 'critical', 'Explicit attack reference'),
    
    # Instruction embedding
    (r'<!--.*?(instruction|command|execute).*?-->', 'high', 'Hidden HTML instruction'),
    (r'\x00|\u200b|\u200c|\u200d|\ufeff', 'medium', 'Hidden characters'),
]

# Quote markers to detect forwarded/replied content
QUOTE_PATTERNS = [
    r'^>+\s*',  # > quote markers
    r'^\|',  # | quote markers
    r'^On\s+.+wrote:',  # "On [date], [name] wrote:"
    r'^-{5,}\s*(Forwarded|Original)',  # Forwarded message dividers
    r'^From:\s+.+\nSent:\s+.+\nTo:',  # Outlook-style quote headers
    r'<blockquote',  # HTML blockquotes
]


def decode_content(text: str) -> str:
    """Decode base64 and quoted-printable content."""
    result = text
    
    # Decode base64 blocks
    base64_pattern = r'([A-Za-z0-9+/]{20,}={0,2})'
    for match in re.finditer(base64_pattern, text):
        try:
            decoded = base64.b64decode(match.group(1)).decode('utf-8', errors='ignore')
            if decoded.isprintable() or '\n' in decoded:
                result = result.replace(match.group(1), f'[DECODED: {decoded}]')
        except:
            pass
    
    # Decode quoted-printable
    try:
        if '=' in result and re.search(r'=[0-9A-F]{2}', result):
            result = quopri.decodestring(result.encode()).decode('utf-8', errors='ignore')
    except:
        pass
    
    # Decode HTML entities
    result = html.unescape(result)
    
    return result


def strip_html(text: str) -> str:
    """Remove HTML tags and extract plain text."""
    # Remove style and script tags entirely
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove HTML comments (but log if they contain suspicious content)
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    
    # Convert breaks to newlines
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</p>', '\n\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</div>', '\n', text, flags=re.IGNORECASE)
    
    # Remove all remaining tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Clean up whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' +', ' ', text)
    
    return text.strip()


def extract_newest_message(text: str) -> str:
    """Extract only the newest message, ignoring quoted/forwarded content."""
    lines = text.split('\n')
    result_lines = []
    in_quote = False
    
    for line in lines:
        # Check if this line starts a quoted section
        is_quote_start = any(re.match(p, line, re.IGNORECASE) for p in QUOTE_PATTERNS)
        
        if is_quote_start:
            in_quote = True
            continue
        
        # Simple quote detection (lines starting with >)
        if line.strip().startswith('>'):
            continue
        
        # Skip lines in quoted sections
        if in_quote:
            # Check if we've exited the quote (blank line followed by non-quote)
            if not line.strip():
                in_quote = False
            continue
        
        result_lines.append(line)
    
    return '\n'.join(result_lines).strip()


def remove_signature(text: str) -> str:
    """Remove email signature from content."""
    # Standard signature delimiter
    sig_match = re.search(r'\n--\s*\n', text)
    if sig_match:
        text = text[:sig_match.start()]
    
    # Common signature patterns
    sig_patterns = [
        r'\n(Best|Kind|Warm)\s+regards?,?\s*\n',
        r'\n(Thanks|Thank you|Cheers|Sincerely),?\s*\n',
        r'\nSent from my (iPhone|iPad|Android|BlackBerry)',
        r'\nGet Outlook for',
    ]
    
    for pattern in sig_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            text = text[:match.start()]
            break
    
    return text.strip()


def detect_injection(text: str) -> list:
    """Scan text for prompt injection patterns."""
    threats = []
    
    for pattern, severity, description in INJECTION_PATTERNS:
        matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            threats.append({
                "severity": severity,
                "description": description,
                "matched_text": match.group(0)[:100],  # Limit length
                "position": match.start()
            })
    
    return threats


def sanitize_content(
    text: str,
    extract_newest: bool = True,
    remove_sig: bool = True,
    decode: bool = True
) -> dict:
    """
    Sanitize email content.
    
    Returns:
        dict with keys:
            - sanitized: The cleaned text
            - threats: List of detected injection attempts
            - is_safe: Boolean indicating if content appears safe
            - warnings: List of warnings
    """
    result = {
        "original_length": len(text),
        "sanitized": "",
        "threats": [],
        "is_safe": True,
        "warnings": []
    }
    
    # Step 1: Decode encoded content
    if decode:
        text = decode_content(text)
    
    # Step 2: Strip HTML
    text = strip_html(text)
    
    # Step 3: Extract newest message
    if extract_newest:
        original_text = text
        text = extract_newest_message(text)
        if len(text) < len(original_text) * 0.5:
            result["warnings"].append("Significant content was quoted/forwarded and ignored")
    
    # Step 4: Remove signature
    if remove_sig:
        text = remove_signature(text)
    
    # Step 5: Detect injection patterns
    result["threats"] = detect_injection(text)
    
    # Determine safety
    critical_threats = [t for t in result["threats"] if t["severity"] == "critical"]
    if critical_threats:
        result["is_safe"] = False
        result["warnings"].append(f"Detected {len(critical_threats)} critical threats")
    
    # Clean up final text
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()
    
    result["sanitized"] = text
    result["sanitized_length"] = len(text)
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Sanitize email content")
    parser.add_argument("--input", help="Path to input file")
    parser.add_argument("--output", help="Path to output file")
    parser.add_argument("--text", help="Raw text to sanitize")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--no-extract", action="store_true", help="Don't extract newest message")
    parser.add_argument("--keep-sig", action="store_true", help="Keep email signature")
    
    args = parser.parse_args()
    
    # Get input text
    if args.text:
        text = args.text
    elif args.input:
        text = Path(args.input).read_text()
    else:
        text = sys.stdin.read()
    
    # Sanitize
    result = sanitize_content(
        text,
        extract_newest=not args.no_extract,
        remove_sig=not args.keep_sig
    )
    
    # Output
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if args.output:
            Path(args.output).write_text(result["sanitized"])
            print(f"Sanitized content written to: {args.output}")
        else:
            print("=== SANITIZED CONTENT ===")
            print(result["sanitized"])
            print("\n=== ANALYSIS ===")
            print(f"Original length: {result['original_length']}")
            print(f"Sanitized length: {result['sanitized_length']}")
            print(f"Is safe: {'✅ Yes' if result['is_safe'] else '❌ No'}")
            
            if result["threats"]:
                print("\n⚠️  THREATS DETECTED:")
                for t in result["threats"]:
                    print(f"  [{t['severity'].upper()}] {t['description']}: '{t['matched_text']}'")
            
            if result["warnings"]:
                print("\nWarnings:")
                for w in result["warnings"]:
                    print(f"  - {w}")


if __name__ == "__main__":
    main()
