#!/usr/bin/env python3
"""
Aruba IAP Diagnostic Script
Run comprehensive diagnostic checks on Aruba Instant AP
"""

import sys
import subprocess
import re
import time
from typing import Dict, List, Tuple

class IAPDiagnostics:
    """Aruba IAP Diagnostics"""
    
    def __init__(self, ap_ip: str, username: str = "aruba", password: str = "aruba123"):
        self.ap_ip = ap_ip
        self.username = username
        self.password = password
        self.ssh_cmd = f"ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 {self.username}@{self.ap_ip}"
    
    def run_ssh_command(self, command: str) -> str:
        """Execute command on IAP via SSH"""
        try:
            # Use sshpass for password authentication if available
            cmd = f'echo "{self.password}" | sshpass -p stdin ssh {self.username}@{self.ap_ip} "{command}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            return result.stdout
        except subprocess.TimeoutExpired:
            return "ERROR: Connection timeout"
        except Exception as e:
            return f"ERROR: {str(e)}"
    
    def check_connectivity(self) -> Dict[str, str]:
        """Check basic connectivity"""
        print("\n=== Connectivity Check ===")
        
        # Ping test
        ping_result = subprocess.run(
            ["ping", "-c", "3", self.ap_ip],
            capture_output=True, text=True
        )
        
        if ping_result.returncode == 0:
            packet_loss = ping_result.stdout.count("packet loss")
            avg_time = self._extract_ping_time(ping_result.stdout)
            print(f"✓ Ping: OK (avg {avg_time}ms)")
            if packet_loss:
                print(f"  ⚠ Warning: {packet_loss}")
        else:
            print("✗ Ping: FAILED")
        
        return {"ping": "OK" if ping_result.returncode == 0 else "FAILED"}
    
    def check_version(self) -> str:
        """Check AP version and model"""
        print("\n=== Version Information ===")
        output = self.run_ssh_command("show version")
        
        if "ERROR" not in output:
            # Extract version info
            version_match = re.search(r'Version\s+(\S+)', output)
            model_match = re.search(r'Model\s+(\S+)', output)
            
            if version_match:
                print(f"✓ Version: {version_match.group(1)}")
            if model_match:
                print(f"✓ Model: {model_match.group(1)}")
            
            return output
        return "ERROR: Could not retrieve version"
    
    def check_configuration(self) -> Dict[str, str]:
        """Check current configuration"""
        print("\n=== Configuration Check ===")
        
        # Check running config
        config = self.run_ssh_command("show running-config")
        
        # Check key parameters
        checks = {
            "hostname": self._check_config_value(config, "hostname"),
            "ip_address": self._check_config_value(config, "ip address"),
            "ssid_count": config.count("ssid"),
            "wlan_count": config.count("wlan"),
            "security_configured": "security" in config
        }
        
        print(f"✓ Hostname: {checks['hostname']}")
        print(f"✓ IP Configured: {checks['ip_address']}")
        print(f"✓ SSIDs: {checks['ssid_count']}")
        print(f"✓ WLANs: {checks['wlan_count']}")
        print(f"✓ Security: {checks['security_configured']}")
        
        return checks
    
    def check_clients(self) -> Dict[str, int]:
        """Check connected clients"""
        print("\n=== Client Information ===")
        output = self.run_ssh_command("show ap client")
        
        if "ERROR" not in output and "show ap client" in output:
            # Extract client count
            lines = output.split('\n')
            client_count = len([l for l in lines if l.strip()])
            
            print(f"✓ Connected Clients: {client_count}")
            
            # Extract client details
            clients = []
            for line in lines:
                if ':' in line and ('mac' in line.lower() or 'ip' in line.lower()):
                    clients.append(line.strip())
            
            if clients and len(clients) <= 10:
                print("  Sample clients:")
                for client in clients[:5]:
                    print(f"    {client}")
            
            return {"count": client_count, "details": clients[:10]}
        
        print("✗ Could not retrieve client information")
        return {"count": 0, "details": []}
    
    def check_radio(self) -> Dict[str, str]:
        """Check radio status"""
        print("\n=== Radio Status ===")
        output = self.run_ssh_command("show radio")
        
        if "ERROR" not in output:
            # Extract radio info
            radio_info = {}
            
            # Check 2.4GHz
            if "2.4GHz" in output:
                radio_2g = self._extract_radio_info(output, "2.4GHz")
                radio_info["2.4GHz"] = radio_2g
            
            # Check 5GHz
            if "5GHz" in output:
                radio_5g = self._extract_radio_info(output, "5GHz")
                radio_info["5GHz"] = radio_5g
            
            print(f"✓ 2.4GHz: {radio_info.get('2.4GHz', 'Unknown')}")
            print(f"✓ 5GHz: {radio_info.get('5GHz', 'Unknown')}")
            
            return radio_info
        
        print("✗ Could not retrieve radio information")
        return {}
    
    def check_logs(self) -> List[str]:
        """Check recent logs"""
        print("\n=== Recent Logs ===")
        output = self.run_ssh_command("show logging")
        
        if "ERROR" not in output:
            # Filter for errors and warnings
            errors = []
            for line in output.split('\n'):
                if any(keyword in line.lower() for keyword in ['error', 'fail', 'critical', 'warning']):
                    errors.append(line.strip())
            
            if errors:
                print(f"✓ Found {len(errors)} log entries")
                for error in errors[:5]:  # Show first 5
                    print(f"  - {error}")
                return errors[:10]
        
        print("✗ No significant log entries")
        return []
    
    def run_full_diagnostics(self):
        """Run all diagnostic checks"""
        print("="*60)
        print("Aruba IAP Diagnostic Tool")
        print(f"Target: {self.ap_ip}")
        print("="*60)
        
        # Run all checks
        results = {}
        
        results['connectivity'] = self.check_connectivity()
        results['version'] = self.check_version()
        results['configuration'] = self.check_configuration()
        results['clients'] = self.check_clients()
        results['radio'] = self.check_radio()
        results['logs'] = self.check_logs()
        
        # Summary
        print("\n" + "="*60)
        print("Diagnostic Summary")
        print("="*60)
        print(f"Connectivity: {results['connectivity'].get('ping', 'UNKNOWN')}")
        print(f"Clients: {results['clients'].get('count', 0)} connected")
        print(f"Log entries: {len(results['logs'])} issues found")
        
        # Recommendations
        print("\n" + "="*60)
        print("Recommendations")
        print("="*60)
        
        if results['clients'].get('count', 0) == 0:
            print("⚠ No clients connected - Check radio and SSID configuration")
        
        if len(results['logs']) > 5:
            print("⚠ Multiple log errors - Review configuration and logs")
        
        if "FAILED" in results['connectivity'].get('ping', ''):
            print("⚠ Connectivity issue - Check network cable and IP settings")
    
    def _check_config_value(self, config: str, keyword: str) -> str:
        """Extract configuration value"""
        lines = config.split('\n')
        for line in lines:
            if keyword in line.lower():
                parts = line.split()
                if len(parts) > 1:
                    return parts[-1]
        return "Not configured"
    
    def _extract_radio_info(self, output: str, band: str) -> str:
        """Extract radio information for specific band"""
        lines = output.split('\n')
        for line in lines:
            if band in line and ('channel' in line.lower() or 'power' in line.lower()):
                return line.strip()
        return "No data"
    
    def _extract_ping_time(self, output: str) -> str:
        """Extract average ping time"""
        match = re.search(r'avg = (\d+\.?\d*)/(\d+\.?\d*) ms', output)
        if match:
            avg = match.group(1)
            return f"{float(avg):.1f}"
        return "N/A"

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 diagnose_iap.py <AP-IP-Address> [username] [password]")
        print("\nExample: python3 diagnose_iap.py 192.168.1.100")
        sys.exit(1)
    
    ap_ip = sys.argv[1]
    username = sys.argv[2] if len(sys.argv) > 2 else "aruba"
    password = sys.argv[3] if len(sys.argv) > 3 else "aruba123"
    
    diagnostics = IAPDiagnostics(ap_ip, username, password)
    diagnostics.run_full_diagnostics()

if __name__ == "__main__":
    main()
