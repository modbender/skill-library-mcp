#!/usr/bin/env python3
"""
CapRover API helper.

Usage:
    from caprover import CapRover, build_tar

    cap = CapRover("https://captain.x.example.com", "mypassword")
    cap.create_app("myapp")
    cap.update_app("myapp", ports=[{"hostPort": 25565, "containerPort": 7777}])
    cap.deploy_tar("myapp", "build.tar.gz")
    print(cap.runtime_logs("myapp"))
"""

import urllib.request
import urllib.error
import json
import ssl
import re
import os
import tarfile
import tempfile
from typing import Optional


def _make_ctx():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


class CapRover:
    def __init__(self, base_url: str, password: str):
        """
        Args:
            base_url: e.g. "https://captain.example.com"
            password: CapRover admin password
        """
        self.base = base_url.rstrip("/")
        self._ctx = _make_ctx()
        self.token = self._login(password)

    def _login(self, password: str) -> str:
        r = self._call("/api/v2/login", {"password": password})
        return r["data"]["token"]

    def _call(self, path: str, data=None, token: str = None, timeout: int = 120,
              raw_body: bytes = None, content_type: str = "application/json"):
        body = raw_body if raw_body else (json.dumps(data).encode() if data else None)
        headers = {"Content-Type": content_type}
        tok = token or getattr(self, "token", None)
        if tok:
            headers["x-captain-auth"] = tok
        req = urllib.request.Request(f"{self.base}{path}", data=body, headers=headers)
        try:
            resp = urllib.request.urlopen(req, context=self._ctx, timeout=timeout)
            return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            body = e.read().decode()[:400]
            raise RuntimeError(f"HTTP {e.code} {path}: {body}")

    # ── App lifecycle ──────────────────────────────────────────────────────

    def create_app(self, app_name: str, has_persistent_data: bool = False) -> dict:
        return self._call("/api/v2/user/apps/appDefinitions/register", {
            "appName": app_name,
            "hasPersistentData": has_persistent_data,
        })

    def delete_app(self, app_name: str, volumes: list = None) -> dict:
        return self._call("/api/v2/user/apps/appDefinitions/delete", {
            "appName": app_name,
            "volumes": volumes or [],
        })

    def get_apps(self) -> list:
        r = self._call("/api/v2/user/apps/appDefinitions")
        return r.get("data", {}).get("appDefinitions", [])

    def get_app(self, app_name: str) -> Optional[dict]:
        apps = self.get_apps()
        return next((a for a in apps if a.get("appName") == app_name), None)

    def update_app(self, app_name: str, **kwargs) -> dict:
        """
        Update app definition. Keyword args map to API fields:
            image_name, instance_count, env_vars, ports, volumes,
            service_update_override, container_http_port, force_ssl,
            has_persistent_data, not_expose_as_sub_domain

        Example:
            cap.update_app("myapp",
                env_vars=[{"key": "FOO", "value": "bar"}],
                ports=[{"hostPort": 25565, "containerPort": 7777}])
        """
        field_map = {
            "image_name": "imageName",
            "instance_count": "instanceCount",
            "env_vars": "envVars",
            "ports": "ports",
            "volumes": "volumes",
            "service_update_override": "serviceUpdateOverride",
            "container_http_port": "containerHttpPort",
            "force_ssl": "forceSsl",
            "has_persistent_data": "hasPersistentData",
            "not_expose_as_sub_domain": "notExposeAsSubDomain",
            "description": "description",
        }
        payload = {"appName": app_name}
        for k, v in kwargs.items():
            api_key = field_map.get(k, k)
            payload[api_key] = v
        return self._call("/api/v2/user/apps/appDefinitions/update", payload)

    def set_service_override(self, app_name: str, override: dict) -> dict:
        """Set Docker Swarm serviceUpdateOverride from a dict (auto-serializes to JSON string)."""
        return self.update_app(app_name, service_update_override=json.dumps(override))

    def clear_service_override(self, app_name: str) -> dict:
        """Clear serviceUpdateOverride (removes all Swarm overrides including mounts)."""
        return self.update_app(app_name, service_update_override="")

    # ── Deploy ─────────────────────────────────────────────────────────────

    def deploy_image(self, app_name: str, image_name: str) -> dict:
        """Deploy a pre-built Docker image."""
        self.update_app(app_name, image_name=image_name)
        return self._call(f"/api/v2/user/apps/appData/{app_name}/redeploy",
                          {"appName": app_name, "gitHash": ""})

    def deploy_tar(self, app_name: str, tar_path: str, timeout: int = 300) -> dict:
        """
        Build and deploy from a .tar.gz file containing captain-definition + Dockerfile.

        The tar must include:
            captain-definition  (JSON: {"schemaVersion": 2, "dockerfilePath": "./Dockerfile"})
            Dockerfile
            <any other files referenced by the Dockerfile>
        """
        with open(tar_path, "rb") as f:
            tar_data = f.read()

        boundary = "----CapRoverFormBoundary7MA4YW"
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="sourceFile"; filename="{os.path.basename(tar_path)}"\r\n'
            f"Content-Type: application/octet-stream\r\n\r\n"
        ).encode() + tar_data + f"\r\n--{boundary}--\r\n".encode()

        return self._call(
            f"/api/v2/user/apps/appData/{app_name}",
            raw_body=body,
            content_type=f"multipart/form-data; boundary={boundary}",
            timeout=timeout,
        )

    def redeploy(self, app_name: str) -> dict:
        """Force redeploy current image."""
        return self._call(f"/api/v2/user/apps/appData/{app_name}/redeploy",
                          {"appName": app_name, "gitHash": ""})

    # ── Logs ───────────────────────────────────────────────────────────────

    def build_logs(self, app_name: str) -> list:
        """Return list of build log lines from the most recent deploy."""
        r = self._call(f"/api/v2/user/apps/appData/{app_name}")
        return r.get("data", {}).get("logs", {}).get("lines", [])

    def runtime_logs(self, app_name: str, clean: bool = True) -> str:
        """
        Return runtime stdout/stderr of the running container.

        Args:
            clean: Strip Docker binary log headers (recommended).
        """
        r = self._call(f"/api/v2/user/apps/appData/{app_name}/logs")
        raw = r.get("data", {}).get("logs", "")
        if clean:
            raw = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', raw)
        return raw

    def tail_logs(self, app_name: str, n: int = 30) -> list:
        """Return last n unique lines of runtime logs."""
        raw = self.runtime_logs(app_name)
        lines = [l.strip() for l in raw.split('\n') if l.strip() and len(l.strip()) > 2]
        seen, out = set(), []
        for l in lines:
            k = l[:120]
            if k not in seen:
                seen.add(k)
                out.append(l)
        return out[-n:]

    # ── System ─────────────────────────────────────────────────────────────

    def system_info(self) -> dict:
        return self._call("/api/v2/user/system/info").get("data", {})

    def nodes(self) -> list:
        return self.system_info().get("nodes", [])


