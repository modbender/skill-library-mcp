#!/usr/bin/env python3
"""
📈 NİKOS - Gelişmiş Tarihsel İndikatör & Formasyon Analizi
Düşen bıçağı tutmamak ve akıllı ticaret yapmak için İndikatör Kesişimlerini, 
Trend Yönlerini ve Uyumsuzluk/Dönüş Sinyallerini (Kıvrımları) okur.
"""
import sys, os, json, argparse, urllib.request, math

def get_historical_data(symbol, range_str="1y", interval="1d"):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval={interval}&range={range_str}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            quote = data["chart"]["result"][0]["indicators"]["quote"][0]
            closes = quote.get("close", [])
            highs = quote.get("high", [])
            lows = quote.get("low", [])
            valid_data = []
            for i in range(len(closes)):
                if list(closes)[i] is not None and list(highs)[i] is not None and list(lows)[i] is not None:
                    valid_data.append({"close": closes[i], "high": highs[i], "low": lows[i]})
            return valid_data
    except Exception as e:
        print(f"⚠️ {symbol} için veri çekilemedi: {e}")
        return None

def calc_sma(data, period):
    if len(data) < period: return [None]*len(data)
    smas = [None]*(period-1)
    for i in range(period-1, len(data)):
        smas.append(sum(d["close"] for d in data[i-period+1:i+1]) / period)
    return smas

def calc_rsi(data, period=14):
    if len(data) < period + 1: return [None]*len(data)
    rsis = [None]*period
    gains, losses = [], []
    for i in range(1, len(data)):
        chg = data[i]["close"] - data[i-1]["close"]
        gains.append(chg if chg > 0 else 0)
        losses.append(abs(chg) if chg < 0 else 0)
    
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    rs = (avg_gain / avg_loss) if avg_loss != 0 else 0
    rsis.append(100 if avg_loss == 0 else 100 - (100 / (1 + rs)))
    
    for i in range(period, len(data)-1):
        change = data[i+1]["close"] - data[i]["close"]
        gain = change if change > 0 else 0
        loss = abs(change) if change < 0 else 0
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period
        rs = (avg_gain / avg_loss) if avg_loss != 0 else 0
        rsis.append(100 if avg_loss == 0 else 100 - (100 / (1 + rs)))
    return rsis

def calc_macd(data):
    if len(data) < 26: return [None]*len(data), [None]*len(data)
    ema12, ema26 = [None]*11, [None]*25
    
    e12 = sum(d["close"] for d in data[:12])/12
    ema12.append(e12)
    for d in data[12:]:
        e12 = (d["close"] - e12) * (2/13) + e12
        ema12.append(e12)
        
    e26 = sum(d["close"] for d in data[:26])/26
    ema26.append(e26)
    for d in data[26:]:
        e26 = (d["close"] - e26) * (2/27) + e26
        ema26.append(e26)
        
    macd = [None]*25
    for i in range(25, len(data)):
        macd.append(ema12[i] - ema26[i])
        
    signal = [None]*33
    if len(macd) > 33:
        valid_macd = macd[25:]
        s9 = sum(valid_macd[:9])/9
        signal.append(s9)
        for m in valid_macd[9:]:
            s9 = (m - s9) * (2/10) + s9
            signal.append(s9)
            
    while len(signal) < len(data): signal.insert(0, None)
    return macd, signal

def calc_stoch(data, period=14):
    if len(data) < period: return [None]*len(data), [None]*len(data)
    stoch_k = [None]*(period-1)
    for i in range(period-1, len(data)):
        window = data[i-period+1:i+1]
        hh = max(d["high"] for d in window)
        ll = min(d["low"] for d in window)
        c = data[i]["close"]
        stoch_k.append(50 if hh == ll else ((c - ll) / (hh - ll)) * 100)
        
    stoch_d = [None]*len(data)
    for i in range(period+1, len(stoch_k)):
        if all(x is not None for x in stoch_k[i-2:i+1]):
            stoch_d[i] = sum(stoch_k[i-2:i+1]) / 3
            
    return stoch_k, stoch_d

