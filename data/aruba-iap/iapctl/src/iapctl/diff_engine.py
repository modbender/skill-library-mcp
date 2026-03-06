"""Configuration diff and command generation."""
import json
from pathlib import Path
from typing import Dict, List, Optional

from .models import Changes, CommandSet
from .secrets import get_secret, redact_secret


def generate_commands(changes: Changes, resolve_secrets: bool = True) -> CommandSet:
    """Generate CLI commands from changes.

    Args:
        changes: Changes model with intent
        resolve_secrets: If True, resolve secret_ref to actual values

    Returns:
        CommandSet with commands to apply
    """
    commands = []
    rollback_commands = []
    secrets_to_redact = []

    for change in changes.changes:
        change_type = change.type

        if change_type == "ntp":
            # NTP configuration
            servers = change.servers
            for i, server in enumerate(servers, 1):
                commands.append(f"ntp server {i} {server}")
                rollback_commands.append(f"no ntp server {i}")

        elif change_type == "dns":
            # DNS configuration
            servers = change.servers
            for i, server in enumerate(servers, 1):
                commands.append(f"ip name-server {i} {server}")
                rollback_commands.append(f"no ip name-server {i}")

        elif change_type == "ssid_vlan":
            # SSID and VLAN configuration
            profile = change.profile
            essid = change.essid
            vlan_id = change.vlan_id

            commands.extend([
                f"wlan {profile}",
                f"  ssid {essid}",
                f"  vlan-id {vlan_id}",
                "  exit",
            ])

            rollback_commands.extend([
                f"no wlan {profile}",
            ])

        elif change_type == "radius_server":
            # RADIUS server configuration
            name = change.name
            ip = change.ip
            auth_port = change.auth_port
            acct_port = change.acct_port
            secret_ref = change.secret_ref

            # Resolve secret if requested
            secret_value = None
            if resolve_secrets:
                secret_value = get_secret(secret_ref)
                if secret_value:
                    secrets_to_redact.append(secret_value)

            # Use resolved secret or keep secret_ref placeholder
            key_value = secret_value if secret_value else f"secret_ref:{secret_ref}"

            commands.extend([
                f"radius-server {name}",
                f"  host {ip}",
                f"  auth-port {auth_port}",
                f"  acct-port {acct_port}",
                f"  key {key_value}",
                "  exit",
            ])

            rollback_commands.extend([
                f"no radius-server {name}",
            ])

        elif change_type == "ssid_bind_radius":
            # SSID to RADIUS binding
            profile = change.profile
            radius_primary = change.radius_primary
            radius_secondary = change.radius_secondary

            commands.extend([
                f"wlan {profile}",
                f"  auth-server {radius_primary}",
            ])

            if radius_secondary:
                commands.append(f"  auth-server {radius_secondary}")

            commands.append("  exit")

            rollback_commands.extend([
                f"wlan {profile}",
                "  no auth-server",
                "  exit",
            ])

        elif change_type == "rf_template":
            # RF template configuration
            template = change.template

            # Templates are pre-defined, just apply
            commands.append(f"rf-profile {template}")
            rollback_commands.append("no rf-profile")

        elif change_type == "snmp_community":
            # SNMP community configuration
            # Note: Aruba IAP doesn't support ro/rw parameter, just community string
            community = change.community_string

            commands.append(f"snmp-server community {community}")
            rollback_commands.append(f"no snmp-server community {community}")

        elif change_type == "snmp_host":
            # SNMP host configuration
            host_ip = change.host_ip
            version = change.version
            community = change.community_string
            is_inform = change.inform

            # Build command
            cmd_parts = [f"snmp-server host {host_ip}", f"version {version}"]
            if community:
                cmd_parts.append(community)
            if is_inform:
                cmd_parts.append("inform")

            commands.append(" ".join(cmd_parts))

            # Rollback - need to know the community to remove
            if community:
                rollback_commands.append(f"no snmp-server host {host_ip}")
            else:
                rollback_commands.append(f"no snmp-server host {host_ip}")

        elif change_type == "syslog_level":
            # Syslog level configuration
            level = change.level
            categories = change.categories

            # Configure syslog level for each category
            for category in categories:
                commands.append(f"syslog-level {level} {category}")

            # Rollback - restore to default (warn)
            for category in categories:
                rollback_commands.append(f"syslog-level warn {category}")

        elif change_type == "ssid_profile":
            # Complete SSID profile configuration
            profile_name = change.profile_name
            essid = change.essid
            opmode = change.opmode
            wpa_passphrase = change.wpa_passphrase
            vlan = change.vlan
            rf_band = change.rf_band

            # Build SSID profile commands for Aruba IAP
            # Format: flat list for config mode (no indentation)
            commands.extend([
                f"wlan ssid-profile {profile_name}",
                "enable",
                "type employee",
                f"essid {essid}",
                f"opmode {opmode}",
                f"vlan {vlan}",
                f"rf-band {rf_band}",
                "captive-portal disable",
                "dtim-period 1",
                "broadcast-filter none",
                "dmo-channel-utilization-threshold 90",
                "local-probe-req-thresh 0",
                "max-clients-threshold 64",
            ])

            # Add WPA passphrase if provided
            if wpa_passphrase:
                commands.append(f"wpa-passphrase {wpa_passphrase}")

            commands.append("exit")  # Exit SSID profile mode

            # Rollback - remove the SSID profile
            rollback_commands.append(f"no wlan ssid-profile {profile_name}")

        elif change_type == "auth_server":
            # Authentication server (RADIUS/CPPM) configuration
            server_name = change.server_name
            ip = change.ip
            port = change.port
            acct_port = change.acct_port
            secret_ref = change.secret_ref
            nas_id_type = change.nas_id_type

            # Resolve secret if requested
            secret_value = None
            if resolve_secrets:
                secret_value = get_secret(secret_ref)
                if secret_value:
                    secrets_to_redact.append(secret_value)

            # Use resolved secret or keep secret_ref placeholder
            key_value = secret_value if secret_value else f"secret_ref:{secret_ref}"

            # Build commands
            commands.extend([
                f"wlan auth-server {server_name}",
                f"  ip {ip}",
                f"  port {port}",
                f"  acctport {acct_port}",
                f"  key {key_value}",
                f"  nas-id {nas_id_type}",
                "  exit",
            ])

            # Rollback - remove the auth server
            rollback_commands.append(f"no wlan auth-server {server_name}")

        elif change_type == "ap_allowlist":
            # AP allowlist configuration
            action = change.action
            mac_address = change.mac_address

            if action == "add":
                commands.append(f"allowed-ap {mac_address}")
                rollback_commands.append(f"no allowed-ap {mac_address}")
            elif action == "remove":
                commands.append(f"no allowed-ap {mac_address}")
                rollback_commands.append(f"allowed-ap {mac_address}")

        elif change_type == "wired_port_profile":
            # Wired port profile configuration
            profile_name = change.profile_name
            switchport_mode = change.switchport_mode
            native_vlan = change.native_vlan
            access_rule_name = change.access_rule_name
            is_shutdown = change.shutdown

            # Build wired port profile commands
            commands.extend([
                f"wired-port-profile {profile_name}",
                f"  switchport-mode {switchport_mode}",
                f"  native-vlan {native_vlan}",
            ])

            if access_rule_name:
                commands.append(f"  access-rule-name {access_rule_name}")

            if is_shutdown:
                commands.append("  shutdown")
            else:
                commands.append("  no shutdown")

            commands.append("  exit")

            # Rollback - remove the wired port profile
            rollback_commands.append(f"no wired-port-profile {profile_name}")

        elif change_type == "ssid_delete":
            # Delete SSID profile
            profile_name = change.profile_name

            # Command to remove SSID profile
            commands.append(f"no wlan ssid-profile {profile_name}")

            # Rollback - cannot easily recreate without full config
            # Just warn that deletion cannot be easily rolled back
            rollback_commands.append("# WARNING: SSID deletion cannot be easily rolled back")

    command_set = CommandSet(
        commands=commands,
        change_id="",  # Will be set by caller
        rollback_commands=rollback_commands,
    )

    # Attach secrets to redact as metadata
    if secrets_to_redact:
        command_set.metadata = {"secrets_to_redact": secrets_to_redact}

    return command_set


