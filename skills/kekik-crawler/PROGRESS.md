# kekik-crawler — Progress

## Durum
- **Faz:** v0.1.0-rc1 hazırlık
- **Genel:** Devam ediyor
- **Son güncelleme:** 2026-02-26 15:26 (Europe/Istanbul)

## Tamamlananlar ✅
- Scrapling-first backend (default)
- Çoklu arama motoru query seed (DuckDuckGo/Bing/Yahoo/Brave web)
- Araştırma modları (`normal`, `wide`, `deep`)
- Hata sınıflandırma (`timeout`, `forbidden`, `rate_limited`, vb.)
- Domain health raporu (`report.json`)
- Checkpoint/resume
- URL canonicalization + dedup
- SQLite cache (`ETag` / `Last-Modified`)
- Proje çıktıları `outputs/` altına taşındı
- `.gitignore` temizlendi

## Devam Edenler 🔄
- Kod yapısını prod düzene çekme (klasörleme/sorumluluk ayrımı)
- Rapor formatını netleştirme (stabilite/başarı matrisi)

## Yeni Tamamlananlar (15:39) ✅
- `crawler.py` parçalandı; sorumluluklar `core/*` modüllerine dağıtıldı
- Tek backend: `backends/scrapling_backend.py` (Scrapling-only)
- `core/fetcher.py`, `core/robots.py`, `core/plugin_manager.py` ile çekirdek ayrıştı
- Legacy/no-op argümanlar temizlendi; CLI sadeleşti
- README mimari odaklı yeniden yazıldı
- Derleme + smoke test başarıyla geçti

## Yeni Tamamlananlar (15:46) ✅
- SRP refactor: orchestration `core/crawl_runner.py` içine taşındı (`CrawlRunner`)
- `crawler.py` legacy kalın gövde yerine ince compatibility wrapper'a indirildi
- `core/checkpoint.py` ile checkpoint sorumluluğu `core/storage.py`'dan ayrıldı
- `core/mode.py` ile mode limit kuralları tek noktaya alındı
- Kod temizliği: storage'dan legacy checkpoint fonksiyonları kaldırıldı
- README mimari bölümü yeni modül yapısına göre güncellendi

## Yeni Tamamlananlar (15:48) ✅
- `pyproject.toml` eklendi (ruff/mypy/pytest temel ayar)
- `core/` ve `backends/` package init dosyaları eklendi
- Temel test hattı eklendi (`tests/`)
- Testler geçti: `5 passed`
- README kalite kontrol komutları güncellendi

## Sıradaki Adımlar ⏭️
1. Ruff/mypy komutlarını CI scriptine bağlamak
2. `v0.1.0-rc1` release notları
3. ClawHub publish hazırlığı

## Takip için
- Çıktılar: `outputs/`
- Ana giriş: `main.py`
- Çekirdek orchestrator: `core/crawl_runner.py`
- Compatibility export: `crawler.py`
- Scrapling backend: `backends/scrapling_backend.py`
