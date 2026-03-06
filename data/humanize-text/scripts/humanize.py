#!/usr/bin/env python3
"""Quick-pass humanizer for text files. Handles the mechanical replacements.
For nuanced rewrites, use the full skill via agent."""

import re
import sys
import argparse

# Em-dash → comma (rough pass — agent should review context)
def fix_emdashes(text):
    # Replace em-dash with comma-space (most common valid replacement)
    text = re.sub(r'\s*—\s*', ', ', text)
    # Clean up double commas
    text = re.sub(r',\s*,', ',', text)
    return text

# Kill dead phrases
DEAD_PHRASES = [
    # Filler
    (r"[Ii]t'?s important to note that\s*", ""),
    (r"[Ii]t'?s worth noting that\s*", ""),
    (r"[Ii]t bears mentioning that\s*", ""),
    (r"[Ll]et'?s dive in\.?\s*", ""),
    (r"[Ll]et'?s delve into\s*", "Let's look at "),
    (r"[Dd]elve into\s*", "explore "),
    (r"[Dd]elves into\s*", "explores "),
    (r"[Ii]n today's rapidly evolving\s+", "In the "),
    (r"[Ii]n the world of\s+", "In "),
    (r"[Ii]n the realm of\s+", "In "),
    (r"[Aa]t the end of the day,?\s*", ""),
    (r"[Ff]irst and foremost,?\s*", ""),
    (r"[Ww]hen it comes to\s+", "For "),
    # Puffery
    (r"\bgame-?changer\b", "shift"),
    (r"\bgroundbreaking\b", "new"),
    (r"\bcutting-?edge\b", "modern"),
    (r"\bparadigm shift\b", "change"),
    (r"\bunparalleled\b", "unusual"),
    (r"\bmultifaceted\b", "complex"),
    (r"\bleverage\b(?! (?:ratio|point))", "use"),
    (r"\butilize[sd]?\b", lambda m: "use" + ("d" if m.group().endswith("d") else "s" if m.group().endswith("s") else "")),
    # Transition filler
    (r"[Ii]n conclusion,?\s*", ""),
    (r"[Ii]n summary,?\s*", ""),
    (r"[Tt]o summarize,?\s*", ""),
    (r"\b[Mm]oreover,?\s+", ""),
    (r"\b[Ff]urthermore,?\s+", ""),
    (r"\b[Aa]dditionally,?\s+", "Also, "),
    (r"\b[Ss]ubsequently,?\s+", "Then, "),
    (r"\b[Nn]evertheless,?\s+", "Still, "),
    (r"\b[Nn]onetheless,?\s+", "Still, "),
    (r"\b[Hh]enceforth,?\s+", "From now on, "),
    # Sycophantic openers (line-start)
    (r"Great question!?\s*", "", 0),
    (r"That'?s a great point\.?\s*", "", 0),
    (r"Absolutely!?\s+", "", 0),
    (r"I'?d be happy to help[.!]?\s*", "", 0),
    (r"I'?m glad you asked[.!]?\s*", "", 0),
    (r"Excellent question!?\s*", "", 0),
    # Vocab swaps
    (r"\bcomprehensive\b", "full"),
    (r"\brobust\b", "solid"),
    (r"\bstreamline\b", "simplify"),
    (r"\binnovative\b", "new"),
    (r"\bseamless(?:ly)?\b", lambda m: "smoothly" if "ly" in m.group() else "smooth"),
    (r"\bcommence[sd]?\b", lambda m: "start" + m.group()[-1] if m.group()[-1] in "ds" else "start"),
    (r"\bnumerous\b", "many"),
    (r"\bsufficient\b", "enough"),
    (r"\bprior to\b", "before"),
    (r"\bin order to\b", "to"),
    (r"\bdue to the fact that\b", "because"),
    (r"\bat this point in time\b", "now"),
]

def kill_phrases(text):
    for pattern in DEAD_PHRASES:
        if len(pattern) == 3:
            text = re.sub(pattern[0], pattern[1], text, flags=pattern[2])
        elif callable(pattern[1]):
            text = re.sub(pattern[0], pattern[1], text)
        else:
            text = re.sub(pattern[0], pattern[1], text)
    # Clean up double spaces
    text = re.sub(r'  +', ' ', text)
    # Clean up space before punctuation
    text = re.sub(r' ([.,;:!?])', r'\1', text)
    # Capitalize after period if needed
    text = re.sub(r'\. ([a-z])', lambda m: '. ' + m.group(1).upper(), text)
    return text

def humanize(text, mode='clean'):
    if mode == 'preserve':
        text = fix_emdashes(text)
        # Only kill worst offenders
        for p in DEAD_PHRASES[:6]:  # First 6 are the worst
            if len(p) == 3:
                text = re.sub(p[0], p[1], text, flags=p[2])
            elif callable(p[1]):
                text = re.sub(p[0], p[1], text)
            else:
                text = re.sub(p[0], p[1], text)
        return text
    
    if mode == 'light':
        text = fix_emdashes(text)
        text = kill_phrases(text)
        return text
    
    # mode == 'clean' — full pass
    text = fix_emdashes(text)
    text = kill_phrases(text)
    return text

def main():
    parser = argparse.ArgumentParser(description='Humanize AI-generated text')
    parser.add_argument('input', help='Input file (- for stdin)')
    parser.add_argument('-o', '--output', help='Output file (default: stdout)')
    parser.add_argument('-m', '--mode', choices=['clean', 'light', 'preserve'], default='clean')
    args = parser.parse_args()
    
    if args.input == '-':
        text = sys.stdin.read()
    else:
        with open(args.input) as f:
            text = f.read()
    
    result = humanize(text, args.mode)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(result)
        print(f"Humanized ({args.mode}): {args.input} → {args.output}", file=sys.stderr)
    else:
        print(result)

if __name__ == '__main__':
    main()
