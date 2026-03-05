#!/usr/bin/env python3
"""
ClawBrain OpenClaw Integration Test (Container Version)

Simulates OpenClaw environment and verifies ClawBrain is properly integrated.
Designed to run inside Docker container or any environment with OpenClaw-like structure.
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime


# Colors for terminal output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color


def log_info(msg): print(f"{Colors.BLUE}ℹ️  {msg}{Colors.NC}")
def log_success(msg): print(f"{Colors.GREEN}✅ {msg}{Colors.NC}")
def log_warning(msg): print(f"{Colors.YELLOW}⚠️  {msg}{Colors.NC}")
def log_error(msg): print(f"{Colors.RED}❌ {msg}{Colors.NC}")
def log_step(msg): print(f"{Colors.CYAN}▶ {msg}{Colors.NC}")


def detect_platform():
    """Detect OpenClaw or ClawdBot installation."""
    home = Path.home()
    
    if (home / ".openclaw").exists():
        return {
            "name": "openclaw",
            "config_dir": home / ".openclaw",
            "skills_dir": home / ".openclaw" / "skills",
            "hooks_dir": home / ".openclaw" / "hooks",
            "data_dir": home / ".openclaw" / "data",
            "logs_dir": home / ".openclaw" / "logs",
        }
    elif (home / ".clawdbot").exists():
        return {
            "name": "clawdbot",
            "config_dir": home / ".clawdbot",
            "skills_dir": home / ".clawdbot" / "skills",
            "hooks_dir": home / ".clawdbot" / "hooks",
            "data_dir": home / ".clawdbot" / "data",
            "logs_dir": home / ".clawdbot" / "logs",
        }
    else:
        return None


def check_skill_installation(platform):
    """Check if ClawBrain skill is installed."""
    skill_dir = platform["skills_dir"] / "clawbrain"
    
    checks = {
        "skill_dir": skill_dir.exists(),
        "clawbrain_py": (skill_dir / "clawbrain.py").exists() if skill_dir.exists() else False,
        "skill_json": (skill_dir / "skill.json").exists() if skill_dir.exists() else False,
    }
    
    return checks


def check_hook_installation(platform):
    """Check if ClawBrain hooks are installed."""
    hook_dir = platform["hooks_dir"] / "clawbrain-startup"
    
    checks = {
        "hook_dir": hook_dir.exists(),
        "handler_js": (hook_dir / "handler.js").exists() if hook_dir.exists() else False,
        "hook_md": (hook_dir / "HOOK.md").exists() if hook_dir.exists() else False,
    }
    
    return checks


def check_pip_installation():
    """Check if ClawBrain is installed via pip."""
    try:
        import clawbrain
        return {
            "installed": True,
            "version": getattr(clawbrain, "__version__", "unknown"),
            "path": clawbrain.__file__,
        }
    except ImportError:
        return {"installed": False}


def test_brain_functionality():
    """Test core Brain functionality."""
    import tempfile
    
    results = {
        "import": False,
        "init": False,
        "encryption": False,
        "storage": False,
        "remember": False,
        "recall": False,
        "errors": [],
    }
    
    try:
        from clawbrain import Brain
        results["import"] = True
    except ImportError as e:
        results["errors"].append(f"Import failed: {e}")
        return results
    
    # Use a temp directory for test to avoid read-only filesystem issues
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            brain = Brain(config={
                "sqlite_path": f"{tmpdir}/test_brain.db",
                "backup_dir": f"{tmpdir}/backups",
            })
            results["init"] = True
            results["storage_backend"] = brain.storage_backend
        except Exception as e:
            results["errors"].append(f"Init failed: {e}")
            return results
        
        try:
            results["encryption"] = brain._cipher is not None
        except Exception as e:
            results["errors"].append(f"Encryption check failed: {e}")
        
        try:
            health = brain.health_check()
            results["storage"] = health.get("sqlite") or health.get("postgresql")
            results["health"] = health
        except Exception as e:
            results["errors"].append(f"Health check failed: {e}")
        
        try:
            memory = brain.remember(
                agent_id="integration-test",
                memory_type="test",
                content=f"Test at {datetime.now().isoformat()}",
                key="integration_test_key"
            )
            results["remember"] = memory is not None
            results["memory_id"] = memory.id if memory else None
        except Exception as e:
            results["errors"].append(f"Remember failed: {e}")
        
        try:
            memories = brain.recall(agent_id="integration-test", memory_type="test")
            results["recall"] = len(memories) > 0
            results["recall_count"] = len(memories)
        except Exception as e:
            results["errors"].append(f"Recall failed: {e}")
        
        try:
            brain.close()
        except:
            pass
    
    return results


def test_cli():
    """Test CLI availability."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "clawbrain_cli", "--help"],
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            "available": result.returncode == 0,
            "output": result.stdout[:200] if result.stdout else None,
        }
    except Exception as e:
        return {"available": False, "error": str(e)}


