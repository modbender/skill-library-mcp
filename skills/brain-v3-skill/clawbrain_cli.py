#!/usr/bin/env python3
"""
ClawBrain CLI - Command-line interface for ClawBrain installation and management

Commands:
    clawbrain setup           - Set up ClawBrain for ClawdBot/OpenClaw
    clawbrain generate-key    - Generate a new encryption key
    clawbrain show-key        - Display current encryption key
    clawbrain backup-key      - Backup encryption key with multiple options
    clawbrain migrate-secrets - Migrate unencrypted secrets to encrypted storage
    clawbrain health          - Check ClawBrain health status
    clawbrain info            - Show installation info
"""

import os
import sys
import json
import shutil
import argparse
import platform
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple

# Check for cryptography
try:
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


def get_config_dir() -> Path:
    """Get the ClawBrain config directory."""
    return Path.home() / ".config" / "clawbrain"


def get_key_path() -> Path:
    """Get the path to the encryption key file."""
    return get_config_dir() / ".brain_key"


def detect_platform() -> Tuple[str, Path, Path]:
    """
    Detect ClawdBot/OpenClaw platform and return paths.
    
    Returns:
        Tuple of (platform_name, config_dir, hooks_dir)
    """
    home = Path.home()
    
    # Check in order of preference
    if (home / ".openclaw").exists():
        return "openclaw", home / ".openclaw", home / ".openclaw" / "hooks"
    elif (home / ".clawdbot").exists():
        return "clawdbot", home / ".clawdbot", home / ".clawdbot" / "hooks"
    elif (home / "clawd").exists():
        return "clawdbot", home / ".clawdbot", home / ".clawdbot" / "hooks"
    else:
        return "unknown", Path(), Path()


def get_package_dir() -> Path:
    """Get the directory where the clawbrain package is installed."""
    import clawbrain
    return Path(clawbrain.__file__).parent


def get_hooks_dir() -> Path:
    """Get the directory where hooks are stored in the package."""
    # Hooks can be in several locations depending on how package was installed
    possible_locations = [
        get_package_dir().parent / "brain" / "hooks",  # Installed via pip (brain package)
        get_package_dir() / "hooks",                    # If clawbrain.py has hooks subdir
        get_package_dir().parent / "hooks",             # If hooks is sibling to clawbrain.py
        Path(__file__).parent / "hooks",                # Relative to CLI module
        Path(__file__).parent / "brain" / "hooks",      # brain/hooks relative to CLI
    ]
    
    for loc in possible_locations:
        if loc.exists() and (loc / "clawbrain-startup").exists():
            return loc
    
    # Return first option as default (may not exist)
    return possible_locations[0]


def get_scripts_dir() -> Path:
    """Get the directory where scripts are stored in the package."""
    possible_locations = [
        get_package_dir().parent / "brain" / "scripts",  # Installed via pip
        get_package_dir() / "scripts",
        get_package_dir().parent / "scripts",
        Path(__file__).parent / "scripts",
        Path(__file__).parent / "brain" / "scripts",
    ]
    
    for loc in possible_locations:
        if loc.exists() and (loc / "brain_bridge.py").exists():
            return loc
    
    return possible_locations[0]


def generate_encryption_key() -> bytes:
    """Generate a new Fernet encryption key."""
    if not CRYPTO_AVAILABLE:
        print("❌ cryptography library not installed!")
        print("   Install with: pip install clawbrain[encryption]")
        sys.exit(1)
    
    return Fernet.generate_key()


