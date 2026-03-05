#!/usr/bin/env python3
"""Fetch remote skill metadata without full download."""
import sys
import urllib.request
import ssl

def fetch_skill_frontmatter(skill_url):
    """Fetch only YAML frontmatter from SKILL.md"""
    try:
        # Handle SSL certificate verification
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        req = urllib.request.Request(
            skill_url,
            headers={'User-Agent': 'Mozilla/5.0 RemoteSkillEngine/1.0'}
        )
        
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            content = ""
            in_frontmatter = False
            frontmatter_lines = []
            
            for line in response:
                line = line.decode('utf-8').rstrip()
                
                if line == '---':
                    if not in_frontmatter:
                        in_frontmatter = True
                        continue
                    else:
                        # End of frontmatter
                        break
                
                if in_frontmatter:
                    frontmatter_lines.append(line)
            
            # Parse YAML manually (simple parser)
            metadata = {}
            current_key = None
            
            for line in frontmatter_lines:
                if ':' in line and not line.startswith(' ') and not line.startswith('#'):
                    key, _, value = line.partition(':')
                    key = key.strip()
                    value = value.strip()
                    metadata[key] = value
                    current_key = key
                elif line.startswith('  ') and current_key:
                    # Handle nested values (simple case)
                    if current_key in metadata:
                        if isinstance(metadata[current_key], str):
                            metadata[current_key] = [metadata[current_key]]
                        metadata[current_key].append(line.strip())
            
            return metadata
            
    except Exception as e:
        print(f"Error fetching skill: {e}", file=sys.stderr)
        return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: fetch-skill.py <skill-url>")
        print("Example: fetch-skill.py https://raw.githubusercontent.com/user/repo/SKILL.md")
        sys.exit(1)
    
    metadata = fetch_skill_frontmatter(sys.argv[1])
    
    if metadata:
        print(f"Name: {metadata.get('name', 'N/A')}")
        print(f"Description: {metadata.get('description', 'N/A')}")
        if 'metadata' in metadata:
            print(f"Metadata: {metadata['metadata']}")
    else:
        sys.exit(1)
