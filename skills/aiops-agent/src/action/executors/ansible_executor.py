"""
Ansible executor for running playbooks and roles.

Supports:
- Running Ansible playbooks
- Running Ansible roles (via ad-hoc playbook)
- Variable injection
- Check mode (dry-run)
- Timeout handling
"""

import asyncio
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog

from src.config.settings import get_settings

logger = structlog.get_logger()


class AnsibleExecutor:
    """
    Executor for Ansible playbooks and roles.

    Features:
    - Playbook execution with variable injection
    - Role execution via temporary playbook
    - Support for check mode (dry-run)
    - Timeout handling
    - Output capture and parsing
    """

    def __init__(self):
        settings = get_settings()
        self._enabled = settings.ansible.enabled
        self._playbooks_dir = Path(settings.ansible.playbooks_dir)
        self._roles_dir = Path(settings.ansible.roles_dir)
        self._inventory_file = settings.ansible.inventory_file
        self._timeout_seconds = settings.ansible.timeout_seconds
        self._forks = settings.ansible.forks
        self._become = settings.ansible.become
        self._become_user = settings.ansible.become_user
        self._extra_vars = settings.ansible.extra_vars

    async def run_playbook(
        self,
        target: str,
        namespace: str,
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Run an Ansible playbook.

        Target format: "playbook/<name>" or direct path

        Parameters:
            hosts: Target hosts (default: from playbook)
            extra_vars: Additional variables
            tags: Tags to run (optional)
            skip_tags: Tags to skip (optional)
            check: Run in check mode (default: false)
            diff: Show diff (default: false)
            limit: Limit hosts (optional)
            verbosity: Verbosity level 0-4 (default: 0)

        Returns:
            Execution result with success status, output, and stats
        """
        if not self._enabled:
            return {"success": False, "error": "Ansible executor is disabled"}

        # Parse target
        playbook_path = self._resolve_playbook_path(target)
        if not playbook_path.exists():
            return {"success": False, "error": f"Playbook not found: {playbook_path}"}

        # Build command
        cmd = self._build_playbook_command(playbook_path, parameters)

        logger.info(
            "Running Ansible playbook",
            playbook=str(playbook_path),
            check_mode=parameters.get("check", False),
        )

        # Execute
        result = await self._execute_ansible(cmd, parameters.get("timeout"))

        return self._parse_result(result)

    async def run_role(
        self,
        target: str,
        namespace: str,
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Run an Ansible role via temporary playbook.

        Target format: "role/<name>" or just role name

        Parameters:
            hosts: Target hosts (required)
            extra_vars: Variables to pass to role
            tags: Tags to run
            check: Run in check mode
            become: Use privilege escalation (default from settings)

        Returns:
            Execution result
        """
        if not self._enabled:
            return {"success": False, "error": "Ansible executor is disabled"}

        # Parse role name
        role_name = target.replace("role/", "")

        # Hosts required for role execution
        hosts = parameters.get("hosts")
        if not hosts:
            return {"success": False, "error": "hosts parameter required for role execution"}

        # Create temporary playbook
        playbook_content = self._generate_role_playbook(role_name, hosts, parameters)

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".yml",
                delete=False,
            ) as f:
                f.write(playbook_content)
                temp_playbook = Path(f.name)

            logger.info(
                "Running Ansible role",
                role=role_name,
                hosts=hosts,
            )

            # Build command
            cmd = self._build_playbook_command(temp_playbook, parameters)

            # Execute
            result = await self._execute_ansible(cmd, parameters.get("timeout"))

            return self._parse_result(result)

        finally:
            # Clean up temp file
            if temp_playbook.exists():
                temp_playbook.unlink()

    def _resolve_playbook_path(self, target: str) -> Path:
        """Resolve playbook path from target string."""
        # Strip prefix
        playbook_name = target.replace("playbook/", "")

        # Check if it's an absolute path
        if playbook_name.startswith("/"):
            return Path(playbook_name)

        # Check in playbooks directory
        playbook_path = self._playbooks_dir / playbook_name
        if not playbook_path.suffix:
            playbook_path = playbook_path.with_suffix(".yml")

        return playbook_path

    def _build_playbook_command(
        self,
        playbook_path: Path,
        parameters: Dict[str, Any],
    ) -> List[str]:
        """Build ansible-playbook command."""
        cmd = ["ansible-playbook", str(playbook_path)]

        # Inventory
        inventory = parameters.get("inventory", self._inventory_file)
        if inventory:
            cmd.extend(["-i", inventory])

        # Forks
        forks = parameters.get("forks", self._forks)
        cmd.extend(["--forks", str(forks)])

        # Become (privilege escalation)
        become = parameters.get("become", self._become)
        if become:
            cmd.append("--become")
            become_user = parameters.get("become_user", self._become_user)
            cmd.extend(["--become-user", become_user])

        # Extra vars
        extra_vars = {**self._extra_vars, **parameters.get("extra_vars", {})}
        if extra_vars:
            cmd.extend(["-e", json.dumps(extra_vars)])

        # Tags
        tags = parameters.get("tags")
        if tags:
            cmd.extend(["--tags", ",".join(tags) if isinstance(tags, list) else tags])

        skip_tags = parameters.get("skip_tags")
        if skip_tags:
            cmd.extend(
                ["--skip-tags", ",".join(skip_tags) if isinstance(skip_tags, list) else skip_tags]
            )

        # Limit
        limit = parameters.get("limit")
        if limit:
            cmd.extend(["--limit", limit])

        # Check mode
        if parameters.get("check", False):
            cmd.append("--check")

        # Diff mode
        if parameters.get("diff", False):
            cmd.append("--diff")

        # Verbosity
        verbosity = parameters.get("verbosity", 0)
        if verbosity > 0:
            cmd.append("-" + "v" * min(verbosity, 4))

        return cmd

    def _generate_role_playbook(
        self,
        role_name: str,
        hosts: str,
        parameters: Dict[str, Any],
    ) -> str:
        """Generate a playbook to run a single role."""
        become = parameters.get("become", self._become)
        extra_vars = parameters.get("extra_vars", {})

        playbook = [
            {
                "name": f"Run role {role_name}",
                "hosts": hosts,
                "become": become,
                "roles": [
                    {
                        "role": role_name,
                        **extra_vars,
                    }
                ],
            }
        ]

        import yaml
        return yaml.dump(playbook, default_flow_style=False)

    async def _execute_ansible(
        self,
        cmd: List[str],
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Execute ansible command and capture output."""
        timeout = timeout or self._timeout_seconds

        # Set up environment
        env = os.environ.copy()
        env["ANSIBLE_FORCE_COLOR"] = "false"
        env["ANSIBLE_NOCOLOR"] = "true"
        env["ANSIBLE_STDOUT_CALLBACK"] = "json"  # JSON output for parsing

        started_at = datetime.utcnow()

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout,
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return {
                    "rc": -1,
                    "stdout": "",
                    "stderr": f"Execution timed out after {timeout} seconds",
                    "started_at": started_at,
                    "completed_at": datetime.utcnow(),
                    "timed_out": True,
                }

            completed_at = datetime.utcnow()

            return {
                "rc": process.returncode,
                "stdout": stdout.decode("utf-8", errors="replace"),
                "stderr": stderr.decode("utf-8", errors="replace"),
                "started_at": started_at,
                "completed_at": completed_at,
                "timed_out": False,
            }

        except Exception as e:
            logger.error("Ansible execution error", error=str(e))
            return {
                "rc": -1,
                "stdout": "",
                "stderr": str(e),
                "started_at": started_at,
                "completed_at": datetime.utcnow(),
                "timed_out": False,
            }

    def _parse_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Ansible execution result."""
        success = result["rc"] == 0 and not result.get("timed_out", False)

        # Try to parse JSON output
        stats = {}
        plays = []
        try:
            output = json.loads(result["stdout"])
            stats = output.get("stats", {})
            plays = output.get("plays", [])
        except json.JSONDecodeError:
            # Non-JSON output, use raw
            pass

        # Calculate duration
        duration = 0
        if result.get("started_at") and result.get("completed_at"):
            duration = int(
                (result["completed_at"] - result["started_at"]).total_seconds()
            )

        # Extract error message
        error = None
        if not success:
            if result.get("timed_out"):
                error = "Execution timed out"
            elif result.get("stderr"):
                error = result["stderr"][:500]
            elif result["rc"] != 0:
                error = f"Ansible exited with code {result['rc']}"

        return {
            "success": success,
            "rc": result["rc"],
            "duration_seconds": duration,
            "stats": stats,
            "plays": plays,
            "stdout": result["stdout"],
            "stderr": result["stderr"],
            "error": error,
            "timed_out": result.get("timed_out", False),
            "rollback_data": {
                "playbook_ran": True,
                "timestamp": result.get("started_at", datetime.utcnow()).isoformat(),
            },
        }

    async def list_playbooks(self) -> List[Dict[str, Any]]:
        """List available playbooks."""
        playbooks = []

        if not self._playbooks_dir.exists():
            return playbooks

        for path in self._playbooks_dir.glob("**/*.yml"):
            playbooks.append({
                "name": path.stem,
                "path": str(path.relative_to(self._playbooks_dir)),
                "full_path": str(path),
            })

        for path in self._playbooks_dir.glob("**/*.yaml"):
            playbooks.append({
                "name": path.stem,
                "path": str(path.relative_to(self._playbooks_dir)),
                "full_path": str(path),
            })

        return playbooks

    async def list_roles(self) -> List[Dict[str, Any]]:
        """List available roles."""
        roles = []

        if not self._roles_dir.exists():
            return roles

        for path in self._roles_dir.iterdir():
            if path.is_dir() and (path / "tasks" / "main.yml").exists():
                roles.append({
                    "name": path.name,
                    "path": str(path),
                })

        return roles

    async def validate_playbook(self, playbook_path: str) -> Dict[str, Any]:
        """Validate a playbook syntax."""
        path = self._resolve_playbook_path(playbook_path)
        if not path.exists():
            return {"valid": False, "error": f"Playbook not found: {path}"}

        cmd = ["ansible-playbook", str(path), "--syntax-check"]

        if self._inventory_file:
            cmd.extend(["-i", self._inventory_file])

        result = await self._execute_ansible(cmd, timeout=30)

        return {
            "valid": result["rc"] == 0,
            "error": result.get("stderr") if result["rc"] != 0 else None,
        }
