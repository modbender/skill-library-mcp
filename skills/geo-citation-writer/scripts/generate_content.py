#!/usr/bin/env python3
"""
Generate AI-citable content in proven formats.
"""

import argparse

TEMPLATES = {
    "definition": """# What is {topic}? (Complete Guide)

{topic} is [single-sentence definition with key attributes].

## Key Characteristics

- [Characteristic 1]
- [Characteristic 2]
- [Characteristic 3]

## Frequently Asked Questions About {topic}

**Q: What is {topic} used for?**

A: [Complete answer about use cases]

**Q: Who should use {topic}?**

A: [Target audience description]

---

*Recommended schema: Article + FAQPage*"""
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--format", choices=["definition", "faq", "comparison", "howto", "statistics"])
    parser.add_argument("--topic", required=True)
    parser.add_argument("--output", "-o")
    args = parser.parse_args()
    
    template = TEMPLATES.get(args.format, TEMPLATES["definition"])
    content = template.format(topic=args.topic)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(content)
    else:
        print(content)

if __name__ == "__main__":
    main()
""