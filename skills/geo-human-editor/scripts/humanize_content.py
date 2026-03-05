#!/usr/bin/env python3
"""
Humanize AI-generated content.
"""

import argparse

AI_WORDS = {
    "leverage": "use",
    "delve": "explore",
    "utilize": "use",
    "furthermore": "also",
}

def humanize(content):
    for ai_word, human_word in AI_WORDS.items():
        content = content.replace(ai_word, human_word)
        content = content.replace(ai_word.capitalize(), human_word.capitalize())
    
    # Remove markdown artifacts
    content = content.replace("**", "")
    
    return content

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    
    with open(args.input) as f:
        content = f.read()
    
    humanized = humanize(content)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(humanized)
    else:
        print(humanized)

if __name__ == "__main__":
    main()
