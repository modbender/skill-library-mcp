#!/usr/bin/env python3
"""Cache a remote skill locally so it works like an installed skill."""
import sys
import os
import urllib.request
import ssl
import json
import subprocess
from pathlib import Path

CACHE_DIR = Path.home() / ".openclaw" / "workspace" / "remote-skills-cache"
SKILLS_DIR = Path.home() / ".openclaw" / "workspace" / "skills"

def parse_source(source):
    """Parse source URL into components."""
    if source.startswith("clawhub://"):
        skill_name = source.replace("clawhub://", "")
        return {
            "type": "clawhub",
            "name": skill_name,
            "url": None
        }
    elif source.startswith("github://"):
        parts = source.replace("github://", "").split("/")
        if len(parts) >= 3:
            return {
                "type": "github",
                "owner": parts[0],
                "repo": parts[1],
                "branch": parts[2] if len(parts) > 2 else "main",
                "path": "/".join(parts[3:]) if len(parts) > 3 else ""
            }
    elif source.startswith("http"):
        return {
            "type": "direct",
            "url": source
        }
    return None

def fetch_skill_metadata(skill_name):
    """Fetch skill metadata from ClawHub."""
    try:
        result = subprocess.run(
            ["clawhub", "search", skill_name, "--limit", "1"],
            capture_output=True,
            text=True
        )
        return result.stdout
    except Exception as e:
        print(f"⚠️  Warning: Could not fetch metadata: {e}")
        return None

def download_file(url, dest_path):
    """Download a file from URL."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 RemoteSkillEngine/1.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
            with open(dest_path, 'wb') as f:
                f.write(response.read())
        return True
    except Exception as e:
        print(f"❌ Failed to download {url}: {e}")
        return False

def cache_skill(skill_name, source_url):
    """Cache a skill from remote source."""
    print(f"🔄 Caching skill: {skill_name}")
    print(f"📍 Source: {source_url}")
    print("")
    
    # Create cache directory
    cache_path = CACHE_DIR / skill_name
    cache_path.mkdir(parents=True, exist_ok=True)
    
    scripts_dir = cache_path / "scripts"
    refs_dir = cache_path / "references"
    assets_dir = cache_path / "assets"
    
    scripts_dir.mkdir(exist_ok=True)
    refs_dir.mkdir(exist_ok=True)
    assets_dir.mkdir(exist_ok=True)
    
    # Parse source
    parsed = parse_source(source_url)
    if not parsed:
        print(f"❌ Invalid source format: {source_url}")
        return False
    
    skill_url = None
    
    if parsed["type"] == "clawhub":
        # Search ClawHub to get actual repo URL
        print("🔍 Searching ClawHub for skill info...")
        result = subprocess.run(
            ["clawhub", "search", skill_name, "--limit", "1"],
            capture_output=True,
            text=True
        )
        # Parse output to get skill name/version
        lines = result.stdout.strip().split('\n')
        for line in lines:
            if skill_name in line.lower():
                print(f"✅ Found: {line}")
                break
        
        # Try to install temporarily to get files, or fetch from known patterns
        print("📥 Attempting to fetch SKILL.md...")
        
        # Common raw URL patterns for ClawHub skills
        possible_urls = [
            f"https://raw.githubusercontent.com/openclaw/{skill_name.replace('-skill', '')}/main/SKILL.md",
            f"https://raw.githubusercontent.com/openclaw/{skill_name}/main/SKILL.md",
            f"https://raw.githubusercontent.com/clawhub/{skill_name}/main/SKILL.md",
        ]
        
        for url in possible_urls:
            print(f"  Trying: {url}")
            dest = cache_path / "SKILL.md"
            if download_file(url, dest):
                skill_url = url
                print(f"  ✅ Success!")
                break
            dest.unlink(miss_ok=True)
        
        if not skill_url:
            print("❌ Could not find SKILL.md from known patterns")
            print("💡 Try providing a direct GitHub URL instead")
            return False
    
    elif parsed["type"] == "github":
        base_url = f"https://raw.githubusercontent.com/{parsed['owner']}/{parsed['repo']}/{parsed['branch']}"
        skill_url = f"{base_url}/{parsed['path']}/SKILL.md" if parsed['path'] else f"{base_url}/SKILL.md"
        
        print(f"📥 Downloading from GitHub...")
        dest = cache_path / "SKILL.md"
        if not download_file(skill_url, dest):
            print("❌ Failed to download SKILL.md")
            return False
        print("✅ SKILL.md downloaded")
    
    elif parsed["type"] == "direct":
        skill_url = source_url
        dest = cache_path / "SKILL.md"
        if not download_file(skill_url, dest):
            print("❌ Failed to download SKILL.md")
            return False
        print("✅ SKILL.md downloaded")
    
    # Try to fetch common additional files
    if skill_url:
        base_url = skill_url.replace("/SKILL.md", "")
        
        # Fetch scripts
        print("📥 Checking for scripts...")
        common_scripts = ["fetch-skill.py", "compare-skills.py", "main.py", "run.py"]
        for script in common_scripts:
            url = f"{base_url}/scripts/{script}"
            dest = scripts_dir / script
            if download_file(url, dest):
                print(f"  ✅ Downloaded: scripts/{script}")
                os.chmod(dest, 0o755)
            else:
                dest.unlink(miss_ok=True)
        
        # Fetch references
        print("📥 Checking for references...")
        common_refs = ["README.md", "API.md", "GUIDE.md"]
        for ref in common_refs:
            url = f"{base_url}/references/{ref}"
            dest = refs_dir / ref
            if download_file(url, dest):
                print(f"  ✅ Downloaded: references/{ref}")
            else:
                dest.unlink(miss_ok=True)
    
    # Save metadata
    metadata = {
        "name": skill_name,
        "source": source_url,
        "cached_at": subprocess.run(["date", "-Iseconds"], capture_output=True, text=True).stdout.strip(),
        "skill_url": skill_url,
        "version": "cached"
    }
    
    with open(cache_path / "cache-metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # Create symlink in skills/ folder
    skills_symlink = SKILLS_DIR / skill_name
    if skills_symlink.exists() or skills_symlink.is_symlink():
        skills_symlink.unlink()
    
    skills_symlink.symlink_to(cache_path)
    print(f"🔗 Created symlink: {skills_symlink} -> {cache_path}")
    
    print("")
    print("=" * 60)
    print(f"✅ Skill '{skill_name}' cached successfully!")
    print(f"📂 Location: {cache_path}")
    print(f"🔗 Symlinked to: {skills_symlink}")
    print(f"🎯 Status: READY TO USE (works like installed skill)")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: cache-skill.py <skill-name> <source-url>")
        print("")
        print("Examples:")
        print("  cache-skill.py security-auditor clawhub://security-auditor")
        print("  cache-skill.py my-skill github://owner/repo/main")
        print("  cache-skill.py my-skill https://raw.githubusercontent.com/.../SKILL.md")
        sys.exit(1)
    
    skill_name = sys.argv[1]
    source_url = sys.argv[2]
    
    success = cache_skill(skill_name, source_url)
    sys.exit(0 if success else 1)
