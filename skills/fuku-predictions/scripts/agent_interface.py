#!/usr/bin/env python3
"""
Agent Interface for Kalshi Autopilot — Conversational profile building and trading.

This is the main interface agents call when users want to:
- Build or modify their trading preferences
- Scan for opportunities matching their profile  
- Place trades based on recommendations
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from profile_builder import (
    extract_user_intent, build_profile_from_intent, analyze_preferences,
    save_user_profile, load_user_profiles, format_profile_summary
)


def handle_profile_request(user_input: str) -> str:
    """Handle user requests to build or modify profiles."""
    user_input = user_input.lower().strip()
    
    # Check if user wants to list existing profiles
    if "list" in user_input and ("profile" in user_input or "preference" in user_input):
        profiles = load_user_profiles()
        if not profiles:
            return "📋 No custom profiles found. Use the default profile or tell me what you're looking for to create one."
        
        response = ["📋 **Your Trading Profiles:**\n"]
        for p in profiles:
            response.append(format_profile_summary(p))
            response.append("")
        
        response.append("Say 'use [profile name]' to switch or describe what you want to create a new one.")
        return "\n".join(response)
    
    # Check if user wants to use a specific profile
    use_match = None
    for keyword in ["use", "switch to", "activate"]:
        if keyword in user_input:
            # Extract profile name after the keyword
            parts = user_input.split(keyword, 1)
            if len(parts) > 1:
                use_match = parts[1].strip().strip('"\'')
                break
    
    if use_match:
        profiles = load_user_profiles()
        for p in profiles:
            if (p.get("_filename", "").lower() == use_match.lower() or 
                p.get("name", "").lower() == use_match.lower()):
                return f"✅ Switched to profile: **{p.get('name')}**\n\n{format_profile_summary(p)}"
        return f"❌ Profile '{use_match}' not found. Say 'list profiles' to see available options."
    
    # Analyze user input for profile building
    analysis = analyze_preferences(user_input)
    
    if not analysis["understood"]:
        return """❓ I can help you define what trading opportunities you care about.
        
**Examples:**
• "I want home dogs getting 7+ points in college basketball"
• "Show me CBB unders in letdown spots after big wins"  
• "Find me NBA spreads when the best player has a 30+ FPR gap"
• "I like $5 bets on close games under 3 points"

**Tell me what you're looking for!**"""
    
    response = ["✅ **Here's what I understood:**"]
    for item in analysis["understood"]:
        response.append(f"• {item}")
    
    if analysis["examples"]:
        response.append("\n💡 **This profile would find:**")
        for ex in analysis["examples"]:
            response.append(f"• {ex}")
    
    if analysis["clarifying_questions"]:
        response.append("\n❓ **To refine further:**")
        for q in analysis["clarifying_questions"]:
            response.append(f"• {q}")
        
        response.append("\n**Want to save this profile, or refine it more?**")
    else:
        response.append("\n**Ready to save this profile?** Give it a name or say 'test it first'.")
    
    return "\n".join(response)


def handle_scan_request(user_input: str, profile_name: str = "default") -> str:
    """Handle requests to scan for opportunities."""
    try:
        # Import here to avoid slow startup
        from autopilot import main as autopilot_main
        from profile_engine import load_profile
        import subprocess
        import os
        
        # Check if profile exists
        try:
            profile = load_profile(profile_name)
        except FileNotFoundError:
            return f"❌ Profile '{profile_name}' not found. Say 'list profiles' or describe what you want."
        
        # Run autopilot scan
        cmd = [
            "arch", "-arm64", "python3", "autopilot.py",
            "--profile", profile_name,
            "--mode", "approve"
        ]
        
        result = subprocess.run(
            cmd, 
            cwd=SCRIPT_DIR,
            capture_output=True, 
            text=True, 
            timeout=120
        )
        
        if result.returncode == 0:
            # Filter out debug logs
            output_lines = [line for line in result.stdout.split('\n') if not line.startswith('[KALSHI]')]
            return '\n'.join(output_lines).strip()
        else:
            error_lines = [line for line in result.stderr.split('\n') if line.strip() and not line.startswith('[KALSHI]')]
            return f"❌ Scan failed: {chr(10).join(error_lines)}"
            
    except subprocess.TimeoutExpired:
        return "⏰ Scan timed out - the API might be slow. Try again in a moment."
    except Exception as e:
        return f"❌ Error running scan: {str(e)}"


def handle_save_profile(user_input: str, profile_data: dict) -> str:
    """Handle requests to save a profile."""
    # Extract profile name from input
    name = "custom-profile"
    
    # Look for quoted names
    import re
    quoted_match = re.search(r'["\']([^"\']+)["\']', user_input)
    if quoted_match:
        name = quoted_match.group(1)
    else:
        # Look for name after keywords
        for keyword in ["call it", "name it", "save as", "name:"]:
            if keyword in user_input.lower():
                parts = user_input.lower().split(keyword, 1)
                if len(parts) > 1:
                    name = parts[1].strip().strip('",.')
                    break
    
    try:
        profile_data["name"] = name.title()
        path = save_user_profile(profile_data, name)
        return f"✅ **Profile saved:** {profile_data['name']}\n📁 Location: {path}\n\nSay 'scan for opportunities' to test it!"
    except Exception as e:
        return f"❌ Error saving profile: {str(e)}"


# ---------------------------------------------------------------------------
# Main conversational interface
# ---------------------------------------------------------------------------

def main_interface(user_input: str, context: dict = None) -> str:
    """Main conversational interface for Kalshi autopilot."""
    user_input = user_input.strip()
    context = context or {}
    
    # Route based on user intent
    if any(word in user_input.lower() for word in ["profile", "preference", "want", "looking for", "find me", "show me"]):
        if any(word in user_input.lower() for word in ["list", "show all", "available"]):
            return handle_profile_request("list profiles")
        else:
            return handle_profile_request(user_input)
    
    elif any(word in user_input.lower() for word in ["scan", "opportunities", "edges", "find trades", "what's available"]):
        profile_name = context.get("current_profile", "default")
        return handle_scan_request(user_input, profile_name)
    
    elif any(word in user_input.lower() for word in ["save", "keep", "store"]) and context.get("profile_data"):
        return handle_save_profile(user_input, context["profile_data"])
    
    else:
        # Default: try to understand as profile building
        return handle_profile_request(user_input)


# ---------------------------------------------------------------------------
# CLI for testing
# ---------------------------------------------------------------------------

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Agent Interface for Kalshi Autopilot")
    parser.add_argument("--input", "-i", help="User input to process")
    parser.add_argument("--scan", action="store_true", help="Run a scan")
    parser.add_argument("--profile", default="default", help="Profile to use for scanning")
    args = parser.parse_args()
    
    if args.scan:
        result = handle_scan_request("scan for opportunities", args.profile)
        print(result)
        return
    
    if args.input:
        result = main_interface(args.input)
        print(result)
        return
    
    # Interactive mode
    print("🤖 Kalshi Autopilot Agent Interface")
    print("   Tell me what trading opportunities you're looking for...\n")
    
    context = {}
    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input or user_input.lower() in ['quit', 'exit', 'done']:
                break
            
            response = main_interface(user_input, context)
            print(f"\nAgent: {response}\n")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break


if __name__ == "__main__":
    main()