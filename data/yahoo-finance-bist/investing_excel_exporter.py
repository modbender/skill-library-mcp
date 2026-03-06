#!/usr/bin/env python3
"""
📊 NİKOS - Geçmiş Veri & İndikatör Excel Dışa Aktarıcı (500 Gün)
BIST veya herhangi bir hissenin son 2 yıllık (yaklaşık 500 işlem günü) Açılış, Kapanış,
Yüksek, Düşük ve Hacim verilerini çeker, üzerine RSI, SMA ve MACD gibi göstergeleri hesaplayarak
doğrudan EXCEL (CSV) tablosuna yazar.
"""
import sys, os, json, argparse, urllib.request, math, csv
from datetime import datetime

def get_historical_data(symbol, range_str="2y", interval="1d"):
    # 2y (2 yıl) ortalama 500 işlem gününe denk gelir
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval={interval}&range={range_str}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            res = data["chart"]["result"][0]
            timestamps = res.get("timestamp", [])
            quote = res["indicators"]["quote"][0]
            
            closes = quote.get("close", [])
            opens = quote.get("open", [])
            highs = quote.get("high", [])
            lows = quote.get("low", [])
            volumes = quote.get("volume", [])
            
            valid_data = []
            for i in range(len(timestamps)):
                if (i < len(closes) and closes[i] is not None and 
                    highs[i] is not None and lows[i] is not None):
                    dt = datetime.fromtimestamp(timestamps[i]).strftime('%Y-%m-%d')
                    valid_data.append({
                        "date": dt,
                        "open": opens[i],
                        "high": highs[i],
                        "low": lows[i],
                        "close": closes[i],
                        "volume": volumes[i] if volumes[i] is not None else 0
                    })
            return valid_data
    except Exception as e:
        print(f"⚠️ {symbol} için veri çekilemedi: {e}")
        return []

# SMA Hesaplayıcı (Seri döner)
def calc_sma_series(prices, period):
    smas = [None]*len(prices)
    for i in range(period-1, len(prices)):
        smas[i] = sum(prices[i-period+1:i+1]) / period
    return smas

# RSI Hesaplayıcı (Seri döner)
def calc_rsi_series(prices, period=14):
    rsis = [None]*len(prices)
    if len(prices) <= period: return rsis
    
    gains, losses = [], []
    for i in range(1, len(prices)):
        chg = prices[i] - prices[i-1]
        gains.append(chg if chg > 0 else 0)
        losses.append(abs(chg) if chg < 0 else 0)
        
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    
    if avg_loss == 0:
        rsis[period] = 100
    else:
        rs = avg_gain / avg_loss
        rsis[period] = 100 - (100 / (1 + rs))
        
    for i in range(period, len(prices)-1):
        change = prices[i+1] - prices[i]
        gain = change if change > 0 else 0
        loss = abs(change) if change < 0 else 0
        
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period
        
        if avg_loss == 0:
            rsis[i+1] = 100
        else:
            rs = avg_gain / avg_loss
            rsis[i+1] = 100 - (100 / (1 + rs))
    return rsis

def export_to_excel(symbol, range_str="2y", interval="1d"):
    label = "500 Günlük" if range_str == "2y" and interval == "1d" else f"{range_str} ({interval} Mumlar)"
    print(f"⏳ {symbol} için {label} piyasa verisi çekiliyor...")
    data = get_historical_data(symbol, range_str, interval)
    if not data:
        print(f"❌ {symbol} için veri bulunamadı.")
        return
        
    print(f"✅ Toplam {len(data)} veri satırı bulundu. İndikatörler hesaplanıyor...")
    closes = [d["close"] for d in data]
    
    sma20 = calc_sma_series(closes, 20)
    sma50 = calc_sma_series(closes, 50)
    sma200 = calc_sma_series(closes, 200)
    rsi14 = calc_rsi_series(closes, 14)
    
    symbol_clean = symbol.replace('.IS', '')
    filename = f"{symbol_clean}_{range_str}_{interval}.csv"
    
    # Verilerin tutulacağı klasörü ayarla
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "symbol_data")
    os.makedirs(data_dir, exist_ok=True)
    
    filepath = os.path.join(data_dir, filename)
    
    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        # Excel'in Türkçe işletim sistemlerinde sütun ayırması için noktalı virgül (;) kullanıyoruz
        writer = csv.writer(f, delimiter=';')
        writer.writerow(["Tarih", "Açılış", "En Yüksek", "En Düşük", "Kapanış", "Hacim", "SMA 20", "SMA 50", "SMA 200", "RSI 14"])
        
        # Sondan başa doğru mu yazalım (En yeni en üstte)? Evet, analiz için daha iyi.
        for i in range(len(data)-1, -1, -1):
            date = data[i]["date"]
            op = f'{data[i]["open"]:.2f}'.replace('.', ',') if data[i]["open"] else ""
            hi = f'{data[i]["high"]:.2f}'.replace('.', ',')
            lo = f'{data[i]["low"]:.2f}'.replace('.', ',')
            cl = f'{data[i]["close"]:.2f}'.replace('.', ',')
            vol = data[i]["volume"]
            
            s_20 = f'{sma20[i]:.2f}'.replace('.', ',') if sma20[i] else ""
            s_50 = f'{sma50[i]:.2f}'.replace('.', ',') if sma50[i] else ""
            s_200 = f'{sma200[i]:.2f}'.replace('.', ',') if sma200[i] else ""
            r_14 = f'{rsi14[i]:.2f}'.replace('.', ',') if rsi14[i] else ""
            
            writer.writerow([date, op, hi, lo, cl, vol, s_20, s_50, s_200, r_14])

    print(f"🎉 Başarılı! {symbol} hissesinin geçmiş verileri ve indikatörleri Excel'e yazıldı:")
    print(f"👉 Dosya Yolu: {filepath}")
    
    # Otomatik Temizlik: 3000'den fazla dosya varsa en eskilerini sil
    csv_files = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith('.csv')]
    if len(csv_files) > 3000:
        # Değiştirilme tarihine göre sırala (en eski en başta)
        csv_files.sort(key=os.path.getmtime)
        excess = len(csv_files) - 3000
        for f in csv_files[:excess]:
            try:
                os.remove(f)
            except:
                pass
        print(f"🧹 Depolama optimizasyonu: En eski {excess} veri dosyası silindi.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="🚀 Nikos - Geçmiş 500 Günlük Excel Dökümü")
    parser.add_argument("symbols", nargs="+", help="BIST Sembolü (Örn: THYAO.IS)")
    parser.add_argument("--interval", default="1d", help="Zaman aralığı: 1m, 5m, 15m, 1h, 1d, 1wk (Varsayılan: 1d)")
    parser.add_argument("--range", default="2y", help="Veri kapsamı: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, max (Varsayılan: 2y)")
    args = parser.parse_args()
    
    for sym in args.symbols:
        export_to_excel(sym, args.range, args.interval)
