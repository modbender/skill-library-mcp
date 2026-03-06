import os
import sys
sys.path.insert(0, '/Users/patrickkarsh/.openclaw/workspace/skills/open_claw_skill')
from scripts.hienergy_skill import HiEnergySkill

try:
    api_key = os.environ.get('HIENERGY_API_KEY')
    skill = HiEnergySkill(api_key=api_key)
    # Direct specific query for Alo Yoga
    print(skill.answer_question("tell me about the advertiser alo yoga"))
except Exception as e:
    print(f"Error: {e}")
