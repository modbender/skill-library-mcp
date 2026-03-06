#!/usr/bin/env python3
"""
Create a new contact in HiEnergy (Admin only).
Usage: python create_contact.py --advertiser_id 123 --email user@example.com --name "John Doe"
"""

import argparse
import os
import sys
from hienergy_skill import HiEnergySkill

def main():
    parser = argparse.ArgumentParser(description="Create a contact in HiEnergy")
    parser.add_argument("--advertiser_id", required=True, help="Advertiser ID or slug")
    parser.add_argument("--email", required=True, help="Contact email")
    parser.add_argument("--name", help="Contact name (optional)")
    parser.add_argument("--title", help="Job title (optional)")
    parser.add_argument("--phone", help="Phone number (optional)")
    
    args = parser.parse_args()
    
    api_key = os.environ.get('HIENERGY_API_KEY')
    if not api_key:
        print("Error: HIENERGY_API_KEY environment variable not set")
        sys.exit(1)
        
    skill = HiEnergySkill(api_key=api_key)
    
    data = {
        "advertiser_id": args.advertiser_id,
        "email": args.email,
    }
    if args.name:
        data["name"] = args.name
    if args.title:
        data["job_title"] = args.title
    if args.phone:
        data["phone"] = args.phone
        
    print(f"Creating contact for Advertiser {args.advertiser_id} ({args.email})...")
    
    try:
        result = skill.create_contact(data)
        cid = result.get("id")
        cemail = result.get("email")
        print(f"✅ Success! Contact created: ID {cid} ({cemail})")
    except Exception as e:
        print(f"❌ Error creating contact: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
