import os
import sys
from scripts.hienergy_skill import HiEnergySkill

def main():
    api_key = os.environ.get('HIENERGY_API_KEY')
    if not api_key:
        print("Error: HIENERGY_API_KEY env var not set.")
        sys.exit(1)

    skill = HiEnergySkill(api_key=api_key)
    
    try:
        # Explicitly sort by date desc for "most recent"
        txs = skill.get_transactions(sort_by='transaction_date', sort_order='desc', limit=5)
        
        if not txs:
            print("No transactions found.")
        else:
            print(f"Found {len(txs)} recent transactions:")
            for tx in txs:
                # Safe access to fields
                t_id = tx.get('id', 'Unknown')
                date = tx.get('transaction_date', 'N/A')
                amount = tx.get('sale_amount') or tx.get('amount') or 'N/A'
                commission = tx.get('commission_amount') or 'N/A'
                status = tx.get('status', 'N/A')
                
                advertiser = tx.get('advertiser') or {}
                adv_name = advertiser.get('name') or tx.get('advertiser_name') or 'Unknown Advertiser'
                
                print(f"- {date}: {adv_name} (ID: {t_id}) | Sale: {amount} | Comm: {commission} | Status: {status}")

    except Exception as e:
        print(f"Error fetching transactions: {e}")

if __name__ == "__main__":
    main()
