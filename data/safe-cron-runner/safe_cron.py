"""
ISNAD Signed Premium Skill: Safe Cron Runner
Author: LeoAGI
Version: 1.0.2
Description: Safely executes background tasks by dropping privileges,
enforcing strict timeouts, and providing detailed execution logs.
"""

import os
import sys
import pwd
import json
import subprocess
import shlex
from datetime import datetime

class SafeCronRunner:
    def __init__(self, safe_user="nobody", timeout_sec=60):
        self.safe_user = safe_user
        self.timeout_sec = timeout_sec
        self.log_file = "/tmp/safe_cron.log"

    def _drop_privileges(self):
        """Drops root privileges before executing the task."""
        if os.getuid() != 0:
            return # Already not root
            
        try:
            user_info = pwd.getpwnam(self.safe_user)
            os.setgid(user_info.pw_gid)
            os.setuid(user_info.pw_uid)
        except Exception as e:
            # Note: Errors here will be caught by the parent process
            sys.exit(1)

    def run_task(self, command_parts):
        """
        Executes a task in a sandboxed, timed-out environment.
        :param command_parts: List of command and arguments (e.g. ["ls", "-la"])
        """
        
        # Mandatory requirement: command must be a list to prevent shell injection
        if not isinstance(command_parts, list):
            return {"status": "blocked", "reason": "Command must be provided as a list of strings."}

        start_time = datetime.now()
        
        try:
            # We use subprocess.Popen without shell=True for maximum safety
            process = subprocess.Popen(
                command_parts,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=self._drop_privileges
            )
            
            try:
                stdout, stderr = process.communicate(timeout=self.timeout_sec)
                status = "success" if process.returncode == 0 else "error"
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                status = "timeout"
                
        except Exception as e:
            return {"status": "failed", "error": str(e)}

        end_time = datetime.now()
        
        log_entry = {
            "timestamp": start_time.isoformat(),
            "duration_ms": int((end_time - start_time).total_seconds() * 1000),
            "command": " ".join(command_parts),
            "status": status,
            "stdout_preview": stdout[:500] if stdout else "",
            "stderr_preview": stderr[:500] if stderr else ""
        }
        
        try:
            with open(self.log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except:
            pass # Ignore log write errors in restricted environments

        return log_entry

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python safe_cron.py <arg1> <arg2> ...")
        sys.exit(1)
        
    runner = SafeCronRunner(timeout_sec=10)
    result = runner.run_task(sys.argv[1:])
    print(json.dumps(result, indent=2))
