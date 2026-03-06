#!/usr/bin/env python3
"""
📓 NİKOS - İşlem Kayıt ve Analiz Paneli (Trade Logger & Dashboard)
Alınan ve satılan hisselerin fiyatını, adedini, tarihini tutar.
Kar/Zarar analizi yapar ve raporu hem CSV (Excel) hem de Görsel Grafikli HTML olarak çıkartır.
"""
import sys, os, json, argparse, csv
from datetime import datetime

TRADE_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trade_history.json")
CSV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Nikos_Islem_Gecmisi.csv")
HTML_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Nikos_Portfoy_Analiz.html")

def load_db():
    if os.path.exists(TRADE_DB):
        with open(TRADE_DB, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"active_positions": {}, "closed_trades": []}

def save_db(data):
    with open(TRADE_DB, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def buy_asset(symbol, price, qty, name=""):
    db = load_db()
    
    if symbol not in db["active_positions"]:
        db["active_positions"][symbol] = []
        
    db["active_positions"][symbol].append({
        "name": name if name else symbol,
        "buy_price": float(price),
        "qty": float(qty),
        "buy_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    save_db(db)
    print(f"✅ ALIM KAYDEDİLDİ: {qty} adet {symbol} ({name}) - Fiyat: {price}")

def sell_asset(symbol, sell_price, qty):
    db = load_db()
    
    if symbol not in db["active_positions"] or not db["active_positions"][symbol]:
        print(f"❌ HATA: {symbol} için aktif açık pozisyon bulunamadı!")
        return
        
    positions = db["active_positions"][symbol]
    sell_qty = float(qty)
    sell_price = float(sell_price)
    sell_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    total_profit = 0
    remaining_sell_qty = sell_qty
    
    for pos in list(positions):
        if remaining_sell_qty <= 0:
            break
            
        pos_qty = pos["qty"]
        if pos_qty <= remaining_sell_qty:
            # Bu alımın tamamını kapat
            profit = (sell_price - pos["buy_price"]) * pos_qty
            total_profit += profit
            db["closed_trades"].append({
                "symbol": symbol,
                "name": pos["name"],
                "buy_date": pos["buy_date"],
                "sell_date": sell_date,
                "buy_price": pos["buy_price"],
                "sell_price": sell_price,
                "qty": pos_qty,
                "profit_loss": profit,
                "roi_percent": ((sell_price - pos["buy_price"]) / pos["buy_price"]) * 100
            })
            remaining_sell_qty -= pos_qty
            positions.remove(pos)
        else:
            # Bu alımın bir kısmını kapat
            profit = (sell_price - pos["buy_price"]) * remaining_sell_qty
            total_profit += profit
            db["closed_trades"].append({
                "symbol": symbol,
                "name": pos["name"],
                "buy_date": pos["buy_date"],
                "sell_date": sell_date,
                "buy_price": pos["buy_price"],
                "sell_price": sell_price,
                "qty": remaining_sell_qty,
                "profit_loss": profit,
                "roi_percent": ((sell_price - pos["buy_price"]) / pos["buy_price"]) * 100
            })
            pos["qty"] -= remaining_sell_qty
            remaining_sell_qty = 0
            
    save_db(db)
    print(f"✅ SATIŞ KAYDEDİLDİ: {sell_qty} adet {symbol} satıldı.")
    print(f"💰 Gerçekleşen Kar/Zarar: {total_profit:.2f}")

def generate_reports():
    db = load_db()
    trades = db.get("closed_trades", [])
    
    if not trades:
        print("📁 Henüz kapatılmış (satılmış) bir pozisyon yok. Rapor oluşturulamadı.")
        return
        
    # 1. CSV EXPORT (Excel İçin)
    with open(CSV_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(["Sembol", "Varlık Adı", "Alış Tarihi", "Satış Tarihi", "Alış F.", "Satış F.", "Miktar", "Kar/Zarar", "ROI (%)"])
        for t in trades:
            writer.writerow([
                t["symbol"], t["name"], t["buy_date"], t["sell_date"],
                f"{t['buy_price']:.4f}", f"{t['sell_price']:.4f}", f"{t['qty']:.2f}",
                f"{t['profit_loss']:.2f}", f"{t['roi_percent']:.2f}%"
            ])
            
    # 2. HTML DASHBOARD (Grafikli Analiz)
    # Verileri JavaScript uyumlu hale getir
    js_labels = [t["sell_date"].split(' ')[0] for t in trades]
    js_profits = [round(t["profit_loss"], 2) for t in trades]
    js_symbols = [t["symbol"] for t in trades]
    
    # Kümülatif Kar Hesapla
    cumulative = []
    total = 0
    for p in js_profits:
        total += p
        cumulative.append(total)
        
    html_content = f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <title>Nikos Portföy ve İşlem Analizi</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; color: #333; margin: 0; padding: 20px; }}
            .container {{ max-width: 1200px; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            h1 {{ text-align: center; color: #2c3e50; }}
            .summary {{ display: flex; justify-content: space-between; margin-bottom: 30px; }}
            .card {{ background: #ecf0f1; padding: 20px; border-radius: 8px; text-align: center; width: 30%; }}
            .card h3 {{ margin: 0 0 10px 0; color: #7f8c8d; }}
            .card p {{ margin: 0; font-size: 24px; font-weight: bold; color: #27ae60; }}
            .negative {{ color: #c0392b !important; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 30px; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #34495e; color: white; }}
            tr:hover {{ background-color: #f1f1f1; }}
            .chart-container {{ position: relative; height: 400px; width: 100%; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 Nikos Yatırım İşlem Geçmişi ve Performans Analizi</h1>
            
            <div class="summary">
                <div class="card">
                    <h3>Toplam İşlem Sayısı</h3>
                    <p>{len(trades)} Adet</p>
                </div>
                <div class="card">
                    <h3>Toplam Net Kar / Zarar</h3>
                    <p class="{'negative' if total < 0 else ''}">{total:.2f} TL/$</p>
                </div>
                <div class="card">
                    <h3>Kazanma Oranı (Win Rate)</h3>
                    <p>{len([p for p in js_profits if p > 0]) / len(trades) * 100:.1f}%</p>
                </div>
            </div>

            <div class="chart-container">
                <canvas id="profitChart"></canvas>
            </div>
            
            <div class="chart-container" style="margin-top:50px;">
                <canvas id="cumulativeChart"></canvas>
            </div>

            <h2 style="margin-top: 50px;">📑 Detaylı İşlem Excel Tablosu</h2>
            <table>
                <tr>
                    <th>Sembol</th>
                    <th>Alış Tarihi</th>
                    <th>Satış Tarihi</th>
                    <th>Alış Fiyatı</th>
                    <th>Satış Fiyatı</th>
                    <th>Kar / Zarar</th>
                    <th>Getiri (ROI)</th>
                </tr>
                {"".join([f"<tr><td>{t['symbol']} ({t['name']})</td><td>{t['buy_date']}</td><td>{t['sell_date']}</td><td>{t['buy_price']}</td><td>{t['sell_price']}</td><td style='color: {'green' if t['profit_loss']>0 else 'red'}'><b>{t['profit_loss']:.2f}</b></td><td style='color: {'green' if t['roi_percent']>0 else 'red'}'><b>%{t['roi_percent']:.2f}</b></td></tr>" for t in trades[::-1]])}
            </table>
        </div>

        <script>
            // İşlem Bazlı Kar/Zarar Çubuk Grafiği
            const ctx1 = document.getElementById('profitChart').getContext('2d');
            new Chart(ctx1, {{
                type: 'bar',
                data: {{
                    labels: {js_symbols},
                    datasets: [{{
                        label: 'İşlem Başına Kar/Zarar',
                        data: {js_profits},
                        backgroundColor: {js_profits}.map(p => p >= 0 ? 'rgba(46, 204, 113, 0.6)' : 'rgba(231, 76, 60, 0.6)'),
                        borderColor: {js_profits}.map(p => p >= 0 ? 'rgba(39, 174, 96, 1)' : 'rgba(192, 57, 43, 1)'),
                        borderWidth: 1
                    }}]
                }},
                options: {{ responsive: true, maintainAspectRatio: false }}
            }});

            // Kümülatif Büyüme Çizgi Grafiği
            const ctx2 = document.getElementById('cumulativeChart').getContext('2d');
            new Chart(ctx2, {{
                type: 'line',
                data: {{
                    labels: {js_labels},
                    datasets: [{{
                        label: 'Kümülatif Portföy Büyümesi (Toplam Kar)',
                        data: {cumulative},
                        fill: true,
                        backgroundColor: 'rgba(52, 152, 219, 0.2)',
                        borderColor: 'rgba(41, 128, 185, 1)',
                        tension: 0.3
                    }}]
                }},
                options: {{ responsive: true, maintainAspectRatio: false }}
            }});
        </script>
    </body>
    </html>
    """
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"\n✅ RAPORLAR BAŞARIYLA OLUŞTURULDU!")
    print(f"📊 1) Excel İçin CSV Dosyası : {CSV_FILE}")
    print(f"📈 2) Görsel Analiz (Grafik) : {HTML_FILE} (Tarayıcıda açın)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Nikos İşlem Loglayıcı ve Analiz Paneli")
    subparsers = parser.add_subparsers(dest="command")

    # BUY Command
    p_buy = subparsers.add_parser("buy")
    p_buy.add_argument("symbol", help="Hisse Sembolü")
    p_buy.add_argument("price", type=float, help="Alınan Fiyat")
    p_buy.add_argument("qty", type=float, help="Alınan Miktar/Lot")
    p_buy.add_argument("--name", default="", help="Hissenin okunaklı adı (Opsiyonel)")

    # SELL Command
    p_sell = subparsers.add_parser("sell")
    p_sell.add_argument("symbol", help="Hisse Sembolü")
    p_sell.add_argument("price", type=float, help="Satılan Fiyat")
    p_sell.add_argument("qty", type=float, help="Satılan Miktar/Lot")

    # REPORT Command
    p_report = subparsers.add_parser("report")

    args = parser.parse_args()

    if args.command == "buy":
        buy_asset(args.symbol, args.price, args.qty, args.name)
    elif args.command == "sell":
        sell_asset(args.symbol, args.price, args.qty)
    elif args.command == "report":
        generate_reports()
    else:
        parser.print_help()
