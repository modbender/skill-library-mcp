"""Test IAP connection initialization."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from iapctl.connection import IAPConnection

print("Testing IAP connection initialization...")

try:
    # Test 1: Password auth
    print("\nTest 1: Password auth")
    conn1 = IAPConnection(
        host="192.168.20.56",
        username="admin",
        password="test123",
    )
    print("  ✓ Connection object created")
    print(f"  Host: {conn1.host}")
    print(f"  User: {conn1.username}")
    print(f"  Password: {'***' if conn1.password else None}")

except Exception as e:
    print(f"  ✗ Error: {e}")

try:
    # Test 2: SSH config
    print("\nTest 2: SSH config")
    conn2 = IAPConnection(
        host="192.168.20.56",
        username="admin",
        ssh_config=Path("~/.ssh/config"),
    )
    print("  ✓ Connection object created")
    print(f"  Host: {conn2.host}")
    print(f"  User: {conn2.username}")
    print(f"  SSH config: {conn2.ssh_config}")

except Exception as e:
    print(f"  ✗ Error: {e}")

try:
    # Test 3: No auth (default)
    print("\nTest 3: No auth (default)")
    conn3 = IAPConnection(
        host="192.168.20.56",
        username="admin",
    )
    print("  ✓ Connection object created")
    print(f"  Host: {conn3.host}")
    print(f"  User: {conn3.username}")

except Exception as e:
    print(f"  ✗ Error: {e}")

print("\n✅ All tests completed!")
