import os
import sys
from scripts.hienergy_skill import HiEnergySkill

def main():
    api_key = os.environ.get('HIENERGY_API_KEY')
    if not api_key:
        print("Error: HIENERGY_API_KEY env var not set.")
        sys.exit(1)

    skill = HiEnergySkill(api_key=api_key)
    
    print("\n--- Testing Deals ---")
    try:
        deals = skill.find_deals(limit=2)
        print(f"Found {len(deals)} deals.")
        if deals:
            print(f"Sample deal: {deals[0].get('title', 'No title')}")
    except Exception as e:
        print(f"Deals failed: {e}")

    print("\n--- Testing Status Changes ---")
    try:
        changes = skill.get_status_changes(limit=2)
        print(f"Found {len(changes)} status changes.")
        if changes:
            print(f"Sample change: {changes[0].get('advertiser_name')} -> {changes[0].get('to_status')}")
    except Exception as e:
        print(f"Status Changes failed: {e}")

    print("\n--- Testing Agencies ---")
    try:
        agencies = skill.get_agencies(limit=2)
        print(f"Found {len(agencies)} agencies.")
        if agencies:
            print(f"Sample agency: {agencies[0].get('name')}")
    except Exception as e:
        print(f"Agencies failed: {e}")

    print("\n--- Testing Transactions ---")
    try:
        txs = skill.get_transactions(limit=2)
        print(f"Found {len(txs)} transactions.")
        if txs:
            print(f"Sample tx: {txs[0].get('id')} - {txs[0].get('amount')}")
    except Exception as e:
        print(f"Transactions failed: {e}")

    print("\n--- Testing Tags ---")
    try:
        tags = skill.search_tags(per_page=2)
        print(f"Found {len(tags)} tags.")
        if tags:
            tag = tags[0]
            t_id = tag.get('id')
            t_name = tag.get('name')
            print(f"Sample tag: {t_name} (ID: {t_id})")
            
            if t_id:
                print(f"--- Testing Advertisers for Tag {t_id} ---")
                tag_ads = skill.get_tag_advertisers(tag_id=str(t_id), per_page=2)
                print(f"Found {len(tag_ads)} advertisers for tag {t_name}")
                if tag_ads:
                     print(f"Sample tag advertiser: {tag_ads[0].get('name')}")
    except Exception as e:
        print(f"Tags failed: {e}")

if __name__ == "__main__":
    main()
