from __future__ import annotations

import importlib.util
import ipaddress
import os
import socket
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib import error, request
from urllib.parse import urlparse

HELPER_SCRIPT = Path(__file__).with_name("larksync_skill_helper.py")
DEFAULT_PORT = 8000
DEFAULT_TIMEOUT = 1.5
HEALTH_PATH = "/health"
KNOWN_COMMANDS = {
    "check",
    "configure-download",
    "create-task",
    "run-task",
    "bootstrap-daily",
}


@dataclass(frozen=True)
class ProbeResult:
    name: str
    base_url: str
    connect_ok: bool
    health_ok: bool
    health_status: int | None
    latency_ms: int | None
    error: str | None


def is_wsl() -> bool:
    if os.getenv("WSL_DISTRO_NAME"):
        return True
    try:
        content = Path("/proc/version").read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return False
    lowered = content.lower()
    return "microsoft" in lowered or "wsl" in lowered


def parse_default_gateway(route_text: str) -> str | None:
    for raw in route_text.splitlines():
        line = raw.strip()
        if not line or not line.startswith("default"):
            continue
        parts = line.split()
        for index, part in enumerate(parts):
            if part == "via" and index + 1 < len(parts):
                value = parts[index + 1].strip()
                if value:
                    return value
    return None


def _parse_ipv4_hex_le(raw: str) -> str | None:
    value = raw.strip()
    if len(value) != 8:
        return None
    try:
        octets = [str(int(value[index:index + 2], 16)) for index in range(6, -2, -2)]
    except ValueError:
        return None
    return ".".join(octets)


def parse_proc_net_route(text: str) -> str | None:
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.lower().startswith("iface"):
            continue
        parts = line.split()
        if len(parts) < 3:
            continue
        destination = parts[1].strip()
        gateway = parts[2].strip()
        if destination != "00000000":
            continue
        parsed = _parse_ipv4_hex_le(gateway)
        if parsed:
            return parsed
    return None


def parse_resolv_nameservers(text: str) -> list[str]:
    result: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if not line.lower().startswith("nameserver"):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        value = parts[1].strip()
        if value:
            result.append(value)
    return result


def _read_default_gateway() -> str | None:
    proc_route = Path("/proc/net/route")
    if proc_route.is_file():
        try:
            return parse_proc_net_route(
                proc_route.read_text(encoding="utf-8", errors="ignore")
            )
        except Exception:
            return None
    return None


def _read_resolv_nameservers() -> list[str]:
    try:
        content = Path("/etc/resolv.conf").read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []
    return parse_resolv_nameservers(content)


def candidate_base_urls(port: int = DEFAULT_PORT) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = [
        ("localhost", f"http://localhost:{port}"),
        ("loopback-ipv4", f"http://127.0.0.1:{port}"),
        ("docker-host-alias", f"http://host.docker.internal:{port}"),
    ]
    gateway = _read_default_gateway()
    if gateway:
        pairs.append(("default-gateway", f"http://{gateway}:{port}"))
    for index, ns in enumerate(_read_resolv_nameservers(), start=1):
        pairs.append((f"resolv-nameserver-{index}", f"http://{ns}:{port}"))

    deduped: list[tuple[str, str]] = []
    seen: set[str] = set()
    for name, base_url in pairs:
        if base_url in seen:
            continue
        seen.add(base_url)
        deduped.append((name, base_url))
    return deduped


def _probe_single(name: str, base_url: str, timeout: float = DEFAULT_TIMEOUT) -> ProbeResult:
    parsed = urlparse(base_url)
    host = parsed.hostname or ""
    port = parsed.port or 80
    connect_ok = False
    health_ok = False
    status: int | None = None
    error_text: str | None = None
    start = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            connect_ok = True
        health_url = f"{base_url.rstrip('/')}{HEALTH_PATH}"
        req = request.Request(health_url, headers={"Accept": "application/json"}, method="GET")
        with request.urlopen(req, timeout=timeout) as resp:
            status = int(resp.getcode())
            health_ok = status == 200
            if not health_ok:
                error_text = f"health HTTP {status}"
    except error.HTTPError as exc:
        status = int(exc.code)
        error_text = f"health HTTP {exc.code}"
    except Exception as exc:  # noqa: BLE001
        error_text = f"{type(exc).__name__}: {exc}"
    latency_ms = int((time.perf_counter() - start) * 1000)
    return ProbeResult(
        name=name,
        base_url=base_url,
        connect_ok=connect_ok,
        health_ok=health_ok,
        health_status=status,
        latency_ms=latency_ms,
        error=error_text,
    )


