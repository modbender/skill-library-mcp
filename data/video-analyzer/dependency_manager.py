"""
Dependency Manager - Auto-install Python packages and system tools
"""

import sys
import subprocess
import shutil
from typing import Dict, List

REQUIRED_PYTHON_PACKAGES = {
    "yt-dlp": "yt-dlp>=2024.0.0",
    "faster_whisper": "faster-whisper>=1.0.0",
    "modelscope": "modelscope>=1.0.0",
    "openai": "openai>=1.0.0",
    "tenacity": "tenacity>=8.0.0",
}

OPTIONAL_PYTHON_PACKAGES = {
    "opencc": "opencc-python-reimplemented",
    "anthropic": "anthropic>=0.18.0",
    "bilibili_api": "bilibili-api-python",
}

SYSTEM_TOOLS = ["ffmpeg", "ffprobe"]


class DependencyManager:
    """Manage dependencies detection and installation."""

    @staticmethod
    def check_python_packages() -> Dict[str, bool]:
        """Check which Python packages are installed."""
        status = {}
        for pkg_name in {**REQUIRED_PYTHON_PACKAGES, **OPTIONAL_PYTHON_PACKAGES}:
            try:
                import_name = pkg_name.replace("-", "_").replace(".", "_")
                __import__(import_name)
                status[pkg_name] = True
            except ImportError:
                status[pkg_name] = False
        return status

    @staticmethod
    def check_system_tools() -> Dict[str, bool]:
        """Check which system tools are available."""
        return {tool: shutil.which(tool) is not None for tool in SYSTEM_TOOLS}

    @staticmethod
    def install_package(package: str) -> bool:
        """Install a Python package."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package],
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except Exception:
            return False

    @staticmethod
    def install_all_missing() -> bool:
        """Install all missing packages."""
        status = DependencyManager.check_python_packages()
        missing = [
            pkg for pkg in REQUIRED_PYTHON_PACKAGES.keys() if not status.get(pkg, False)
        ]

        if not missing:
            return True

        print(f"[INFO] Installing {len(missing)} packages...")
        for pkg in missing:
            print(f"  - {pkg}")
            if not DependencyManager.install_package(REQUIRED_PYTHON_PACKAGES[pkg]):
                print(f"  [ERROR] Failed: {pkg}")
                return False

        return True

    @staticmethod
    def get_system_guide() -> str:
        """Get FFmpeg installation guide for current OS."""
        import platform

        os_name = platform.system()

        guides = {
            "Windows": "winget install ffmpeg  # or: choco install ffmpeg",
            "Darwin": "brew install ffmpeg",
            "Linux": "sudo apt install ffmpeg  # Ubuntu/Debian\nsudo yum install ffmpeg  # CentOS",
        }

        return guides.get(os_name, "Download from https://ffmpeg.org/download.html")


def check_and_install_dependencies() -> bool:
    """Check and install all dependencies. Returns True if ready."""
    print("[INFO] Checking dependencies...")

    # Check Python packages
    py_status = DependencyManager.check_python_packages()
    missing_py = [
        pkg for pkg in REQUIRED_PYTHON_PACKAGES.keys() if not py_status.get(pkg, False)
    ]

    if missing_py:
        print(f"[WARN] {len(missing_py)} required Python packages missing")
        if not DependencyManager.install_all_missing():
            print("[ERROR] Python package installation failed")
            return False

    missing_optional = [
        pkg for pkg in OPTIONAL_PYTHON_PACKAGES.keys() if not py_status.get(pkg, False)
    ]
    if missing_optional:
        print(
            "[WARN] Optional packages missing (features may be limited): "
            + ", ".join(missing_optional)
        )

    # Check system tools
    sys_status = DependencyManager.check_system_tools()
    missing_sys = [tool for tool, ok in sys_status.items() if not ok]

    if missing_sys:
        print(f"[ERROR] System tools missing: {', '.join(missing_sys)}")
        print(f"[INFO] Installation guide:\n{DependencyManager.get_system_guide()}")
        return False

    print("[OK] All required dependencies ready")
    return True
