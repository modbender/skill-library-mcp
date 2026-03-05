import sys
import os

# Add the parent directory to sys.path so we can import 'scripts' package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.hienergy_skill import HiEnergySkill

def main():
    skill = HiEnergySkill()
    
    # 1. Search for Advertiser
    advertiser_name = "Sleep Number"
    print(f"Searching for advertiser: {advertiser_name}")
    advertisers = skill.get_advertisers(search=advertiser_name, limit=5)
    
    if not advertisers:
        print("No advertiser found for 'Sleep Number'")
        return

    # Print found advertisers to pick the correct one
    for adv in advertisers:
        print(f"Found Advertiser: {adv.get('name')} (ID: {adv.get('id')})")
    
    # Pick the best match (first one usually)
    target_adv = advertisers[0]
    adv_id = target_adv.get('id')
    print(f"Using Advertiser ID: {adv_id}")

    # 2. Fetch Transactions for this advertiser
    print(f"Fetching transactions for Advertiser ID: {adv_id}")
    transactions = skill.get_transactions(advertiser_id=adv_id, limit=50) # fetch more to filter locally

    if not transactions:
        print("No transactions found.")
        return

    # 3. Filter for Publisher "Bob Loblaws"
    publisher_query = "bob loblaws"
    print(f"Filtering for publisher matching: {publisher_query}")
    
    matching_txs = []
    for tx in transactions:
        # Inspect transaction structure for publisher info
        # It might be under 'publisher', 'sub_id', 'click_ref', etc.
        # Let's check typical fields.
        publisher = tx.get('publisher')
        pub_name = ""
        if isinstance(publisher, dict):
            pub_name = publisher.get('name', '')
        elif isinstance(publisher, str):
            pub_name = publisher
        
        # Also check sub_id or similar if publisher name isn't direct
        # But user asked for "publisher bob loblaws", so let's look for that name.
        
        if publisher_query.lower() in pub_name.lower():
            matching_txs.append(tx)
    
    print(f"Found {len(matching_txs)} matching transactions.")
    
    # Output results
    for tx in matching_txs:
        print(f"Transaction: {tx.get('transaction_date')} - {tx.get('commission_amount')} {tx.get('currency')} - Status: {tx.get('status')}")
        # Print full tx for debugging/inspection if needed, or just relevant fields
        print(f"  Publisher: {tx.get('publisher')}")

    if not matching_txs and transactions:
        print("Sample of non-matching transactions (to debug structure):")
        print(transactions[0])

if __name__ == "__main__":
    main()
