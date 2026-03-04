#!/usr/bin/env python3
"""
OpenClaw Memory Configuration Script
===================================

Configures OpenClaw to automatically index all critical workspace files
in its built-in memory system, ensuring mandatory memory recall.

This script adds the missing memorySearch configuration that makes
OpenClaw's memory system comprehensive and prevents directive violations.

Usage:
    python scripts/configure_openclaw.py [--dry-run] [--backup]

Requirements:
    - OpenClaw 2026.2.17 or later
    - Write access to OpenClaw configuration

Author: Jakebot (2026-02-19)
Issue: Missing OpenClaw memorySearch configuration causes directive violations
"""

import json
import os
import sys
import subprocess
import argparse
from datetime import datetime
import shutil

def get_openclaw_config_path():
    """Find OpenClaw configuration file location."""
    possible_paths = [
        os.path.expanduser("~/.openclaw/openclaw.json"),
        os.path.expanduser("~/.openclaw/config.json"),
        "./openclaw.json"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

def backup_config(config_path):
    """Create a timestamped backup of the current configuration."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{config_path}.backup_{timestamp}"
    shutil.copy2(config_path, backup_path)
    print(f"✅ Configuration backed up to: {backup_path}")
    return backup_path

def get_memory_search_config():
    """Return the complete memorySearch configuration block."""
    return {
        "enabled": True,
        "sources": ["memory", "sessions"],
        "extraPaths": [
            "SOUL.md",
            "AGENTS.md", 
            "HEARTBEAT.md",
            "PROJECTS.md",
            "TOOLS.md",
            "IDENTITY.md",
            "USER.md",
            "reference/",
            "ARCHITECTURE.md"
        ],
        "experimental": {
            "sessionMemory": True
        },
        "chunking": {
            "maxChunkSize": 2048,
            "overlap": 200
        },
        "provider": "local",
        "sync": {
            "onSessionStart": True,
            "onSearch": True,
            "watch": True
        }
    }

def apply_memory_config(config_path, dry_run=False):
    """Apply memory search configuration to OpenClaw config."""
    try:
        # Load current configuration
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Check if memorySearch already exists
        memory_config = get_memory_search_config()
        
        if 'agents' not in config:
            config['agents'] = {}
        
        if 'defaults' not in config['agents']:
            config['agents']['defaults'] = {}
        
        # Add or update memorySearch configuration
        existing_memory = config['agents']['defaults'].get('memorySearch', {})
        
        if existing_memory:
            print(f"⚠️  memorySearch configuration already exists")
            print(f"   Current extraPaths: {existing_memory.get('extraPaths', [])}")
            
            # Merge configurations - add any missing extraPaths
            current_paths = set(existing_memory.get('extraPaths', []))
            new_paths = set(memory_config['extraPaths'])
            missing_paths = new_paths - current_paths
            
            if missing_paths:
                existing_memory['extraPaths'] = existing_memory.get('extraPaths', [])
                existing_memory['extraPaths'].extend(list(missing_paths))
                print(f"➕ Adding missing paths: {list(missing_paths)}")
            else:
                print(f"✅ All critical files already in extraPaths")
                return False
        else:
            print(f"➕ Adding complete memorySearch configuration")
            config['agents']['defaults']['memorySearch'] = memory_config
        
        if dry_run:
            print(f"\n🔍 DRY RUN - Configuration changes:")
            print(json.dumps(config['agents']['defaults']['memorySearch'], indent=2))
            return False
        
        # Write updated configuration
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ OpenClaw configuration updated successfully")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing configuration file: {e}")
        return False
    except Exception as e:
        print(f"❌ Error updating configuration: {e}")
        return False

def restart_openclaw():
    """Restart OpenClaw to apply configuration changes."""
    try:
        result = subprocess.run(['openclaw', 'gateway', 'restart'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ OpenClaw restarted successfully")
            return True
        else:
            print(f"⚠️  OpenClaw restart command returned code {result.returncode}")
            print(f"   stdout: {result.stdout}")
            print(f"   stderr: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️  OpenClaw restart timed out (30s)")
        return False
    except FileNotFoundError:
        print("⚠️  'openclaw' command not found - restart manually")
        return False
    except Exception as e:
        print(f"⚠️  Error restarting OpenClaw: {e}")
        return False

def verify_configuration():
    """Verify the configuration was applied correctly."""
    try:
        # Use OpenClaw CLI to check configuration
        result = subprocess.run(['openclaw', 'config', 'get'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            try:
                config = json.loads(result.stdout)
                memory_search = config.get('agents', {}).get('defaults', {}).get('memorySearch', {})
                
                if memory_search.get('enabled'):
                    extra_paths = memory_search.get('extraPaths', [])
                    required_paths = get_memory_search_config()['extraPaths']
                    missing_paths = set(required_paths) - set(extra_paths)
                    
                    if not missing_paths:
                        print("✅ Configuration verification successful")
                        print(f"   memorySearch enabled with {len(extra_paths)} extraPaths")
                        return True
                    else:
                        print(f"⚠️  Configuration incomplete - missing paths: {list(missing_paths)}")
                        return False
                else:
                    print("❌ memorySearch not enabled in active configuration")
                    return False
                    
            except json.JSONDecodeError:
                print("⚠️  Could not parse OpenClaw configuration output")
                return False
        else:
            print("⚠️  Could not retrieve OpenClaw configuration for verification")
            return False
            
    except Exception as e:
        print(f"⚠️  Configuration verification failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Configure OpenClaw memory system integration')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be changed without making modifications')
    parser.add_argument('--backup', action='store_true', default=True,
                       help='Create backup before making changes (default: True)')
    parser.add_argument('--no-restart', action='store_true',
                       help='Skip automatic OpenClaw restart')
    
    args = parser.parse_args()
    
    print("🔧 OpenClaw Memory Configuration Script")
    print("=" * 50)
    
    # Find configuration file
    config_path = get_openclaw_config_path()
    if not config_path:
        print("❌ Could not find OpenClaw configuration file")
        print("   Expected locations:")
        print("   - ~/.openclaw/openclaw.json")
        print("   - ~/.openclaw/config.json") 
        print("   - ./openclaw.json")
        sys.exit(1)
    
    print(f"📁 Found configuration: {config_path}")
    
    # Create backup
    if args.backup and not args.dry_run:
        backup_config(config_path)
    
    # Apply configuration
    changes_made = apply_memory_config(config_path, args.dry_run)
    
    if not changes_made:
        print("ℹ️  No configuration changes needed")
        sys.exit(0)
    
    if args.dry_run:
        print("\n🔍 Dry run completed - use without --dry-run to apply changes")
        sys.exit(0)
    
    # Restart OpenClaw
    if not args.no_restart:
        print("\n🔄 Restarting OpenClaw to apply changes...")
        restart_success = restart_openclaw()
        
        if restart_success:
            print("⏳ Waiting for restart to complete...")
            import time
            time.sleep(5)
            
            # Verify configuration
            print("🔍 Verifying configuration...")
            if verify_configuration():
                print("\n🎉 OpenClaw memory configuration completed successfully!")
                print("\nNext steps:")
                print("1. Test memory search: openclaw memory search 'your query'")
                print("2. Verify indexing of critical files (SOUL.md, AGENTS.md, etc.)")
                print("3. Check that directives are now being found in memory searches")
            else:
                print("\n⚠️  Configuration applied but verification failed")
                print("   Manual verification recommended")
        else:
            print("\n⚠️  Configuration updated but restart failed")
            print("   Please restart OpenClaw manually: openclaw gateway restart")
    else:
        print("\n✅ Configuration updated")
        print("   Restart OpenClaw to apply changes: openclaw gateway restart")

if __name__ == "__main__":
    main()