import os
import sys
# Ensure the skill directory is in sys.path
sys.path.insert(0, '/Users/patrickkarsh/.openclaw/workspace/skills/open_claw_skill')
from scripts.hienergy_skill import HiEnergySkill

try:
    api_key = os.environ.get('HIENERGY_API_KEY')
    if not api_key:
        print("Error: HIENERGY_API_KEY not found in environment")
        sys.exit(1)
    
    skill = HiEnergySkill(api_key=api_key)
    question = "tell me about glp1 affiliate programs I can join"
    
    print(f"Running query: {question}")
    answer = skill.answer_question(question)
    print("\n--- Answer ---")
    print(answer)

except Exception as e:
    print(f"Error executing skill: {e}")
    import traceback
    traceback.print_exc()
