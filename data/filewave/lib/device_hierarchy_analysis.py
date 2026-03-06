#!/usr/bin/env python3
"""
Advanced Device Hierarchy Analysis - Phase 4.2

Performs system-wide analysis of device clone patterns and generates
optimization recommendations.
"""

import requests
import json
from typing import Dict, List, Optional
from device_hierarchy import DeviceHierarchyAnalyzer, DeviceHierarchyInfo
from api_utils import normalize_server_url, create_filewave_session, safe_api_request


class ClonePatternAnalyzer:
    """Analyzes clone patterns across multiple devices"""
    
    def __init__(self, server: str, token: str):
        self.server = normalize_server_url(server)
        self.token = token
        self.analyzer = DeviceHierarchyAnalyzer(server, token)
        self.session = create_filewave_session(token)
    
    def scan_devices_for_clones(self, limit: int = 50) -> List[DeviceHierarchyInfo]:
        """Scan devices and find those with clone relationships"""
        results = []
        
        url = f"{self.server}/filewave/api/devices/v1/devices"
        success, data = safe_api_request(
            self.session, "get", url, params={"limit": limit}
        )
        
        if success and data:
            # Handle paginated response format
            results_data = data.get('results', {})
            if isinstance(results_data, dict) and 'rows' in results_data:
                devices = results_data['rows']
            elif isinstance(results_data, list):
                devices = results_data
            else:
                devices = []
            
            for device in devices[:limit]:
                device_id = device.get('id')
                if device_id:
                    hierarchy = self.analyzer.get_device_hierarchy(device_id)
                    if hierarchy and len(hierarchy.groups) > 0:
                        results.append(hierarchy)
        
        return results
    
    def analyze_patterns(self, hierarchies: List[DeviceHierarchyInfo]) -> Dict:
        """Analyze patterns across multiple device hierarchies"""
        
        devices_with_clones = []
        devices_original_only = []
        clone_group_distribution = {}
        original_groups_used = {}
        
        for h in hierarchies:
            clones = h.get_clone_groups()
            if clones:
                devices_with_clones.append({
                    'device_id': h.device_id,
                    'name': h.device_name,
                    'type': h.device_type,
                    'clone_group_count': len(clones),
                    'clone_groups': [g.name for g in clones]
                })
                
                # Track distribution
                count = len(clones)
                clone_group_distribution[count] = clone_group_distribution.get(count, 0) + 1
            else:
                devices_original_only.append({
                    'device_id': h.device_id,
                    'name': h.device_name,
                    'type': h.device_type
                })
            
            # Track which original groups are used most
            original = h.get_original_group()
            if original:
                key = f"{original.id}:{original.name}"
                original_groups_used[key] = original_groups_used.get(key, 0) + 1
        
        return {
            'total_devices_analyzed': len(hierarchies),
            'devices_with_clones': devices_with_clones,
            'devices_original_only': devices_original_only,
            'clone_group_distribution': clone_group_distribution,
            'original_groups_used': original_groups_used,
            'summary': {
                'total_with_clones': len(devices_with_clones),
                'total_original_only': len(devices_original_only),
                'avg_clone_groups': sum(len(h.get_clone_groups()) for h in hierarchies) / len(hierarchies) if hierarchies else 0
            }
        }
    
    def report_analysis(self, analysis: Dict) -> str:
        """Generate human-readable report"""
        lines = []
        
        lines.append("=" * 80)
        lines.append("DEVICE HIERARCHY ANALYSIS REPORT")
        lines.append("=" * 80)
        
        summary = analysis['summary']
        lines.append(f"\nSummary:")
        lines.append(f"  Total devices analyzed: {analysis['total_devices_analyzed']}")
        lines.append(f"  Devices with clone memberships: {summary['total_with_clones']}")
        lines.append(f"  Devices with original-only groups: {summary['total_original_only']}")
        lines.append(f"  Average clone groups per device: {summary['avg_clone_groups']:.1f}")
        
        lines.append(f"\nClone Group Distribution:")
        distribution = analysis['clone_group_distribution']
        for count in sorted(distribution.keys()):
            lines.append(f"  {count} clone groups: {distribution[count]} devices")
        
        lines.append(f"\nMost-Used Original Groups:")
        top_groups = sorted(
            analysis['original_groups_used'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        for group_info, count in top_groups:
            group_name = group_info.split(":", 1)[1]
            lines.append(f"  • {group_name}: {count} devices")
        
        if analysis['devices_with_clones']:
            lines.append(f"\nDevices with Multiple Clone Groups:")
            multi_clone = [d for d in analysis['devices_with_clones'] if d['clone_group_count'] >= 2]
            for device in multi_clone[:10]:
                lines.append(f"  • {device['name']} ({device['clone_group_count']} clone groups)")
        
        lines.append("\n" + "=" * 80)
        return "\n".join(lines)


def main():
    """Test clone pattern analysis (requires profile config)"""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from config_manager import FileWaveConfig
    
    config = FileWaveConfig()
    profile = config.get_profile()
    if not profile:
        print("ERROR: No profile configured. Run: filewave setup")
        sys.exit(1)
    
    server = profile["server"]
    token = profile["token"]
    
    analyzer = ClonePatternAnalyzer(server, token)
    print("Scanning devices for clone patterns...")
    hierarchies = analyzer.scan_devices_for_clones(limit=30)
    
    if hierarchies:
        analysis = analyzer.analyze_patterns(hierarchies)
        print(analyzer.report_analysis(analysis))
    else:
        print("No hierarchies found to analyze")


if __name__ == "__main__":
    main()