# ── Tar builder helper ────────────────────────────────────────────────────

def build_tar(output_path: str, files: dict, captain_definition: dict = None) -> str:
    """
    Build a deployable .tar.gz for CapRover.

    Args:
        output_path: Where to write the tar file.
        files: Dict of {filename: content_str_or_bytes}. Include "Dockerfile".
        captain_definition: Defaults to {"schemaVersion": 2, "dockerfilePath": "./Dockerfile"}.

    Returns:
        output_path

    Example:
        build_tar("deploy.tar.gz", {
            "Dockerfile": "FROM debian:slim\nCMD echo hello",
            "run.sh": "#!/bin/bash\necho running",
        })
    """
    if captain_definition is None:
        captain_definition = {"schemaVersion": 2, "dockerfilePath": "./Dockerfile"}

    all_files = {"captain-definition": json.dumps(captain_definition), **files}

    with tarfile.open(output_path, "w:gz") as tar:
        for name, content in all_files.items():
            if isinstance(content, str):
                content = content.encode()
            import io
            info = tarfile.TarInfo(name=name)
            info.size = len(content)
            tar.addfile(info, io.BytesIO(content))

    return output_path


# ── CLI usage ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: caprover.py <base_url> <password> [app_name]")
        sys.exit(1)

    cap = CapRover(sys.argv[1], sys.argv[2])
    print(f"Authenticated. Token: {cap.token[:20]}...")

    if len(sys.argv) >= 4:
        app = sys.argv[3]
        print(f"\n=== Runtime logs: {app} ===")
        for line in cap.tail_logs(app, 20):
            print(line)
    else:
        print("\n=== Apps ===")
        for a in cap.get_apps():
            print(f"  {a['appName']:30} image={a.get('imageName','<custom build>')}")
