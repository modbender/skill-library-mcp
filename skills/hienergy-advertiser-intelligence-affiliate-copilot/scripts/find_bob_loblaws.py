import sys
import os

# Add the parent directory to sys.path so we can import 'scripts' package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.hienergy_skill import HiEnergySkill

def main():
    skill = HiEnergySkill()
    
    print("Searching for CONTACTS matching 'Bob Loblaws'...")
    try:
        contacts = skill.get_contacts(search="Bob Loblaws", limit=10)
        if contacts:
            for c in contacts:
                print(f"Contact: {c.get('name')} (ID: {c.get('id')})")
        else:
            print("No contacts found.")
    except Exception as e:
        print(f"Error searching contacts: {e}")

    # Also try to search deals/offers if that's relevant
    # But mainly user asked for "transactions for sleep number on the publisher bob loblaws".
    # This implies looking up transactions where (Advertiser=Sleep Number AND Publisher=Bob Loblaws).
    
    # Let's try to fetch transactions with a broad search query string
    # The API might support full-text search on transaction metadata including publisher name.
    
    print("\nSearching transactions with query 'Sleep Number Bob Loblaws'...")
    try:
        txs = skill.get_transactions(search="Sleep Number Bob Loblaws", limit=10)
        if txs:
            print(f"Found {len(txs)} transactions directly via search!")
            for t in txs:
                print(t)
        else:
            print("No transactions found via direct search.")
    except Exception as e:
        print(f"Error searching transactions: {e}")

    # Try searching for "Bob Loblaws" in transactions (maybe without advertiser filter first)
    print("\nSearching transactions for 'Bob Loblaws' only...")
    try:
        txs = skill.get_transactions(search="Bob Loblaws", limit=20)
        if txs:
            print(f"Found {len(txs)} transactions for Bob Loblaws!")
            for t in txs:
                adv = t.get('advertiser', {})
                adv_name = adv.get('name') if isinstance(adv, dict) else str(adv)
                if 'sleep' in adv_name.lower():
                    print(f"*** MATCH: {t.get('transaction_date')} - {adv_name} - {t.get('commission_amount')}")
                else:
                    print(f"  - {t.get('transaction_date')} - {adv_name} (Not Sleep Number)")
        else:
            print("No transactions found for Bob Loblaws.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
