#!/usr/bin/env python3
"""
Poe API Test Script
Quick test to verify Poe API connection
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from poe_client import PoeClient, test_connection

def main():
    """Main test"""
    
    print("=" * 80)
    print("🧪 Testing Poe API Orchestrator")
    print("=" * 80)
    print()
    
    # Check API key
    api_key = os.getenv("POE_API_KEY", "")
    if not api_key:
        print("❌ POE_API_KEY not set!")
        print()
        print("Please set your Poe API key:")
        print("  export POE_API_KEY='your-api-key-here'")
        print()
        return 1
    
    print(f"✅ API Key found: {api_key[:20]}...")
    print()
    
    # Test connection
    test_connection()
    
    # Interactive test
    print("=" * 80)
    print("🎮 Interactive Test")
    print("=" * 80)
    print()
    
    client = PoeClient()
    
    while True:
        print("\nChoose test:")
        print("1. Coding (GPT-5.3-Codex)")
        print("2. Design (Gemini-3.1-Pro)")
        print("3. Analysis (Claude-Sonnet-4.6)")
        print("4. Reasoning (Claude-Opus-4.6)")
        print("5. Exit")
        print()
        
        choice = input("Enter choice (1-5): ").strip()
        
        if choice == "5":
            print("\n👋 Goodbye!")
            break
        
        if choice not in ["1", "2", "3", "4"]:
            print("❌ Invalid choice")
            continue
        
        prompt = input("\nEnter your prompt: ").strip()
        
        if not prompt:
            print("❌ Empty prompt")
            continue
        
        print("\n⏳ Processing...")
        
        if choice == "1":
            result = client.query_coding(prompt)
        elif choice == "2":
            result = client.query_design(prompt)
        elif choice == "3":
            result = client.query_analysis(prompt)
        elif choice == "4":
            result = client.query_reasoning(prompt)
        
        print()
        print("=" * 80)
        print("📋 Result")
        print("=" * 80)
        
        if result["success"]:
            print(result["response"])
        else:
            print(f"❌ Error: {result['error']}")
        
        print("=" * 80)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
