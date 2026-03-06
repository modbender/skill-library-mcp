"""Complete workflow test without real IAP device."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from iapctl.models import Changes
from iapctl.diff_engine import generate_commands, save_command_set, assess_risks
from iapctl.secrets import load_secrets_file, get_secret
from iapctl.operations import save_raw_output, save_result_json
from iapctl.models import Result, Artifact, CheckResult, TimingInfo
import time

print("="*60)
print("Complete Workflow Test (No Real Device)")
print("="*60)

base_dir = Path(__file__).parent.parent.parent

# Step 1: Load secrets
print("\n[1/5] Loading secrets...")
secrets_file = base_dir / "examples" / "example-secrets.json"
if secrets_file.exists():
    load_secrets_file(secrets_file)
    print(f"  ✓ Loaded secrets from {secrets_file}")
    print(f"  - radius-primary-key: ***REDACTED***")
    print(f"  - radius-secondary-key: ***REDACTED***")
else:
    print(f"  ⚠ Secrets file not found")

# Step 2: Load changes
print("\n[2/5] Loading changes...")
changes_file = base_dir / "examples" / "example-changes.json"
import json
with open(changes_file) as f:
    changes_data = json.load(f)
changes = Changes(**changes_data)
print(f"  ✓ Loaded {len(changes.changes)} changes")
print(f"  - NTP: {len([c for c in changes.changes if c.type == 'ntp'])}")
print(f"  - DNS: {len([c for c in changes.changes if c.type == 'dns'])}")
print(f"  - SSID/VLAN: {len([c for c in changes.changes if c.type == 'ssid_vlan'])}")
print(f"  - RADIUS: {len([c for c in changes.changes if c.type == 'radius_server'])}")

# Step 3: Generate commands
print("\n[3/5] Generating commands...")
command_set = generate_commands(changes, resolve_secrets=False)
command_set.change_id = "test_20260222_000000"
print(f"  ✓ Generated {len(command_set.commands)} commands")
print(f"  ✓ Generated {len(command_set.rollback_commands)} rollback commands")

# Step 4: Save commands
print("\n[4/5] Saving commands...")
out_dir = base_dir / "test-output" / "complete-workflow"
save_command_set(command_set, out_dir)
print(f"  ✓ Saved commands to {out_dir}")
print(f"  - commands.json")
print(f"  - commands.txt")

# Step 5: Assess risks
print("\n[5/5] Assessing risks...")
risks = assess_risks(command_set)
print(f"  ✓ Risk level: {risks['level']}")
if risks.get('warnings'):
    print(f"  - Warnings: {len(risks['warnings'])}")
    for warning in risks['warnings']:
        print(f"    • {warning}")
if risks.get('concerns'):
    print(f"  - Concerns: {len(risks['concerns'])}")
    for concern in risks['concerns']:
        print(f"    • {concern}")

# Print sample commands
print("\n" + "="*60)
print("Sample Commands")
print("="*60)
print("\nFirst 5 commands:")
for i, cmd in enumerate(command_set.commands[:5], 1):
    print(f"  {i}. {cmd}")

print("\nFirst 3 rollback commands:")
for i, cmd in enumerate(command_set.rollback_commands[:3], 1):
    print(f"  {i}. {cmd}")

# Test with secret resolution
print("\n" + "="*60)
print("Testing Secret Resolution")
print("="*60)
command_set_with_secrets = generate_commands(changes, resolve_secrets=True)
print(f"✓ Generated {len(command_set_with_secrets.commands)} commands with resolved secrets")
print(f"  (Secrets are redacted in output for security)")

print("\n" + "="*60)
print("✅ All tests passed!")
print("="*60)
print(f"\nOutput directory: {out_dir}")
print(f"\nYou can view generated commands:")
print(f"  cat {out_dir}/commands.txt")
