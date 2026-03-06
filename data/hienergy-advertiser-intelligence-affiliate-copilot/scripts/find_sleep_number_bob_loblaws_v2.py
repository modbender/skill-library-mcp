import sys
import os

# Add the parent directory to sys.path so we can import 'scripts' package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.hienergy_skill import HiEnergySkill

def main():
    try:
        skill = HiEnergySkill()
    except Exception as e:
        print(f"Error initializing skill: {e}")
        return

    print("Searching for advertiser 'Sleep Number'...")
    sys.stdout.flush()
    try:
        advertisers = skill.get_advertisers(search="Sleep Number", limit=5)
    except Exception as e:
        print(f"Error searching advertisers: {e}")
        return

    if not advertisers:
        print("No advertiser found for 'Sleep Number'")
        return

    target_adv = advertisers[0]
    adv_id = target_adv.get('id')
    print(f"Using Advertiser ID: {adv_id}")
    sys.stdout.flush()

    print(f"Fetching transactions for Advertiser ID: {adv_id}")
    sys.stdout.flush()
    try:
        transactions = skill.get_transactions(advertiser_id=adv_id, limit=50)
    except Exception as e:
        print(f"Error fetching transactions: {e}")
        return

    if not transactions:
        print("No transactions found.")
        return

    publisher_query = "bob loblaws"
    print(f"Filtering for publisher matching: {publisher_query}")
    sys.stdout.flush()
    
    matching_txs = []
    for tx in transactions:
        publisher = tx.get('publisher')
        pub_name = ""
        if isinstance(publisher, dict):
            pub_name = publisher.get('name', '')
        elif isinstance(publisher, str):
            pub_name = publisher
        
        if publisher_query.lower() in pub_name.lower():
            matching_txs.append(tx)
    
    print(f"Found {len(matching_txs)} matching transactions.")
    sys.stdout.flush()
    
    for tx in matching_txs:
        # Check available fields for display
        date = tx.get('transaction_date') or tx.get('occurred_at') or 'Unknown Date'
        amount = tx.get('commission_amount') or tx.get('amount') or '0'
        currency = tx.get('currency') or 'USD'
        status = tx.get('status') or 'unknown'
        # Also check if there's publisher specific data
        pub = tx.get('publisher')
        pub_name = pub.get('name') if isinstance(pub, dict) else str(pub)

        print(f"Transaction: {date} - {amount} {currency} - Status: {status} - Publisher: {pub_name}")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
