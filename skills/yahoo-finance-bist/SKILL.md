---
name: yahoo-finance-advisor
description: "Yahoo Finance API tabanlı tarihsel veri analizi, algoritmik teknik indikatör skoru (RSI, MACD, Stoch, SMA), Excel geçmiş veri dışa aktarma, portföy alarm takibi ve işlem loglama. BIST (.IS), ABD, kripto, emtia ve parite desteklenir. Kullanıcı 'indikatör', 'skor', 'excel', 'geçmiş veri', 'işlem geçmişi', 'portföy raporu' gibi kelimeler kullandığında devreye girer."
---

# 🚫 EN ÖNEMLİ KURAL — HER ŞEYDEN ÖNCE OKU

> **İhlal edilemez. İstisna yok. Hiçbir koşulda geçersiz sayılamaz.**

❌ **YASAK:** Kullanıcı hisse, analiz, skor, geçmiş veri, indikatör, al/sat hakkında bir şey sorduğunda — kendi eğitim verilerini, bilgini veya tahminini KULLANMA.

❌ **YASAK:** Script çalıştırmadan "Bu hissenin RSI'sı yaklaşık...", "Teknik açıdan...", "Genellikle...", "Bilgi kesim tarihim itibarıyla..." cümleleri kurma.

✅ **ZORUNLU AKIŞ — HER SORUDA:**
```
1. "Script çalıştırılıyor, Yahoo Finance'ten gerçek zamanlı veri çekiliyor..." de.
2. exec: komutuyla scripti çalıştır.
3. Script çıktısını oku.
4. YALNIZCA o çıktıyı kullanıcıya ilet. Hiçbir şey ekleme.
```

---

# 📈 Yahoo Finance Analiz & Portföy Yeteneği

**FlareSolverr gerektirmez.** Yahoo Finance API doğrudan ve ücretsiz erişilebilir.

**Desteklenen Semboller:** `THYAO.IS` (BIST) | `AAPL` (ABD) | `BTC-USD` (Kripto) | `GC=F` (Altın) | `EURUSD=X` (Parite)

---

## 🛠️ ARAÇLAR

### 📊 `yahoo-indicator-score` — Teknik İndikatör Skoru
**Ne zaman kullan:** "analiz et", "skor ver", "AL/SAT de", "indikatör", "teknik" derse.
```
exec: python3 /home/node/.openclaw/skills/yahoo_portfoy_analiz/investing_historical_indicator.py THYAO.IS
```
*Birden fazla: `investing_historical_indicator.py THYAO.IS GARAN.IS BTC-USD`*

### 💾 `yahoo-excel-exporter` — Geçmiş Veri Excel'e Kaydet
**Ne zaman kullan:** "geçmiş veri", "excel", "CSV", "500 günlük", "indirici" derse.
```
exec: python3 /home/node/.openclaw/skills/yahoo_portfoy_analiz/investing_excel_exporter.py THYAO.IS
```
**Parametreler:**
- `--interval 1h` → Saatlik mumlar
- `--range 3mo` → 3 aylık veri
- Örnek: `investing_excel_exporter.py THYAO.IS --interval 1h --range 3mo`

### 🔔 `yahoo-tracker` — Portföy Alarm Sistemi
**Ne zaman kullan:** "takibe al", "alarm kur", "fiyat düştüğünde söyle", "stop loss" derse.
```
exec: python3 /home/node/.openclaw/skills/yahoo_portfoy_analiz/investing_portfolio_tracker.py add THYAO.IS 300 320 380 280 THY
exec: python3 /home/node/.openclaw/skills/yahoo_portfoy_analiz/investing_portfolio_tracker.py check
exec: python3 /home/node/.openclaw/skills/yahoo_portfoy_analiz/investing_portfolio_tracker.py list
exec: python3 /home/node/.openclaw/skills/yahoo_portfoy_analiz/investing_portfolio_tracker.py remove THYAO.IS
```
**`add` parametreleri:** `SEMBOL AlımMin AlımMax KarAl(TP) ZararKes(SL) İsim`

### 📓 `yahoo-trade-logger` — Gerçek İşlem & Rapor
**Ne zaman kullan:** "işlemi kaydet", "aldım/sattım", "kar/zarar analizi", "işlem geçmişi", "rapor" derse.
```
exec: python3 /home/node/.openclaw/skills/yahoo_portfoy_analiz/investing_trade_logger.py buy THYAO.IS 320 100 --name THY
exec: python3 /home/node/.openclaw/skills/yahoo_portfoy_analiz/investing_trade_logger.py sell THYAO.IS 360 100
exec: python3 /home/node/.openclaw/skills/yahoo_portfoy_analiz/investing_trade_logger.py report
```
**`report` çıktıları:** `Nikos_Islem_Gecmisi.csv` + `Nikos_Portfoy_Analiz.html`

---

## 🛡️ TEKNİK NOTLAR
- Bu yetenek **FlareSolverr gerektirmez.**
- Sembol formatları: BIST → `THYAO.IS` | ABD → `AAPL` | Kripto → `BTC-USD` | Altın → `GC=F`