def save_key(key: bytes, path: Path) -> None:
    """Save encryption key to file with secure permissions."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(key)
    
    # Set restrictive permissions (Unix-like systems only)
    if platform.system() != "Windows":
        os.chmod(path, 0o600)


def load_key(path: Path) -> Optional[bytes]:
    """Load encryption key from file."""
    if path.exists():
        return path.read_bytes()
    return None


def print_key_info(key: bytes, show_full: bool = False) -> None:
    """Print information about an encryption key."""
    key_str = key.decode()
    
    if show_full:
        print(f"\n🔑 Encryption Key:")
        print(f"   {key_str}")
    else:
        # Show only first and last 8 characters
        masked = f"{key_str[:8]}...{key_str[-8:]}"
        print(f"\n🔑 Encryption Key (masked): {masked}")
    
    print(f"\n📋 Key Length: {len(key_str)} characters")
    print(f"📅 Generated: {datetime.now().isoformat()}")


def cmd_setup(args):
    """Set up ClawBrain for ClawdBot/OpenClaw."""
    print("🧠 ClawBrain Setup")
    print("=" * 40)
    
    # Detect platform
    platform_name, config_dir, hooks_dir = detect_platform()
    
    if platform_name == "unknown":
        print("\n⚠️  ClawdBot/OpenClaw not detected.")
        print("   ClawBrain can still be used as a Python library.")
        print("   For full integration, install ClawdBot or OpenClaw first.")
        
        if not args.force:
            response = input("\nContinue with basic setup? (y/N) ").strip().lower()
            if response != 'y':
                print("Setup cancelled.")
                return 1
    else:
        print(f"\n📍 Detected platform: {platform_name}")
        print(f"📁 Config directory: {config_dir}")
        print(f"📁 Hooks directory: {hooks_dir}")
    
    # Step 1: Generate encryption key
    print("\n📦 Step 1: Setting up encryption...")
    key_path = get_key_path()
    
    if key_path.exists() and not args.force:
        print(f"   ✅ Encryption key already exists at {key_path}")
        key = load_key(key_path)
    else:
        if CRYPTO_AVAILABLE:
            key = generate_encryption_key()
            save_key(key, key_path)
            print(f"   ✅ Generated new encryption key")
            print(f"   📁 Saved to: {key_path}")
            
            # Show key backup options
            print("\n   ⚠️  IMPORTANT: Backup your encryption key!")
            print("   Lost keys = lost encrypted data.")
            print(f"\n   Run 'clawbrain backup-key' to create a backup.")
        else:
            print("   ⚠️  cryptography not installed - encryption disabled")
            print("   Install with: pip install clawbrain[encryption]")
            key = None
    
    # Step 2: Install hooks (if platform detected)
    if platform_name != "unknown":
        print("\n📦 Step 2: Installing hooks...")
        
        try:
            hooks_src_dir = get_hooks_dir()
            hook_src = hooks_src_dir / "clawbrain-startup"
            hook_dst = hooks_dir / "clawbrain-startup"
            
            if hook_src.exists():
                hooks_dir.mkdir(parents=True, exist_ok=True)
                
                if hook_dst.exists():
                    shutil.rmtree(hook_dst)
                
                shutil.copytree(hook_src, hook_dst)
                print(f"   ✅ Installed hook: clawbrain-startup")
                print(f"   📁 Location: {hook_dst}")
            else:
                print(f"   ⚠️  Hook source not found at {hook_src}")
                print("   You may need to install hooks manually.")
                print(f"   Check: {hooks_src_dir}")
        except Exception as e:
            print(f"   ❌ Failed to install hooks: {e}")
    
    # Step 3: Test installation
    print("\n📦 Step 3: Testing installation...")
    unencrypted_count = 0
    try:
        from clawbrain import Brain
        brain = Brain()
        health = brain.health_check()
        
        if health.get("sqlite") or health.get("postgresql"):
            print("   ✅ ClawBrain is working!")
            print(f"   Storage: {brain.storage_backend}")
            
            # Check for unencrypted secrets
            if key and hasattr(brain, 'get_unencrypted_secrets'):
                try:
                    unencrypted = brain.get_unencrypted_secrets()
                    unencrypted_count = len(unencrypted)
                except Exception:
                    pass  # Ignore errors during check
        else:
            print("   ⚠️  Storage backend not available")
        
        brain.close()
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
    
    # Check for personality files
    personality_files_found = False
    if platform_name != "unknown":
        personality_files = ["SOUL.md", "IDENTITY.md", "USER.md", "MEMORY.md"]
        for pf in personality_files:
            if (config_dir / pf).exists():
                personality_files_found = True
                break
    
    # Summary
    print("\n" + "=" * 40)
    print("✅ Setup complete!")
    
    if platform_name != "unknown":
        service_name = platform_name
        print(f"\n🎉 Restart your service to activate:")
        print(f"   sudo systemctl restart {service_name}")
    
    if key:
        print(f"\n🔐 Encryption is enabled!")
        print(f"   Key location: {key_path}")
        print(f"   Run 'clawbrain backup-key' to backup your key.")
        
        # Alert about unencrypted secrets
        if unencrypted_count > 0:
            print(f"\n⚠️  Found {unencrypted_count} existing unencrypted secret(s)!")
            print("   These were stored before encryption was enabled.")
            print("   Run 'clawbrain migrate-secrets' to encrypt them.")
    
    # Suggest personality import
    if personality_files_found:
        print(f"\n📄 Found OpenClaw personality files!")
        print("   Import them to seed ClawBrain's memory:")
        print("   clawbrain import-personality")
    
    print("\n📚 Documentation: https://github.com/clawcolab/clawbrain")
    
    return 0


def cmd_generate_key(args):
    """Generate a new encryption key."""
    print("🔑 Generating Encryption Key")
    print("=" * 40)
    
    key_path = get_key_path()
    
    if key_path.exists() and not args.force:
        print(f"\n⚠️  An encryption key already exists at {key_path}")
        print("   Generating a new key will NOT affect existing encrypted data.")
        print("   You'll need to keep the old key to decrypt old data.")
        
        response = input("\nGenerate a new key anyway? (y/N) ").strip().lower()
        if response != 'y':
            print("Cancelled.")
            return 1
        
        # Backup old key
        backup_path = key_path.with_suffix(f".backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        shutil.copy(key_path, backup_path)
        print(f"\n📁 Old key backed up to: {backup_path}")
    
    # Generate new key
    key = generate_encryption_key()
    save_key(key, key_path)
    
    print(f"\n✅ New encryption key generated!")
    print_key_info(key, show_full=args.show)
    
    print(f"\n📁 Saved to: {key_path}")
    print("\n⚠️  IMPORTANT: Run 'clawbrain backup-key' to backup this key!")
    
    return 0


def cmd_show_key(args):
    """Display the current encryption key."""
    print("🔑 Current Encryption Key")
    print("=" * 40)
    
    key_path = get_key_path()
    
    if not key_path.exists():
        print("\n❌ No encryption key found!")
        print("   Run 'clawbrain setup' or 'clawbrain generate-key' first.")
        return 1
    
    key = load_key(key_path)
    print_key_info(key, show_full=args.full)
    
    print(f"\n📁 Key location: {key_path}")
    
    if args.full:
        print("\n⚠️  Keep this key secret! Anyone with this key can decrypt your data.")
    
    return 0


def cmd_backup_key(args):
    """Backup the encryption key with multiple options."""
    print("💾 Backup Encryption Key")
    print("=" * 40)
    
    key_path = get_key_path()
    
    if not key_path.exists():
        print("\n❌ No encryption key found!")
        print("   Run 'clawbrain setup' or 'clawbrain generate-key' first.")
        return 1
    
    key = load_key(key_path)
    key_str = key.decode()
    
    backup_methods = []
    
    # Method 1: File backup
    if args.output or args.all:
        backup_path = Path(args.output) if args.output else Path.home() / "clawbrain_key_backup.txt"
        
        backup_content = f"""ClawBrain Encryption Key Backup
