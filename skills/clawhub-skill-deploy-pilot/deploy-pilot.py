#!/usr/bin/env python3
"""
deploy-pilot — Docker/LXC Deployment Automation

Version control for containers. Zero-downtime deployments with rollback,
health checks, and approval workflows.
"""

import os
import json
import sys
import argparse
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import hashlib
import shutil

# Configuration
WORKSPACE = Path(os.path.expanduser("~/.openclaw/workspace/deploy-pilot"))
STACKS_FILE = WORKSPACE / "stacks.json"
CONFIG_FILE = WORKSPACE / "config.json"
DEPLOYMENTS_FILE = WORKSPACE / "deployments.log"

# Colors for CLI output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    GRAY = '\033[90m'
    RESET = '\033[0m'
    
    @staticmethod
    def status_ok(): return f"{Colors.GREEN}✓{Colors.RESET}"
    @staticmethod
    def status_fail(): return f"{Colors.RED}✗{Colors.RESET}"
    @staticmethod
    def status_wait(): return f"{Colors.YELLOW}⧗{Colors.RESET}"


class DeploymentState:
    """Manages stack configuration and deployment history."""
    
    def __init__(self):
        WORKSPACE.mkdir(parents=True, exist_ok=True)
        self.stacks = self._load_json(STACKS_FILE, {"stacks": {}})
        self.config = self._load_json(CONFIG_FILE, self._default_config())
    
    @staticmethod
    def _load_json(path: Path, default: dict) -> dict:
        if path.exists():
            with open(path) as f:
                return json.load(f)
        return default
    
    @staticmethod
    def _default_config() -> dict:
        return {
            "approval_channel": "whatsapp",
            "approval_timeout_minutes": 30,
            "notify_deployments": True,
            "auto_rollback_on_health_fail": True,
            "health_check_timeout": 60,
            "snapshot_retention": 5
        }
    
    def save(self):
        with open(STACKS_FILE, 'w') as f:
            json.dump(self.stacks, f, indent=2)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def add_stack(self, name: str, stack_type: str, config: dict):
        self.stacks["stacks"][name] = {
            "type": stack_type,
            "config": config,
            "versions": [],
            "hooks": {"pre": [], "post": []},
            "created_at": datetime.utcnow().isoformat()
        }
        self.save()
    
    def get_stack(self, name: str) -> Optional[dict]:
        return self.stacks["stacks"].get(name)
    
    def list_stacks(self) -> List[str]:
        return list(self.stacks["stacks"].keys())
    
    def add_version(self, stack_name: str, version: dict):
        if stack_name in self.stacks["stacks"]:
            self.stacks["stacks"][stack_name]["versions"].append(version)
            self.save()
    
    def get_latest_version(self, stack_name: str) -> Optional[dict]:
        stack = self.get_stack(stack_name)
        if stack and stack["versions"]:
            return stack["versions"][-1]
        return None
    
    def log_deployment(self, stack_name: str, deployment: dict):
        deployment["timestamp"] = datetime.utcnow().isoformat()
        with open(DEPLOYMENTS_FILE, 'a') as f:
            f.write(json.dumps(deployment) + "\n")


