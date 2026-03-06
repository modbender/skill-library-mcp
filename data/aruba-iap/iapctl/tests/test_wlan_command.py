"""Test wlan command on standalone AP."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from iapctl.connection import IAPConnection

print("Testing wlan command on standalone AP...")

try:
    conn = IAPConnection(
        host="192.168.20.56",
        username="admin",
        password="sh8beijing",
    )

    with conn:
        print("✓ Connected")

        # Test version and device mode
        print("\n[1] Getting version info...")
        version_info = conn.get_version()
        print(f"  Model: {version_info.get('model')}")
        print(f"  OS: {version_info.get('os_version')}")
        print(f"  VC: {version_info.get('is_vc')}")
        print(f"  Mode: {version_info.get('device_mode')}")

        # Test device mode detection
        print("\n[2] Detecting device mode...")
        device_mode = conn.detect_device_mode()
        print(f"  Mode: {device_mode.get('mode')}")
        print(f"  Is VC: {device_mode.get('is_vc')}")

        # Test wlan command
        print("\n[3] Testing wlan command...")
        try:
            wlan_output = conn.send_command("wlan")
            print(f"  ✓ wlan command succeeded")
            print(f"  Output length: {len(wlan_output)} chars")
            print(f"  First 200 chars: {wlan_output[:200]}")
        except Exception as e:
            print(f"  ✗ wlan command failed: {e}")

        # Test show wlan
        print("\n[4] Testing 'show wlan' command...")
        try:
            show_wlan_output = conn.send_command("show wlan")
            print(f"  ✓ show wlan command succeeded")
            print(f"  Output length: {len(show_wlan_output)} chars")
            print(f"  First 200 chars: {show_wlan_output[:200]}")
        except Exception as e:
            print(f"  ✗ show wlan command failed: {e}")

        # Try configuration mode
        print("\n[5] Testing configuration mode...")
        try:
            # Enter configuration mode
            output = conn.send_command("configure terminal")
            print(f"  ✓ Entered config mode")
            print(f"  Output: {output[:100]}")

            # Try wlan in config mode
            wlan_config = conn.send_command("wlan")
            print(f"  ✓ wlan in config mode succeeded")
            print(f"  Output length: {len(wlan_config)} chars")

            # Exit config mode
            conn.send_command("exit")
            print(f"  ✓ Exited config mode")
        except Exception as e:
            print(f"  ✗ Config mode failed: {e}")

except Exception as e:
    print(f"✗ Connection failed: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Test completed!")
