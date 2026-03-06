#!/usr/bin/env python3
"""
Guardian Update Checker
Checks ClawHub registry for new Guardian versions and notifies user.
"""
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

SKILL_DIR = Path(__file__).parent.parent
WORKSPACE = SKILL_DIR.parent.parent

def get_installed_version():
    """Read version from SKILL.md"""
    skill_md = SKILL_DIR / 'SKILL.md'
    if not skill_md.exists():
        return None
    
    for line in skill_md.read_text().splitlines():
        if line.startswith('version:'):
            return line.split(':', 1)[1].strip()
    return None

def get_latest_from_clawhub():
    """Check ClawHub registry for latest version"""
    try:
        result = subprocess.run(
            ['clawhub', 'inspect', 'guardian'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode != 0:
            return None, None
        
        latest = None
        for line in result.stdout.splitlines():
            if line.startswith('Latest:'):
                latest = line.split(':', 1)[1].strip()
                break
        
        return latest, result.stdout
    except Exception as e:
        print(f"Error checking ClawHub: {e}", file=sys.stderr)
        return None, None

def parse_changelog(inspect_output):
    """Extract changelog from clawhub inspect output (if available)"""
    # For now, just return placeholder - ClawHub inspect doesn't show changelog
    # Could fetch from README or releases API in future
    return "See https://clawhub.ai/skills/guardian for full changelog"

def main():
    installed = get_installed_version()
    if not installed:
        print("❌ Could not determine installed Guardian version", file=sys.stderr)
        sys.exit(1)
    
    latest, inspect_output = get_latest_from_clawhub()
    if not latest:
        print("⚠️  Could not check ClawHub for updates (network issue?)", file=sys.stderr)
        sys.exit(0)  # Don't fail, just skip this check
    
    if latest == installed:
        # Up to date - silent success
        print(f"✅ Guardian {installed} is up to date")
        sys.exit(0)
    
    # Update available - notify user
    changelog = parse_changelog(inspect_output)
    
    message = f"""🆕 **Guardian Update Available**

**Current:** v{installed}  
**Latest:** v{latest}

**What's new:**
{changelog}

**Update now:**
```
clawhub update guardian
```

Or auto-update with approval:
```
python3 skills/guardian/scripts/update.py
```

**Skip this version:**
```
python3 skills/guardian/scripts/check_updates.py --skip {latest}
```
"""
    
    print(message)
    
    # Also log to file for dashboard visibility
    updates_log = WORKSPACE / 'guardian-updates.json'
    updates_log.write_text(json.dumps({
        'checked_at': datetime.utcnow().isoformat() + 'Z',
        'installed': installed,
        'latest': latest,
        'update_available': True,
        'changelog_url': 'https://clawhub.ai/skills/guardian'
    }, indent=2))

def run_local_audit() -> None:
    """Run the local security audit pipeline alongside update check."""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "local_audit",
            Path(__file__).parent / "local_audit.py",
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.main()
    except Exception as e:
        print(f"Warning: local audit failed: {e}", file=sys.stderr)


if __name__ == '__main__':
    main()
    run_local_audit()
