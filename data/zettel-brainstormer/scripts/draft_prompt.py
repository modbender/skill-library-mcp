#!/usr/bin/env python3
"""
Draft script: expand outline into a Markdown draft using a pro model.
Usage: draft.py --outline outline.json --out draft.md
"""
import sys
import json
import argparse
from pathlib import Path
from config_manager import ConfigManager

def read_json(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))

def generate_prompt(outline, templates_content=None):
    """
    Generate a prompt for an agent using the outline and context.
    """

    title = outline.get('headlines', ["Untitled"])[0]
    points = outline.get('points', [])
    linked_docs = outline.get('linked_docs', [])
    tag_similar = outline.get('tag_similar_docs', [])

    seen_paths = set()

    # Construct context from linked docs
    context_str = ""
    if linked_docs:
        context_str += "## Referenced Notes\n"
        for doc in linked_docs:
            path = doc.get('path', 'unknown')
            if path in seen_paths:
                continue
            seen_paths.add(path)

            # Simple truncation to avoid blowing up context
            content_snippet = doc.get('content', '')[:1000]
            context_str += f"### Note: {Path(path).stem}\n{content_snippet}\n...\n\n"

    if tag_similar:
        context_str += "## Related Ideas (Context)\n"
        for doc in tag_similar:
            path = doc.get('path', 'unknown')
            if path in seen_paths:
                continue
            seen_paths.add(path)

            content_snippet = doc.get('content', '')[:500]
            context_str += f"### Note: {Path(path).stem}\n{content_snippet}\n...\n\n"

    # Construct system prompt
    system_prompt = "You are an expert writer and researcher."
    if templates_content:
        system_prompt += f"\n\nUse the following templates and style guide:\n{templates_content}"

    system_prompt += """\n\nIMPORTANT:
1. Synthesize ALL relevant information from the context notes.
2. Follow the structure and formatting defined in the templates.
3. Your goal is a comprehensive, detailed draft that leaves no key insight behind."""

    # Construct user prompt
    user_prompt = f"""
    Please write a comprehensive draft based on the following outline and context.

    # Title: {title}

    # Key Points to Cover:
    {json.dumps(points, indent=2)}

    # Context Material:
    {context_str}

    Output Format: Markdown.
    """

    return f"# PROMPT FOR AGENT\n\n**System**:\n{system_prompt}\n\n**User**:\n{user_prompt}"

if __name__ == '__main__':
    # Load configuration
    config = ConfigManager.load()
    # default_model is no longer used for generation in this script

    p = argparse.ArgumentParser()
    p.add_argument('--outline', required=True)
    p.add_argument('--out')
    p.add_argument('--templates', help="Path to templates.md", default="references/templates.md")
    # Removed --model argument as it's not used by this script anymore
    args = p.parse_args()

    outline = read_json(args.outline)

    templates_content = None
    if args.templates and Path(args.templates).exists():
        templates_content = Path(args.templates).read_text(encoding='utf-8')

    prompt_content = generate_prompt(outline, templates_content)

    if args.out:
        Path(args.out).write_text(prompt_content, encoding='utf-8')
        print(f'Wrote prompt to file: {args.out}')
    else:
        print(prompt_content)
