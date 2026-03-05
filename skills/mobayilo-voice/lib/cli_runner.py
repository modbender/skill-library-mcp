import json
import os
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


class MobayiloCliError(RuntimeError):
    def __init__(self, message: str, exit_code: int, stdout: str, stderr: str):
        super().__init__(message)
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr


@dataclass
class CliResult:
    command: List[str]
    exit_code: int
    stdout: str
    stderr: str
    json: Optional[Any] = None


class CliRunner:
    def __init__(self, cli_path: Optional[str] = None, timeout: int = 30):
        self.cli_path = cli_path or os.environ.get("MOBY_CLI_PATH", "/usr/local/bin/moby")
        self.timeout = timeout

    def _extract_last_json_block(self, text: str) -> Optional[str]:
        if not text:
            return None

        blocks: List[str] = []
        start = None
        depth = 0
        in_string = False
        escaped = False

        for idx, ch in enumerate(text):
            if in_string:
                if escaped:
                    escaped = False
                elif ch == "\\":
                    escaped = True
                elif ch == '"':
                    in_string = False
                continue

            if ch == '"':
                in_string = True
                continue

            if ch == "{":
                if depth == 0:
                    start = idx
                depth += 1
            elif ch == "}" and depth > 0:
                depth -= 1
                if depth == 0 and start is not None:
                    blocks.append(text[start : idx + 1])
                    start = None

        if not blocks:
            return None
        return blocks[-1]

    def _resolve_command(self, args: List[str]) -> List[str]:
        binary = Path(self.cli_path).expanduser()
        if not binary.exists():
            raise FileNotFoundError(f"Mobayilo CLI not found at {binary}")
        return [str(binary), *args]

    def run(self, args: List[str], parse_json: bool = False, env: Optional[Dict[str, str]] = None) -> CliResult:
        command = self._resolve_command(args)
        merged_env = os.environ.copy()
        if env:
            merged_env.update(env)

        proc = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=merged_env,
            timeout=self.timeout,
            text=True,
            check=False,
        )

        stdout = proc.stdout.strip()
        stderr = proc.stderr.strip()

        result = CliResult(command=command, exit_code=proc.returncode, stdout=stdout, stderr=stderr)

        if proc.returncode != 0:
            raise MobayiloCliError(
                message=f"moby command failed: {' '.join(shlex.quote(part) for part in command)}",
                exit_code=proc.returncode,
                stdout=stdout,
                stderr=stderr,
            )

        if parse_json and stdout:
            try:
                result.json = json.loads(stdout)
            except json.JSONDecodeError:
                candidate = self._extract_last_json_block(stdout)
                if candidate:
                    try:
                        result.json = json.loads(candidate)
                        return result
                    except json.JSONDecodeError:
                        pass
                raise MobayiloCliError(
                    message=f"Failed to parse JSON output for command: {' '.join(command)}",
                    exit_code=proc.returncode,
                    stdout=stdout,
                    stderr="Could not locate valid JSON object in stdout",
                )

        return result
