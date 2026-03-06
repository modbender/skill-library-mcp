"""Debug connection issue."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from iapctl.connection import IAPConnection

print("Debugging connection parameters...")

# Test different scenarios
test_cases = [
    {
        "name": "No ssh_config (None)",
        "params": {
            "host": "192.168.20.56",
            "username": "admin",
            "ssh_config": None,
        }
    },
    {
        "name": "ssh_config = None (default)",
        "params": {
            "host": "192.168.20.56",
            "username": "admin",
        }
    },
]

for test_case in test_cases:
    print(f"\n{'='*60}")
    print(f"Test: {test_case['name']}")
    print(f"{'='*60}")

    params = test_case['params']
    print(f"  ssh_config type: {type(params.get('ssh_config'))}")
    print(f"  ssh_config value: {params.get('ssh_config')}")

    try:
        conn = IAPConnection(**params)
        print(f"  ✓ IAPConnection created successfully")
    except Exception as e:
        print(f"  ✗ Error creating IAPConnection: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*60)
print("All debug tests completed!")
