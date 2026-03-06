"""Data models for iapctl."""
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class CheckResult(BaseModel):
    """Result of a verification check."""
    name: str
    status: str = Field(..., pattern="^(pass|fail|warning|skip)$")
    message: str
    details: Optional[Dict] = None


class TimingInfo(BaseModel):
    """Timing information for operations."""
    total_seconds: float
    steps: Dict[str, float] = Field(default_factory=dict)


class Artifact(BaseModel):
    """Generated file artifact."""
    name: str
    path: str
    size_bytes: int
    content_type: str


class Result(BaseModel):
    """Unified result format for all iapctl operations."""
    ok: bool
    action: str = Field(..., pattern="^(discover|snapshot|diff|apply|verify|rollback|monitor)$")
    cluster: str
    vc: str
    os_major: Optional[str] = None
    is_vc: Optional[bool] = None
    artifacts: List[Artifact] = Field(default_factory=list)
    checks: List[CheckResult] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    timing: TimingInfo
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    class Config:
        json_schema_extra = {
            "example": {
                "ok": True,
                "action": "snapshot",
                "cluster": "office-iap",
                "vc": "10.10.10.5",
                "os_major": "8",
                "is_vc": True,
                "artifacts": [
                    {
                        "name": "result.json",
                        "path": "./out/snapshot/result.json",
                        "size_bytes": 1024,
                        "content_type": "application/json"
                    }
                ],
                "checks": [],
                "warnings": [],
                "errors": [],
                "timing": {"total_seconds": 2.5},
                "timestamp": "2026-02-22T10:30:00.000Z"
            }
        }


class NTPChange(BaseModel):
    """NTP configuration change."""
    type: str = "ntp"
    servers: List[str]


class DNSChange(BaseModel):
    """DNS configuration change."""
    type: str = "dns"
    servers: List[str]


class SsidVlanChange(BaseModel):
    """SSID and VLAN configuration change."""
    type: str = "ssid_vlan"
    profile: str
    essid: str
    vlan_id: int


class RadiusServerChange(BaseModel):
    """RADIUS server configuration change."""
    type: str = "radius_server"
    name: str
    ip: str
    auth_port: int = 1812
    acct_port: int = 1813
    secret_ref: str = Field(..., description="Reference to secret storage, not plain text")


class SsidBindRadiusChange(BaseModel):
    """SSID to RADIUS binding change."""
    type: str = "ssid_bind_radius"
    profile: str
    radius_primary: str
    radius_secondary: Optional[str] = None


class RfTemplateChange(BaseModel):
    """RF template configuration change."""
    type: str = "rf_template"
    template: str = Field(..., pattern="^(office-default|high-density|conference|corridor)$")


class SnmpCommunityChange(BaseModel):
    """SNMP community configuration change."""
    type: str = "snmp_community"
    community_string: str
    access: str = Field(default="ro", pattern="^(ro|rw)$")


class SnmpHostChange(BaseModel):
    """SNMP host configuration change."""
    type: str = "snmp_host"
    host_ip: str
    version: str = Field(default="2c", pattern="^(1|2c|3)$")
    community_string: Optional[str] = None
    inform: bool = False


class SyslogLevelChange(BaseModel):
    """Syslog level configuration change."""
    type: str = "syslog_level"
    level: str = Field(..., pattern="^(emergency|alert|critical|error|warning|notice|info|debug)$")
    categories: List[str] = Field(
        default_factory=lambda: ["ap-debug", "network", "security", "system", "user", "user-debug", "wireless"]
    )


class SsidProfileChange(BaseModel):
    """Complete SSID profile configuration change."""
    type: str = "ssid_profile"
    profile_name: str
    essid: str
    opmode: str = Field(default="wpa2-psk-aes", pattern="^(wpa2-psk-aes|wpa2-enterprise|open)$")
    wpa_passphrase: Optional[str] = None
    vlan: int = Field(default=1)
    rf_band: str = Field(default="all", pattern="^(all|2.4|5|6)$")


class AuthServerChange(BaseModel):
    """Authentication server (RADIUS/CPPM) configuration change."""
    type: str = "auth_server"
    server_name: str
    ip: str
    port: int = Field(default=1812)
    acct_port: int = Field(default=1813)
    secret_ref: str = Field(..., description="Reference to secret storage")
    nas_id_type: str = Field(default="mac", pattern="^(mac|ip|serial)$")


class ApAllowlistChange(BaseModel):
    """AP allowlist configuration change."""
    type: str = "ap_allowlist"
    action: str = Field(..., pattern="^(add|remove)$")
    mac_address: str = Field(..., pattern="^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$")


class WiredPortProfileChange(BaseModel):
    """Wired port profile configuration change."""
    type: str = "wired_port_profile"
    profile_name: str
    switchport_mode: str = Field(default="access", pattern="^(access|trunk)$")
    native_vlan: int = Field(default=1)
    access_rule_name: Optional[str] = None
    shutdown: bool = False


class SsidDeleteChange(BaseModel):
    """Delete SSID profile change."""
    type: str = "ssid_delete"
    profile_name: str


# Union type for all change types
Change = (
    NTPChange | DNSChange | SsidVlanChange |
    RadiusServerChange | SsidBindRadiusChange | RfTemplateChange |
    SnmpCommunityChange | SnmpHostChange | SyslogLevelChange |
    SsidProfileChange | AuthServerChange | ApAllowlistChange |
    WiredPortProfileChange | SsidDeleteChange
)


class Changes(BaseModel):
    """Intent model for configuration changes."""
    changes: List[Change]
    metadata: Optional[Dict] = None


class CommandSet(BaseModel):
    """Set of CLI commands to apply."""
    commands: List[str]
    change_id: str
    rollback_commands: List[str] = Field(default_factory=list)
    metadata: Optional[Dict] = Field(default_factory=dict)
