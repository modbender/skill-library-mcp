---
name: prayer-times-id
description: Menjadwalkan reminder waktu shalat (Indonesia) ke OpenClaw System Event berdasarkan lokasi, lengkap dengan quote harian Islami dan status Ramadan otomatis.
---

# prayer-times-id

Skill ini menjalankan engine Node.js untuk:
1. mengambil jadwal shalat harian dari AlAdhan API,
2. menentukan status Ramadan (otomatis/manual),
3. membuat one-shot cron job OpenClaw untuk setiap waktu shalat yang belum lewat,
4. mengirim pesan reminder berformat rapi dengan quote harian.

## Struktur File

- `engine.js` — engine utama penjadwalan reminder.
- `prayer_config.json` — konfigurasi lokasi + pengaturan perhitungan.
- `quotes_id.json` — kumpulan quote Islami berbahasa Indonesia.

## Dependensi

- Node.js 18+ (disarankan 20+)
- OpenClaw CLI tersedia di PATH (`openclaw`)
- Akses internet ke:
  - `https://api.aladhan.com/v1/timings`
  - `https://api.aladhan.com/v1/gToH`

## Konfigurasi

Edit `prayer_config.json`:

```json
{
  "location": {
    "name": "Cimahi",
    "latitude": -6.8722,
    "longitude": 107.5427,
    "expires": "2026-03-02"
  },
  "settings": {
    "auto_ramadan": true,
    "manual_override": null,
    "method": 11,
    "timezone": "Asia/Jakarta"
  },
  "sources": {
    "quotes_enabled": true,
    "current_day_source": "local"
  }
}
```

Keterangan penting:
- `location.name`: label lokasi yang tampil di pesan.
- `latitude` / `longitude`: koordinat lokasi.
- `settings.method`: metode kalkulasi AlAdhan.
- `settings.timezone`: timezone IANA (contoh `Asia/Jakarta`).
- `settings.auto_ramadan`: deteksi Ramadan otomatis dari tanggal Hijriah.
- `settings.manual_override`: `true`/`false` untuk override status Ramadan; `null` untuk otomatis.

## Cara Menjalankan

Dari folder skill:

```bash
node engine.js --dry-run
```

- Tidak menulis cron job, hanya simulasi output JSON.

```bash
node engine.js
```

- Menambahkan cron one-shot ke OpenClaw untuk waktu shalat hari ini yang belum lewat.

## Output

Engine mengeluarkan JSON ringkas, contoh:

- `status`: hasil eksekusi
- `dryRun`: mode simulasi atau real
- `location`, `timezone`, `ramadan`
- `registered`: jumlah job yang berhasil dijadwalkan
- `jobs[]`: detail job per waktu shalat

## Keamanan & Kepatuhan

- Tidak ada hardcoded secret/token/api key.
- Tidak ada hardcoded private/public IP.
- Eksekusi CLI memakai `execFileSync` (tanpa shell command interpolation) untuk meminimalkan risiko command injection.
- Penjadwalan job memakai `openclaw cron add --at ... --system-event ...` secara langsung (tanpa nested command / shell-style job string).
- Input konfigurasi divalidasi (nama lokasi, koordinat, metode).
- Input user `location.name` sekarang disanitasi untuk keamanan (hanya alphanumeric, spasi, dan `-`).
- Request API dibatasi timeout (`AbortSignal.timeout`) agar tidak hang.

## Catatan Operasional

- Engine hanya menjadwalkan reminder **hari berjalan**; jalankan ulang harian (mis. via scheduler induk) untuk generate jadwal hari berikutnya.
- Engine hanya menggunakan mode modern OpenClaw Cron (`--at` + `--system-event`) dan tidak lagi menyediakan fallback legacy berbasis `--job 'at ...'`.
