#!/usr/bin/env python3
"""
Example script demonstrating how to use the HiEnergy API Skill
"""

import os
from scripts.hienergy_skill import HiEnergySkill


def main():
    # Option 1: Initialize with API key directly
    api_key = os.environ.get('HIENERGY_API_KEY', 'your_api_key_here')
    skill = HiEnergySkill(api_key=api_key)
    
    print("=" * 70)
    print("HiEnergy API Skill - Example Usage")
    print("=" * 70)
    
    # Example 1: Search for advertisers
    print("\n1. Searching for advertisers:")
    print("-" * 70)
    try:
        advertisers = skill.get_advertisers(search="technology", limit=5)
        print(f"Found {len(advertisers)} advertisers")
        for adv in advertisers[:3]:
            print(f"  - {adv.get('name', 'Unknown')}: {adv.get('description', 'N/A')}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Example 2: Get affiliate programs
    print("\n2. Getting affiliate programs:")
    print("-" * 70)
    try:
        programs = skill.get_affiliate_programs(search="fashion", limit=5)
        print(f"Found {len(programs)} programs")
        for prog in programs[:3]:
            print(f"  - {prog.get('name', 'Unknown')}: Commission {prog.get('commission_rate', 'N/A')}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Example 3: Find deals
    print("\n3. Finding deals:")
    print("-" * 70)
    try:
        deals = skill.find_deals(search="discount", limit=5)
        print(f"Found {len(deals)} deals")
        for deal in deals[:3]:
            print(f"  - {deal.get('title', 'Unknown')}: {deal.get('description', 'N/A')}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Example 4: Get transactions
    print("\n4. Getting transactions:")
    print("-" * 70)
    try:
        transactions = skill.get_transactions(status="completed", limit=5)
        print(f"Found {len(transactions)} transactions")
        for tx in transactions[:3]:
            print(f"  - {tx.get('id', 'Unknown')}: amount={tx.get('amount', 'N/A')} status={tx.get('status', 'N/A')}")
    except Exception as e:
        print(f"  Error: {e}")

    # Example 5: Get contacts
    print("\n5. Getting contacts:")
    print("-" * 70)
    try:
        contacts = skill.get_contacts(search="john", limit=5)
        print(f"Found {len(contacts)} contacts")
        for contact in contacts[:3]:
            name = contact.get('name') or contact.get('full_name') or 'Unknown'
            print(f"  - {name}: {contact.get('email', 'N/A')}")
    except Exception as e:
        print(f"  Error: {e}")

    # Example 6: Answer natural language questions
    print("\n6. Answering questions:")
    print("-" * 70)
    questions = [
        "What advertisers are available in electronics?",
        "Show me affiliate programs with high commissions",
        "Find deals for Black Friday",
        "Show me recent completed transactions",
        "Find contacts named Sarah"
    ]
    
    for question in questions:
        print(f"\nQ: {question}")
        try:
            answer = skill.answer_question(question)
            print(f"A: {answer}")
        except Exception as e:
            print(f"A: Error - {e}")
    
    # Example 7: Get specific details
    print("\n7. Getting specific details:")
    print("-" * 70)
    try:
        # First get some advertisers
        advertisers = skill.get_advertisers(limit=1)
        if advertisers:
            adv_id = advertisers[0].get('id')
            details = skill.get_advertiser_details(adv_id)
            print(f"Advertiser details for ID {adv_id}:")
            print(f"  Name: {details.get('name', 'N/A')}")
            print(f"  Description: {details.get('description', 'N/A')}")
    except Exception as e:
        print(f"  Error: {e}")
    
    print("\n" + "=" * 70)
    print("Note: This example requires a valid HiEnergy API key.")
    print("Set HIENERGY_API_KEY environment variable or update the script.")
    print("=" * 70)


if __name__ == '__main__':
    main()