def diagnose_wsl_endpoints(timeout: float = DEFAULT_TIMEOUT) -> list[ProbeResult]:
    return [_probe_single(name, base_url, timeout=timeout) for name, base_url in candidate_base_urls()]


def select_reachable_base_url(results: Iterable[ProbeResult]) -> str | None:
    for item in results:
        if item.health_ok:
            return item.base_url
    return None


def _is_loopback_host(host: str) -> bool:
    if host.lower() == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def _extract_base_url(args: list[str]) -> str | None:
    for index, arg in enumerate(args):
        if arg == "--base-url":
            if index + 1 < len(args):
                return args[index + 1].strip()
            return None
        if arg.startswith("--base-url="):
            return arg.split("=", 1)[1].strip()
    return None


def _find_command_index(args: list[str]) -> int:
    for index, arg in enumerate(args):
        if arg in KNOWN_COMMANDS:
            return index
    for index, arg in enumerate(args):
        if not arg.startswith("-"):
            return index
    return len(args)


def ensure_remote_allow_flag(args: list[str]) -> list[str]:
    base_url = _extract_base_url(args)
    if not base_url:
        return list(args)
    parsed = urlparse(base_url)
    host = parsed.hostname or ""
    if not host or _is_loopback_host(host):
        return list(args)
    if "--allow-remote-base-url" in args:
        return list(args)
    patched = list(args)
    insert_at = _find_command_index(patched)
    patched.insert(insert_at, "--allow-remote-base-url")
    return patched


def _inject_base_url(args: list[str], base_url: str) -> list[str]:
    patched = list(args)
    insert_at = _find_command_index(patched)
    patched[insert_at:insert_at] = ["--base-url", base_url]
    return patched


def _print_diagnostics(results: list[ProbeResult]) -> None:
    print("WSL -> LarkSync 连接诊断:")
    for item in results:
        if item.health_ok:
            status = "OK"
        elif item.connect_ok:
            status = "PORT_OPEN_HEALTH_FAIL"
        else:
            status = "UNREACHABLE"
        health_part = str(item.health_status) if item.health_status is not None else "-"
        latency = f"{item.latency_ms}ms" if item.latency_ms is not None else "-"
        detail = item.error or "-"
        print(
            f"  - [{status}] {item.name}: {item.base_url} "
            f"(health={health_part}, latency={latency}, detail={detail})"
        )


def _load_inner_helper():
    spec = importlib.util.spec_from_file_location("larksync_skill_helper", HELPER_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载 helper 脚本: {HELPER_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _run_inner_helper(args: list[str]) -> int:
    module = _load_inner_helper()
    return int(module.main(args))


def _print_help() -> None:
    print("用法:")
    print("  python larksync_wsl_helper.py diagnose")
    print("  python larksync_wsl_helper.py <larksync_skill_helper 参数...>")
    print("")
    print("说明:")
    print("  - 在 WSL 下未指定 --base-url 时，会自动探测 Windows 宿主机可达地址。")
    print("  - 若检测到远程 base-url，会自动补充 --allow-remote-base-url。")
    print("  - 本脚本不会自动安装依赖，也不会自动拉起后端。")


def main(argv: list[str] | None = None) -> int:
    final_args = list(argv if argv is not None else sys.argv[1:])
    if not final_args or final_args[0] in {"-h", "--help"}:
        _print_help()
        return 0

    if final_args[0] == "diagnose":
        results = diagnose_wsl_endpoints()
        _print_diagnostics(results)
        return 0 if select_reachable_base_url(results) else 2

    if is_wsl() and _extract_base_url(final_args) is None:
        diagnostics = diagnose_wsl_endpoints()
        selected = select_reachable_base_url(diagnostics)
        _print_diagnostics(diagnostics)
        if not selected:
            print("未找到可达的 LarkSync 服务地址（:8000）。请先在 Windows 侧启动 LarkSync。")
            print("排查建议：")
            print("  1) Windows 端确认 LarkSync 后端已启动。")
            print("  2) Windows 端若手动设置过 LARKSYNC_BACKEND_BIND_HOST=127.0.0.1，请移除该变量或改为 0.0.0.0 后重启 LarkSync。")
            print("  3) 放行 Windows 防火墙 TCP 8000（WSL 网段）。")
            return 2
        print(f"自动选择可达地址: {selected}")
        final_args = _inject_base_url(final_args, selected)

    final_args = ensure_remote_allow_flag(final_args)
    return _run_inner_helper(final_args)


if __name__ == "__main__":
    raise SystemExit(main())