def test_hook_syntax(platform):
    """Test that handler.js has valid syntax."""
    hook_file = platform["hooks_dir"] / "clawbrain-startup" / "handler.js"
    
    if not hook_file.exists():
        return {"valid": False, "error": "handler.js not found"}
    
    try:
        result = subprocess.run(
            ["node", "--check", str(hook_file)],
            capture_output=True,
            text=True,
            timeout=10
        )
        return {"valid": result.returncode == 0, "error": result.stderr if result.returncode != 0 else None}
    except FileNotFoundError:
        return {"valid": None, "error": "Node.js not available"}
    except Exception as e:
        return {"valid": False, "error": str(e)}


def test_brain_bridge(platform):
    """Test that brain_bridge.py exists and is valid Python."""
    possible_paths = [
        platform["skills_dir"] / "clawbrain" / "scripts" / "brain_bridge.py",
        platform["skills_dir"] / "clawbrain" / "brain" / "scripts" / "brain_bridge.py",
    ]
    
    for path in possible_paths:
        if path.exists():
            try:
                # Use ast.parse instead of py_compile to avoid __pycache__ creation
                import ast
                with open(path, 'r') as f:
                    source = f.read()
                ast.parse(source)
                return {
                    "found": True,
                    "path": str(path),
                    "valid": True,
                }
            except SyntaxError as e:
                return {"found": True, "path": str(path), "valid": False, "error": str(e)}
            except Exception as e:
                return {"found": True, "path": str(path), "valid": False, "error": str(e)}
    
    return {"found": False}


