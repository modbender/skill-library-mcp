#!/usr/bin/env python3
"""
Example of how an OpenClaw agent uses the FatSecret skill.
This shows the complete user interaction flow.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.fatsecret_agent_helper import (
    get_authentication_flow,
    complete_authentication_flow,
    save_user_credentials
)
from scripts.fatsecret_diary_simple import quick_log, load_tokens

class FatSecretAgent:
    """Example agent using FatSecret skill."""
    
    def __init__(self):
        self.user_id = None
        self.state = "initial"
    
    def send_message(self, message: str):
        """Simulate sending message to user."""
        print(f"🤖 AGENT → {message}")
    
    def get_user_input(self, prompt: str) -> str:
        """Simulate receiving user input."""
        print(f"👤 USER ← {prompt}")
        # In a real agent, this would wait for user response
        # For this example, we simulate input
        if "PIN" in prompt:
            return "123456"  # Simulated PIN
        elif "Consumer Key" in prompt:
            return "77cf230fbbf54a1da062204d168faee3"  # Simulated key
        elif "Consumer Secret" in prompt:
            return "c48fa65779554fdbb3060a3a3684d4e0"  # Simulated secret
        else:
            return "simulated_input"
    
    async def handle_fatsecret_setup(self):
        """Handle complete FatSecret setup."""
        self.send_message("Starting FatSecret setup!")
        
        # Step 1: Check status
        self.send_message("Checking if you're already connected to FatSecret...")
        state = get_authentication_flow()
        
        if state["status"] == "already_authenticated":
            self.send_message(state["message"])
            self.send_message(state["test_result"]["message"])
            return True
        
        elif state["status"] == "need_credentials":
            self.send_message("I need your FatSecret credentials.")
            
            # Ask for consumer key
            consumer_key = await self.get_user_input("Enter Consumer Key:")
            
            # Ask for consumer secret
            consumer_secret = await self.get_user_input("Enter Consumer Secret:")
            
            # Save credentials
            self.send_message("Saving your credentials...")
            result = save_user_credentials(consumer_key, consumer_secret)
            
            if result["status"] != "success":
                self.send_message(result["message"])
                return False
            
            self.send_message("✅ Credentials saved!")
        
        # Step 2: Start OAuth1 authentication
        self.send_message("Starting OAuth1 authentication...")
        state = get_authentication_flow()
        
        if state["status"] == "need_authorization":
            self.send_message("You need to authorize the application:")
            self.send_message(f"🔗 Visit: {state['authorization_url']}")
            self.send_message("After authorizing, send me the PIN you see.")
            
            # Wait for PIN from user
            pin = await self.get_user_input("Enter the PIN from FatSecret:")
            
            # Complete authentication
            self.send_message("Completing authentication with the PIN...")
            result = complete_authentication_flow(pin)
            
            if result["status"] == "authenticated":
                self.send_message("✅ Authentication complete!")
                self.send_message(result["test_result"]["message"])
                return True
            else:
                self.send_message(f"❌ Error: {result['message']}")
                return False
        
        else:
            self.send_message(f"Unexpected status: {state['status']}")
            self.send_message(state["message"])
            return False
    
    async def log_breakfast(self):
        """Log standard breakfast."""
        self.send_message("Logging your standard breakfast to FatSecret...")
        
        try:
            # Use quick_log to add 3 eggs
            success = quick_log("egg", quantity=3, meal="Breakfast")
            
            if success:
                self.send_message("✅ Breakfast logged! 3 eggs added to diary.")
                
                # Show nutritional summary
                self.send_message("""
🍳 Breakfast summary:
• 3 eggs (Breakfast)
• Smoothie: banana + orange + kiwi + 15g chia + 40g oats

📊 Estimated total: 668 kcal
🥩 29g protein | 🍚 86g carbs | 🥑 23.5g fat
""")
                return True
            else:
                self.send_message("❌ Error logging breakfast.")
                return False
                
        except Exception as e:
            self.send_message(f"❌ Error: {type(e).__name__}: {e}")
            return False
    
    async def search_food(self, query: str):
        """Search for a food."""
        self.send_message(f"🔍 Searching: {query}")
        
        from scripts.fatsecret_diary_simple import load_tokens, search_food
        
        tokens = load_tokens()
        if not tokens:
            self.send_message("❌ Not authenticated. Run setup first.")
            return
        
        foods = search_food(query, tokens, max_results=3)
        
        if not foods:
            self.send_message("❌ No results found.")
            return
        
        self.send_message(f"📋 Found {len(foods)} results:")
        
        for i, food in enumerate(foods, 1):
            name = food.get("food_name", "Unknown")
            brand = food.get("brand_name", "")
            brand_str = f" ({brand})" if brand else ""
            food_id = food.get("food_id")
            
            self.send_message(f"{i}. {name}{brand_str} (ID: {food_id})")
    
    async def interactive_log(self):
        """Interactive mode for logging foods."""
        self.send_message("Starting interactive diary mode...")
        
        # Import here to avoid circular dependencies
        import subprocess
        import os
        
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        script_path = os.path.join(script_dir, "scripts", "fatsecret_diary_simple.py")
        
        # Run interactive script
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=script_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            self.send_message("✅ Operation complete!")
            # Could parse output to show to user
        else:
            self.send_message(f"❌ Error: {result.stderr}")

async def main():
    """Example complete flow."""
    agent = FatSecretAgent()
    
    print("="*60)
    print("EXAMPLE: Agent using FatSecret skill")
    print("="*60)
    
    # 1. Setup authentication
    print("\n1. 🔐 Authentication Setup")
    print("-"*40)
    success = await agent.handle_fatsecret_setup()
    
    if not success:
        print("❌ Setup failed.")
        return
    
    # 2. Log breakfast
    print("\n2. 🍳 Logging Breakfast")
    print("-"*40)
    await agent.log_breakfast()
    
    # 3. Search food
    print("\n3. 🔍 Searching Food")
    print("-"*40)
    await agent.search_food("chicken breast")
    
    # 4. Interactive mode
    print("\n4. 📝 Interactive Mode")
    print("-"*40)
    # await agent.interactive_log()  # Commented for example
    
    print("\n" + "="*60)
    print("✅ Example complete!")
    print("="*60)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())