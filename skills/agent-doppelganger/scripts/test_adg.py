import sys
import os
# Add the skill directory to path if needed, but we'll just import the script directly
sys.path.append(os.path.join(os.getcwd(), "skills/agent-doppelganger/scripts"))
from adg import AgentDoppelganger

def run_tests():
    adg = AgentDoppelganger()
    
    test_cases = [
        ("Can we do a call tomorrow at 2pm?", "email", "Safe/Allowed (Scheduling)"),
        ("I need to send you $500 for the project.", "whatsapp", "Blocked (Finance)"),
        ("What is your opinion on the current political landscape in Kashmir?", "discord", "Blocked (Politics)"),
        ("Hi, just checking in on the status of the design.", "slack", "Safe/Allowed (Clarification)"),
    ]

    print("# ADG Test Run")
    print("-" * 30)
    
    for msg, channel, expected_desc in test_cases:
        print(f"Input: '{msg}' | Channel: {channel}")
        print(f"Goal: {expected_desc}")
        
        # We need to tweak the analyze_intent in adg.py for these tests 
        # since the current scaffold is static. 
        # I'll update adg.py briefly to handle these specific keywords for the demo.
        
        result = adg.handle_message(msg, channel)
        print(f"Result: {result}")
        print("-" * 30)

if __name__ == "__main__":
    run_tests()
