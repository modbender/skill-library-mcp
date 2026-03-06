TikTok Skill (openclaw-style)
=================================

Purpose
-------
This folder contains a small skill for generating TikTok image carousels and drafting posts to a draft-upload service (Postiz). It's designed to be simple, cost-aware, and easy to extend.

Quick start
-----------
1. Install dependencies in a venv:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
```

2. Set environment variables (example):

```powershell
$env:OPENAI_API_KEY = 'sk-...'
$env:POSTIZ_API_KEY = 'postiz-...'
```

3. Generate locally (uses placeholder images if no OPENAI_API_KEY):

```powershell
python scripts\generate.py "small kitchen makeover" --out images --slides 6
```

4. Upload and create draft (Postiz service must be configured):

```powershell
python scripts\upload.py images\final_slide_*.png --caption "My AI-generated carousel"
```

Files
-----
- `tiktok_content_gen.py` — orchestrator and image/text utilities.
- `postiz_api_integration.py` — Postiz API client.
- `scripts/generate.py` — CLI wrapper for generation.
- `scripts/upload.py` — CLI wrapper for uploading images and creating draft.

Notes
-----
- Keep keys out of source control. Use environment variables or a secrets manager.
- The implementation includes placeholder behavior so you can test end-to-end without incurring API costs.
