#!/usr/bin/env python3
"""
environment-survey.py; conducts privacy-respecting environment detection for AI agent research.

Outputs a minimal JSON object to stdout. Designed to be reviewed by the user
before any data is sent anywhere.

What this script collects (and why):
  - os              : operating system family (linux / windows / macos / other)
  - arch            : CPU architecture (x86_64, arm64, …)
  - container       : whether a container runtime was detected, and which type
  - vm              : whether a hypervisor was detected, and which type
  - signals         : individual boolean indicators used to reach the above conclusions
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import subprocess
import sys
from typing import Any, Dict, Optional, Tuple


def run_cmd(cmd: list[str], timeout: float = 2.0) -> Tuple[int, str, str]:
    try:
        p = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            check=False,
        )
        return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()
    except FileNotFoundError:
        return 127, "", "not found"
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"
    except Exception as e:
        return 1, "", f"error: {e!r}"


def read_text(path: str, max_bytes: int = 64_000) -> Optional[str]:
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read(max_bytes)
    except Exception:
        return None


def file_exists(path: str) -> bool:
    try:
        return os.path.exists(path)
    except Exception:
        return False


def normalize_type(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s


def normalize_os_name(system_name: str) -> str:
    os_name = (system_name or "").strip().lower()
    if os_name == "darwin":
        return "macos"
    return os_name


def linux_detect_container() -> Tuple[Dict[str, Any], Dict[str, bool]]:
    """Returns (container_result, signals_dict)."""
    container_type = "none"

    # 1) systemd-detect-virt --container (use rc only, discard stdout)
    rc, out, _err = run_cmd(["systemd-detect-virt", "--container"])
    sdv_detected = rc == 0 and out and out != "none"
    if sdv_detected:
        container_type = normalize_type(out)

    # 2) Sentinel files
    has_dockerenv = file_exists("/.dockerenv")
    has_containerenv = file_exists("/run/.containerenv")

    if container_type == "none":
        if has_containerenv:
            container_type = "podman"
        elif has_dockerenv:
            container_type = "docker"

    # 3) cgroup hints
    cgroup1 = read_text("/proc/1/cgroup") or ""
    cgroup_self = read_text("/proc/self/cgroup") or ""
    cg = (cgroup1 + "\n" + cgroup_self).lower()
    cgroup_hints = bool(re.search(r"(docker|kubepods|containerd|podman|lxc|libpod)", cg))

    if container_type == "none" and cgroup_hints:
        container_type = "hint"

    # Note: /proc/1/sched first line is intentionally omitted (can expose process names)

    is_container = container_type != "none"
    signals = {
        "has_dockerenv": has_dockerenv,
        "has_containerenv": has_containerenv,
        "cgroup_hints": cgroup_hints,
    }
    return {"is_container": is_container, "type": container_type}, signals


def linux_detect_vm() -> Tuple[Dict[str, Any], Dict[str, bool]]:
    """Returns (vm_result, signals_dict)."""
    vm_type = "none"

    # 1) systemd-detect-virt --vm
    rc, out, _err = run_cmd(["systemd-detect-virt", "--vm"])
    if rc == 0 and out and out != "none":
        vm_type = normalize_type(out)

    # 2) virt-what (rc + stdout used for type, raw output discarded)
    if vm_type == "none":
        rc, out, _err = run_cmd(["virt-what"], timeout=3.0)
        if rc == 0 and out:
            types = [normalize_type(x) for x in out.splitlines() if x.strip()]
            if types:
                vm_type = types[0]

    # 3) DMI hints — only store boolean, never raw strings
    dmi_vendor = (read_text("/sys/class/dmi/id/sys_vendor") or "").strip()
    dmi_product = (read_text("/sys/class/dmi/id/product_name") or "").strip()
    dmi_version = (read_text("/sys/class/dmi/id/product_version") or "").strip()
    dmi_board = (read_text("/sys/class/dmi/id/board_vendor") or "").strip()
    dmi_blob = " ".join([dmi_vendor, dmi_product, dmi_version, dmi_board]).lower()
    dmi_vm_hints = bool(
        re.search(r"(vmware|virtualbox|kvm|qemu|xen|hyper-v|microsoft corporation|parallels|bochs)", dmi_blob)
    )
    # Raw DMI strings are intentionally dropped here.

    if vm_type == "none" and dmi_vm_hints:
        vm_type = "hint"

    # 4) CPU hypervisor flag
    cpuinfo = (read_text("/proc/cpuinfo") or "").lower()
    cpuinfo_hypervisor_flag = "hypervisor" in cpuinfo
    if vm_type == "none" and cpuinfo_hypervisor_flag:
        vm_type = "hint"

    is_vm = vm_type != "none"
    signals = {
        "dmi_vm_hints": dmi_vm_hints,
        "cpuinfo_hypervisor_flag": cpuinfo_hypervisor_flag,
    }
    return {"is_vm": is_vm, "type": vm_type}, signals

def macos_detect_container() -> Tuple[Dict[str, Any], Dict[str, bool]]:
    """
    macOS generally doesn't run Linux containers natively; most "containers on macOS"
    are actually Linux containers inside a Linux VM. Still, handle edge-cases safely:
    - sentinel files if present
    - cgroup hints if /proc happens to exist (some sandboxes / unusual setups)
    - very conservative env hints
    """
    container_type = "none"

    # 1) Sentinel files (rare on macOS host, but harmless to check)
    has_dockerenv = file_exists("/.dockerenv")
    has_containerenv = file_exists("/run/.containerenv")

    if has_containerenv:
        container_type = "podman"
    elif has_dockerenv:
        container_type = "docker"

    # 2) cgroup hints (normally absent on macOS; only used if files exist)
    cgroup_hints = False
    cgroup1 = read_text("/proc/1/cgroup")
    cgroup_self = read_text("/proc/self/cgroup")
    if cgroup1 or cgroup_self:
        cg = ((cgroup1 or "") + "\n" + (cgroup_self or "")).lower()
        cgroup_hints = bool(re.search(r"(docker|kubepods|containerd|podman|lxc|libpod)", cg))
        if container_type == "none" and cgroup_hints:
            container_type = "hint"

    # 3) Conservative env hint (avoid collecting env values; only check presence)
    # Some environments set a generic "container" marker.
    has_container_envvar = bool(os.environ.get("container"))
    if container_type == "none" and has_container_envvar:
        container_type = "hint"

    is_container = container_type != "none"
    signals = {
        "has_dockerenv": has_dockerenv,
        "has_containerenv": has_containerenv,
        "cgroup_hints": cgroup_hints,
    }
    return {"is_container": is_container, "type": container_type}, signals


def macos_detect_vm() -> Tuple[Dict[str, Any], Dict[str, bool]]:
    """
    macOS VM detection using:
      - sysctl CPU feature flags (Intel: VMM)
      - ioreg platform strings (vendor/product hints), but only keep boolean
    Raw strings are never stored in the output (privacy rule).
    """
    vm_type = "none"

    # 1) sysctl: hypervisor-related CPU flags (Intel Macs often expose "VMM")
    cpuinfo_hypervisor_flag = False
    for key in ("machdep.cpu.features", "machdep.cpu.leaf7_features"):
        rc, out, _err = run_cmd(["sysctl", "-n", key])
        if rc == 0 and out:
            # Only compute boolean; discard raw output
            if "vmm" in out.lower().split():
                cpuinfo_hypervisor_flag = True
                break

    if cpuinfo_hypervisor_flag:
        vm_type = "hint"

    # 2) ioreg: look for common VM vendor/product keywords (boolean only)
    dmi_vm_hints = False
    rc, out, _err = run_cmd(["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"], timeout=3.0)
    if rc == 0 and out:
        blob = out.lower()
        dmi_vm_hints = bool(
            re.search(
                r"(vmware|virtualbox|qemu|xen|parallels|bochs|hyper-v|microsoft corporation|kvm)",
                blob,
            )
        )
        # Raw ioreg output intentionally discarded after boolean extraction.
        if vm_type == "none" and dmi_vm_hints:
            vm_type = "hint"

    is_vm = vm_type != "none"
    signals = {
        "dmi_vm_hints": dmi_vm_hints,
        "cpuinfo_hypervisor_flag": cpuinfo_hypervisor_flag,
    }
    return {"is_vm": is_vm, "type": vm_type}, signals

def windows_powershell_json(ps_script: str, timeout: float = 4.0) -> Tuple[bool, Any, str]:
    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script]
    rc, out, err = run_cmd(cmd, timeout=timeout)
    if rc != 0:
        return False, None, f"rc={rc}"
    if not out:
        return False, None, "empty"
    try:
        return True, json.loads(out), ""
    except Exception as e:
        return False, None, f"parse error: {e!r}"


def windows_detect_container() -> Tuple[Dict[str, Any], Dict[str, bool]]:
    container_type = "none"
    csmp = os.environ.get("CONTAINER_SANDBOX_MOUNT_POINT", "")
    if csmp:
        container_type = "windows_container"

    is_container = container_type != "none"
    signals: Dict[str, bool] = {
        "has_dockerenv": False,
        "has_containerenv": False,
        "cgroup_hints": False,
    }
    return {"is_container": is_container, "type": container_type}, signals


def windows_detect_vm() -> Tuple[Dict[str, Any], Dict[str, bool]]:
    vm_type = "none"

    # Only extract HypervisorPresent bool and a vendor-hint bool; drop Name/Serial/BIOSVersion
    ps = r"""
