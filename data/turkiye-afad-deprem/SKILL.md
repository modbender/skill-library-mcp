---
name: turkiye-afad-deprem
description: Turkiye AFAD deprem verisini kullanarak zaman, buyukluk ve bolge filtreli deprem ozeti uretir.
metadata:
  openclaw:
    homepage: https://github.com/barancaki/turkey_earthquake_skill
    os: any
    user-invocable: true
    requires:
      network: true
---

# Turkiye AFAD Deprem Skill

## Ne Zaman Cagrilir

Bu skill, kullanici AFAD tabanli guncel deprem bilgisi istediginde cagrilir.

Net trigger cumleleri:
- "AFAD son depremleri goster"
- "Son 24 saatte deprem var mi?"
- "Son 7 gun M4+ depremleri listele"
- "Izmir civarindaki depremleri getir"
- "Bugun olan depremleri ozetle"
- "4 ve ustu depremleri goster"

## Kullanici Girdisini Yorumlama

### Zaman Araligi

- "son 1 saat" => simdiden geriye 1 saat
- "bugun" => yerel saate gore bugunun 00:00-23:59 araligi
- "son 24 saat" => simdiden geriye 24 saat
- "son 7 gun" => simdiden geriye 7 gun
- belirtilmezse varsayilan: son 24 saat

### Minimum Buyukluk

- "M4+", "4+", "4 ve ustu" => `min_magnitude = 4.0`
- "M5.2+" => `min_magnitude = 5.2`
- belirtilmezse tum buyuklukler dahil edilir

### Bolge / Sehir

- Metin filtreleme: kullanici bolge/sehir ifadesi (`"Izmir civari"`, `"Marmara"`, `"Van"`) yer bilgisinde aranir.
- Opsiyonel yakin eslesme: birebir eslesme yoksa yazim farklari icin yakin eslesme uygulanabilir.
- Birden fazla bolge verilirse herhangi birine uyan kayitlar dahil edilir.

## Cikti Formati

Yaniti su sirada uret:

1. Tek satir ozet: `<N> deprem bulundu.`
2. En buyuk deprem:
   `En buyuk: <tarih-saat> | M<buyukluk> | <yer>`
3. Son 5 deprem tablo gibi:

| Tarih-Saat | Buyukluk | Yer |
|---|---:|---|
| ... | ... | ... |

4. Kaynak linki:
   `Kaynak: <AFAD veri linki>`

## Hata Mesajlari ve Fallback

- Veri kaynagi yanit vermedi:
  `AFAD veri kaynagina su anda erisilemiyor. Lutfen kisa bir sure sonra tekrar deneyin.`
- Bos sonuc:
  `Secilen filtrelerle deprem kaydi bulunamadi. Zaman araligini genisletmeyi veya min buyuklugu dusurmeyi deneyin.`

## Guvenlik

- Bu skill komut calistirmaz.
- Yalnizca public AFAD deprem verisini okur ve filtreler.
- Kullanici tarafinda sistem degisikligi, dosya yazma veya harici komut tetikleme yapmaz.
