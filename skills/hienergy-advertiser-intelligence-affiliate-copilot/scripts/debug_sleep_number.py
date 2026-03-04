import sys
import os

# Add the parent directory to sys.path so we can import 'scripts' package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.hienergy_skill import HiEnergySkill

def main():
    skill = HiEnergySkill()
    
    print("Searching for ALL advertisers matching 'Sleep Number'...")
    advertisers = skill.get_advertisers(search="Sleep Number", limit=10)
    
    if not advertisers:
        print("No advertiser found for 'Sleep Number'")
        return

    for i, adv in enumerate(advertisers):
        print(f"[{i}] Name: {adv.get('name')} | ID: {adv.get('id')} | Slug: {adv.get('slug')}")

    # Try fetching transactions for each potential advertiser ID
    for adv in advertisers:
        adv_id = adv.get('id')
        adv_name = adv.get('name')
        print(f"\nChecking transactions for: {adv_name} (ID: {adv_id})")
        
        try:
            # Try getting transactions with just advertiser_id
            txs = skill.get_transactions(advertiser_id=adv_id, limit=5)
            if txs:
                print(f"  Found {len(txs)} transactions! Showing first one:")
                print(f"  {txs[0]}")
                
                # If we found transactions, let's filter them for "Bob Loblaws"
                print(f"  Fetching more transactions to search for publisher 'Bob Loblaws'...")
                all_txs = skill.get_transactions(advertiser_id=adv_id, limit=100)
                matching = [t for t in all_txs if 'bob loblaws' in str(t.get('publisher', '')).lower()]
                if matching:
                    print(f"  MATCH FOUND! {len(matching)} transactions for Bob Loblaws.")
                    for m in matching:
                        print(f"    - {m.get('transaction_date')} : {m.get('commission_amount')} {m.get('currency')} ({m.get('status')})")
                else:
                    print("  No transactions for Bob Loblaws found in this batch.")
            else:
                print("  No transactions found.")
        except Exception as e:
            print(f"  Error fetching transactions: {e}")

if __name__ == "__main__":
    main()
