#!/usr/bin/env python3
"""
OpenClaw Config Validator
Safely validates configuration files without modifying them.
"""

import json
import sys
import os
from pathlib import Path

def validate_json_structure(file_path):
    """Validate JSON syntax and structure"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return True, data, None
    except json.JSONDecodeError as e:
        return False, None, f"Invalid JSON: {e}"
    except Exception as e:
        return False, None, f"Error reading file: {e}"

def check_openclaw_config(config_data):
    """Check OpenClaw-specific configuration requirements"""
    warnings = []
    errors = []
    
    # Required top-level keys
    required_keys = ['agents', 'gateway']
    for key in required_keys:
        if key not in config_data:
            errors.append(f"Missing required key: {key}")
    
    # Check for sandbox configuration
    if 'agents' in config_data and 'defaults' in config_data['agents']:
        defaults = config_data['agents']['defaults']
        if 'sandbox' in defaults:
            warnings.append("Sandbox configuration detected - ensure you have a backup!")
    
    # Check for memory management keys
    memory_keys = ['compaction', 'contextPruning', 'memorySearch', 'experimental']
    found_memory_keys = []
    
    if 'agents' in config_data and 'defaults' in config_data['agents']:
        for key in memory_keys:
            if key in config_data['agents']['defaults']:
                found_memory_keys.append(key)
    
    if found_memory_keys:
        warnings.append(f"Memory management keys found: {found_memory_keys}")
    
    return warnings, errors

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 config_validator.py <path-to-openclaw.json>")
        sys.exit(1)
    
    config_path = sys.argv[1]
    
    if not os.path.exists(config_path):
        print(f"❌ Error: File not found: {config_path}")
        sys.exit(1)
    
    print(f"🔍 Validating: {config_path}")
    print("")
    
    # Validate JSON structure
    is_valid, config_data, error = validate_json_structure(config_path)
    
    if not is_valid:
        print(f"❌ JSON Validation Failed: {error}")
        sys.exit(1)
    
    print("✅ JSON syntax is valid")
    
    # Check OpenClaw-specific requirements
    warnings, errors = check_openclaw_config(config_data)
    
    if errors:
        print("\n❌ Configuration Errors:")
        for error in errors:
            print(f"  • {error}")
        sys.exit(1)
    
    if warnings:
        print("\n⚠️  Configuration Warnings:")
        for warning in warnings:
            print(f"  • {warning}")
    
    print("\n🎉 Configuration validation completed")
    
    # Show file stats
    file_size = os.path.getsize(config_path)
    print(f"📊 File size: {file_size} bytes")
    print(f"📊 Top-level keys: {list(config_data.keys())}")
    
    if not warnings and not errors:
        print("✅ No issues found!")

if __name__ == "__main__":
    main()