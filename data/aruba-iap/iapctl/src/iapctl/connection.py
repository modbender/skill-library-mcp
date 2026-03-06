"""IAP connection handling using scrapli."""
import time
import re
from typing import Optional
from pathlib import Path

from scrapli import Scrapli
from scrapli.exceptions import ScrapliException


class IAPConnection:
    """Aruba IAP connection manager."""

    def __init__(
        self,
        host: str,
        username: str = "admin",
        password: Optional[str] = None,
        port: int = 22,
        ssh_config: Optional[Path] = None,
    ):
        """Initialize IAP connection.

        Args:
            host: IAP VC IP address
            username: SSH username (default: admin)
            password: SSH password
            port: SSH port (default: 22)
            ssh_config: Path to SSH config file (optional)
        """
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.ssh_config = ssh_config

        # Connection will be lazy-loaded
        self._conn: Optional[Scrapli] = None

    def connect(self) -> None:
        """Establish SSH connection to IAP."""
        if self._conn is not None:
            return  # Already connected

        # Build connection arguments
        conn_args = {
            "host": self.host,
            "port": self.port,
            "auth_username": self.username,
            "auth_strict_key": False,  # Accept any host key
        }

        # Determine authentication method
        # Priority: SSH config > Password > Default SSH key

        # 1. Check if using SSH config
        if self.ssh_config is not None:
            config_path = Path(self.ssh_config).expanduser()
            if config_path.exists():
                # Use SSH config for key discovery
                conn_args["ssh_config_file"] = str(config_path)

        # 2. Add password if provided (explicit password auth)
        if self.password:
            conn_args["auth_password"] = self.password
        # 3. No password - let Scrapli use default SSH key discovery
        # Don't set auth_private_key at all, let Scrapli handle it

        # Add platform-specific settings for Aruba IAP
        # Use generic platform to avoid scrapli-community platform issues
        conn_args.update({
            "platform": "generic",
            "transport": "paramiko",  # More stable for legacy SSH
            "timeout_socket": 30,
            "timeout_transport": 30,
            "timeout_ops": 60,
        })

        self._conn = Scrapli(**conn_args)

        try:
            self._conn.open()
        except ScrapliException as e:
            raise ConnectionError(f"Failed to connect to IAP {self.host}: {e}") from e

    def disconnect(self) -> None:
        """Close SSH connection."""
        if self._conn is not None:
            try:
                self._conn.close()
            except ScrapliException:
                pass
            self._conn = None

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()

    def send_command(self, command: str, timeout: int = 60) -> str:
        """Send a command and get response.

        Args:
            command: CLI command to execute
            timeout: Command timeout in seconds

        Returns:
            Command output as string
        """
        if self._conn is None:
            raise RuntimeError("Not connected to IAP. Call connect() first.")

        try:
            response = self._conn.send_command(command, timeout_ops=timeout)
            return response.result
        except ScrapliException as e:
            raise RuntimeError(f"Command failed: {command}: {e}") from e

    def send_commands(self, commands: list[str], timeout: int = 60) -> list[str]:
        """Send multiple commands and get responses.

        Args:
            commands: List of CLI commands to execute
            timeout: Command timeout in seconds

        Returns:
            List of command outputs
        """
        if self._conn is None:
            raise RuntimeError("Not connected to IAP. Call connect() first.")

        try:
            responses = self._conn.send_commands(commands, timeout_ops=timeout)
            return [r.result for r in responses]
        except ScrapliException as e:
            raise RuntimeError(f"Commands failed: {e}") from e

    def get_version(self) -> dict:
        """Get IAP version information.

        Returns:
            Dict with version info: {os_major, os_version, is_vc, model, uptime, device_mode}
        """
        output = self.send_command("show version")

        # Parse version info
        result = {
            "os_major": "unknown",
            "os_version": "unknown",
            "is_vc": False,
            "model": "unknown",
            "uptime": "unknown",
            "device_mode": "standalone",  # Default to standalone mode
        }

        for line in output.split("\n"):
            if "ArubaOS (MODEL:" in line:
                # Extract model
                parts = line.split("MODEL:")[1].split(")")
                result["model"] = parts[0].strip() if parts else "unknown"

            # Use separate if statements to allow multiple matches on same line
            if "Version" in line:
                # Extract version - format: "ArubaOS (MODEL: 224), Version 8.6.0.14"
                parts = line.split("Version")
                if len(parts) > 1:
                    version_part = parts[1].strip()
                    # Version may be followed by newline or space
                    version = version_part.split()[0] if version_part else "unknown"
                    result["os_version"] = version
                    # Extract major version
                    try:
                        result["os_major"] = version.split(".")[0]
                    except:
                        pass  # Keep default "unknown"

            # Check for VC mode - multiple indicators
            if "Virtual Controller" in line.lower() or "Master" in line.lower():
                result["is_vc"] = True
                result["device_mode"] = "virtual-controller"

            if "uptime is" in line:
                # Extract uptime
                parts = line.split("uptime is")
                if len(parts) > 1:
                    result["uptime"] = parts[1].strip()

        # Additional VC detection: check if device has VC role
        try:
            role_output = self.send_command("show role")
            if "Virtual Controller" in role_output or "Master" in role_output:
                result["is_vc"] = True
                result["device_mode"] = "virtual-controller"
        except:
            # Command not supported - assume standalone
            result["device_mode"] = "standalone"

        return result

    def get_ap_info(self) -> list[dict]:
        """Get AP cluster information.

        Returns:
            List of AP info dicts
        """
        try:
            output = self.send_command("show ap database")
        except Exception:
            # Command failed - might be standalone AP
            try:
                # Try alternative command for standalone AP
                output = self.send_command("show ap info")
            except Exception:
                # Return empty list if both commands fail
                return []

        aps = []

        # Check if this is a parse error (standalone AP)
        if "Parse error" in output or "Incomplete command" in output:
            # This is likely a standalone AP - get its own info
            version_info = self.get_version()
            return [{
                "name": version_info.get("model", "Unknown"),
                "ip": self.host,
                "mac": "N/A",
                "status": "up",
                "mode": "standalone",
                "role": "standalone",
            }]

        # Parse AP entries (format varies by version)
        current_ap = {}
        for line in output.split("\n"):
            line = line.strip()

            # Skip headers and separators
            if "Name" in line and ("IP Address" in line or "IP" in line):
                continue  # Header line
            if line.startswith("---") or line.startswith("==="):
                continue
            if not line:
                continue

            # Simple parsing - split by whitespace
            parts = line.split()
            if len(parts) >= 3:
                current_ap = {
                    "name": parts[0],
                    "ip": parts[1] if len(parts) > 1 else "N/A",
                    "mac": parts[2] if len(parts) > 2 else "N/A",
                    "status": parts[3] if len(parts) > 3 else "unknown",
                }
                aps.append(current_ap)

        return aps

    def get_wlan_list(self) -> list[dict]:
        """Get WLAN configuration list.

        For standalone APs, uses 'wlan' command instead of 'show wlan'.

        Returns:
            List of WLAN info dicts
        """
        version_info = self.get_version()

        # For standalone APs, use 'wlan' command
        if version_info.get("device_mode") == "standalone":
            try:
                output = self.send_command("wlan")
                wlans = []

                # Parse wlan output
                current_wlan = {}
                for line in output.split("\n"):
                    line = line.strip()

                    # Skip empty lines and headers
                    if not line or line.startswith("---"):
                        continue

                    # WLAN ID pattern: "1 MySSID"
                    if line and line[0].isdigit():
                        parts = line.split(maxsplit=1)
                        if len(parts) >= 1:
                            current_wlan = {
                                "id": parts[0],
                                "ssid": parts[1] if len(parts) > 1 else "N/A",
                                "status": "up",
                            }
                            wlans.append(current_wlan)

                return wlans
            except Exception:
                return []

        # For VC mode, try 'show wlan' command
        else:
            try:
                output = self.send_command("show wlan")
                # Parse show wlan output
                wlans = []

                # Check for parse error
                if "Parse error" in output:
                    # Fall back to wlan command
                    return self.get_wlan_list()

                # Parse output (format varies)
                for line in output.split("\n"):
                    line = line.strip()
                    # Simple parsing - add WLAN entries
                    if line and not line.startswith("WLAN") and not line.startswith("---"):
                        parts = line.split()
                        if len(parts) >= 2:
                            wlans.append({
                                "id": parts[0],
                                "ssid": " ".join(parts[1:]),
                                "status": "up",
                            })

                return wlans
            except Exception:
                return []

        return []

    def get_radio_info(self) -> dict:
        """Get radio information.

        For standalone APs, uses appropriate commands.

        Returns:
            Dict with radio info
        """
        version_info = self.get_version()

        # Try different commands based on device mode
        commands_to_try = [
            "show ap radio",
            "show radio info",
            "show radio",
        ]

        for cmd in commands_to_try:
            try:
                output = self.send_command(cmd)

                # Check for parse errors
                if "Parse error" in output or "Incomplete command" in output:
                    continue

                # Parse radio info
                result = {
                    "2.4ghz": {"status": "unknown"},
                    "5ghz": {"status": "unknown"},
                }

                # Simple parsing
                for line in output.split("\n"):
                    line = line.lower().strip()
                    if "2.4" in line or "24ghz" in line:
                        result["2.4ghz"]["status"] = "up"
                    if "5" in line and "ghz" in line:
                        result["5ghz"]["status"] = "up"

                return result
            except Exception:
                continue

        # All commands failed, return basic info
        return {
            "2.4ghz": {"status": "unknown"},
            "5ghz": {"status": "unknown"},
        }

    def detect_device_mode(self) -> dict:
        """Detect device mode (VC, Single-Node Cluster, or Standalone AP).

        Returns:
            Dict with device mode info: {mode, is_vc, role, ap_count?}
        """
        version_info = self.get_version()

        # Check 1: VC mode was detected in get_version
        if version_info.get("is_vc"):
            return {
                "mode": "virtual-controller",
                "is_vc": True,
                "role": "virtual-controller",
            }

        # Check 2: Look for virtual-controller-key in running config
        try:
            config_output = self.send_command("show running-config")
            if "virtual-controller-key" in config_output:
                # Has VC configuration - check BSS table for AP count
                try:
                    bss_output = self.send_command("show ap bss-table")
                    # Parse "Num APs:" line
                    if "Num APs:" in bss_output:
                        match = re.search(r"Num APs:(\d+)", bss_output)
                        if match:
                            num_aps = int(match.group(1))
                            # More than 2 APs indicates a real VC cluster
                            # (2 APs is usually the same device with 2 radios)
                            if num_aps > 2:
                                return {
                                    "mode": "virtual-controller",
                                    "is_vc": True,
                                    "role": "virtual-controller",
                                    "ap_count": num_aps,
                                }
                            else:
                                # Single node cluster (1-2 BSS entries)
                                return {
                                    "mode": "single-node-cluster",
                                    "is_vc": False,
                                    "role": "single-node-cluster",
                                    "ap_count": num_aps,
                                }
                except Exception:
                    # If we can't determine AP count but have VC config,
                    # assume single-node cluster
                    return {
                        "mode": "single-node-cluster",
                        "is_vc": False,
                        "role": "single-node-cluster",
                    }
        except Exception:
            pass

        # Check 3: Try traditional AP list method
        try:
            ap_list = self.get_ap_info()
            if len(ap_list) > 1:
                return {
                    "mode": "virtual-controller",
                    "is_vc": True,
                    "role": "virtual-controller",
                    "ap_count": len(ap_list),
                }
        except Exception:
            pass

        # Default: standalone AP (no VC configuration)
        return {
            "mode": "standalone",
            "is_vc": False,
            "role": "standalone",
        }

    def send_config_commands(self, config_commands: list[str]) -> str:
        """Send configuration commands in config mode.

        Aruba IAP uses interactive configuration mode:
        1. Enter config mode: configure terminal
        2. Enter sub-mode (e.g., wlan ssid-profile <name>)
        3. Configure parameters
        4. Exit sub-mode: exit
        5. Exit config mode: exit
        6. Save: write memory
        7. Apply: commit apply

        Args:
            config_commands: List of configuration commands

        Returns:
            Combined output from all commands
        """
        if self._conn is None:
            raise RuntimeError("Not connected to IAP. Call connect() first.")

        outputs = []
        delay = 0.3  # Delay between commands

        try:
            # Enter configuration mode
            self._conn.channel.write("configure terminal\n")
            time.sleep(2)
            response = self._conn.channel.read()
            outputs.append(response.decode('utf-8', errors='ignore'))

            # Send each configuration command
            for cmd in config_commands:
                self._conn.channel.write(f"{cmd}\n")
                time.sleep(delay)

            # Read final response
            time.sleep(1)
            response = self._conn.channel.read()
            outputs.append(response.decode('utf-8', errors='ignore'))

            return "\n".join(outputs)

        except Exception as e:
            raise RuntimeError(f"Config commands failed: {e}") from e

    def send_config_and_apply(self, config_commands: list[str]) -> str:
        """Send configuration commands and apply them.

        Args:
            config_commands: List of configuration commands

        Returns:
            Combined output from all commands
        """
        if self._conn is None:
            raise RuntimeError("Not connected to IAP. Call connect() first.")

        outputs = []
        delay = 0.3  # Delay between commands

        try:
            # Enter configuration mode
            self._conn.channel.write("configure terminal\n")
            time.sleep(2)
            response = self._conn.channel.read()
            outputs.append(response.decode('utf-8', errors='ignore'))

            # Send each configuration command
            for cmd in config_commands:
                self._conn.channel.write(f"{cmd}\n")
                time.sleep(delay)

            # Wait for all commands to be processed
            time.sleep(1)
            response = self._conn.channel.read()
            outputs.append(response.decode('utf-8', errors='ignore'))

            # Exit configuration mode
            self._conn.channel.write("exit\n")
            time.sleep(1)
            response = self._conn.channel.read()
            outputs.append(response.decode('utf-8', errors='ignore'))

            # Save configuration
            self._conn.channel.write("write memory\n")
            time.sleep(2)
            response = self._conn.channel.read()
            outputs.append(response.decode('utf-8', errors='ignore'))

            # Commit and apply
            self._conn.channel.write("commit apply\n")
            time.sleep(3)
            response = self._conn.channel.read()
            outputs.append(response.decode('utf-8', errors='ignore'))

            return "\n".join(outputs)

        except Exception as e:
            raise RuntimeError(f"Config and apply failed: {e}") from e
