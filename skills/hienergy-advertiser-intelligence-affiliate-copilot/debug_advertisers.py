import os
import sys
# Ensure the skill directory is in sys.path
sys.path.insert(0, '/Users/patrickkarsh/.openclaw/workspace/skills/open_claw_skill')
from scripts.hienergy_skill import HiEnergySkill

try:
    api_key = os.environ.get('HIENERGY_API_KEY')
    skill = HiEnergySkill(api_key=api_key)
    
    print("Calling get_advertisers('weightloss', limit=1)...")
    advertisers = skill.get_advertisers(search='weightloss', limit=1)
    print(f"Found {len(advertisers)} advertisers.")
    if advertisers:
        print("First advertiser:", advertisers[0].get('name'))

except Exception as e:
    print(f"Error executing skill: {e}")
    import traceback
    traceback.print_exc()
