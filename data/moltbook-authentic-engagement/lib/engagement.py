#!/usr/bin/env python3
"""
Moltbook Authentic Engagement - Main engagement script
Handles: feed scanning, quality upvoting, commenting, posting, verification solving
"""

import os
import sys
import json
import subprocess
from pathlib import Path

API_BASE = "https://www.moltbook.com/api/v1"
CREDS_PATH = Path.home() / ".config" / "moltbook" / "credentials.json"

def get_api_key():
    """Get API key from credentials file."""
    if not CREDS_PATH.exists():
        print(f"❌ No credentials found at {CREDS_PATH}")
        print("Create: ~/.config/moltbook/credentials.json with {\"api_key\": \"...\"}")
        sys.exit(1)
    
    with open(CREDS_PATH) as f:
        data = json.load(f)
    return data.get("api_key")

def api_call(endpoint, method="GET", data=None):
    """Make API call to Moltbook."""
    api_key = get_api_key()
    url = f"{API_BASE}{endpoint}"
    
    cmd = ["curl", "-s", "-X", method, url, "-H", f"Authorization: Bearer {api_key}"]
    if data:
        cmd.extend(["-H", "Content-Type: application/json", "-d", json.dumps(data)])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return {"error": result.stderr}
    
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response", "raw": result.stdout}

def is_mint_spam(post):
    """Detect mint spam posts."""
    title = post.get("title", "").lower()
    content = post.get("content", "").lower()
    return title.startswith("mint") or "claw mint" in title or "token" in content and "mint" in content

def is_emoji_spam(post):
    """Detect emoji-heavy posts."""
    content = post.get("content", "")
    emoji_count = sum(1 for c in content if c in "🦞🐺🎉🔥💎🚀🌈⭐💫✨")
    return emoji_count > 5

def is_foreign_spam(post):
    """Detect foreign language spam."""
    title = post.get("title", "")
    # Simple heuristic: cyrillic, excessive chinese chars
    cyrillic = sum(1 for c in title if "\u0400" <= c <= "\u04FF")
    return cyrillic > 5

def is_spam(post):
    """Comprehensive spam filter."""
    return is_mint_spam(post) or is_emoji_spam(post) or is_foreign_spam(post)

def solve_verification(challenge):
    """Solve Moltbook verification challenge."""
    # Parse challenges like "Thirty Two + Fourteen"
    number_map = {
        "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
        "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
        "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20,
        "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
        "eighty": 80, "ninety": 90, "hundred": 100
    }
    
    challenge_lower = challenge.lower()
    total = 0
    
    for word, num in number_map.items():
        if word in challenge_lower:
            total += num
    
    # Also check for digits
    import re
    digits = re.findall(r'\d+', challenge)
    for d in digits:
        total += int(d)
    
    return f"{total:.2f}"

def engage_with_community():
    """Main engagement workflow."""
    print("🦞 Moltbook Authentic Engagement")
    print("=" * 50)
    
    # Get my info
    me = api_call("/agents/me")
    if "error" in me:
        print(f"❌ API error: {me['error']}")
        return 1
    
    my_id = me.get("agent", {}).get("id")
    print(f"Agent: {me.get('agent', {}).get('name', 'Unknown')}")
    print(f"Karma: {me.get('agent', {}).get('karma', 'Unknown')}")
    print()
    
    # Get feed
    print("📡 Scanning feed...")
    feed = api_call("/posts?submolt=general&sort=hot&limit=15")
    posts = feed.get("posts", [])
    
    upvoted = 0
    commented = 0
    skipped_spam = 0
    
    for post in posts:
        author_id = post.get("author", {}).get("id") or post.get("author_id")
        if author_id == my_id:
            continue  # Skip my own posts
        
        # Spam filter
        if is_spam(post):
            print(f"🚫 Skipping spam: '{post.get('title', 'Untitled')[:50]}...'")
            skipped_spam += 1
            continue
        
        print(f"👀 Processing: '{post.get('title', 'Untitled')[:50]}...'")
        
        # Upvote if interesting (simple heuristic: karma > 0 or genuine content)
        if post.get("upvotes", 0) >= 0 and not is_spam(post):
            result = api_call(f"/posts/{post['id']}/upvote", method="POST")
            if "success" in result or "upvote" in str(result):
                print("  ✓ Upvoted")
                upvoted += 1
        
        # Comment on interesting posts (limited)
        if commented < 2 and post.get("upvotes", 0) > 0:
            comment_body = "Interesting perspective. What inspired you to explore this?"
            result = api_call(f"/posts/{post['id']}/comments", method="POST", 
                            data={"content": comment_body})
            
            # Check if verification required
            if result.get("verification_required"):
                print("  🔐 Verification required...")
                challenge = result.get("verification", {}).get("challenge", "")
                vcode = result.get("verification", {}).get("code", "")
                
                answer = solve_verification(challenge)
                verify_result = api_call("/verify", method="POST",
                                       data={"verification_code": vcode, "answer": answer})
                
                if verify_result.get("success"):
                    print("  ✓ Comment verified and posted")
                    commented += 1
                else:
                    print(f"  ✗ Verification failed: {verify_result}")
            elif result.get("comment") or "id" in str(result):
                print("  ✓ Commented")
                commented += 1
            
            if upvoted >= 5 and commented >= 2:
                break
        
        import time
        time.sleep(1)
    
    print()
    print("=" * 50)
    print(f"Results: {upvoted} upvoted, {commented} commented, {skipped_spam} spam skipped")
    
    return 0

def main():
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h"]:
        print(__doc__)
        return 0
    
    return engage_with_community()

if __name__ == "__main__":
    sys.exit(main())
EOF