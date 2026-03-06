#!/usr/bin/env python3
"""
Nova Act Usability Testing Skill - Setup Script
Handles all dependencies and configuration automatically.
"""

import sys
import subprocess
import os
import json
from pathlib import Path

def print_step(step, message):
    """Print formatted step message."""
    print(f"\n{'='*60}")
    print(f"Step {step}: {message}")
    print(f"{'='*60}")

def run_command(cmd, description, ignore_errors=False):
    """Run a shell command and handle errors."""
    print(f"\n→ {description}...")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode != 0 and not ignore_errors:
            print(f"  ⚠️  Warning: {description} had issues")
            if result.stderr:
                print(f"     {result.stderr[:200]}")
            return False
        else:
            print(f"  ✅ {description} complete")
            return True
    except subprocess.TimeoutExpired:
        print(f"  ⚠️  Warning: {description} timed out")
        return False
    except Exception as e:
        print(f"  ⚠️  Warning: {description} failed - {str(e)}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} is too old")
        print(f"   This skill requires Python 3.8 or newer")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def install_python_packages():
    """Install required Python packages."""
    print_step(1, "Installing Python Dependencies")
    
    packages = [
        "nova-act",
        "pydantic>=2.0",
        "playwright>=1.40",
    ]
    
    print("Required packages:")
    for pkg in packages:
        print(f"  • {pkg}")
    
    # Try pip3 first
    pip_cmd = "pip3"
    if not run_command(f"{pip_cmd} --version", "Check pip3", ignore_errors=True):
        # Fallback to python -m pip
        pip_cmd = f"{sys.executable} -m pip"
    
    # Install with --break-system-packages for Linux package managers
    install_cmd = f"{pip_cmd} install --break-system-packages {' '.join(packages)}"
    
    success = run_command(install_cmd, "Install Python packages")
    
    if not success:
        # Try without --break-system-packages
        install_cmd = f"{pip_cmd} install {' '.join(packages)}"
        success = run_command(install_cmd, "Install Python packages (retry without flag)")
    
    if not success:
        print("\n⚠️  Automatic installation had issues. You may need to install manually:")
        print(f"   pip3 install {' '.join(packages)}")
        return False
    
    return True

def install_playwright_browsers():
    """Install Playwright browsers."""
    print_step(2, "Installing Playwright Browsers")
    
    print("Installing Chromium browser for Nova Act...")
    print("(This downloads ~300MB - may take a few minutes)")
    
    # Try multiple approaches
    commands = [
        (f"{sys.executable} -m playwright install chromium", "Install via Python module"),
        ("playwright install chromium", "Install via playwright CLI"),
    ]
    
    for cmd, desc in commands:
        if run_command(cmd, desc, ignore_errors=True):
            print("\n✅ Playwright browser installed successfully")
            return True
    
    print("\n⚠️  Browser installation had issues. You may need to install manually:")
    print("   playwright install chromium")
    return False

def install_system_dependencies():
    """Install system dependencies for Playwright (optional)."""
    print_step(3, "System Dependencies (Optional)")
    
    print("Checking for system dependencies...")
    print("(These are needed for Playwright to run browsers)")
    
    # Check if we're on Linux
    if sys.platform.startswith('linux'):
        print("\n→ Detected Linux system")
        print("  Playwright may need system libraries (libgobject, libx11, etc.)")
        print("  You can install these with:")
        print("     sudo playwright install-deps chromium")
        print("\n  ℹ️  Skipping automatic installation (requires sudo)")
        print("     If tests fail with library errors, run the command above")
    else:
        print("  ℹ️  Non-Linux system detected, skipping")
    
    return True

