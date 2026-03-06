"""Installation script for desktop-skill.

This script helps AI agents and users install the desktop-skill easily.
"""
import subprocess
import sys
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.12+."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 12):
        print(f"❌ Python 3.12+ required. Current version: {version.major}.{version.minor}")
        print("   Please upgrade your Python installation.")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True


def check_uv():
    """Check if uv is installed."""
    try:
        result = subprocess.run(
            ["uv", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            print(f"✅ uv is installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ uv not found")
            return False
    except FileNotFoundError:
        print("❌ uv not found")
        return False


def install_uv():
    """Provide instructions to install uv."""
    print("\n📦 To install uv, run:")
    print("   Windows (PowerShell): irm https://astral.sh/uv/install.ps1 | iex")
    print("   macOS/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh")
    return False


def install_dependencies():
    """Install project dependencies using uv."""
    print("\n📦 Installing dependencies...")
    try:
        result = subprocess.run(
            ["uv", "sync"],
            check=True,
            capture_output=True,
            text=True,
        )
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e.stderr}")
        return False


def verify_installation():
    """Verify the installation by running help command."""
    print("\n🔍 Verifying installation...")
    try:
        result = subprocess.run(
            ["python", "main.py", "--help"],
            capture_output=True,
            text=True,
            check=True,
        )
        print("✅ Installation verified successfully")
        print("\n" + "="*50)
        print("Desktop Control Skill is ready to use!")
        print("="*50)
        print("\nQuick start:")
        print("  python main.py --help              # Show all commands")
        print("  python main.py mouse position      # Get mouse position")
        print("  python main.py screen size         # Get screen size")
        print("\nFor full documentation, see SKILL.md")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Verification failed: {e.stderr}")
        return False


def main():
    """Main installation process."""
    print("="*50)
    print("Desktop Control Skill - Installation")
    print("="*50)
    print()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check for uv
    if not check_uv():
        if not install_uv():
            sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Verify installation
    if not verify_installation():
        sys.exit(1)
    
    print("\n✨ Installation complete!")


if __name__ == "__main__":
    main()
