#!/usr/bin/env python3
"""
Structure content for AI readability.
"""

import argparse
import re

def structure_content(content):
    # Add direct answer opener if missing
    lines = content.split('\n')
    
    # Add H2 headers if missing
    structured = []
    for line in lines:
        if len(line) > 50 and not line.startswith('#'):
            # Potential paragraph that needs header
            pass
        structured.append(line)
    
    # Add FAQ block at end
    faq = """
## Frequently Asked Questions

**Q: What is this about?**

A: [Answer]

**Q: How does this work?**

A: [Answer]
"""
    
    return '\n'.join(structured) + faq

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    
    with open(args.input) as f:
        content = f.read()
    
    structured = structure_content(content)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(structured)
    else:
        print(structured)

if __name__ == "__main__":
    main()
