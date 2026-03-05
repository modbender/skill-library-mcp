#!/usr/bin/env python3
"""
Aruba IAP Client Monitor Script
Monitor connected clients in real-time
"""

import sys
import subprocess
import time
import signal
from datetime import datetime
from typing import Dict, List

class IAPClientMonitor:
    """Aruba IAP Client Monitor"""
    
    def __init__(self, ap_ip: str, username: str = "aruba", password: str = "aruba123"):
        self.ap_ip = ap_ip
        self.username = username
        self.password = password
        self.running = True
        self.client_history = {}
        self.last_client_count = 0
    
    def run_ssh_command(self, command: str) -> str:
        """Execute command on IAP via SSH"""
        try:
            cmd = f'echo "{self.password}" | sshpass -p stdin ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 {self.username}@{self.ap_ip} "{command}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
            return result.stdout
        except Exception as e:
            return ""
    
    def get_clients(self) -> Dict[str, int]:
        """Get current client list"""
        output = self.run_ssh_command("show ap client")
        
        if not output or "ERROR" in output:
            return {"count": 0, "details": []}
        
        # Parse client list
        clients = []
        lines = output.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and ':' in line:
                # Extract client info (MAC, IP, SSID, RSSI, etc.)
                client_info = self._parse_client_line(line)
                if client_info:
                    clients.append(client_info)
        
        return {"count": len(clients), "details": clients}
    
    def _parse_client_line(self, line: str) -> Dict[str, str]:
        """Parse a single client line"""
        info = {}
        
        # Simple parsing - extract key fields
        if 'mac:' in line.lower():
            parts = [p.strip() for p in line.split(':')]
            for part in parts:
                if 'mac' in part.lower():
                    info['mac'] = part.split()[-1].strip()
                elif 'ip' in part.lower():
                    info['ip'] = part.split()[-1].strip()
                elif 'ssid' in part.lower():
                    info['ssid'] = part.split()[-1].strip()
                elif 'rssi' in part.lower():
                    info['rssi'] = part.split()[-1].strip()
        
        return info if info else None
    
    def display_clients(self, clients: Dict[str, int]):
        """Display client information"""
        print(f"\n{'='*60}")
        print(f"Connected Clients: {clients['count']}")
        print(f"Last Updated: {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*60}")
        
        if clients['count'] == 0:
            print("No clients connected")
            return
        
        # Display client summary
        print("\nClient Summary:")
        print(f"{'─'*60}")
        
        # Count clients per SSID
        ssid_counts = {}
        for client in clients['details']:
            ssid = client.get('ssid', 'Unknown')
            ssid_counts[ssid] = ssid_counts.get(ssid, 0) + 1
        
        for ssid, count in ssid_counts.items():
            print(f"  • {ssid}: {count} clients")
        
        # Display top clients (by RSSI if available)
        print(f"\n{'─'*60}")
        rssi_clients = [c for c in clients['details'] if c.get('rssi')]
        if rssi_clients:
            # Sort by RSSI (higher is better)
            sorted_clients = sorted(rssi_clients, key=lambda x: self._extract_rssi(x.get('rssi', '')), reverse=True)
            
            print("Top Clients by Signal Strength:")
            for i, client in enumerate(sorted_clients[:5], 1):
                rssi = self._extract_rssi(client.get('rssi', ''))
                print(f"  {i}. {client.get('mac', 'Unknown')} - {client.get('ip', 'Unknown')} - RSSI: {rssi}")
    
    def _extract_rssi(self, rssi_str: str) -> int:
        """Extract numeric RSSI value"""
        try:
            # Extract number from string like "-45 dBm"
            import re
            match = re.search(r'(-?\d+)', rssi_str)
            if match:
                return int(match.group(1))
        except:
            pass
        return -100  # Default if parsing fails
    
    def check_client_changes(self, current_clients: Dict[str, int]):
        """Check for client changes"""
        current_count = current_clients['count']
        
        if current_count != self.last_client_count:
            change = current_count - self.last_client_count
            direction = "↑" if change > 0 else "↓"
            
            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f"\n[{timestamp}] Client count changed: {self.last_client_count} → {current_count} ({direction}{abs(change)})")
            
            self.last_client_count = current_count
            
            # Alert on significant changes
            if abs(change) >= 5:
                print(f"⚠ Significant client count change detected!")
        elif current_count > self.last_client_count:
            # Log new clients
            for client in current_clients['details']:
                mac = client.get('mac', '')
                if mac and mac not in self.client_history:
                    self.client_history[mac] = {
                        'first_seen': datetime.now(),
                        'ssid': client.get('ssid', ''),
                        'ip': client.get('ip', '')
                    }
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    print(f"[{timestamp}] New client: {mac} on {client.get('ssid', 'Unknown')}")
    
    def run_monitor(self, interval: int = 30):
        """Run continuous monitoring"""
        print("="*60)
        print("Aruba IAP Client Monitor")
        print(f"Target: {self.ap_ip}")
        print(f"Update Interval: {interval}s")
        print("="*60)
        
        # Set up signal handler for graceful exit
        def signal_handler(signum, frame):
            print("\n\nStopping monitor...")
            self.running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Initial client check
        print("\nStarting initial scan...")
        clients = self.get_clients()
        self.display_clients(clients)
        self.last_client_count = clients['count']
        
        # Monitoring loop
        try:
            while self.running:
                time.sleep(interval)
                
                # Get current clients
                clients = self.get_clients()
                
                # Check for changes
                self.check_client_changes(clients)
                
                # Update display periodically
                if self.last_client_count % (60 // interval) == 0:  # Every ~1 minute
                    self.display_clients(clients)
        
        except KeyboardInterrupt:
            print("\n\nMonitor stopped by user")
        
        # Final summary
        print("\n" + "="*60)
        print("Monitoring Summary")
        print("="*60)
        print(f"Total unique clients seen: {len(self.client_history)}")
        print(f"Final client count: {self.last_client_count}")
        print(f"Monitor stopped at: {datetime.now().strftime('%H:%M:%S')}")
        print("="*60)
    
    def run_single_check(self):
        """Run a single client check and display results"""
        print("="*60)
        print("Aruba IAP Client Check")
        print(f"Target: {self.ap_ip}")
        print("="*60)
        
        clients = self.get_clients()
        self.display_clients(clients)
        
        # Additional info
        if clients['count'] > 0:
            print("\nAdditional Information:")
            print("  Use 'show ap client' for detailed client information")
            print("  Use 'show ap client trail-info <mac>' for client history")
        
        return clients

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 monitor_clients.py <AP-IP-Address> [interval] [username] [password]")
        print("\nExamples:")
        print("  python3 monitor_clients.py 192.168.1.100")
        print("  python3 monitor_clients.py 192.168.1.100 15")
        print("  python3 monitor_clients.py 192.168.1.100 30 admin mypass")
        print("\nModes:")
        print("  Default mode: Single check (shows clients and exits)")
        print("  Continuous mode: Monitor continuously (Ctrl+C to stop)")
        print("\nNote: Add '--continuous' flag to enable continuous monitoring")
        sys.exit(1)
    
    ap_ip = sys.argv[1]
    interval = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 30
    username = sys.argv[3] if len(sys.argv) > 3 else "aruba"
    password = sys.argv[4] if len(sys.argv) > 4 else "aruba123"
    
    # Check for continuous mode
    continuous = '--continuous' in sys.argv
    
    monitor = IAPClientMonitor(ap_ip, username, password)
    
    if continuous:
        monitor.run_monitor(interval)
    else:
        monitor.run_single_check()

if __name__ == "__main__":
    main()
