from api import get_zakat_gold_silver, load_config

def handle_zakat_command(args):
    config = load_config()
    currency = args.currency or config['zakat']['currency']
    
    data = get_zakat_gold_silver(currency)
    
    if data and 'error' in data:
        print(f"Error: {data['error']}")
        return

    if not data or 'data' not in data:
        print("Could not retrieve Zakat data.")
        return

    data = data.get('data', {})
    thresholds = data.get('nisab_thresholds', {})
    
    gold_data = thresholds.get('gold', {})
    silver_data = thresholds.get('silver', {})
    
    gold_price = gold_data.get('unit_price', 0)
    gold_nisab = gold_data.get('nisab_amount', 0)
    
    silver_price = silver_data.get('unit_price', 0)
    silver_nisab = silver_data.get('nisab_amount', 0)
    
    print(f"Zakat Nisab ({currency.upper()}):")
    print(f"Gold (1g):   {gold_price:,.2f}")
    print(f"Gold Nisab (85g): {gold_nisab:,.2f}")
    print("-" * 20)
    print(f"Silver (1g): {silver_price:,.2f}")
    print(f"Silver Nisab (595g): {silver_nisab:,.2f}")
