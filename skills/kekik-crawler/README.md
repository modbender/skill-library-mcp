# kekik-crawler

Scrapling tabanlı, browser'sız, temiz mimarili crawler.

## Mimari
- `main.py` → CLI giriş noktası
- `crawler.py` → compatibility wrapper (`run` export)
- `core/crawl_runner.py` → ana orchestrator (`CrawlRunner`)
- `core/mode.py` → mode bazlı limit/strateji
- `core/checkpoint.py` → checkpoint okuma/yazma
- `backends/scrapling_backend.py` → fetch backend
- `core/` → küçük sorumluluk modülleri (`errors`, `fetcher`, `metrics`, `plugin_manager`, `robots`, `search_engines`, `storage`, `urlutils`)
- `plugins/` → domain extractor'ları
- `outputs/` → runtime çıktıları (jsonl/report/cache/checkpoint)

## Kurulum
```bash
pip install -r requirements.txt
```

## Kalite Kontrol
```bash
python3 -m pytest -q
python3 -m py_compile main.py crawler.py core/*.py backends/*.py plugins/*.py
```

## Kullanım
```bash
# Basit crawl
python main.py --urls https://example.org --max-pages 20 --concurrency 6

# Kişi araştırma (preset)
python main.py --queries "Ömer Faruk Sancak" keyiflerolsun --preset person-research \
  --out outputs/person.jsonl --report outputs/person-report.json

# Derin araştırma
python main.py --queries "Ömer Faruk Sancak" keyiflerolsun --preset deep-research \
  --out outputs/deep.jsonl --report outputs/deep-report.json

# Sertifika sorunlu test ortamı
python main.py --urls https://example.org --insecure
```

## Plugin kontratı
`plugins/<domain>.py`
```python
def extract(url: str, html: str, tree):
    return {"title": "...", "text": "...", "links": ["https://..."]}
```