def analyze_asset(symbol, name):
    print(f"\n🔍 GEREKÇELİ VE KONTROLLÜ ANALİZ: {name} ({symbol})")
    
    data = get_historical_data(symbol, range_str="1y", interval="1d")
    if not data or len(data) < 50:
        print("   ❌ Analiz için yeterli geçmiş veri bulunamadı.")
        return
        
    c_idx = -1
    p_idx = -2
    pp_idx = -3
    
    current_price = data[c_idx]["close"]
    
    sma_50 = calc_sma(data, 50)
    sma_200 = calc_sma(data, 200)
    rsi = calc_rsi(data, 14)
    macd, signal = calc_macd(data)
    stoch_k, stoch_d = calc_stoch(data, 14)
    
    # Güncel değerler
    r_c, r_p = rsi[c_idx], rsi[p_idx]
    m_c, m_p = macd[c_idx], macd[p_idx]
    s_c, s_p = signal[c_idx], signal[p_idx]
    k_c, k_p = stoch_k[c_idx], stoch_k[p_idx]
    d_c, d_p = stoch_d[c_idx], stoch_d[p_idx]
    
    print(f"   Anlık Fiyat     : {current_price:.2f}")
    
    # 1. DÜŞEN BIÇAK KONTROLÜ (Oversold but no reversal)
    is_falling_knife = False
    if r_c and r_c < 30:
        if m_c and s_c and m_c < s_c and k_c and k_c < 20 and k_c <= k_p:
            is_falling_knife = True
            
    # 2. SAHTE YÜKSELİŞ KONTROLÜ / AŞIRI ALIM (Overbought but momentum losing)
    is_exhausted_bull = False
    if r_c and r_c > 70:
        if m_c and s_c and m_c > s_c and (m_c - s_c) < (m_p - s_p) and k_c and k_c > 80 and k_c <= k_p:
            is_exhausted_bull = True

    # 3. YÜKSELİŞ TEYİDİ (Oversold reversal / Golden Cross / Curl up)
    is_dip_buy = False
    if r_c and r_p and r_c < 40 and r_c > r_p: # RSI kıvrılıyor
        if (m_c and s_c and m_p and s_p and m_c > s_c and m_p <= s_p) or (k_c and d_c and k_p and d_p and k_c > d_c and k_p <= d_p):
            is_dip_buy = True
            
    score = 50 # Merkez
    
    print("\n   [ AKILLI İNDİKATÖR KONTROLLERİ ]")
    
    # RSI Yorumu
    if r_c:
        if r_c < 30:
            if r_p and r_c > r_p:
                print(f"   🟢 RSI ({r_c:.1f}): Aşırı satışta yönünü yukarı çevirmiş (Kıvrım var = Olumlu)")
                score += 15
            else:
                print(f"   🔴 RSI ({r_c:.1f}): Aşırı satışta ve hala düşüyor (Dİkkat! Dip bulunmamış olabilir)")
                score -= 10
        elif r_c > 70:
            if r_p and r_c < r_p:
                print(f"   🔴 RSI ({r_c:.1f}): Aşırı alımda ve yorulma emareleri var (Dönüş riski)")
                score -= 15
            else:
                print(f"   🟡 RSI ({r_c:.1f}): Aşırı alımda ama trend hala çok güçlü (FOMO bölgesi)")
                score += 5
        else:
            if r_p and r_c > 50 and r_c > r_p:
                print(f"   🟢 RSI ({r_c:.1f}): Nötr bölgede, yukarı yönlü güçlü trend devam ediyor")
                score += 10
            elif r_p and r_c < 50 and r_c < r_p:
                print(f"   🔴 RSI ({r_c:.1f}): Nötr bölgede, zayıflama devam ediyor")
                score -= 10
            else:
                print(f"   🟡 RSI ({r_c:.1f}): Yön arayışında (Yatay)")

    # MACD Yorumu
    if m_c and s_c and m_p and s_p:
        if m_c > s_c:
            if m_p <= s_p:
                print(f"   🟢 MACD: YENİ AL SİNYALİ ÜRETTİ! (Taze Kesişim - Potansiyel büyük)")
                score += 20
            else:
                # Kesişim çoktansa ve mesafe kapanıyorsa ivme kayboluyor demektir.
                if (m_c - s_c) < (m_p - s_p):
                    print(f"   🟡 MACD: AL konumunda ama ivme kaybediyor (Eski sinyal, momentum yavaşlıyor)")
                    score += 5
                else:
                    print(f"   🟢 MACD: AL konumunda, pozitif ivme artarak devam ediyor.")
                    score += 10
        else:
            if m_p >= s_p:
                print(f"   🔴 MACD: YENİ SAT SİNYALİ ÜRETTİ! (Taze Kesişim)")
                score -= 20
            else:
                print(f"   🔴 MACD: SAT konumunda, negatif bölgede devam ediyor.")
                score -= 10

    # STOCHASTIC Yorumu
    if k_c and d_c and k_p and d_p:
        if k_c < 20 and d_c < 20:
            if k_c > d_c and k_p <= d_p:
                print(f"   🟢 STOCH ({k_c:.1f}): YENİ AL SİNYALİ ÜRETTİ! (Aşırı satıştan taze dip kesişimi)")
                score += 15
            elif k_c < d_c:
                print(f"   🔴 STOCH ({k_c:.1f}): Aşırı satış bölgesinde ölü taklidi yapıyor (Trend hala zayıf)")
                score -= 5
            else:
                 print(f"   🟡 STOCH ({k_c:.1f}): Eski alım sinyali, dipten dönüş başlamış.")
                 score += 5
        elif k_c > 80 and d_c > 80:
            if k_c < d_c and k_p >= d_p:
                print(f"   🔴 STOCH ({k_c:.1f}): YENİ SAT SİNYALİ ÜRETTİ! (Aşırı alımdan tepe dönüşü)")
                score -= 15
            elif k_c > d_c:
                print(f"   🟡 STOCH ({k_c:.1f}): Tepede tutunuyor, güçlü trend ama patlamaya hazır itici güç yok")
                score += 5
            else:
                print(f"   🔴 STOCH ({k_c:.1f}): Eski SAT sinyali hala devrede, düşüş sürüyor.")
                score -= 5
        else:
            if k_c > d_c:
                if k_p <= d_p:
                    print(f"   🟢 STOCH ({k_c:.1f}): Nötr bölgede taze yukarı yönlü kesişim!")
                    score += 10
                else:
                    print(f"   🟡 STOCH ({k_c:.1f}): Nötr bölgede yukarı yönlü ivme (Eski sinyal)")
                    score += 5
            else:
                if k_p >= d_p:
                    print(f"   🔴 STOCH ({k_c:.1f}): Nötr bölgede taze aşağı yönlü kesişim!")
                    score -= 10
                else:
                    print(f"   🟡 STOCH ({k_c:.1f}): Nötr bölgede aşağı yönlü ivme (Eski düşüş sinyali)")
                    score -= 5

    # Trend Filtresi (200 SMA)
    if sma_200[c_idx]:
        if current_price > sma_200[c_idx]:
            print(f"   🛡️ ANA TREND: 200 SMA ({sma_200[c_idx]:.2f}) ÜZERİNDE (BOĞA PİYASASI)")
            score += 10
        else:
            print(f"   ⚠️ ANA TREND: 200 SMA ({sma_200[c_idx]:.2f}) ALTINDA (AYI PİYASASI)")
            score -= 10

    # Nihai Karar
    print("\n   [ RİSK VE STRATEJİ YORUMU ]")
    if is_falling_knife:
        print("   🗡️ UYARI: DÜŞEN BIÇAK! Göstergeler aşırı satışta olsa da ALIM SİNYALİ YOK. Trend tamamen aşağı bakıyor. Yaklaşmayın!")
        score -= 20
    elif is_exhausted_bull:
        print("   📉 UYARI: YORULMUŞ BOĞA! Çok yükselmiş, göstergelerde zayıflama (uyumsuzluk veya eğim kaybı) var. Kar alma zamanı olabilir.")
        score -= 20
    elif is_dip_buy:
        print("   💎 FIRSAT: DİPTEN DÖNÜŞ SİNYALİ! Hem aşırı satışta kıvrılma, hem de MACD/Stoch teyidi var. Risk-ödül oranı yüksek bir alım noktası!")
        score += 20
    else:
        print("   ⚖️ RİSK: Olağan piyasa koşulları. Keskin bir dönüş veya düşen bıçak formasyonu tespit edilmedi.")

    # Score Sınırları 0 - 100
    score = max(0, min(100, score))

    print("   ----------------------------------------")
    print(f"   🎯 AKILLI ALGORİTMİK PUAN: {score:.1f} / 100")
    
    if score >= 75:
        print("   📢 KARAR: GÜÇLÜ AL 🟢 (Risk düşük, dip teyit edilmiş veya momentum çok güçlü)")
    elif score >= 60:
        print("   📢 KARAR: AL 📈 (Yön yukarı, göstergeler pozitif)")
    elif score >= 40:
        print("   📢 KARAR: İZLE / NÖTR 🟡 (Kararsız bölge, net bir dönüş/kırılım yok)")
    elif score >= 25:
        print("   📢 KARAR: SAT 📉 (Negatif görünüm ve zayıflayan fiyat hareketi)")
    else:
        print("   📢 KARAR: GÜÇLÜ SAT 🔴 (Düşüş sertleşiyor, destekler kırılmış, alım yönünde tehlikeli!)")
    print("="*80)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("symbols", nargs="*")
    args = parser.parse_args()
    
    if args.symbols:
        for sym in args.symbols:
            analyze_asset(sym, sym)
    else:
        for sym, name in [("THYAO.IS", "Türk Hava Yolları"), ("SASA.IS", "SASA"), ("BTC-USD", "Bitcoin")]:
            analyze_asset(sym, name)
