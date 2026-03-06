#!/usr/bin/env python3
"""Compare multiple remote skills side-by-side."""
import sys
import json

def compare_skills(skill_data_list):
    """Generate comparison table for skills"""
    print("\n### Skill Comparison\n")
    print("| Skill | Version | Description | Requirements |")
    print("|-------|---------|-------------|--------------|")
    
    for skill in skill_data_list:
        name = skill.get('name', 'N/A')
        version = skill.get('version', 'N/A')
        desc = skill.get('description', 'N/A')
        
        # Truncate description if too long
        if len(desc) > 60:
            desc = desc[:57] + '...'
        
        # Extract requirements if available
        reqs = 'None'
        if 'metadata' in skill:
            meta = skill['metadata']
            if 'openclaw' in meta and 'requires' in meta['openclaw']:
                bins = meta['openclaw']['requires'].get('bins', [])
                if bins:
                    reqs = ', '.join(bins)
        
        print(f"| {name} | {version} | {desc} | {reqs} |")
    
    print("\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Read from file
        try:
            with open(sys.argv[1], 'r') as f:
                skills = json.load(f)
            compare_skills(skills)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Read from stdin
        try:
            skills = json.load(sys.stdin)
            compare_skills(skills)
        except json.JSONDecodeError:
            print("Error: Invalid JSON input", file=sys.stderr)
            sys.exit(1)
