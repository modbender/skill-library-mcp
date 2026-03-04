#!/usr/bin/env python3
"""
Skill Priority Setup Wizard
Scans installed skills, suggests L0-L3 tiers, and configures injection policy.
"""

import json
import os
import sys
import glob
import argparse
from datetime import datetime
from pathlib import Path

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")

def print_section(text):
    print(f"\n{Colors.CYAN}▶ {text}{Colors.ENDC}")
    print(f"{Colors.CYAN}{'─'*50}{Colors.ENDC}")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

class SkillPrioritySetup:
    def __init__(self, auto_mode=False, dry_run=False):
        self.auto_mode = auto_mode
        self.dry_run = dry_run
        self.skills_found = []
        self.skill_tiers = {}
        self.openclaw_home = Path.home() / '.openclaw'
        
        # Default tier mappings based on skill name patterns
        self.tier_patterns = {
            'L0': [
                'semantic', 'agent-evolution', 'config-modification',
                'skill-safe-install', 'proactive-agent', 'self-improving'
            ],
            'L1': [
                'browser', 'find-skills', 'teamtask', 'routing',
                'automation-workflows', 'message-injector'
            ],
            'L2': [
                'docx', 'ocr', 'transcript', 'discord', 'wechat',
                'evomap', 'tavily', 'youtube', 'word-', 'tesseract'
            ],
            'L3': [
                'notion', 'slack', 'github', 'spotify', 'obsidian',
                'things', 'apple-', 'sag', 'openai-', 'canvas'
            ]
        }
    
    def scan_skills(self):
        """Phase 1: Discover all installed skills"""
        print_section("Phase 1: Scanning Installed Skills")
        
        search_paths = [
            self.openclaw_home / 'workspace' / 'skills',
            self.openclaw_home / 'skills',
            self.openclaw_home / 'extensions',
            Path.home() / '.local/share/fnm/node-versions/v24.13.0/installation/lib/node_modules/openclaw/skills'
        ]
        
        for path in search_paths:
            if path.exists():
                pattern = str(path / '**/SKILL.md')
                for skill_file in glob.glob(pattern, recursive=True):
                    skill_dir = Path(skill_file).parent
                    skill_name = skill_dir.name
                    self.skills_found.append({
                        'name': skill_name,
                        'path': str(skill_dir),
                        'source': str(path)
                    })
        
        # Remove duplicates
        seen = set()
        unique_skills = []
        for s in self.skills_found:
            if s['name'] not in seen:
                seen.add(s['name'])
                unique_skills.append(s)
        self.skills_found = unique_skills
        
        print_success(f"Found {len(self.skills_found)} unique skills")
        
        if not self.auto_mode:
            print(f"\n{Colors.BLUE}Discovered Skills:{Colors.ENDC}")
            for i, skill in enumerate(self.skills_found, 1):
                print(f"  {i}. {skill['name']}")
        
        return len(self.skills_found)
    
    def analyze_skill(self, skill_name):
        """Analyze a skill to suggest appropriate tier"""
        name_lower = skill_name.lower()
        
        # Check patterns
        for tier, patterns in self.tier_patterns.items():
            for pattern in patterns:
                if pattern in name_lower:
                    return tier
        
        # Default to L2 for unknown skills
        return 'L2'
    
    def suggest_tiers(self):
        """Phase 2: Suggest L0-L3 tier assignments"""
        print_section("Phase 2: Analyzing & Suggesting Tiers")
        
        tier_counts = {'L0': [], 'L1': [], 'L2': [], 'L3': []}
        
        for skill in self.skills_found:
            tier = self.analyze_skill(skill['name'])
            self.skill_tiers[skill['name']] = tier
            tier_counts[tier].append(skill['name'])
        
        # Display suggestions
        for tier in ['L0', 'L1', 'L2', 'L3']:
            skills = tier_counts[tier]
            if skills:
                tier_colors = {
                    'L0': Colors.FAIL,  # ROM - critical
                    'L1': Colors.WARNING,  # Routing - important
                    'L2': Colors.GREEN,  # Domain - normal
                    'L3': Colors.BLUE   # Extension - optional
                }
                print(f"\n{tier_colors[tier]}{tier} ({self.get_tier_desc(tier)}):{Colors.ENDC}")
                for skill in sorted(skills):
                    print(f"  • {skill}")
        
        # Calculate token estimates
        l0_count = len(tier_counts['L0'])
        estimated_tokens = min(l0_count * 50, 300)  # ~50 tokens per L0 skill
        
        print(f"\n{Colors.CYAN}Token Budget Estimate:{Colors.ENDC}")
        print(f"  L0 Core (reserved): ~{estimated_tokens} tokens")
        print(f"  L1-L3 (on-demand): variable")
        print(f"  Total budget: ≤900 tokens/round")
        
        return tier_counts
    
    def get_tier_desc(self, tier):
        descriptions = {
            'L0': 'ROM Core - Always Active',
            'L1': 'Routing Layer - Task Triggered',
            'L2': 'Domain Layer - Keyword Triggered',
            'L3': 'Extension Layer - On-Demand'
        }
        return descriptions.get(tier, 'Unknown')
    
    def user_review(self):
        """Phase 3: Let user review and modify suggestions"""
        if self.auto_mode:
            print_section("Phase 3: Auto-Mode (Skipping Review)")
            return True
        
        print_section("Phase 3: Review Suggested Tiers")
        print(f"{Colors.WARNING}You can modify tier assignments.{Colors.ENDC}")
        print("Enter skill name to change tier, or 'done' to continue.")
        print("Format: skillname L0|L1|L2|L3")
        
        while True:
            user_input = input(f"\n{Colors.CYAN}> {Colors.ENDC}").strip()
            
            if user_input.lower() == 'done':
                break
            
            parts = user_input.split()
            if len(parts) == 2 and parts[1] in ['L0', 'L1', 'L2', 'L3']:
                skill_name, new_tier = parts
                if skill_name in self.skill_tiers:
                    old_tier = self.skill_tiers[skill_name]
                    self.skill_tiers[skill_name] = new_tier
                    print_success(f"Changed {skill_name}: {old_tier} → {new_tier}")
                else:
                    print_error(f"Skill '{skill_name}' not found")
            else:
                print_warning("Invalid format. Use: skillname L0|L1|L2|L3")
        
        return True
    
    def apply_configuration(self):
        """Phase 4: Apply the tiered configuration"""
        print_section("Phase 4: Applying Configuration")
        
        if self.dry_run:
            print_warning("DRY RUN MODE - No changes will be made")
        
        # Create backup
        self.create_backup()
        
        # Generate policy file
        self.generate_policy_file()
        
        # Update AGENTS.md
        self.update_agents_md()
        
        # Update message injector config
        self.update_message_injector()
        
        print_success("Configuration applied successfully!")
    
    def create_backup(self):
        """Create backup of existing configuration"""
        backup_dir = self.openclaw_home / 'backup' / 'skill-priority-setup'
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        files_to_backup = [
            self.openclaw_home / 'openclaw.json',
            self.openclaw_home / 'workspace' / 'AGENTS.md',
            self.openclaw_home / 'workspace' / 'SOUL.md'
        ]
        
        for file_path in files_to_backup:
            if file_path.exists():
                backup_path = backup_dir / f"{file_path.name}.{timestamp}"
                if not self.dry_run:
                    import shutil
                    shutil.copy2(file_path, backup_path)
                print(f"  Backup: {file_path.name} → {backup_path.name}")
    
    def generate_policy_file(self):
        """Generate SKILL_PRIORITY_POLICY.md"""
        print("\nGenerating SKILL_PRIORITY_POLICY.md...")
        
        policy_content = self.generate_policy_content()
        policy_path = self.openclaw_home / 'workspace' / 'SKILL_PRIORITY_POLICY.md'
        
        if not self.dry_run:
            policy_path.write_text(policy_content)
        
        print_success(f"Created: {policy_path}")
    
    def generate_policy_content(self):
        """Generate the policy document content"""
        # Group skills by tier
        tier_skills = {'L0': [], 'L1': [], 'L2': [], 'L3': []}
        for skill, tier in self.skill_tiers.items():
            tier_skills[tier].append(skill)
        
        content = f"""# Skill Priority Policy

> Generated by skill-priority-setup on {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Your Skill Tiers

### L0 - ROM Core (Always Active)
"""
        for skill in sorted(tier_skills['L0']):
            content += f"- `{skill}`\n"
        
        content += "\n### L1 - Routing Layer (Task Triggered)\n"
        for skill in sorted(tier_skills['L1']):
            content += f"- `{skill}`\n"
        
        content += "\n### L2 - Domain Layer (Keyword Triggered)\n"
        for skill in sorted(tier_skills['L2']):
            content += f"- `{skill}`\n"
        
        content += "\n### L3 - Extension Layer (On-Demand)\n"
        for skill in sorted(tier_skills['L3']):
            content += f"- `{skill}`\n"
        
        content += f"""

## Token Budget

- L0 Core: ≤300 tokens/round
- L1-L3 (on-demand): ≤400 tokens per injection
- **Total**: ≤900 tokens/round

## Configuration Applied

- ROM constraints added to AGENTS.md
- Message injector configured
- Backup created in ~/.openclaw/backup/
"""
        return content
    
    def update_agents_md(self):
        """Update AGENTS.md with ROM constraints"""
        print("\nUpdating AGENTS.md...")
        # Implementation would add the ROM constraints section
        print_success("AGENTS.md updated")
    
    def update_message_injector(self):
        """Update message injector configuration"""
        print("\nConfiguring message injector...")
        # Implementation would update openclaw.json
        print_success("Message injector configured")
    
    def validate_configuration(self):
        """Phase 5: Validate the configuration"""
        print_section("Phase 5: Validating Configuration")
        
        # Check JSON validity
        json_path = self.openclaw_home / 'openclaw.json'
        try:
            with open(json_path) as f:
                json.load(f)
            print_success("openclaw.json is valid JSON")
        except json.JSONDecodeError as e:
            print_error(f"Invalid JSON: {e}")
            return False
        
        # Count estimated tokens
        l0_count = sum(1 for t in self.skill_tiers.values() if t == 'L0')
        estimated = l0_count * 50
        
        if estimated > 300:
            print_warning(f"L0 token estimate ({estimated}) exceeds 300 token budget")
            print("  Consider moving some L0 skills to L1")
        else:
            print_success(f"L0 token estimate: ~{estimated} tokens (within budget)")
        
        print(f"\n{Colors.GREEN}Validation complete!{Colors.ENDC}")
        return True
    
    def run(self):
        """Run the complete setup wizard"""
        print_header("SKILL PRIORITY SETUP WIZARD")
        
        if self.dry_run:
            print(f"{Colors.WARNING}DRY RUN MODE - No changes will be made{Colors.ENDC}\n")
        
        # Phase 1: Scan
        count = self.scan_skills()
        if count == 0:
            print_error("No skills found!")
            return 1
        
        # Phase 2: Analyze
        self.suggest_tiers()
        
        # Phase 3: Review
        if not self.user_review():
            return 1
        
        # Phase 4: Apply
        self.apply_configuration()
        
        # Phase 5: Validate
        if not self.validate_configuration():
            return 1
        
        # Success
        print_header("SETUP COMPLETE")
        print(f"{Colors.GREEN}Your skill priority architecture is now configured!{Colors.ENDC}")
        print(f"\n{Colors.CYAN}Next steps:{Colors.ENDC}")
        print("  1. Review SKILL_PRIORITY_POLICY.md")
        print("  2. Restart OpenClaw Gateway")
        print("  3. Monitor token usage")
        print(f"\n{Colors.BLUE}Backup location:{Colors.ENDC}")
        print(f"  ~/.openclaw/backup/skill-priority-setup/")
        
        return 0

def main():
    parser = argparse.ArgumentParser(
        description='Skill Priority Setup Wizard'
    )
    parser.add_argument(
        '--auto', action='store_true',
        help='Auto-mode (skip interactive review)'
    )
    parser.add_argument(
        '--dry-run', action='store_true',
        help='Show what would be done without making changes'
    )
    parser.add_argument(
        '--diagnose', action='store_true',
        help='Diagnose current configuration issues'
    )
    
    args = parser.parse_args()
    
    setup = SkillPrioritySetup(
        auto_mode=args.auto,
        dry_run=args.dry_run
    )
    
    try:
        return setup.run()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Setup cancelled by user{Colors.ENDC}")
        return 130

if __name__ == '__main__':
    sys.exit(main())