def setup_config_file():
    """Create config file template if it doesn't exist."""
    print_step(4, "Configuration Setup")
    
    config_dir = Path.home() / ".openclaw" / "config"
    config_file = config_dir / "nova-act.json"
    
    # Create config directory
    config_dir.mkdir(parents=True, exist_ok=True)
    print(f"  ✅ Config directory: {config_dir}")
    
    if config_file.exists():
        print(f"  ✅ Config file already exists: {config_file}")
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                if 'apiKey' in config and config['apiKey']:
                    print(f"  ✅ API key configured")
                    return True
                else:
                    print(f"  ⚠️  Config file exists but API key not set")
        except:
            pass
    else:
        # Create template
        template = {
            "apiKey": "your-nova-act-api-key-here"
        }
        
        with open(config_file, 'w') as f:
            json.dump(template, f, indent=2)
        
        print(f"  ✅ Created config template: {config_file}")
    
    print("\n  📝 Next Steps:")
    print(f"     1. Get your Nova Act API key from AWS Console")
    print(f"     2. Edit: {config_file}")
    print(f"     3. Replace 'your-nova-act-api-key-here' with your actual key")
    
    return True

def verify_installation():
    """Verify that everything is installed correctly."""
    print_step(5, "Verification")
    
    all_good = True
    
    # Check Python packages via pip
    print("\n→ Checking Python packages...")
    
    # Try pip3 first
    pip_cmd = "pip3"
    check_cmd = f"{pip_cmd} show"
    result = subprocess.run(f"{pip_cmd} --version", shell=True, capture_output=True)
    if result.returncode != 0:
        pip_cmd = f"{sys.executable} -m pip"
        check_cmd = f"{pip_cmd} show"
    
    packages = {
        'nova-act': 'nova_act',
        'pydantic': 'pydantic',
        'playwright': 'playwright'
    }
    
    for pkg_name, import_name in packages.items():
        result = subprocess.run(
            f"{check_cmd} {pkg_name}",
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"  ✅ {pkg_name}")
        else:
            # Fallback: try importing
            try:
                __import__(import_name)
                print(f"  ✅ {pkg_name} (via import)")
            except ImportError:
                print(f"  ❌ {pkg_name} - Not installed")
                all_good = False
    
    # Check Playwright browsers
    print("\n→ Checking Playwright browsers...")
    playwright_cache = Path.home() / ".cache" / "ms-playwright"
    
    if playwright_cache.exists():
        browsers = list(playwright_cache.glob("chromium-*"))
        if browsers:
            print(f"  ✅ Chromium browser installed")
        else:
            print(f"  ⚠️  No Chromium browser found")
            all_good = False
    else:
        print(f"  ⚠️  Playwright cache directory not found")
        all_good = False
    
    # Check config
    print("\n→ Checking configuration...")
    config_file = Path.home() / ".openclaw" / "config" / "nova-act.json"
    
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                if 'apiKey' in config and config['apiKey'] != 'your-nova-act-api-key-here':
                    print(f"  ✅ API key configured")
                else:
                    print(f"  ⚠️  API key not set in config")
                    all_good = False
        except:
            print(f"  ⚠️  Config file exists but is invalid")
            all_good = False
    else:
        print(f"  ⚠️  Config file not found")
        all_good = False
    
    return all_good

def main():
    """Main setup routine."""
    print("\n🦅 Nova Act Usability Testing Skill - Setup")
    print("="*60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install packages
    install_python_packages()
    
    # Install browsers
    install_playwright_browsers()
    
    # System dependencies (informational only)
    install_system_dependencies()
    
    # Setup config
    setup_config_file()
    
    # Verify
    print("\n")
    all_good = verify_installation()
    
    # Summary
    print("\n" + "="*60)
    if all_good:
        print("✅ SETUP COMPLETE")
        print("="*60)
        print("\n🎉 The skill is ready to use!")
        print("\nYou can now run usability tests:")
        print("  'Test the usability of https://example.com'")
    else:
        print("⚠️  SETUP INCOMPLETE")
        print("="*60)
        print("\n⚠️  Some components need manual setup.")
        print("   Review the messages above and follow the instructions.")
        print("\n📚 For help, see:")
        print("   ~/.openclaw/skills/nova-act-usability/README.md")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
