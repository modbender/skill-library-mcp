#!/usr/bin/env python3
"""
Aruba IAP Configuration Backup Script
Backup running configuration from Aruba Instant AP
"""

import sys
import subprocess
import datetime
from typing import Optional

class IAPBackup:
    """Aruba IAP Configuration Backup"""
    
    def __init__(self, ap_ip: str, username: str = "aruba", password: str = "aruba123"):
        self.ap_ip = ap_ip
        self.username = username
        self.password = password
    
    def run_ssh_command(self, command: str) -> str:
        """Execute command on IAP via SSH"""
        try:
            cmd = f'echo "{self.password}" | sshpass -p stdin ssh -o StrictHostKeyChecking=no -o ConnectTimeout=30 {self.username}@{self.ap_ip} "{command}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
            return result.stdout
        except subprocess.TimeoutExpired:
            return "ERROR: Connection timeout"
        except Exception as e:
            return f"ERROR: {str(e)}"
    
    def backup_config(self, output_file: Optional[str] = None) -> bool:
        """Backup running configuration"""
        print(f"Backing up configuration from {self.ap_ip}...")
        
        # Get configuration
        config = self.run_ssh_command("show running-config")
        
        if "ERROR" in config or not config.strip():
            print("✗ Failed to retrieve configuration")
            return False
        
        # Generate filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        default_filename = f"iap-backup-{self.ap_ip}-{timestamp}.txt"
        filename = output_file if output_file else default_filename
        
        # Save configuration
        try:
            with open(filename, 'w') as f:
                f.write(f"# Aruba IAP Configuration Backup\n")
                f.write(f"# AP: {self.ap_ip}\n")
                f.write(f"# Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# User: {self.username}\n")
                f.write(f"# ========================================\n\n")
                f.write(config)
            
            print(f"✓ Configuration saved to: {filename}")
            return True
        except Exception as e:
            print(f"✗ Failed to save configuration: {str(e)}")
            return False
    
    def backup_version_info(self) -> bool:
        """Backup version and system info"""
        print("Backing up system information...")
        
        # Get version
        version = self.run_ssh_command("show version")
        
        # Get system info
        system = self.run_ssh_command("show system")
        
        # Save to file
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"iap-system-info-{self.ap_ip}-{timestamp}.txt"
        
        try:
            with open(filename, 'w') as f:
                f.write("# Aruba IAP System Information\n")
                f.write(f"# AP: {self.ap_ip}\n")
                f.write(f"# Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# ========================================\n\n")
                f.write("=== VERSION ===\n\n")
                f.write(version)
                f.write("\n=== SYSTEM ===\n\n")
                f.write(system)
            
            print(f"✓ System info saved to: {filename}")
            return True
        except Exception as e:
            print(f"✗ Failed to save system info: {str(e)}")
            return False
    
    def backup_client_info(self) -> bool:
        """Backup client list"""
        print("Backing up client information...")
        
        clients = self.run_ssh_command("show ap client")
        
        if "ERROR" in clients or not clients.strip():
            print("✗ Failed to retrieve client list")
            return False
        
        # Save to file
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"iap-clients-{self.ap_ip}-{timestamp}.txt"
        
        try:
            with open(filename, 'w') as f:
                f.write("# Aruba IAP Client List\n")
                f.write(f"# AP: {self.ap_ip}\n")
                f.write(f"# Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# ========================================\n\n")
                f.write(clients)
            
            print(f"✓ Client list saved to: {filename}")
            return True
        except Exception as e:
            print(f"✗ Failed to save client list: {str(e)}")
            return False
    
    def backup_all(self) -> bool:
        """Backup all configuration data"""
        print("="*60)
        print("Aruba IAP Full Backup")
        print(f"Target: {self.ap_ip}")
        print("="*60)
        
        success = True
        
        # Backup configuration
        if not self.backup_config():
            success = False
        
        # Backup version info
        if not self.backup_version_info():
            success = False
        
        # Backup client list
        if not self.backup_client_info():
            success = False
        
        # Summary
        print("\n" + "="*60)
        if success:
            print("✓ All backups completed successfully")
        else:
            print("✗ Some backups failed")
        print("="*60)
        
        return success

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 config_backup.py <AP-IP-Address> [output-file] [username] [password]")
        print("\nExamples:")
        print("  python3 config_backup.py 192.168.1.100")
        print("  python3 config_backup.py 192.168.1.100 my-backup.txt")
        print("  python3 config_backup.py 192.168.1.100 my-backup.txt admin mypass")
        sys.exit(1)
    
    ap_ip = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    username = sys.argv[3] if len(sys.argv) > 3 else "aruba"
    password = sys.argv[4] if len(sys.argv) > 4 else "aruba123"
    
    backup = IAPBackup(ap_ip, username, password)
    backup.backup_all()

if __name__ == "__main__":
    main()
