
import subprocess
import sys
import json

def run_tailscale_command(command_args):
    """Runs a tailscale CLI command and returns its output."""
    try:
        # Prepend 'tailscale' to the command arguments
        full_command = ["tailscale"] + command_args
        result = subprocess.run(full_command, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except FileNotFoundError:
        print("Error: Tailscale CLI not found. Please ensure Tailscale is installed and in your system PATH.", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error executing Tailscale command: {e.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

def get_status():
    """Retrieves and formats the Tailscale status."""
    output = run_tailscale_command(["status", "--json"])
    try:
        status_data = json.loads(output)
        # Extract relevant information for a concise summary
        summary = []
        summary.append(f"Tailscale Status: {status_data.get("BackendState", "Unknown")}")
        summary.append(f"  Logged In: {status_data.get("Self", {}).get("Online", False)}")
        summary.append(f"  IP Address: {', '.join(status_data.get("Self", {}).get("TailscaleIPs", []))}")
        summary.append(f"  Hostname: {status_data.get("Self", {}).get("HostName", "N/A")}")
        summary.append(f"  Peers: {len(status_data.get("Peer", {}))}")
        return "\n".join(summary)
    except json.JSONDecodeError:
        return f"Raw Tailscale status:\n{output}"

def list_devices():
    """Lists connected Tailscale devices."""
    output = run_tailscale_command(["status", "--json"])
    try:
        status_data = json.loads(output)
        devices = []
        for peer_id, peer_data in status_data.get("Peer", {}).items():
            device_name = peer_data.get("HostName", "Unknown")
            ips = ", ".join(peer_data.get("TailscaleIPs", []))
            online = "Online" if peer_data.get("Online", False) else "Offline"
            devices.append(f"- {device_name} ({ips}) - {online}")
        if not devices:
            return "No other Tailscale devices found."
        return "\n".join(["Connected Tailscale Devices:"] + devices)
    except json.JSONDecodeError:
        return f"Raw Tailscale devices list:\n{output}"

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 main.py [status|devices]", file=sys.stderr)
        sys.exit(1)

    action = sys.argv[1]

    if action == "status":
        print(get_status())
    elif action == "devices":
        print(list_devices())
    else:
        print(f"Unknown action: {action}. Use 'status' or 'devices'.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
