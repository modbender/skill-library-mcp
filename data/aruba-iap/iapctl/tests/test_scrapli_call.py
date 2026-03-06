"""Test connection with actual Scrapli call."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from iapctl.connection import IAPConnection

print("Testing actual connection attempt...")

try:
    conn = IAPConnection(
        host="192.168.20.56",
        username="admin",
        ssh_config=None,
    )
    print("✓ IAPConnection created")
    print(f"  host: {conn.host}")
    print(f"  username: {conn.username}")
    print(f"  ssh_config: {conn.ssh_config}")
    print(f"  password: {'***' if conn.password else None}")

    print("\nAttempting to connect...")
    conn.connect()
    print("✓ Connected (unexpected!)")

except Exception as e:
    print(f"Connection attempt failed as expected:")
    print(f"  Error type: {type(e).__name__}")
    print(f"  Error: {e}")

    import traceback
    print("\nFull traceback:")
    traceback.print_exc()
