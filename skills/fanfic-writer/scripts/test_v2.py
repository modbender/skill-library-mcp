#!/usr/bin/env python3
"""
Fanfic Writer v2.0 - Quick Test
Run this to verify installation
"""
import sys
from pathlib import Path

def test_imports():
    """Test all modules can be imported"""
    print("Testing imports...")
    
    try:
        from scripts.v2 import utils
        print("  ✓ utils")
        
        from scripts.v2 import atomic_io
        print("  ✓ atomic_io")
        
        from scripts.v2 import workspace
        print("  ✓ workspace")
        
        from scripts.v2 import config_manager
        print("  ✓ config_manager")
        
        from scripts.v2 import state_manager
        print("  ✓ state_manager")
        
        from scripts.v2 import prompt_registry
        print("  ✓ prompt_registry")
        
        from scripts.v2 import prompt_assembly
        print("  ✓ prompt_assembly")
        
        from scripts.v2 import phase_runner
        print("  ✓ phase_runner")
        
        from scripts.v2 import writing_loop
        print("  ✓ writing_loop")
        
        from scripts.v2 import safety_mechanisms
        print("  ✓ safety_mechanisms")
        
        return True
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        return False


def test_directory_structure():
    """Test prompts directory exists"""
    print("\nTesting directory structure...")
    
    skill_dir = Path(__file__).parent.parent
    
    prompts_v1 = skill_dir / "prompts" / "v1"
    prompts_v2 = skill_dir / "prompts" / "v2_addons"
    
    if prompts_v1.exists():
        print(f"  ✓ prompts/v1/ ({len(list(prompts_v1.glob('*.md')))} templates)")
    else:
        print("  ✗ prompts/v1/ missing")
        return False
    
    if prompts_v2.exists():
        print(f"  ✓ prompts/v2_addons/ ({len(list(prompts_v2.glob('*.md')))} templates)")
    else:
        print("  ✗ prompts/v2_addons/ missing")
        return False
    
    return True


def main():
    print("="*50)
    print("Fanfic Writer v2.0 - Installation Test")
    print("="*50)
    
    success = True
    
    success = test_imports() and success
    success = test_directory_structure() and success
    
    print("\n" + "="*50)
    if success:
        print("✓ All tests passed!")
        print("="*50)
        return 0
    else:
        print("✗ Some tests failed")
        print("="*50)
        return 1


if __name__ == '__main__':
    sys.exit(main())