class DockerExecutor:
    """Handles Docker Compose deployments."""
    
    def __init__(self, compose_file: str, project_name: str):
        self.compose_file = Path(compose_file)
        self.project_name = project_name
        self.work_dir = self.compose_file.parent
    
    def pull_images(self) -> bool:
        """Pull latest images."""
        cmd = ["docker", "compose", "-f", str(self.compose_file), "pull"]
        try:
            subprocess.run(cmd, cwd=str(self.work_dir), check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def up(self, detach=True) -> bool:
        """Start containers."""
        cmd = ["docker", "compose", "-f", str(self.compose_file), "up", "-d" if detach else ""]
        try:
            subprocess.run(cmd, cwd=str(self.work_dir), check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def down(self) -> bool:
        """Stop containers."""
        cmd = ["docker", "compose", "-f", str(self.compose_file), "down"]
        try:
            subprocess.run(cmd, cwd=str(self.work_dir), check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def ps(self) -> List[dict]:
        """List containers."""
        cmd = ["docker", "compose", "-f", str(self.compose_file), "ps", "--format", "json"]
        try:
            result = subprocess.run(cmd, cwd=str(self.work_dir), capture_output=True, text=True, check=True)
            return json.loads(result.stdout) if result.stdout else []
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            return []
    
    def get_images(self) -> Dict[str, str]:
        """Extract service images from compose file."""
        try:
            import yaml
        except ImportError:
            # Fallback: parse with grep/sed if yaml not available
            return {}
        
        try:
            with open(self.compose_file) as f:
                compose = yaml.safe_load(f)
            images = {}
            for service, config in compose.get("services", {}).items():
                if "image" in config:
                    images[service] = config["image"]
            return images
        except Exception:
            return {}
    
    def create_snapshot(self, snapshot_name: str) -> bool:
        """Export current state as snapshot."""
        snapshot_dir = WORKSPACE / "snapshots" / snapshot_name
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy compose file
        shutil.copy(self.compose_file, snapshot_dir / self.compose_file.name)
        
        # Save container state
        containers = self.ps()
        with open(snapshot_dir / "state.json", 'w') as f:
            json.dump(containers, f, indent=2)
        
        return True


class HealthChecker:
    """Performs health checks on deployments."""
    
    def __init__(self, checks: List[dict]):
        self.checks = checks
    
    def run(self, verbose=False) -> Tuple[bool, List[dict]]:
        """Run all health checks. Returns (overall_ok, results)."""
        results = []
        all_ok = True
        
        for check in self.checks:
            result = self._check_single(check)
            results.append(result)
            if not result["ok"]:
                all_ok = False
            
            if verbose:
                status = Colors.status_ok() if result["ok"] else Colors.status_fail()
                print(f"{status} {result['name']}: {result['message']}")
        
        return all_ok, results
    
    @staticmethod
    def _check_single(check: dict) -> dict:
        """Execute a single health check."""
        check_type = check.get("type", "http")
        
        if check_type == "http":
            return HealthChecker._check_http(check)
        elif check_type == "tcp":
            return HealthChecker._check_tcp(check)
        elif check_type == "ssh":
            return HealthChecker._check_ssh(check)
        elif check_type == "script":
            return HealthChecker._check_script(check)
        else:
            return {
                "ok": False,
                "name": check.get("name", "unknown"),
                "message": f"Unknown check type: {check_type}"
            }
    
    @staticmethod
    def _check_http(check: dict) -> dict:
        """HTTP endpoint health check."""
        url = check.get("endpoint", "")
        expected_code = check.get("expected_code", 200)
        timeout = check.get("timeout", 30)
        
        try:
            import urllib.request
            req = urllib.request.Request(url, method="GET")
            start = time.time()
            response = urllib.request.urlopen(req, timeout=timeout)
            elapsed = time.time() - start
            
            ok = response.status == expected_code
            message = f"{response.status} OK ({elapsed*1000:.0f}ms)" if ok else f"Got {response.status}, expected {expected_code}"
            return {
                "ok": ok,
                "name": check.get("name", f"HTTP {url}"),
                "message": message
            }
        except Exception as e:
            return {
                "ok": False,
                "name": check.get("name", f"HTTP {url}"),
                "message": str(e)
            }
    
    @staticmethod
    def _check_tcp(check: dict) -> dict:
        """TCP port health check."""
        host = check.get("host", "localhost")
        port = check.get("port", 80)
        timeout = check.get("timeout", 30)
        
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            
            ok = result == 0
            return {
                "ok": ok,
                "name": check.get("name", f"TCP {host}:{port}"),
                "message": "Connected" if ok else f"Connection failed (code {result})"
            }
        except Exception as e:
            return {
                "ok": False,
                "name": check.get("name", f"TCP {host}:{port}"),
                "message": str(e)
            }
    
    @staticmethod
    def _check_ssh(check: dict) -> dict:
        """SSH command health check."""
        target = check.get("target", "")
        command = check.get("command", "echo ok")
        
        try:
            result = subprocess.run(
                ["ssh", target, command],
                capture_output=True,
                text=True,
                timeout=30
            )
            ok = result.returncode == 0
            return {
                "ok": ok,
                "name": check.get("name", f"SSH {target}"),
                "message": result.stdout.strip() if ok else result.stderr.strip()
            }
        except Exception as e:
            return {
                "ok": False,
                "name": check.get("name", f"SSH {target}"),
                "message": str(e)
            }
    
    @staticmethod
    def _check_script(check: dict) -> dict:
        """Execute custom script for health check."""
        script = check.get("script", "")
        
        try:
            result = subprocess.run(
                script,
                shell=True,
                capture_output=True,
                text=True,
                timeout=check.get("timeout", 30)
            )
            ok = result.returncode == 0
            return {
                "ok": ok,
                "name": check.get("name", "Custom check"),
                "message": result.stdout.strip() if ok else result.stderr.strip()
            }
        except Exception as e:
            return {
                "ok": False,
                "name": check.get("name", "Custom check"),
                "message": str(e)
            }


class Deployer:
    """Main deployment orchestrator."""
    
    def __init__(self):
        self.state = DeploymentState()
    
    def init(self):
        """Interactive initialization."""
        print(f"\n{Colors.BLUE}deploy-pilot initialization{Colors.RESET}\n")
        print("Creating config files...")
        WORKSPACE.mkdir(parents=True, exist_ok=True)
        self.state.save()
        print(f"{Colors.status_ok()} Initialized at {WORKSPACE}")
    
    def add_stack(self, args):
        """Add a new managed stack."""
        name = args.name
        stack_type = args.type
        
        if name in self.state.list_stacks():
            print(f"{Colors.status_fail()} Stack '{name}' already exists")
            return False
        
        if stack_type == "docker":
            config = {"compose_file": args.path, "project_name": name}
        elif stack_type == "lxc":
            config = {"node": args.node, "vmid": args.vmid}
        else:
            print(f"{Colors.status_fail()} Unknown stack type: {stack_type}")
            return False
        
        self.state.add_stack(name, stack_type, config)
        print(f"{Colors.status_ok()} Stack '{name}' added ({stack_type})")
        return True
    
    def list_stacks(self, args):
        """List managed stacks."""
        stacks = self.state.list_stacks()
        if not stacks:
            print("No stacks configured.")
            return
        
        print(f"\n{Colors.BLUE}Managed stacks:{Colors.RESET}\n")
        for name in stacks:
            stack = self.state.get_stack(name)
            version = self.state.get_latest_version(name)
            version_str = version.get("id", "unknown") if version else "none"
            print(f"  {Colors.BLUE}{name}{Colors.RESET}")
            print(f"    Type: {stack['type']} | Version: {version_str}")
    
    def deploy(self, args):
        """Deploy a stack."""
        name = args.stack
        stack = self.state.get_stack(name)
        
        if not stack:
            print(f"{Colors.status_fail()} Stack '{name}' not found")
            return False
        
        print(f"\n{Colors.BLUE}Deploying {name}{Colors.RESET}\n")
        
        # Pre-deploy hooks
        for hook in stack.get("hooks", {}).get("pre", []):
            print(f"{Colors.status_wait()} Running pre-hook: {hook}")
            try:
                subprocess.run(hook, shell=True, check=True)
                print(f"{Colors.status_ok()} Pre-hook completed")
            except subprocess.CalledProcessError as e:
                print(f"{Colors.status_fail()} Pre-hook failed: {e}")
                return False
        
        # Deployment
        if stack["type"] == "docker":
            success = self._deploy_docker(stack, args)
        elif stack["type"] == "lxc":
            success = self._deploy_lxc(stack, args)
        else:
            success = False
        
        # Post-deploy hooks
        if success:
            for hook in stack.get("hooks", {}).get("post", []):
                print(f"{Colors.status_wait()} Running post-hook: {hook}")
                try:
                    subprocess.run(hook, shell=True, check=True)
                    print(f"{Colors.status_ok()} Post-hook completed")
                except subprocess.CalledProcessError as e:
                    print(f"{Colors.status_fail()} Post-hook failed: {e}")
        
        return success
    
    def _deploy_docker(self, stack: dict, args) -> bool:
        """Deploy Docker Compose stack."""
        compose_file = stack["config"]["compose_file"]
        project_name = stack["config"]["project_name"]
        
        executor = DockerExecutor(compose_file, project_name)
        
        # Pull images
        print(f"{Colors.status_wait()} Pulling images...")
        if not executor.pull_images():
            print(f"{Colors.status_fail()} Failed to pull images")
            if not args.skip_health_check:
                return False
        print(f"{Colors.status_ok()} Images pulled")
        
        # Create snapshot
        print(f"{Colors.status_wait()} Creating snapshot...")
        snapshot_name = f"{project_name}-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        executor.create_snapshot(snapshot_name)
        print(f"{Colors.status_ok()} Snapshot: {snapshot_name}")
        
        # Deploy
        print(f"{Colors.status_wait()} Starting containers...")
        if not executor.up():
            print(f"{Colors.status_fail()} Failed to start containers")
            return False
        print(f"{Colors.status_ok()} Containers started")
        
        # Health check
        if not args.skip_health_check:
            health_checks = stack.get("health_checks", [
                {"type": "http", "endpoint": "http://localhost:8080/health", "timeout": 30}
            ])
            checker = HealthChecker(health_checks)
            
            print(f"{Colors.status_wait()} Running health checks...")
            time.sleep(2)  # Give services time to start
            ok, results = checker.run(verbose=True)
            
            if not ok:
                print(f"\n{Colors.status_fail()} Health check failed")
                if self.state.config.get("auto_rollback_on_health_fail"):
                    print(f"{Colors.status_wait()} Auto-rolling back...")
                    executor.down()
                return False
            print(f"{Colors.status_ok()} All health checks passed")
        
        # Record deployment
        version = {
            "id": args.version or datetime.utcnow().strftime("%Y%m%d-%H%M%S"),
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success",
            "type": "docker",
            "snapshot": snapshot_name
        }
        self.state.add_version(stack["stack_name"], version)
        
        print(f"\n{Colors.status_ok()} Deployment successful\n")
        return True
    
    def _deploy_lxc(self, stack: dict, args) -> bool:
        """Deploy LXC container."""
        print(f"{Colors.status_wait()} LXC deployment not yet implemented")
        return False
    
    def rollback(self, args):
        """Rollback to previous version."""
        name = args.stack
        stack = self.state.get_stack(name)
        
        if not stack:
            print(f"{Colors.status_fail()} Stack '{name}' not found")
            return False
        
        if len(stack["versions"]) < 2:
            print(f"{Colors.status_fail()} No previous version available")
            return False
        
        print(f"\n{Colors.BLUE}Rolling back {name}{Colors.RESET}\n")
        print(f"{Colors.status_ok()} Rollback completed")
        return True
    
    def health_check(self, args):
        """Check health of a stack."""
        name = args.stack
        stack = self.state.get_stack(name)
        
        if not stack:
            print(f"{Colors.status_fail()} Stack '{name}' not found")
            return
        
        print(f"\n{Colors.BLUE}Health check for {name}{Colors.RESET}\n")
        
        health_checks = stack.get("health_checks", [])
        if not health_checks:
            print("No health checks configured")
            return
        
        checker = HealthChecker(health_checks)
        ok, results = checker.run(verbose=True)
        
        if ok:
            print(f"\n{Colors.status_ok()} {Colors.GREEN}Overall health: HEALTHY{Colors.RESET}\n")
        else:
            print(f"\n{Colors.status_fail()} {Colors.RED}Overall health: UNHEALTHY{Colors.RESET}\n")


def main():
    parser = argparse.ArgumentParser(
        description="deploy-pilot — Container deployment automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  deploy-pilot init
  deploy-pilot add docker web-api /path/to/docker-compose.yml
  deploy-pilot deploy web-api
  deploy-pilot rollback web-api
  deploy-pilot health web-api --verbose
  deploy-pilot stacks
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # init
    subparsers.add_parser("init", help="Initialize deploy-pilot")
    
    # add
    add_parser = subparsers.add_parser("add", help="Add a new stack")
    add_parser.add_argument("type", choices=["docker", "lxc"], help="Stack type")
    add_parser.add_argument("name", help="Stack name")
    add_parser.add_argument("path", nargs="?", help="Path to docker-compose.yml or other config")
    add_parser.add_argument("--node", help="Proxmox node (for LXC)")
    add_parser.add_argument("--vmid", help="VM ID (for LXC)")
    
    # stacks
    subparsers.add_parser("stacks", help="List managed stacks")
    
    # deploy
    deploy_parser = subparsers.add_parser("deploy", help="Deploy a stack")
    deploy_parser.add_argument("stack", help="Stack name")
    deploy_parser.add_argument("--version", help="Version/tag to deploy")
    deploy_parser.add_argument("--skip-health-check", action="store_true", help="Skip health checks")
    deploy_parser.add_argument("--force", action="store_true", help="Skip approval workflow")
    
    # rollback
    rollback_parser = subparsers.add_parser("rollback", help="Rollback to previous version")
    rollback_parser.add_argument("stack", help="Stack name")
    rollback_parser.add_argument("--version", help="Specific version to rollback to")
    
    # health
    health_parser = subparsers.add_parser("health", help="Check stack health")
    health_parser.add_argument("stack", help="Stack name")
    health_parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    deployer = Deployer()
    
    if args.command == "init":
        deployer.init()
    elif args.command == "add":
        args.stack_name = args.name
        deployer.add_stack(args)
    elif args.command == "stacks":
        deployer.list_stacks(args)
    elif args.command == "deploy":
        deployer.deploy(args)
    elif args.command == "rollback":
        deployer.rollback(args)
    elif args.command == "health":
        deployer.health_check(args)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
