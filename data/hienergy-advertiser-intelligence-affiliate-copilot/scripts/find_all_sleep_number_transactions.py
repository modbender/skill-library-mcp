import sys
import os
import datetime

# Add the parent directory to sys.path so we can import 'scripts' package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.hienergy_skill import HiEnergySkill

def main():
    print("Starting comprehensive search...")
    sys.stdout.flush()
    try:
        skill = HiEnergySkill()
    except Exception as e:
        print(f"Error init: {e}")
        return
    
    # 1. Search for Advertiser
    print("Searching for ALL advertisers matching 'Sleep Number'...")
    sys.stdout.flush()
    advertisers = skill.get_advertisers(search="Sleep Number", limit=20)
    
    if not advertisers:
        print("No advertiser found for 'Sleep Number'")
        return

    print(f"Found {len(advertisers)} advertisers.")
    sys.stdout.flush()

    # 2. Check each advertiser for transactions
    start_date = (datetime.datetime.now() - datetime.timedelta(days=90)).strftime('%Y-%m-%d')
    print(f"Checking transactions since {start_date} for each...")
    sys.stdout.flush()

    for adv in advertisers:
        adv_id = adv.get('id')
        name = adv.get('name')
        print(f"\n--- Checking Advertiser: {name} (ID: {adv_id}) ---")
        sys.stdout.flush()
        
        try:
            # Try getting transactions with start_date
            txs = skill.get_transactions(
                advertiser_id=adv_id, 
                start_date=start_date, 
                limit=10
            )
            if txs:
                print(f"  > Found {len(txs)}+ transactions!")
                
                # Check for "Bob Loblaws" in this batch
                matching = [t for t in txs if 'bob loblaws' in str(t.get('publisher', '')).lower()]
                if matching:
                    print(f"  > MATCH FOUND! {len(matching)} transactions for Bob Loblaws.")
                    for m in matching:
                        print(f"    - {m.get('transaction_date')} : {m.get('commission_amount')} {m.get('currency')} ({m.get('status')})")
                else:
                    print("  > No immediate match for Bob Loblaws in first batch.")
                    
                    # Fetch more if needed? Maybe later.
            else:
                print("  > No transactions found.")
        except Exception as e:
            print(f"  > Error fetching transactions: {e}")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