def diff_config(
    current_config: str,
    changes: Changes,
    change_id: str,
) -> CommandSet:
    """Generate diff between current config and desired changes.

    Args:
        current_config: Current running configuration
        changes: Desired changes
        change_id: Change ID for audit trail

    Returns:
        CommandSet with commands to apply
    """
    command_set = generate_commands(changes)
    command_set.change_id = change_id
    
    return command_set


def save_command_set(
    command_set: CommandSet,
    out_dir: Path,
) -> None:
    """Save command set to files.

    Args:
        command_set: Command set to save
        out_dir: Output directory
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Save commands
    commands_file = out_dir / "commands.json"
    commands_file.write_text(command_set.model_dump_json(indent=2))
    
    # Save as plain text for human review
    commands_txt = out_dir / "commands.txt"
    lines = [f"# Change ID: {command_set.change_id}"]
    lines.append("# Commands to apply:")
    lines.extend(command_set.commands)
    lines.append("")
    lines.append("# Rollback commands:")
    lines.extend(command_set.rollback_commands)
    commands_txt.write_text("\n".join(lines))


def assess_risks(command_set: CommandSet) -> Dict:
    """Assess risks of applying commands.

    Args:
        command_set: Command set to assess

    Returns:
        Risk assessment dict
    """
    risks = {
        "level": "low",
        "warnings": [],
        "concerns": [],
    }

    commands_text = " ".join(command_set.commands).lower()

    # Check for high-risk operations
    if "no wlan" in commands_text or "no radius" in commands_text:
        risks["level"] = "medium"
        risks["warnings"].append("Removing WLAN or RADIUS configuration may disconnect users")

    if "no snmp-server" in commands_text:
        risks["level"] = "medium"
        risks["warnings"].append("Removing SNMP configuration may affect monitoring systems")

    if "syslog-level debug" in commands_text:
        risks["warnings"].append("Debug syslog level may generate excessive logs and affect performance")

    if "wpa-passphrase" in commands_text:
        risks["warnings"].append("WPA passphrase changes will require clients to re-authenticate")

    if "allowed-ap" in commands_text:
        risks["concerns"].append("AP allowlist changes may prevent APs from joining the cluster")

    if "wired-port-profile" in commands_text:
        risks["concerns"].append("Wired port profile changes may affect wired client connectivity")

    if "vlan-id" in commands_text or "native-vlan" in commands_text:
        risks["concerns"].append("VLAN changes may affect network connectivity")

    # Check for many changes
    if len(command_set.commands) > 20:
        risks["level"] = "medium" if risks["level"] == "low" else "high"
        risks["warnings"].append("Large number of changes - consider applying in stages")

    # Check for shutdown operations
    if "shutdown" in commands_text and "no shutdown" not in commands_text:
        risks["warnings"].append("Shutdown operations detected - verify intended behavior")

    return risks
