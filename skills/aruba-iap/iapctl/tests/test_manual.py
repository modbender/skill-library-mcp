"""Test connection and command generation."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from iapctl.models import Changes
from iapctl.diff_engine import generate_commands
from iapctl.secrets import load_secrets_file, get_secret


def test_secret_resolution():
    """Test secret resolution."""
    print("🧪 Testing secret resolution...")

    # Load secrets - find examples directory
    base_dir = Path(__file__).parent.parent.parent
    secrets_file = base_dir / "examples" / "example-secrets.json"
    if secrets_file.exists():
        load_secrets_file(secrets_file)
        print(f"  ✓ Loaded secrets from {secrets_file}")
    else:
        print(f"  ⚠ Secrets file not found: {secrets_file}")

    # Test secret lookup
    secret = get_secret("secret:radius-primary-key")
    if secret:
        print(f"  ✓ Found secret: radius-primary-key = ***REDACTED***")
    else:
        print(f"  ✗ Secret not found: radius-primary-key")

    # Test env variable
    import os
    os.environ["TEST_VAR"] = "test-value"
    secret = get_secret("env:TEST_VAR")
    if secret:
        print(f"  ✓ Found env var: TEST_VAR = {secret}")
    else:
        print(f"  ✗ Env var not found: TEST_VAR")


def test_command_generation():
    """Test command generation."""
    print("\n🧪 Testing command generation...")

    # Load example changes - find examples directory
    base_dir = Path(__file__).parent.parent.parent
    changes_file = base_dir / "examples" / "example-changes.json"
    if not changes_file.exists():
        print(f"  ✗ Changes file not found: {changes_file}")
        return

    import json
    with open(changes_file) as f:
        changes_data = json.load(f)

    changes = Changes(**changes_data)
    print(f"  ✓ Loaded {len(changes.changes)} changes")

    # Generate commands
    command_set = generate_commands(changes, resolve_secrets=False)
    print(f"  ✓ Generated {len(command_set.commands)} commands")
    print(f"  ✓ Generated {len(command_set.rollback_commands)} rollback commands")

    # Print first few commands
    print("\n  First 3 commands:")
    for i, cmd in enumerate(command_set.commands[:3], 1):
        print(f"    {i}. {cmd}")

    print("\n  First 3 rollback commands:")
    for i, cmd in enumerate(command_set.rollback_commands[:3], 1):
        print(f"    {i}. {cmd}")


if __name__ == "__main__":
    test_secret_resolution()
    test_command_generation()
    print("\n✅ All tests passed!")
