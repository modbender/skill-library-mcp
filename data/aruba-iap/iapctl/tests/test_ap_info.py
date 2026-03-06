"""Test AP info commands."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from iapctl.connection import IAPConnection

print("Testing AP info commands...")

try:
    conn = IAPConnection(
        host="192.168.20.56",
        username="admin",
        password="sh8beijing",
    )

    with conn:
        print("✓ Connected")

        # Test show ap info
        print("\n[1] Testing 'show ap info'...")
        try:
            ap_info_output = conn.send_command("show ap info")
            print(f"  ✓ show ap info succeeded")
            print(f"  Output length: {len(ap_info_output)} chars")
            print(f"\n  Output preview:")
            for line in ap_info_output.split('\n')[:10]:
                print(f"    {line}")
        except Exception as e:
            print(f"  ✗ show ap info failed: {e}")

        # Test get_ap_info with device mode detection
        print("\n[2] Testing get_ap_info()...")
        try:
            ap_info = conn.get_ap_info()
            print(f"  ✓ get_ap_info succeeded")
            print(f"  Number of APs: {len(ap_info)}")
            for i, ap in enumerate(ap_info[:3], 1):
                print(f"    AP {i}: {ap}")
        except Exception as e:
            print(f"  ✗ get_ap_info failed: {e}")

        # Test device mode detection
        print("\n[3] Testing detect_device_mode()...")
        try:
            device_mode = conn.detect_device_mode()
            print(f"  ✓ detect_device_mode succeeded")
            print(f"  Mode: {device_mode}")
        except Exception as e:
            print(f"  ✗ detect_device_mode failed: {e}")

except Exception as e:
    print(f"✗ Connection failed: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Test completed!")