================================
Generated: {datetime.now().isoformat()}
Key: {key_str}

IMPORTANT:
- Store this file in a secure location (encrypted drive, password manager, etc.)
- Delete this file after storing the key safely
- Lost keys = lost encrypted data
- Do not share this key with anyone

To restore:
1. Copy the key above
2. Set environment variable: export BRAIN_ENCRYPTION_KEY="{key_str}"
   OR
3. Save to: {key_path}
"""
        backup_path.write_text(backup_content)
        
        # Set restrictive permissions
        if platform.system() != "Windows":
            os.chmod(backup_path, 0o600)
        
        print(f"\n✅ Key backed up to file: {backup_path}")
        backup_methods.append("file")
    
    # Method 2: Display as QR code (if qrcode library available)
    if args.qr or args.all:
        try:
            import qrcode
            from io import StringIO
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=1,
                border=1,
            )
            qr.add_data(key_str)
            qr.make(fit=True)
            
            # Print QR code as ASCII
            print("\n📱 QR Code (scan with phone):")
            print("-" * 40)
            
            f = StringIO()
            qr.print_ascii(out=f)
            f.seek(0)
            print(f.read())
            print("-" * 40)
            print("Scan this QR code with your phone's camera to backup the key.")
            
            backup_methods.append("qr")
        except ImportError:
            if args.qr:  # Only warn if explicitly requested
                print("\n⚠️  QR code requires qrcode library:")
                print("   pip install qrcode")
    
    # Method 3: Copy to clipboard
    if args.clipboard or args.all:
        try:
            import pyperclip
            pyperclip.copy(key_str)
            print("\n✅ Key copied to clipboard!")
            print("   Paste it into your password manager or secure notes.")
            backup_methods.append("clipboard")
        except ImportError:
            if args.clipboard:  # Only warn if explicitly requested
                print("\n⚠️  Clipboard copy requires pyperclip library:")
                print("   pip install pyperclip")
    
    # Method 4: Display the key
    if args.display or args.all or not backup_methods:
        print("\n🔑 Encryption Key:")
        print("-" * 40)
        print(key_str)
        print("-" * 40)
        print("\nCopy this key and store it securely:")
        print("  • Password manager (1Password, Bitwarden, etc.)")
        print("  • Encrypted notes app")
        print("  • Printed and stored in a safe")
        backup_methods.append("display")
    
    # Summary
    print("\n" + "=" * 40)
    print("✅ Backup complete!")
    print(f"   Methods used: {', '.join(backup_methods)}")
    print("\n⚠️  IMPORTANT:")
    print("   • Store backup in a secure location")
    print("   • Delete temporary files after securing the key")
    print("   • Lost keys = lost encrypted data")
    
    return 0


def cmd_health(args):
    """Check ClawBrain health status."""
    print("🏥 ClawBrain Health Check")
    print("=" * 40)
    
    try:
        from clawbrain import Brain
        
        brain = Brain()
        health = brain.health_check()
        
        print(f"\n📦 Storage Backend: {brain.storage_backend}")
        print(f"🔐 Encryption: {'Enabled' if brain._cipher else 'Disabled'}")
        
        print("\n📊 Backend Status:")
        for backend, status in health.items():
            icon = "✅" if status else "❌"
            print(f"   {icon} {backend}: {'Available' if status else 'Not available'}")
        
        brain.close()
        print("\n✅ ClawBrain is healthy!")
        return 0
        
    except Exception as e:
        print(f"\n❌ Health check failed: {e}")
        return 1


def cmd_info(args):
    """Show installation information."""
    print("ℹ️  ClawBrain Information")
    print("=" * 40)
    
    try:
        import clawbrain
        print(f"\n📦 Version: {getattr(clawbrain, '__version__', 'unknown')}")
        print(f"📁 Package Location: {get_package_dir()}")
    except ImportError:
        print("\n❌ ClawBrain not installed!")
        return 1
    
    print(f"\n🔧 Configuration:")
    print(f"   Config Dir: {get_config_dir()}")
    print(f"   Key Path: {get_key_path()}")
    print(f"   Key Exists: {'Yes' if get_key_path().exists() else 'No'}")
    
    platform_name, config_dir, hooks_dir = detect_platform()
    print(f"\n🖥️  Platform:")
    print(f"   Detected: {platform_name}")
    if platform_name != "unknown":
        print(f"   Config Dir: {config_dir}")
        print(f"   Hooks Dir: {hooks_dir}")
    
    print(f"\n🐍 Python:")
    print(f"   Version: {sys.version}")
    print(f"   Executable: {sys.executable}")
    
    print(f"\n📚 Optional Dependencies:")
    deps = [
        ("cryptography", "Encryption"),
        ("psycopg2", "PostgreSQL"),
        ("redis", "Redis Cache"),
        ("sentence_transformers", "Semantic Search"),
        ("qrcode", "QR Code Backup"),
        ("pyperclip", "Clipboard Copy"),
    ]
    
    for module, desc in deps:
        try:
            __import__(module)
            print(f"   ✅ {desc} ({module})")
        except ImportError:
            print(f"   ❌ {desc} ({module})")
    
    return 0


def cmd_migrate_secrets(args):
    """Migrate unencrypted secrets to encrypted storage."""
    print("🔐 ClawBrain Secret Migration")
    print("=" * 40)
    
    # Check for encryption key
    key_path = get_key_path()
    if not key_path.exists():
        print("\n❌ No encryption key found!")
        print("   Run 'clawbrain setup' or 'clawbrain generate-key' first.")
        return 1
    
    try:
        from brain.clawbrain import Brain
    except ImportError:
        try:
            from clawbrain import Brain
        except ImportError:
            print("\n❌ Cannot import Brain class!")
            return 1
    
    # Set up environment for encryption
    os.environ.setdefault("BRAIN_ENCRYPTION_KEY", key_path.read_text().strip())
    
    try:
        brain = Brain()
        
        if args.dry_run:
            print("\n🔍 Dry run - checking for unencrypted secrets...")
            result = brain.migrate_secrets(dry_run=True)
            
            if result["count"] == 0:
                print("\n✅ No unencrypted secrets found! All secrets are already encrypted.")
                return 0
            
            print(f"\n⚠️  Found {result['count']} unencrypted secret(s):")
            for secret in result.get("secrets", []):
                print(f"   • ID: {secret['id'][:8]}... | Agent: {secret.get('agent_id', 'N/A')}")
            
            print(f"\n💡 Run 'clawbrain migrate-secrets' (without --dry-run) to encrypt them.")
            return 0
        
        # Confirm migration
        if not args.force:
            print("\n⚠️  This will encrypt all unencrypted secrets in the database.")
            print("   Make sure you have backed up your encryption key!")
            response = input("\n   Proceed? [y/N]: ").strip().lower()
            if response not in ("y", "yes"):
                print("\n❌ Migration cancelled.")
                return 1
        
        print("\n🔄 Migrating secrets...")
        result = brain.migrate_secrets(dry_run=False)
        
        if result.get("count", 0) == 0:
            print("\n✅ No unencrypted secrets found! Nothing to migrate.")
            return 0
        
        if result.get("success"):
            print(f"\n✅ Successfully migrated {result['migrated']} secret(s)!")
        else:
            print(f"\n⚠️  Migration completed with issues:")
            print(f"   Migrated: {result['migrated']}")
            print(f"   Failed: {result['failed']}")
            if result.get("errors"):
                for err in result["errors"]:
                    print(f"   • Error: {err['error']}")
        
        print("\n⚠️  Important: Your encryption key is critical for accessing these secrets!")
        print(f"   Key location: {key_path}")
        print("   Run 'clawbrain backup-key --all' to create backups.")
        
        return 0 if result.get("success") else 1
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        return 1


def parse_personality_file(filepath: Path) -> dict:
    """
    Parse an OpenClaw personality file (SOUL.md, IDENTITY.md, USER.md, MEMORY.md).
    
    Returns dict with:
        - title: The file type (e.g., "SOUL", "IDENTITY")
        - content: Full file content
        - sections: Dict of section_name -> section_content
    """
    if not filepath.exists():
        return None
    
    content = filepath.read_text(encoding="utf-8")
    title = filepath.stem  # SOUL, IDENTITY, USER, MEMORY
    
    # Parse sections (## headers)
    sections = {}
    current_section = "main"
    current_content = []
    
    for line in content.split("\n"):
        if line.startswith("## "):
            # Save previous section
            if current_content:
                sections[current_section] = "\n".join(current_content).strip()
            current_section = line[3:].strip()
            current_content = []
        else:
            current_content.append(line)
    
    # Save last section
    if current_content:
        sections[current_section] = "\n".join(current_content).strip()
    
    return {
        "title": title,
        "filename": filepath.name,
        "content": content,
        "sections": sections
    }


def cmd_import_personality(args):
    """Import OpenClaw personality files into ClawBrain memories."""
    print("📥 Import OpenClaw Personality Files")
    print("=" * 40)
    
    # Detect or use provided path
    if args.path:
        base_path = Path(args.path)
        if not base_path.exists():
            print(f"\n❌ Path not found: {args.path}")
            return 1
    else:
        platform_name, config_dir, _ = detect_platform()
        if platform_name == "unknown":
            print("\n❌ OpenClaw/ClawdBot not detected.")
            print("   Use --path to specify the directory containing personality files.")
            return 1
        base_path = config_dir
        print(f"\n📍 Detected: {platform_name}")
        print(f"📁 Looking in: {base_path}")
    
    # Personality files to import
    personality_files = ["SOUL.md", "IDENTITY.md", "USER.md", "MEMORY.md"]
    found_files = []
    
    print("\n🔍 Scanning for personality files...")
    
    for filename in personality_files:
        filepath = base_path / filename
        if filepath.exists():
            parsed = parse_personality_file(filepath)
            if parsed:
                found_files.append(parsed)
                print(f"   ✅ Found: {filename}")
        else:
            print(f"   ⚠️  Not found: {filename}")
    
    if not found_files:
        print("\n❌ No personality files found!")
        return 1
    
    print(f"\n📋 Found {len(found_files)} personality file(s)")
    
    # Show what will be imported
    for pf in found_files:
        print(f"\n   📄 {pf['filename']}")
        if pf['sections']:
            for section_name in list(pf['sections'].keys())[:5]:
                content_preview = pf['sections'][section_name][:50].replace('\n', ' ')
                print(f"      • {section_name}: {content_preview}...")
    
    if args.dry_run:
        print("\n🔍 Dry run - no changes made.")
        return 0
    
    # Import into ClawBrain
    print("\n📦 Importing into ClawBrain...")
    
    try:
        from clawbrain import Brain
        brain = Brain(agent_id=args.agent)
        
        imported_count = 0
        skipped_count = 0
        
        # File type to memory type mapping
        type_mapping = {
            "SOUL": "core_identity",
            "IDENTITY": "personality", 
            "USER": "user_profile",
            "MEMORY": "long_term_memory"
        }
        
        for pf in found_files:
            file_type = pf['title'].upper()
            memory_type = type_mapping.get(file_type, "personality")
            
            # Check if already imported (look for matching memory)
            if not args.force:
                existing = brain.recall(
                    query=f"OpenClaw {file_type} personality file",
                    limit=1,
                    memory_type=memory_type
                )
                if existing and len(existing) > 0:
                    # Check if it's our import marker
                    for mem in existing:
                        if hasattr(mem, 'metadata') and mem.metadata:
                            meta = mem.metadata if isinstance(mem.metadata, dict) else {}
                            if meta.get("source") == f"openclaw_{file_type.lower()}":
                                print(f"   ⏭️  Skipping {pf['filename']} (already imported)")
                                skipped_count += 1
                                continue
            
            # Store the full content as a memory
            memory_id = brain.remember(
                content=pf['content'],
                memory_type=memory_type,
                metadata={
                    "source": f"openclaw_{file_type.lower()}",
                    "filename": pf['filename'],
                    "imported_at": datetime.now().isoformat(),
                    "sections": list(pf['sections'].keys())
                }
            )
            
            if memory_id:
                print(f"   ✅ Imported {pf['filename']} → {memory_type} (ID: {memory_id[:8]}...)")
                imported_count += 1
            else:
                print(f"   ❌ Failed to import {pf['filename']}")
        
        brain.close()
        
        # Summary
        print("\n" + "=" * 40)
        print(f"✅ Import complete!")
        print(f"   Imported: {imported_count}")
        print(f"   Skipped:  {skipped_count}")
        print(f"   Agent ID: {args.agent}")
        
        print("\n💡 Use these memories in your agent:")
        print("   brain.recall('core identity', memory_type='core_identity')")
        print("   brain.recall('user preferences', memory_type='user_profile')")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="clawbrain",
        description="ClawBrain - Personal AI Memory System CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  clawbrain setup                    # Set up ClawBrain
  clawbrain generate-key             # Generate new encryption key
  clawbrain backup-key --all         # Backup key with all methods
  clawbrain migrate-secrets --dry-run  # Check for unencrypted secrets
  clawbrain health                   # Check health status

Documentation: https://github.com/clawcolab/clawbrain
        """
    )
    
    parser.add_argument("--version", action="version", version="ClawBrain 0.1.10")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # setup command
    setup_parser = subparsers.add_parser("setup", help="Set up ClawBrain for ClawdBot/OpenClaw")
    setup_parser.add_argument("--force", "-f", action="store_true", help="Force setup even if already configured")
    setup_parser.set_defaults(func=cmd_setup)
    
    # generate-key command
    genkey_parser = subparsers.add_parser("generate-key", help="Generate a new encryption key")
    genkey_parser.add_argument("--force", "-f", action="store_true", help="Force generate even if key exists")
    genkey_parser.add_argument("--show", "-s", action="store_true", help="Show full key after generation")
    genkey_parser.set_defaults(func=cmd_generate_key)
    
    # show-key command
    showkey_parser = subparsers.add_parser("show-key", help="Display current encryption key")
    showkey_parser.add_argument("--full", "-f", action="store_true", help="Show full key (unmasked)")
    showkey_parser.set_defaults(func=cmd_show_key)
    
    # backup-key command
    backup_parser = subparsers.add_parser("backup-key", help="Backup encryption key")
    backup_parser.add_argument("--output", "-o", help="Output file path for backup")
    backup_parser.add_argument("--qr", action="store_true", help="Display as QR code")
    backup_parser.add_argument("--clipboard", "-c", action="store_true", help="Copy to clipboard")
    backup_parser.add_argument("--display", "-d", action="store_true", help="Display key on screen")
    backup_parser.add_argument("--all", "-a", action="store_true", help="Use all backup methods")
    backup_parser.set_defaults(func=cmd_backup_key)
    
    # health command
    health_parser = subparsers.add_parser("health", help="Check ClawBrain health status")
    health_parser.set_defaults(func=cmd_health)
    
    # info command
    info_parser = subparsers.add_parser("info", help="Show installation info")
    info_parser.set_defaults(func=cmd_info)
    
    # migrate-secrets command
    migrate_parser = subparsers.add_parser("migrate-secrets", help="Migrate unencrypted secrets to encrypted storage")
    migrate_parser.add_argument("--dry-run", action="store_true", help="Show what would be migrated without making changes")
    migrate_parser.add_argument("--force", "-f", action="store_true", help="Skip confirmation prompt")
    migrate_parser.set_defaults(func=cmd_migrate_secrets)
    
    # import-personality command
    import_parser = subparsers.add_parser("import-personality", help="Import OpenClaw personality files (SOUL.md, IDENTITY.md, USER.md, MEMORY.md)")
    import_parser.add_argument("--path", "-p", help="Path to OpenClaw directory (auto-detected if not specified)")
    import_parser.add_argument("--agent", "-a", default="default", help="Agent ID to store memories under (default: 'default')")
    import_parser.add_argument("--dry-run", action="store_true", help="Show what would be imported without making changes")
    import_parser.add_argument("--force", "-f", action="store_true", help="Re-import even if already imported")
    import_parser.set_defaults(func=cmd_import_personality)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return 0
    
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
