import sys
import os

# Add the parent directory to sys.path so we can import 'scripts' package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.hienergy_skill import HiEnergySkill

def main():
    skill = HiEnergySkill()
    
    queries = ["Sleep Number", "SleepNumber", "Select Comfort", "Sleep"]
    
    for q in queries:
        print(f"\nSearching for: '{q}'")
        advertisers = skill.get_advertisers(search=q, limit=5)
        if not advertisers:
            print("  No results.")
            continue
        
        for adv in advertisers:
            print(f"  - {adv.get('name')} (ID: {adv.get('id')})")
            # If name is close to "Sleep Number", break and check transactions
            if "sleep number" in adv.get('name', '').lower():
                print(f"    *** FOUND MATCH: {adv.get('name')} ***")
                # Check transactions
                txs = skill.get_transactions(advertiser_id=adv.get('id'), limit=5)
                if txs:
                    print(f"    Found {len(txs)} transactions.")
                else:
                    print(f"    No transactions found for this ID.")

if __name__ == "__main__":
    main()