$cs = Get-CimInstance Win32_ComputerSystem
$cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
$obj = [PSCustomObject]@{
  Manufacturer = $cs.Manufacturer
  Model = $cs.Model
  HypervisorPresent = $cpu.HypervisorPresent
}
$obj | ConvertTo-Json -Compress
"""
    ok, data, _err = windows_powershell_json(ps, timeout=6.0)
    hypervisor_present = False
    vendor_hint = False

    if ok and isinstance(data, dict):
        hypervisor_present = bool(data.get("HypervisorPresent", False))
        # Check vendor/model for VM keywords; raw strings are not stored
        blob = " ".join(str(data.get(k, "") or "") for k in ["Manufacturer", "Model"]).lower()
        vendor_hint = bool(
            re.search(r"(vmware|virtualbox|kvm|qemu|xen|hyper-v|microsoft corporation|parallels|bochs)", blob)
        )
        if hypervisor_present:
            vm_type = "hypervisor_present"
        elif vendor_hint:
            vm_type = "hint"

    is_vm = vm_type != "none"
    signals = {
        "dmi_vm_hints": vendor_hint,
        "cpuinfo_hypervisor_flag": hypervisor_present,
    }
    return {"is_vm": is_vm, "type": vm_type}, signals


def main() -> int:
    os_name = normalize_os_name(platform.system())
    arch = platform.machine()

    container_result: Dict[str, Any] = {}
    vm_result: Dict[str, Any] = {}
    signals: Dict[str, bool] = {
        "has_dockerenv": False,
        "has_containerenv": False,
        "cgroup_hints": False,
        "cpuinfo_hypervisor_flag": False,
        "dmi_vm_hints": False,
    }

    if os_name == "linux":
        container_result, c_signals = linux_detect_container()
        vm_result, v_signals = linux_detect_vm()
        signals.update(c_signals)
        signals.update(v_signals)
    elif os_name == "windows":
        container_result, c_signals = windows_detect_container()
        vm_result, v_signals = windows_detect_vm()
        signals.update(c_signals)
        signals.update(v_signals)
    elif os_name == "macos": 
        container_result, c_signals = macos_detect_container()
        vm_result, v_signals = macos_detect_vm()
        signals.update(c_signals)
        signals.update(v_signals)
    else:
        container_result = {"is_container": False, "type": "unsupported_os"}
        vm_result = {"is_vm": False, "type": "unsupported_os"}

    result = {
        "os": os_name,
        "arch": arch,
        "container": container_result,
        "vm": vm_result,
        "signals": signals,
    }

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
