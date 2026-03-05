#!/usr/bin/env python3
"""
📊 NİKOS - Portföy & Alarm Takipçisi (Portfolio Tracker)
Kullanıcının belirlediği alım aralığı (Buy Zone), Kar Al (Take Profit) ve Zarar Kes (Stop Loss) seviyelerine göre varlıkları takip eder.
"""
import sys, os, json, argparse, urllib.request, urllib.error

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "portfolio_alerts.json")

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_current_price(symbol):
    """Yahoo Finance üzerinden anlık fiyat çeker (API Key gerektirmez, ücretsizdir).
    Örn: BIST için 'THYAO.IS', ABD için 'AAPL', Kripto için 'BTC-USD', Parite için 'EURUSD=X', Emtia için 'GC=F' (Altın)
    """
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json'
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            return data["chart"]["result"][0]["meta"]["regularMarketPrice"]
    except Exception as e:
        return None

def add_asset(symbol, buy_min, buy_max, tp, sl, name):
    db = load_db()
    db[symbol] = {
        "name": name,
        "buy_min": float(buy_min),
        "buy_max": float(buy_max),
        "tp": float(tp),
        "sl": float(sl)
    }
    save_db(db)
    print(f"✅ Başarıyla Eklendi: {symbol} - {name} | Alım Aralığı: {buy_min}-{buy_max} | Kar Al (TP): {tp} | Zarar Kes (SL): {sl}")

def remove_asset(symbol):
    db = load_db()
    if symbol in db:
        del db[symbol]
        save_db(db)
        print(f"🗑️ Başarıyla Silindi: {symbol}")
    else:
        print(f"⚠️ Bulunamadı: {symbol}")

def check_alerts():
    db = load_db()
    if not db:
        print("📁 Takip edilen varlık yok. Lütfen portföye ekleme yapın.")
        return

    print("\n🔍 PORTFÖY ALARM KONTROLÜ (Güncel Piyasa Durumu)\n" + "="*70)
    for symbol, data in db.items():
        price = get_current_price(symbol)
        if price is None:
            print(f"⚠️ {symbol} fiyatı çekilemedi. Sembol hatalı veya sistem dışı olabilir.")
            continue
        
        status = "⏳ BEKLEMEDE"
        action = "Gözlemle"
        
        if price >= data["tp"]:
            status = "🎯 KAR AL (TAKE PROFIT) HEDEFİNE ULAŞTI"
            action = "SATIŞ YAPILMALI"
        elif price <= data["sl"]:
            status = "🛑 ZARAR KES (STOP LOSS) SEVİYESİNİ KIRDI"
            action = "SATIŞ YAPILMALI"
        elif data["buy_min"] <= price <= data["buy_max"]:
            status = "✅ ALIM BÖLGESİNDE (BUY ZONE)"
            action = "ALIM FIRSATI"
            
        print(f"💼 {data['name']} ({symbol}): Anlık Fiyat: {price:.4f}")
        print(f"   Durum: {status} => Öneri: {action}")
        print("-" * 70)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Nikos Portfolio Tracker")
    subparsers = parser.add_subparsers(dest="command")

    # ADD Command
    p_add = subparsers.add_parser("add")
    p_add.add_argument("symbol", help="YF Sembolü (örn. THYAO.IS, BTC-USD)")
    p_add.add_argument("buy_min", type=float)
    p_add.add_argument("buy_max", type=float)
    p_add.add_argument("tp", type=float, help="Take Profit (Kar Al)")
    p_add.add_argument("sl", type=float, help="Stop Loss (Zarar Kes)")
    p_add.add_argument("name", help="Varlığın Adı")

    # REMOVE Command
    p_rm = subparsers.add_parser("remove")
    p_rm.add_argument("symbol")

    # CHECK Command
    p_check = subparsers.add_parser("check")
    
    # LIST Command
    p_list = subparsers.add_parser("list")

    args = parser.parse_args()

    if args.command == "add":
        add_asset(args.symbol, args.buy_min, args.buy_max, args.tp, args.sl, args.name)
    elif args.command == "remove":
        remove_asset(args.symbol)
    elif args.command == "check":
        check_alerts()
    elif args.command == "list":
        db = load_db()
        print("📁 Liste:")
        for k, v in db.items():
            print(f"{k} -> {v}")
    else:
        parser.print_help()
