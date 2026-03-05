#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw Self-Healing Skill V2.0 - Installer
"""
import os
import shutil
import json
from pathlib import Path


def install_skill():
    """Install the skill to OpenClaw skills directory"""
    
    # Paths
    source_dir = Path.home() / ".iflow" / "memory" / "openclaw"
    skill_dir = Path.home() / ".openclaw" / "skills" / "openclaw-iflow-doctor"
    
    print("=" * 60)
    print("OpenClaw Self-Healing Skill V2.0 - Installer")
    print("=" * 60)
    print()
    
    # Check if source exists
    if not source_dir.exists():
        print(f"Error: Source directory not found: {source_dir}")
        print("Please ensure the skill files are in ~/.iflow/memory/openclaw/")
        return False
    
    # Create skill directory
    print("Step 1: Creating skill directory...")
    skill_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy files
    print("Step 2: Copying skill files...")
    files_to_copy = [
        ("skill.md", "skill.md"),
        ("openclaw_memory.py", "openclaw_memory.py"),
        ("cases.json", "cases.json"),
        ("config.json", "config.json"),
    ]
    
    for src_name, dst_name in files_to_copy:
        src = source_dir / src_name
        dst = skill_dir / dst_name
        if src.exists():
            shutil.copy2(src, dst)
            print(f"  ✓ {src_name}")
        else:
            print(f"  ✗ {src_name} not found")
    
    # Create records.json if not exists
    print("Step 3: Creating records.json...")
    records_file = skill_dir / "records.json"
    if not records_file.exists():
        records_data = {
            "version": "1.0",
            "last_updated": "2026-02-27",
            "records": []
        }
        with open(records_file, 'w', encoding='utf-8') as f:
            json.dump(records_data, f, ensure_ascii=False, indent=2)
        print("  ✓ records.json created")
    else:
        print("  ✓ records.json already exists")
    
    # Create symlink or update working directory reference
    print("Step 4: Creating launcher script...")
    launcher = skill_dir / "heal.bat"
    with open(launcher, 'w', encoding='utf-8') as f:
        f.write('@echo off\n')
        f.write(f'cd /d "{skill_dir}"\n')
        f.write('python openclaw_memory.py %*\n')
    print("  ✓ heal.bat created")
    
    print()
    print("=" * 60)
    print("Installation completed!")
    print("=" * 60)
    print()
    print(f"Skill location: {skill_dir}")
    print()
    print("Usage:")
    print("  1. Auto-trigger: The skill activates on OpenClaw errors")
    print("  2. Manual run:   Double-click heal.bat")
    print("  3. CLI:          python heal.py --fix \"error description\"")
    print()
    print("Note: To integrate with OpenClaw gateway, add to your openclaw.json:")
    print('  "skills": [')
    print('    "~/.openclaw/skills/openclaw-iflow-doctor/skill.md"')
    print('  ]')
    print()
    
    return True


def create_cli_wrapper():
    """Create a CLI wrapper in .iflow directory"""
    iflow_dir = Path.home() / ".iflow" / "bin"
    iflow_dir.mkdir(parents=True, exist_ok=True)
    
    # Create heal.bat
    heal_bat = iflow_dir / "heal.bat"
    with open(heal_bat, 'w', encoding='utf-8') as f:
        f.write('@echo off\n')
        f.write('python "%USERPROFILE%\\.iflow\\memory\\openclaw\\openclaw_memory.py" %*\n')
    
    print(f"CLI wrapper created: {heal_bat}")
    print("You can now use: heal --fix \"error description\"")
    print()


if __name__ == "__main__":
    if install_skill():
        create_cli_wrapper()
        print("Installation successful! ✓")
    else:
        print("Installation failed! ✗")
        exit(1)
