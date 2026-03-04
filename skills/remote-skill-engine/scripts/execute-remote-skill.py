#!/usr/bin/env python3
"""Execute a remote skill directly without downloading."""
import sys
import urllib.request
import ssl
import tempfile
import os
import subprocess

def fetch_and_execute_skill(skill_url, command):
    """Fetch SKILL.md and execute a command using the skill's instructions."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    try:
        # Fetch SKILL.md
        req = urllib.request.Request(
            skill_url,
            headers={'User-Agent': 'Mozilla/5.0 RemoteSkillEngine/1.0'}
        )
        
        with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
            skill_content = response.read().decode('utf-8')
        
        # Create temporary directory for skill
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_file = os.path.join(tmpdir, 'SKILL.md')
            with open(skill_file, 'w') as f:
                f.write(skill_content)
            
            print(f"📦 Loaded skill from: {skill_url}")
            print(f"📄 Skill size: {len(skill_content)} bytes")
            print(f"🔧 Ready to execute: {command}")
            print("")
            print("=" * 60)
            print("SKILL LOADED - Following instructions:")
            print("=" * 60)
            
            # Display key sections (first 2000 chars for context)
            print(skill_content[:2000])
            if len(skill_content) > 2000:
                print("\n... [skill continues]")
            
            print("")
            print("=" * 60)
            print("To use this skill, follow the instructions in SKILL.md above")
            print("or execute specific commands/scripts from the skill's scripts/")
            print("=" * 60)
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: execute-remote-skill.py <skill-url> [command]")
        print("Example: execute-remote-skill.py https://raw.githubusercontent.com/user/repo/SKILL.md 'run security scan'")
        sys.exit(1)
    
    skill_url = sys.argv[1]
    command = sys.argv[2] if len(sys.argv) > 2 else ""
    
    success = fetch_and_execute_skill(skill_url, command)
    sys.exit(0 if success else 1)
