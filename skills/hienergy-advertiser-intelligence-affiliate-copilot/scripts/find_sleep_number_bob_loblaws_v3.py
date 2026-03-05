import sys
import os
import datetime

# Add the parent directory to sys.path so we can import 'scripts' package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.hienergy_skill import HiEnergySkill

def main():
    skill = HiEnergySkill()
    
    # 1. Search for Advertiser
    print("Searching for Advertiser 'Sleep Number'...")
    advertisers = skill.get_advertisers(search="Sleep Number", limit=5)
    
    if not advertisers:
        print("No advertiser found for 'Sleep Number'")
        return

    target_adv = advertisers[0]
    adv_id = target_adv.get('id')
    print(f"Using Advertiser: {target_adv.get('name')} (ID: {adv_id})")

    # 2. Fetch Transactions with start_date
    start_date = (datetime.datetime.now() - datetime.timedelta(days=90)).strftime('%Y-%m-%d')
    print(f"Fetching transactions since {start_date} for Advertiser ID: {adv_id}")
    
    try:
        transactions = skill.get_transactions(
            advertiser_id=adv_id, 
            start_date=start_date, 
            limit=100
        )
    except Exception as e:
        print(f"Error fetching transactions: {e}")
        return

    if not transactions:
        print("No transactions found even with start_date.")
        # Try without advertiser_id but with search query
        print("Trying search='Sleep Number' directly in transactions...")
        try:
            transactions = skill.get_transactions(search="Sleep Number", limit=100)
        except Exception as e:
            print(f"Error fetching by search: {e}")
            return
        
        if not transactions:
            print("Still no transactions found.")
            return

    # 3. Filter for Publisher "Bob Loblaws"
    publisher_query = "bob loblaws"
    print(f"Filtering {len(transactions)} transactions for publisher matching: '{publisher_query}'")
    
    matching_txs = []
    for tx in transactions:
        # Check typical fields
        pub = tx.get('publisher')
        pub_name = ""
        if isinstance(pub, dict):
            pub_name = pub.get('name', '')
        elif isinstance(pub, str):
            pub_name = pub
            
        # Also check sub_id or similar if relevant
        sub_id = tx.get('sub_id', '')
        
        if (publisher_query.lower() in pub_name.lower()) or (publisher_query.lower() in str(sub_id).lower()):
            matching_txs.append(tx)
    
    if matching_txs:
        print(f"Found {len(matching_txs)} matching transactions:")
        for tx in matching_txs:
            d = tx.get('transaction_date') or tx.get('date') or tx.get('occurred_at')
            amt = tx.get('commission_amount') or tx.get('amount')
            curr = tx.get('currency')
            status = tx.get('status')
            pub = tx.get('publisher')
            pub_n = pub.get('name') if isinstance(pub, dict) else str(pub)
            print(f"- {d}: {amt} {curr} ({status}) - Pub: {pub_n}")
    else:
        print("No matching transactions for Bob Loblaws.")
        print("Sample transaction publishers found:")
        seen_pubs = set()
        for tx in transactions[:10]:
            p = tx.get('publisher')
            pn = p.get('name') if isinstance(p, dict) else str(p)
            if pn not in seen_pubs:
                print(f"  - {pn}")
                seen_pubs.add(pn)

if __name__ == "__main__":
    main()
