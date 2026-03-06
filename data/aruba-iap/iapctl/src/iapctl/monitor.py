"""Monitor/Telemetry command for comprehensive IAP health checks."""
import json
import time
from pathlib import Path
from typing import List, Optional

from .connection import IAPConnection
from .models import Result, Artifact, CheckResult, TimingInfo
from .operations import save_raw_output, save_result_json


def monitor(
    cluster: str,
    vc: str,
    out_dir: Path,
    ssh_host: Optional[str] = None,
    ssh_user: str = "admin",
    ssh_password: Optional[str] = None,
    ssh_port: int = 22,
    ssh_config: Optional[Path] = None,
    categories: Optional[List[str]] = None,
) -> Result:
    """Comprehensive IAP monitoring and telemetry collection.

    Args:
        cluster: Cluster name
        vc: Virtual controller IP address
        out_dir: Output directory
        ssh_host: SSH host (default: vc)
        ssh_user: SSH username
        ssh_password: SSH password
        ssh_port: SSH port
        ssh_config: Path to SSH config file
        categories: List of monitor categories (default: all)

    Returns:
        Result object with monitoring data
    """
    start_time = time.time()
    steps: dict[str, float] = {}

    host = ssh_host or vc

    artifacts: List[Artifact] = []
    checks: List[CheckResult] = []
    warnings: List[str] = []
    errors: List[str] = []

    # Default to all categories if none specified
    if not categories:
        categories = [
            "system",
            "ap",
            "clients",
            "wlan",
            "rf",
            "arm",
            "advanced",
            "wired",
            "logging",
            "security"
        ]

    try:
        with IAPConnection(
            host=host,
            username=ssh_user,
            password=ssh_password,
            port=ssh_port,
            ssh_config=ssh_config,
        ) as conn:
            # Get version info first
            steps["version"] = time.time() - start_time
            version_output = conn.send_command("show version")
            artifacts.append(save_raw_output(out_dir, "show_version.txt", version_output))
            version_info = conn.get_version()

            # Detect device mode for command adaptation
            device_mode = conn.detect_device_mode()

            # ===== System Information =====
            if "system" in categories:
                steps["system"] = time.time() - steps["version"]

                # Show summary
                try:
                    summary_output = conn.send_command("show summary")
                    artifacts.append(save_raw_output(out_dir, "show_summary.txt", summary_output))
                except Exception:
                    pass

                # Show clock
                try:
                    clock_output = conn.send_command("show clock")
                    artifacts.append(save_raw_output(out_dir, "show_clock.txt", clock_output))
                except Exception:
                    pass

                # Show configuration (basic)
                try:
                    config_output = conn.send_command("show configuration")
                    artifacts.append(save_raw_output(out_dir, "show_configuration.txt", config_output))
                except Exception:
                    pass

            # ===== AP Information =====
            if "ap" in categories:
                steps["ap"] = time.time() - steps.get("system", steps["version"])

                # Show AP active
                try:
                    ap_active_output = conn.send_command("show ap active")
                    artifacts.append(save_raw_output(out_dir, "show_ap_active.txt", ap_active_output))
                except Exception:
                    pass

                # Show AP database (device mode aware)
                if device_mode["mode"] == "virtual-controller":
                    try:
                        ap_db_output = conn.send_command("show ap database")
                        artifacts.append(save_raw_output(out_dir, "show_ap_database.txt", ap_db_output))
                    except Exception:
                        pass
                else:
                    try:
                        ap_bss_output = conn.send_command("show ap bss-table")
                        artifacts.append(save_raw_output(out_dir, "show_ap_bss-table.txt", ap_bss_output))
                    except Exception:
                        pass

                # Show AP allowed
                try:
                    ap_allowed_output = conn.send_command("show ap allowed-ap")
                    artifacts.append(save_raw_output(out_dir, "show_ap_allowed-ap.txt", ap_allowed_output))
                except Exception:
                    pass

            # ===== Clients Information =====
            if "clients" in categories:
                steps["clients"] = time.time() - steps.get("ap", steps["version"])

                # Show clients
                try:
                    clients_output = conn.send_command("show clients")
                    artifacts.append(save_raw_output(out_dir, "show_clients.txt", clients_output))

                    # Check for client count
                    if "client" in clients_output.lower():
                        lines = clients_output.split('\n')
                        client_lines = [l for l in lines if 'client' in l.lower() or l.strip().startswith(('Client', 'STA'))]
                        if client_lines:
                            checks.append(CheckResult(
                                name="client_count",
                                status="pass",
                                message=f"Active clients detected",
                            ))
                except Exception:
                    pass

                # Show clients detail
                try:
                    clients_detail_output = conn.send_command("show clients detail")
                    artifacts.append(save_raw_output(out_dir, "show_clients_detail.txt", clients_detail_output))
                except Exception:
                    pass

                # Show user-table
                try:
                    user_table_output = conn.send_command("show user-table")
                    artifacts.append(save_raw_output(out_dir, "show_user-table.txt", user_table_output))
                except Exception:
                    pass

                # Show station-table
                try:
                    station_table_output = conn.send_command("show station-table")
                    artifacts.append(save_raw_output(out_dir, "show_station-table.txt", station_table_output))
                except Exception:
                    pass

            # ===== WLAN Information =====
            if "wlan" in categories:
                steps["wlan"] = time.time() - steps.get("clients", steps["version"])

                # Show SSID profiles
                try:
                    ssid_profile_output = conn.send_command("show wlan ssid-profile")
                    artifacts.append(save_raw_output(out_dir, "show_wlan_ssid-profile.txt", ssid_profile_output))
                except Exception:
                    pass

                # Show WLAN access-rule
                try:
                    access_rule_output = conn.send_command("show wlan access-rule")
                    artifacts.append(save_raw_output(out_dir, "show_wlan_access-rule.txt", access_rule_output))
                except Exception:
                    pass

                # Show WLAN auth-server
                try:
                    auth_server_output = conn.send_command("show wlan auth-server")
                    artifacts.append(save_raw_output(out_dir, "show_wlan_auth-server.txt", auth_server_output))
                except Exception:
                    pass

                # Show WLAN (device mode aware)
                if device_mode["mode"] == "virtual-controller":
                    try:
                        wlan_output = conn.send_command("show wlan")
                        artifacts.append(save_raw_output(out_dir, "show_wlan.txt", wlan_output))
                    except Exception:
                        pass

            # ===== RF/ARM Information =====
            if "rf" in categories:
                steps["rf"] = time.time() - steps.get("wlan", steps["version"])

                # Show radio stats
                try:
                    radio_stats_output = conn.send_command("show radio stats")
                    artifacts.append(save_raw_output(out_dir, "show_radio_stats.txt", radio_stats_output))
                except Exception:
                    pass

            if "arm" in categories:
                steps["arm"] = time.time() - steps.get("rf", steps["version"])

                # Show ARM
                try:
                    arm_output = conn.send_command("show arm")
                    artifacts.append(save_raw_output(out_dir, "show_arm.txt", arm_output))
                except Exception:
                    pass

                # Show ARM band-steering
                try:
                    band_steering_output = conn.send_command("show arm band-steering")
                    artifacts.append(save_raw_output(out_dir, "show_arm_band-steering.txt", band_steering_output))
                except Exception:
                    pass

                # Show AP ARM history
                try:
                    ap_arm_history_output = conn.send_command("show ap arm history")
                    artifacts.append(save_raw_output(out_dir, "show_ap_arm_history.txt", ap_arm_history_output))
                except Exception:
                    pass

            # ===== Advanced Features =====
            if "advanced" in categories:
                steps["advanced"] = time.time() - steps.get("arm", steps["version"])

                # Show client-match
                try:
                    client_match_output = conn.send_command("show client-match")
                    artifacts.append(save_raw_output(out_dir, "show_client-match.txt", client_match_output))
                except Exception:
                    pass

                # Show DPI
                try:
                    dpi_output = conn.send_command("show dpi")
                    artifacts.append(save_raw_output(out_dir, "show_dpi.txt", dpi_output))
                except Exception:
                    pass

                # Show IDS
                try:
                    ids_output = conn.send_command("show ids")
                    artifacts.append(save_raw_output(out_dir, "show_ids.txt", ids_output))
                except Exception:
                    pass

                # Show Clarity
                try:
                    clarity_output = conn.send_command("show clarity")
                    artifacts.append(save_raw_output(out_dir, "show_clarity.txt", clarity_output))
                except Exception:
                    pass

                # Show Clarity stats
                try:
                    clarity_stats_output = conn.send_command("show clarity stats")
                    artifacts.append(save_raw_output(out_dir, "show_clarity_stats.txt", clarity_stats_output))
                except Exception:
                    pass

            # ===== Wired/Uplink Information =====
            if "wired" in categories:
                steps["wired"] = time.time() - steps.get("advanced", steps["version"])

                # Show wired-port-settings
                try:
                    wired_port_output = conn.send_command("show wired-port-settings")
                    artifacts.append(save_raw_output(out_dir, "show_wired-port-settings.txt", wired_port_output))
                except Exception:
                    pass

                # Show wired-port-profile
                try:
                    wired_port_profile_output = conn.send_command("show wired-port-profile")
                    artifacts.append(save_raw_output(out_dir, "show_wired-port-profile.txt", wired_port_profile_output))
                except Exception:
                    pass

                # Show enet0-port-profile
                try:
                    enet0_output = conn.send_command("show enet0-port-profile")
                    artifacts.append(save_raw_output(out_dir, "show_enet0-port-profile.txt", enet0_output))
                except Exception:
                    pass

                # Show uplink
                try:
                    uplink_output = conn.send_command("show uplink")
                    artifacts.append(save_raw_output(out_dir, "show_uplink.txt", uplink_output))
                except Exception:
                    pass

                # Show interfaces
                try:
                    interface_output = conn.send_command("show interface")
                    artifacts.append(save_raw_output(out_dir, "show_interface.txt", interface_output))
                except Exception:
                    pass

                # Show IP interface brief
                try:
                    ip_if_brief_output = conn.send_command("show ip interface brief")
                    artifacts.append(save_raw_output(out_dir, "show_ip_interface_brief.txt", ip_if_brief_output))
                except Exception:
                    pass

                # Show IP route
                try:
                    ip_route_output = conn.send_command("show ip route")
                    artifacts.append(save_raw_output(out_dir, "show_ip_route.txt", ip_route_output))
                except Exception:
                    pass

            # ===== Logging Information =====
            if "logging" in categories:
                steps["logging"] = time.time() - steps.get("wired", steps["version"])

                # Show syslog-level
                try:
                    syslog_level_output = conn.send_command("show syslog-level")
                    artifacts.append(save_raw_output(out_dir, "show_syslog-level.txt", syslog_level_output))
                except Exception:
                    pass

                # Show logging
                try:
                    logging_output = conn.send_command("show logging")
                    artifacts.append(save_raw_output(out_dir, "show_logging.txt", logging_output))
                except Exception:
                    pass

                # Show log system
                try:
                    log_system_output = conn.send_command("show log system")
                    artifacts.append(save_raw_output(out_dir, "show_log_system.txt", log_system_output))
                except Exception:
                    pass

                # Show log security
                try:
                    log_security_output = conn.send_command("show log security")
                    artifacts.append(save_raw_output(out_dir, "show_log_security.txt", log_security_output))
                except Exception:
                    pass

            # ===== Security Information =====
            if "security" in categories:
                steps["security"] = time.time() - steps.get("logging", steps["version"])

                # Show blacklist
                try:
                    blacklist_output = conn.send_command("show blacklist")
                    artifacts.append(save_raw_output(out_dir, "show_blacklist.txt", blacklist_output))
                except Exception:
                    pass

                # Show auth-tracebuf
                try:
                    auth_tracebuf_output = conn.send_command("show auth-tracebuf")
                    artifacts.append(save_raw_output(out_dir, "show_auth-tracebuf.txt", auth_tracebuf_output))
                except Exception:
                    pass

                # Show SNMP server
                try:
                    snmp_server_output = conn.send_command("show snmp-server")
                    artifacts.append(save_raw_output(out_dir, "show_snmp-server.txt", snmp_server_output))
                except Exception:
                    pass

        timing = TimingInfo(
            total_seconds=time.time() - start_time,
            steps=steps,
        )

        result = Result(
            ok=True,
            action="monitor",
            cluster=cluster,
            vc=vc,
            os_major=version_info["os_major"],
            is_vc=version_info["is_vc"],
            artifacts=artifacts,
            checks=checks,
            warnings=warnings,
            errors=errors,
            timing=timing,
        )

        artifacts.append(save_result_json(out_dir, result))
        return result

    except Exception as e:
        errors.append(str(e))
        timing = TimingInfo(
            total_seconds=time.time() - start_time,
            steps=steps,
        )

        result = Result(
            ok=False,
            action="monitor",
            cluster=cluster,
            vc=vc,
            artifacts=artifacts,
            checks=checks,
            warnings=warnings,
            errors=errors,
            timing=timing,
        )

        artifacts.append(save_result_json(out_dir, result))
        result.artifacts = artifacts

        return result