def run_tests():
    """Run all integration tests."""
    print("\n" + "=" * 60)
    print("  ClawBrain OpenClaw Integration Test")
    print("=" * 60)
    print(f"  Date: {datetime.now().isoformat()}")
    print(f"  Python: {sys.version.split()[0]}")
    print("=" * 60 + "\n")
    
    all_passed = True
    
    # Step 1: Detect platform
    log_step("Step 1: Detecting platform")
    platform = detect_platform()
    
    if platform:
        log_success(f"Detected: {platform['name']}")
        log_info(f"Config: {platform['config_dir']}")
    else:
        log_warning("No OpenClaw/ClawdBot directory found")
        log_info("Creating simulated environment for testing...")
        
        # Create simulated environment
        home = Path.home()
        platform = {
            "name": "simulated",
            "config_dir": home / ".openclaw",
            "skills_dir": home / ".openclaw" / "skills",
            "hooks_dir": home / ".openclaw" / "hooks",
            "data_dir": home / ".openclaw" / "data",
            "logs_dir": home / ".openclaw" / "logs",
        }
    
    print()
    
    # Step 2: Check skill installation
    log_step("Step 2: Checking skill installation")
    skill_checks = check_skill_installation(platform)
    
    if skill_checks["skill_dir"]:
        log_success(f"Skill directory: {platform['skills_dir'] / 'clawbrain'}")
    else:
        log_warning("Skill directory not found")
    
    if skill_checks.get("clawbrain_py"):
        log_success("clawbrain.py found")
    if skill_checks.get("skill_json"):
        log_success("skill.json found")
    
    # Also check pip
    pip_info = check_pip_installation()
    if pip_info["installed"]:
        log_success(f"Pip install: v{pip_info['version']}")
    else:
        if not skill_checks["skill_dir"]:
            log_error("ClawBrain not installed!")
            all_passed = False
    
    print()
    
    # Step 3: Check hook installation
    log_step("Step 3: Checking hook installation")
    hook_checks = check_hook_installation(platform)
    
    if hook_checks["hook_dir"]:
        log_success(f"Hook directory: {platform['hooks_dir'] / 'clawbrain-startup'}")
    else:
        log_warning("Hook directory not found")
        log_info("Run 'clawbrain setup' to install hooks")
    
    if hook_checks.get("handler_js"):
        log_success("handler.js found")
        
        # Test syntax
        syntax = test_hook_syntax(platform)
        if syntax.get("valid"):
            log_success("handler.js syntax valid")
        elif syntax.get("valid") is None:
            log_warning(f"Cannot check syntax: {syntax.get('error')}")
        else:
            log_error(f"handler.js syntax error: {syntax.get('error')}")
            all_passed = False
    
    print()
    
    # Step 4: Check brain_bridge.py
    log_step("Step 4: Checking brain_bridge.py")
    bridge = test_brain_bridge(platform)
    
    if bridge["found"]:
        log_success(f"brain_bridge.py found: {bridge['path']}")
        if bridge.get("valid"):
            log_success("brain_bridge.py syntax valid")
        else:
            log_error(f"brain_bridge.py error: {bridge.get('error')}")
            all_passed = False
    else:
        log_warning("brain_bridge.py not found in skill directory")
    
    print()
    
    # Step 5: Test CLI
    log_step("Step 5: Testing CLI")
    cli = test_cli()
    
    if cli["available"]:
        log_success("CLI available and responds to --help")
    else:
        log_error(f"CLI not available: {cli.get('error')}")
        all_passed = False
    
    print()
    
    # Step 6: Test Brain functionality
    log_step("Step 6: Testing Brain functionality")
    brain_results = test_brain_functionality()
    
    if brain_results["import"]:
        log_success("ClawBrain imported successfully")
    else:
        log_error("Failed to import ClawBrain")
        all_passed = False
    
    if brain_results["init"]:
        log_success(f"Brain initialized ({brain_results.get('storage_backend', 'unknown')} storage)")
    else:
        log_error("Failed to initialize Brain")
        all_passed = False
    
    if brain_results["encryption"]:
        log_success("Encryption enabled")
    else:
        log_warning("Encryption not available")
    
    if brain_results["storage"]:
        log_success("Storage backend healthy")
    else:
        log_error("Storage backend issue")
        all_passed = False
    
    if brain_results["remember"]:
        log_success(f"Memory stored: {brain_results.get('memory_id', 'unknown')[:8]}...")
    else:
        log_error("Failed to store memory")
        all_passed = False
    
    if brain_results["recall"]:
        log_success(f"Memory recalled: {brain_results.get('recall_count', 0)} items")
    else:
        log_error("Failed to recall memory")
        all_passed = False
    
    if brain_results["errors"]:
        for err in brain_results["errors"]:
            log_error(err)
    
    print()
    
    # Summary
    print("=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    
    if all_passed:
        log_success("All integration tests passed!")
        print()
        log_info(f"ClawBrain is properly integrated with {platform['name']}")
        return 0
    else:
        log_error("Some tests failed!")
        print()
        log_info("Troubleshooting:")
        print("  1. pip install clawbrain[all]")
        print("  2. clawbrain setup")
        print("  3. Check logs for errors")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
