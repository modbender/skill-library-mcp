#!/usr/bin/env python3
"""
Device analytics module for FileWave skill — Phase 5: Intelligence & Analytics.

Provides aggregation, grouping, and insight generation from inventory query data.
All operations are read-only and non-destructive.

Features:
- OS platform breakdown (macOS, Windows, iOS, Android, ChromeOS, etc.)
- OS version distribution within each platform
- Stale device detection (not seen in N days)
- Fleet summary statistics
"""

import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple


# ── OS Platform Classification ──────────────────────────────────────────────

# Map OperatingSystem_name prefixes to canonical platform names
PLATFORM_PATTERNS = [
    (re.compile(r"^macOS", re.IGNORECASE), "macOS"),
    (re.compile(r"^iOS", re.IGNORECASE), "iOS"),
    (re.compile(r"^iPadOS", re.IGNORECASE), "iPadOS"),
    (re.compile(r"^Windows", re.IGNORECASE), "Windows"),
    (re.compile(r"^Android", re.IGNORECASE), "Android"),
    (re.compile(r"^Chrome\s*OS", re.IGNORECASE), "ChromeOS"),
    (re.compile(r"^tvOS", re.IGNORECASE), "tvOS"),
    (re.compile(r"^watchOS", re.IGNORECASE), "watchOS"),
    (re.compile(r"^Linux", re.IGNORECASE), "Linux"),
]


def classify_platform(os_name: str) -> str:
    """Classify an OperatingSystem_name into a canonical platform.

    Args:
        os_name: Raw OS name from FileWave (e.g., "macOS 14 Sonoma")

    Returns:
        Canonical platform string (e.g., "macOS") or "Unknown"
    """
    if not os_name:
        return "Unknown"
    for pattern, platform in PLATFORM_PATTERNS:
        if pattern.search(os_name):
            return platform
    return "Unknown"


def parse_os_version(os_name: str, os_version: Optional[str] = None) -> str:
    """Extract a human-friendly OS version label.

    Prefers OperatingSystem_version when available, falls back to parsing
    the full OperatingSystem_name.

    Examples:
        ("macOS 14 Sonoma", "14.5")      → "14.5 (Sonoma)"
        ("macOS 15 Sequoia", "15.1.0")   → "15.1.0 (Sequoia)"
        ("Windows 10 Pro", None)          → "Windows 10 Pro"
        ("iOS", "17.2.1")                 → "17.2.1"
    """
    # macOS has nice codenames embedded in the name field
    codename_match = re.search(
        r"macOS\s+\d+\s+(\w+)", os_name or "", re.IGNORECASE
    )
    codename = codename_match.group(1) if codename_match else None

    if os_version:
        if codename:
            return f"{os_version} ({codename})"
        return os_version

    # Fallback: use the raw name
    return os_name or "Unknown"


# ── Device Row Helpers ──────────────────────────────────────────────────────

def rows_to_dicts(fields: List[str], values: List[List[Any]]) -> List[Dict[str, Any]]:
    """Convert FileWave column-oriented response to list of dicts."""
    return [
        {fields[i]: (row[i] if i < len(row) else None) for i in range(len(fields))}
        for row in values
    ]


def _get_field(device: Dict[str, Any], *candidates: str) -> Optional[str]:
    """Return the first non-None value from candidate field names."""
    for key in candidates:
        val = device.get(key)
        if val is not None:
            return str(val)
    return None


# ── Analytics Classes ───────────────────────────────────────────────────────

class PlatformBreakdown:
    """Aggregated platform/version counts."""

    def __init__(self):
        # platform → {version_label → count}
        self.platforms: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.total = 0

    def add_device(self, device: Dict[str, Any]):
        os_name = _get_field(device, "OperatingSystem_name", "os_name")
        os_version = _get_field(device, "OperatingSystem_version", "os_version")

        platform = classify_platform(os_name)
        version_label = parse_os_version(os_name, os_version)

        self.platforms[platform][version_label] += 1
        self.total += 1

    def platform_totals(self) -> List[Tuple[str, int]]:
        """Return [(platform, count)] sorted by count descending."""
        totals = [(p, sum(vers.values())) for p, vers in self.platforms.items()]
        return sorted(totals, key=lambda x: -x[1])

    def version_breakdown(self, platform: str) -> List[Tuple[str, int]]:
        """Return [(version_label, count)] for a platform, sorted by count desc."""
        vers = self.platforms.get(platform, {})
        return sorted(vers.items(), key=lambda x: -x[1])

    def format_text(self, *, show_versions: bool = True, indent: int = 2) -> str:
        """Pretty-print the breakdown."""
        pad = " " * indent
        lines = [f"Fleet Summary: {self.total} device(s)\n"]

        for platform, count in self.platform_totals():
            pct = (count / self.total * 100) if self.total else 0
            lines.append(f"{pad}{platform}: {count} ({pct:.0f}%)")

            if show_versions:
                for ver, vcount in self.version_breakdown(platform):
                    lines.append(f"{pad}  • {ver}: {vcount}")

        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        """Serializable dict for JSON output."""
        result = {"total": self.total, "platforms": {}}
        for platform, count in self.platform_totals():
            result["platforms"][platform] = {
                "count": count,
                "versions": dict(self.version_breakdown(platform)),
            }
        return result


