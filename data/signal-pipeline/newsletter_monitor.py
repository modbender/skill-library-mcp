#!/usr/bin/env python3
"""
Newsletter Monitor - Fetch marketing/business newsletters from Gmail

Uses gog CLI to access Gmail newsletters.
"""

import subprocess
import json
import re
from datetime import datetime

# Newsletter sources to monitor
NEWSLETTERS = [
    {"name": "Ad Age", "search": "from:adage"},
    {"name": "Campaign Asia", "search": "from:campaign"},
    {"name": "Railway", "search": "from:railway"},
    {"name": "Dune", "search": "from:dune"},
    {"name": "阿里云", "search": "from:aliyun"},
]

def run_gog(query):
    """Run gog command and return JSON"""
    try:
        result = subprocess.run(
            f"gog gmail search '{query} newer_than:30d' --max 5 --json",
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        return {"threads": []}
    except Exception as e:
        print(f"Error: {e}")
        return {"threads": []}

def extract_content(email_json):
    """Extract relevant info from email"""
    threads = email_json.get("threads", [])
    emails = []
    
    for t in threads:
        # Get subject and from
        subject = t.get("subject", "")
        from_addr = t.get("from", "")
        
        # Extract sender name
        match = re.search(r'(.*?)\s*<', from_addr)
        sender = match.group(1).strip() if match else from_addr[:30]
        
        emails.append({
            "subject": subject,
            "sender": sender,
            "date": t.get("date", "")[:10]
        })
    
    return emails

def fetch_newsletters():
    """Fetch all newsletters"""
    all_newsletters = []
    
    for nl in NEWSLETTERS:
        data = run_gog(nl["search"])
        emails = extract_content(data)
        
        for e in emails:
            e["newsletter"] = nl["name"]
        
        all_newsletters.extend(emails)
    
    return all_newsletters

def get_marketing_signals():
    """Get marketing-related newsletters"""
    newsletters = fetch_newsletters()
    
    # Filter for marketing/business content
    keywords = ["marketing", "brand", "advertising", "growth", "campaign", "media", "agency", "platform"]
    
    signals = []
    for nl in newsletters:
        subject = nl["subject"].lower()
        if any(k in subject for k in keywords):
            signals.append(nl)
    
    return signals

if __name__ == "__main__":
    print("Fetching newsletters...")
    newsletters = fetch_newsletters()
    
    print(f"\nFound {len(newsletters)} newsletter emails")
    print("\nRecent:")
    for nl in newsletters[:10]:
        print(f"  {nl['newsletter']}: {nl['subject'][:50]}...")
    
    print("\n" + "=" * 50)
    print("Marketing signals:")
    signals = get_marketing_signals()
    print(f"Found {len(signals)} marketing signals")
    for s in signals[:5]:
        print(f"  {s['newsletter']}: {s['subject'][:50]}...")
