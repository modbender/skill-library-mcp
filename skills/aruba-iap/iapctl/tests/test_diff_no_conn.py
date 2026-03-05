"""Test diff without connection."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from iapctl.models import Changes
from iapctl.diff_engine import generate_commands, save_command_set

# Load example changes
base_dir = Path(__file__).parent.parent.parent
changes_file = base_dir / "examples" / "example-changes.json"
import json
with open(changes_file) as f:
    changes_data = json.load(f)

changes = Changes(**changes_data)

# Generate commands
command_set = generate_commands(changes, resolve_secrets=False)

# Save commands
out_dir = Path("/Users/scsun/.openclaw/workspace/skills/aruba-iap/test-output/diff-no-conn")
save_command_set(command_set, out_dir)

print(f"✓ Generated {len(command_set.commands)} commands")
print(f"✓ Saved to {out_dir}")

# Print first 5 commands
print("\nFirst 5 commands:")
for i, cmd in enumerate(command_set.commands[:5], 1):
    print(f"  {i}. {cmd}")