class StaleDeviceReport:
    """Find devices not seen in N days."""

    def __init__(self, threshold_days: int = 30):
        self.threshold_days = threshold_days
        self.stale: List[Dict[str, Any]] = []
        self.active: List[Dict[str, Any]] = []
        self.unknown: List[Dict[str, Any]] = []  # no last-seen data

    def analyze(self, devices: List[Dict[str, Any]]):
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(days=self.threshold_days)

        for device in devices:
            last_seen_raw = _get_field(
                device,
                "Client_last_connected_to_fwxserver",
                "last_connected",
                "last_seen",
            )
            if not last_seen_raw:
                self.unknown.append(device)
                continue

            try:
                # ISO 8601 parse (handles 'Z' suffix and +00:00)
                last_seen_str = last_seen_raw.replace("Z", "+00:00")
                last_seen = datetime.fromisoformat(last_seen_str)
                if last_seen.tzinfo is None:
                    last_seen = last_seen.replace(tzinfo=timezone.utc)
            except (ValueError, TypeError):
                self.unknown.append(device)
                continue

            if last_seen < cutoff:
                self.stale.append(device)
            else:
                self.active.append(device)

    def format_text(self, indent: int = 2) -> str:
        pad = " " * indent
        total = len(self.stale) + len(self.active) + len(self.unknown)
        lines = [
            f"Stale Device Report (>{self.threshold_days} days)\n",
            f"{pad}Active:  {len(self.active)}",
            f"{pad}Stale:   {len(self.stale)}",
            f"{pad}Unknown: {len(self.unknown)}",
            f"{pad}Total:   {total}",
        ]

        if self.stale:
            lines.append(f"\n{pad}Stale Devices:")
            for device in self.stale[:20]:
                name = _get_field(device, "Client_device_name", "name") or "?"
                last_seen = _get_field(
                    device,
                    "Client_last_connected_to_fwxserver",
                    "last_connected",
                )
                lines.append(f"{pad}  • {name} (last seen: {last_seen})")
            if len(self.stale) > 20:
                lines.append(f"{pad}  ... and {len(self.stale) - 20} more")

        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "threshold_days": self.threshold_days,
            "active": len(self.active),
            "stale": len(self.stale),
            "unknown": len(self.unknown),
            "stale_devices": [
                {
                    "name": _get_field(d, "Client_device_name", "name"),
                    "last_seen": _get_field(
                        d, "Client_last_connected_to_fwxserver", "last_connected"
                    ),
                }
                for d in self.stale
            ],
        }


class DeviceInsights:
    """High-level analytics runner: call with raw API response data."""

    def __init__(self, fields: List[str], values: List[List[Any]]):
        self.devices = rows_to_dicts(fields, values)
        self.fields = fields

    @classmethod
    def from_device_dicts(cls, devices: List[Dict[str, Any]]):
        """Create from pre-parsed device dicts (e.g., from FileWaveClient.query_inventory)."""
        instance = cls.__new__(cls)
        instance.devices = devices
        instance.fields = list(devices[0].keys()) if devices else []
        return instance

    def platform_breakdown(self) -> PlatformBreakdown:
        breakdown = PlatformBreakdown()
        for device in self.devices:
            breakdown.add_device(device)
        return breakdown

    def stale_report(self, threshold_days: int = 30) -> StaleDeviceReport:
        report = StaleDeviceReport(threshold_days)
        report.analyze(self.devices)
        return report

    def field_summary(self, field: str) -> Dict[str, int]:
        """Generic count-by for any field."""
        counts: Dict[str, int] = defaultdict(int)
        for device in self.devices:
            val = device.get(field, "Unknown")
            counts[str(val) if val is not None else "Unknown"] += 1
        return dict(sorted(counts.items(), key=lambda x: -x[1]))


# ── Standalone test ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Quick self-test with sample data
    sample_fields = [
        "Client_device_name",
        "OperatingSystem_name",
        "OperatingSystem_version",
        "Client_last_connected_to_fwxserver",
    ]
    sample_values = [
        ["MacBook-1", "macOS 14 Sonoma", "14.5", "2026-02-12T14:00:00Z"],
        ["MacBook-2", "macOS 15 Sequoia", "15.1.0", "2026-02-10T10:00:00Z"],
        ["iPhone-1", "iOS", "17.2.1", "2026-01-01T00:00:00Z"],
        ["iPad-1", "iPadOS", "17.3", "2025-12-01T00:00:00Z"],
        ["Win-PC-1", "Windows 11 Pro", "23H2", "2026-02-12T12:00:00Z"],
    ]

    insights = DeviceInsights(sample_fields, sample_values)

    print("=" * 60)
    print("PLATFORM BREAKDOWN")
    print("=" * 60)
    breakdown = insights.platform_breakdown()
    print(breakdown.format_text())

    print()
    print("=" * 60)
    print("STALE DEVICE REPORT")
    print("=" * 60)
    report = insights.stale_report(threshold_days=30)
    print(report.format_text())
