"""Test IAP connection attempt."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from iapctl.connection import IAPConnection

print("Testing IAP connection attempt...")

try:
    # Try to connect (will fail, but we can see the error)
    print("\nAttempting to connect to 192.168.20.56...")
    conn = IAPConnection(
        host="192.168.20.56",
        username="admin",
        password="test123",
    )
    
    with conn:
        print("  ✗ Unexpected: connection succeeded!")
        output = conn.send_command("show version")
        print(f"  Output: {output[:100]}...")

except ConnectionError as e:
    print(f"  ✓ ConnectionError (expected): {e}")
except Exception as e:
    print(f"  ✗ Unexpected error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Test completed!")
