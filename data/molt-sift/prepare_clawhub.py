#!/usr/bin/env python3
"""
Prepare molt-sift for ClawHub upload
Verifies package integrity and structure
"""

import json
import sys
from pathlib import Path


def check_package_structure():
    """Verify all required files exist."""
    root = Path(__file__).parent
    required_files = [
        "SKILL.md",
        "README.md",
        "setup.py",
        "manifest.json",
        "scripts/molt_sift.py",
        "scripts/sifter.py",
        "scripts/bounty_agent.py",
        "scripts/payaclaw_client.py",
        "scripts/solana_payment.py",
        "scripts/api_server.py",
    ]
    
    print("[*] Checking package structure...")
    missing = []
    for f in required_files:
        path = root / f
        if path.exists():
            print(f"  [OK] {f}")
        else:
            print(f"  [FAIL] {f} - MISSING")
            missing.append(f)
    
    return len(missing) == 0


def check_manifest():
    """Verify manifest.json is valid."""
    print("\n[*] Checking manifest.json...")
    try:
        with open("manifest.json", "r") as f:
            manifest = json.load(f)
        
        required_fields = ["name", "version", "description", "author"]
        for field in required_fields:
            if field in manifest:
                print(f"  [OK] {field}: {manifest[field]}")
            else:
                print(f"  [FAIL] Missing field: {field}")
                return False
        
        return True
    except Exception as e:
        print(f"  [FAIL] Invalid manifest.json: {e}")
        return False


def check_skill_md():
    """Verify SKILL.md exists and has required sections."""
    print("\n[*] Checking SKILL.md...")
    try:
        with open("SKILL.md", "r") as f:
            content = f.read()
        
        required_sections = [
            "name:",
            "description:",
            "Quick Start",
            "Features"
        ]
        
        for section in required_sections:
            if section in content:
                print(f"  [OK] Has '{section}'")
            else:
                print(f"  [WARN] Missing section: '{section}'")
        
        return True
    except Exception as e:
        print(f"  [FAIL] Error reading SKILL.md: {e}")
        return False


def check_readme():
    """Verify README.md exists."""
    print("\n[*] Checking README.md...")
    try:
        with open("README.md", "r") as f:
            content = f.read()
        
        if len(content) > 100:
            print(f"  [OK] README.md ({len(content)} bytes)")
            return True
        else:
            print(f"  [WARN] README.md seems short")
            return True
    except Exception as e:
        print(f"  [FAIL] Error reading README.md: {e}")
        return False


def main():
    """Run all checks."""
    print("=" * 60)
    print("Molt Sift - ClawHub Package Verification")
    print("=" * 60)
    
    checks = [
        ("Package Structure", check_package_structure),
        ("Manifest JSON", check_manifest),
        ("SKILL.md", check_skill_md),
        ("README.md", check_readme),
    ]
    
    results = []
    for name, check_fn in checks:
        try:
            result = check_fn()
            results.append((name, result))
        except Exception as e:
            print(f"\n[ERROR] {name}: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {name}")
    
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n[SUCCESS] Package is ready for ClawHub upload!")
        print("\nNext steps:")
        print("  1. Create ZIP package")
        print("  2. Upload to https://clawhub.com")
        print("  3. Set tags: validation, bounty, data-quality, solana")
        return 0
    else:
        print("\n[FAIL] Fix issues before uploading")
        return 1


if __name__ == "__main__":
    sys.exit(main())
