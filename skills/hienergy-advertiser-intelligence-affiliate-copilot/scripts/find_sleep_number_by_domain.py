import sys
import os

# Add the parent directory to sys.path so we can import 'scripts' package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.hienergy_skill import HiEnergySkill

def main():
    skill = HiEnergySkill()
    
    domain = "sleepnumber.com"
    print(f"Searching for advertiser by domain: {domain}")
    sys.stdout.flush()
    
    try:
        if hasattr(skill, 'get_advertisers_by_domain'):
            # Try passing domain as first positional argument
            try:
                advertisers = skill.get_advertisers_by_domain("sleepnumber.com")
            except Exception:
                 # Try with url=
                 advertisers = skill.get_advertisers_by_domain(url="sleepnumber.com")
        else:
            advertisers = skill.get_advertisers(search="sleepnumber.com")
            
        if not advertisers:
            print(f"No advertiser found for domain '{domain}'")
            return

        for adv in advertisers:
            print(f"Found Advertiser: {adv.get('name')} (ID: {adv.get('id')})")
            
            # Check transactions
            print(f"Fetching transactions for ID: {adv.get('id')}...")
            txs = skill.get_transactions(advertiser_id=adv.get('id'), limit=100)
            
            bob_txs = [t for t in txs if 'bob' in str(t.get('publisher', '')).lower()]
            if bob_txs:
                print(f"  FOUND {len(bob_txs)} transactions for Bob!")
                for t in bob_txs:
                     print(f"  - {t.get('transaction_date')}: {t.get('commission_amount')} {t.get('currency')}")
            else:
                print("  No transactions for Bob found.")
                if txs:
                    print(f"  (Total transactions found: {len(txs)})")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
