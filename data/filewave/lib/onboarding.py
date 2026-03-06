#!/usr/bin/env python3
"""
Post-installation onboarding for FileWave skill.

Called by OpenClaw/clawhub after skill installation.
Guides user through initial server configuration.
"""

import sys
from pathlib import Path

# Add skill directory to path
skill_dir = Path(__file__).parent
sys.path.insert(0, str(skill_dir))

from config_manager import FileWaveConfig, setup_wizard


def run_onboarding():
    """Run onboarding flow for first-time setup.
    
    Called automatically during installation.
    User configures first server and can immediately use the skill.
    """
    
    print("\n" + "="*70)
    print("  ✓ FileWave Skill Installed Successfully")
    print("="*70)
    print()
    print("The FileWave UEM API skill lets you query device inventory across")
    print("multiple FileWave servers with intelligent filtering and multi-server")
    print("support.")
    print()
    print("This installer will guide you through adding your first FileWave server.")
    print("After this, you can immediately start querying devices.")
    print()
    
    config = FileWaveConfig()
    profiles = config.list_profiles()
    
    # Check if already configured
    if profiles:
        print(f"Existing profiles found: {', '.join(profiles)}")
        print()
        response = input("Would you like to add another server? (yes/no): ").strip().lower()
        if response not in ("yes", "y"):
            print_ready_message(profiles)
            return True
    
    # Get first server setup
    print("\n" + "-"*70)
    print("  Server Configuration")
    print("-"*70)
    print()
    print("You'll need:")
    print("  1. Profile name (e.g., 'lab', 'production')")
    print("  2. FileWave server hostname (e.g., 'filewave.company.com')")
    print("  3. API token from FileWave Admin Console")
    print()
    
    try:
        # Interactive setup
        profile_name = input("Profile name (e.g., 'lab'): ").strip()
        if not profile_name:
            print("\n✗ Profile name required. Skipping setup.")
            return False
        
        print()
        server = input("Server hostname/URL (e.g., 'filewave.company.com'): ").strip()
        if not server:
            print("\n✗ Server required. Skipping setup.")
            return False
        
        # Normalize server URL
        if not server.startswith("http"):
            server = f"https://{server}"
        
        print()
        print("To get your API token:")
        print("  1. Log in to FileWave Admin Console")
        print("  2. Go to Settings → API")
        print("  3. Click 'Generate Token'")
        print("  4. Copy and paste below")
        print()
        
        token = input("API Token: ").strip()
        if not token:
            print("\n✗ Token required. Skipping setup.")
            return False
        
        print()
        description = input("Description (optional, e.g., 'Lab environment'): ").strip()
        
        # Save profile
        config.add_profile(profile_name, server, token, description)
        
        # Set as default if first profile
        if not config.get_default_profile():
            config.set_default_profile(profile_name)
            print(f"\n✓ Profile '{profile_name}' created and set as default")
        else:
            print(f"\n✓ Profile '{profile_name}' created")
        
        print(f"✓ Config saved to: ~/.filewave/config")
        print(f"✓ Permissions: 600 (secure, user only)\n")
        
        # Show ready message
        print_ready_message([profile_name])
        return True
        
    except KeyboardInterrupt:
        print("\n\n✗ Setup cancelled by user")
        print("\nYou can configure later with:")
        print("  filewave setup")
        return False
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nYou can try again with:")
        print("  filewave setup")
        return False


def print_ready_message(profiles):
    """Print ready-to-use message with examples and next steps."""
    
    print("\n" + "="*70)
    print("  ✓ FileWave Skill is Ready!")
    print("="*70)
    print()
    
    if profiles:
        print(f"Configured profiles: {', '.join(profiles)}")
        print()
    
    print("---")
    print("  QUICK START EXAMPLES")
    print("---\n")
    
    print("1. List your configured servers:")
    print("   $ filewave profiles\n")
    
    print("2. Query all devices from your default server:")
    print("   $ filewave query --query-id 1\n")
    
    print("3. Query with a custom name (for comparison later):")
    print("   $ filewave query --query-id 1 --reference my_devices\n")
    
    print("4. Filter devices (natural language):")
    print("   $ filewave query --query-id 1 --filter 'last_seen > 30 days'\n")
    
    print("5. Get JSON output for scripting:")
    print("   $ filewave query --query-id 1 --format json\n")
    
    print("---")
    print("  WHAT YOU CAN DO")
    print("---\n")
    
    print("✓ Query device inventory across multiple FileWave servers")
    print("✓ Filter devices by OS, status, last seen, and more")
    print("✓ Find stale devices (not checked in for 30+ days)")
    print("✓ Compare device counts across servers")
    print("✓ Track queries in a session with named references")
    print("✓ Export data as JSON for analysis")
    print("✓ Add more servers anytime with: filewave setup\n")
    
    print("---")
    print("  NEXT STEPS")
    print("---\n")
    
    print("Try your first query:")
    print("  $ filewave query --query-id 1\n")
    
    print("For more examples and options:")
    print("  $ filewave --help\n")
    
    print("Full documentation:")
    print("  ~/.openclaw/workspace/skills/filewave/README.md")
    print("  ~/.openclaw/workspace/skills/filewave/CLI_REFERENCE.md\n")


if __name__ == "__main__":
    success = run_onboarding()
    sys.exit(0 if success else 1)
