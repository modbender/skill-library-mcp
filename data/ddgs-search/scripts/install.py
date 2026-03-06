#!/usr/bin/env python3
"""
Cross-platform install script for ddgs-search.
Works on macOS, Linux, and Windows (Python 3.8+).
"""
import subprocess
import sys
import shutil
import os


def run(cmd, check=True):
    print(f"  → {' '.join(cmd)}")
    return subprocess.run(cmd, check=check, capture_output=True, text=True)


def pip_install(packages):
    """Install packages using pip, preferring --user on non-venv systems."""
    pip_cmd = [sys.executable, "-m", "pip", "install"]
    if not (hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)):
        pip_cmd.append("--user")
    pip_cmd.extend(packages)
    result = run(pip_cmd, check=False)
    if result.returncode != 0:
        print("  ⚠️  pip install failed, retrying without --user...")
        run([sys.executable, "-m", "pip", "install"] + packages)


def main():
    print("🔧 Installing ddgs-search dependencies...\n")

    # 1. Check Python version
    v = sys.version_info
    print(f"Python: {v.major}.{v.minor}.{v.micro}")
    if v < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    print(f"  ✅ Python {v.major}.{v.minor}\n")

    # 2. Install ddgs
    print("Installing ddgs CLI...")
    pip_install(["ddgs"])

    # 3. Verify ddgs is accessible
    print("\n🔍 Verifying installation...")
    errors = []

    # Check ddgs import
    try:
        result = run([sys.executable, "-c", "import ddgs; print('ok')"], check=False)
        if result.returncode == 0:
            print("  ✅ ddgs (Python module)")
        else:
            errors.append("ddgs")
            print("  ❌ ddgs (Python module)")
    except Exception:
        errors.append("ddgs")
        print("  ❌ ddgs (Python module)")

    # Check ddgs CLI
    ddgs_bin = shutil.which("ddgs")
    if ddgs_bin:
        print(f"  ✅ ddgs CLI ({ddgs_bin})")
    else:
        # Check common user-install locations
        user_bin_paths = []
        if sys.platform == "win32":
            user_bin_paths.append(os.path.join(os.environ.get("APPDATA", ""), "Python", f"Python{v.major}{v.minor}", "Scripts"))
        elif sys.platform == "darwin":
            user_bin_paths.append(os.path.expanduser(f"~/Library/Python/{v.major}.{v.minor}/bin"))
        user_bin_paths.append(os.path.expanduser("~/.local/bin"))

        found = None
        for p in user_bin_paths:
            candidate = os.path.join(p, "ddgs.exe" if sys.platform == "win32" else "ddgs")
            if os.path.exists(candidate):
                found = candidate
                break

        if found:
            print(f"  ✅ ddgs CLI ({found})")
            if os.path.dirname(found) not in os.environ.get("PATH", ""):
                print(f"  ⚠️  Add to PATH: export PATH=\"{os.path.dirname(found)}:$PATH\"")
        else:
            print("  ⚠️  ddgs CLI not in PATH")
            print("     The scripts use the CLI directly. Add ~/.local/bin to PATH:")
            if sys.platform == "win32":
                print("     set PATH=%APPDATA%\\Python\\Scripts;%PATH%")
            else:
                print("     export PATH=\"$HOME/.local/bin:$PATH\"")

    # 4. Quick test
    print("\n🧪 Quick test...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    search_script = os.path.join(script_dir, "search.py")

    if os.path.exists(search_script):
        result = run([sys.executable, search_script, "-q", "test", "-m", "1", "-b", "duckduckgo"], check=False)
        if result.returncode == 0 and '"results"' in result.stdout:
            print("  ✅ Web search works")
        else:
            print("  ⚠️  Web search returned no results (may be rate-limited, try again)")

    arxiv_script = os.path.join(script_dir, "arxiv_search.py")
    if os.path.exists(arxiv_script):
        result = run([sys.executable, arxiv_script, "-q", "test", "-m", "1"], check=False)
        if result.returncode == 0 and '"results"' in result.stdout:
            print("  ✅ arXiv search works")
        else:
            print("  ⚠️  arXiv search failed (may be network issue)")

    # 5. Install ddgs-search CLI wrapper
    print("\n📦 Installing ddgs-search CLI wrapper...")
    wrapper_src = os.path.join(script_dir, "ddgs-search")
    if os.path.exists(wrapper_src):
        user_bin = os.path.expanduser("~/.local/bin")
        os.makedirs(user_bin, exist_ok=True)
        wrapper_dst = os.path.join(user_bin, "ddgs-search")
        import shutil as _shutil
        _shutil.copy2(wrapper_src, wrapper_dst)
        os.chmod(wrapper_dst, 0o755)
        print(f"  ✅ Installed {wrapper_dst}")
        if user_bin not in os.environ.get("PATH", ""):
            print(f"  ⚠️  Add to PATH: export PATH=\"{user_bin}:$PATH\"")
    else:
        print("  ⚠️  ddgs-search wrapper not found in scripts/, skipping")

    if errors:
        print(f"\n❌ Missing: {', '.join(errors)}")
        sys.exit(1)
    else:
        print("\n✅ ddgs-search ready!")
        print("\nUsage:")
        print(f"  ddgs-search \"your query\" 5 google          # CLI wrapper (recommended)")
        print(f"  python3 {search_script} -q \"your query\" -m 5  # Python JSON output")
        print(f"  python3 {arxiv_script} -q \"machine learning\" -m 10")


if __name__ == "__main__":
    main()
