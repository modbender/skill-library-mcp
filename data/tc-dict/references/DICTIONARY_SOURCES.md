# MOE Dictionary Data Sources

## Metadata

- **Official Site**: https://language.moe.gov.tw/001/Upload/Files/site_content/M0001/respub/index.html
- **License**: Creative Commons Attribution 3.0 Taiwan (CC BY 3.0 TW)
  - Allows commercial use, redistribution, and transmission
  - Must preserve attribution
  - Must not modify the content

## Available Dictionaries

### 國語辭典簡編本 (Concised Mandarin Dictionary)

**Status**: PRIMARY DICTIONARY (currently implemented)

**Download Page**: https://language.moe.gov.tw/001/Upload/Files/site_content/M0001/respub/dict_concised_download.html

**File Structure**:
```
dict_concised_2014_YYYYMMDD.zip
├── (extract to) dict_concised_2014_YYYYMMDD/
│   └── dict_concised_2014.xlsx [Main data file]
```

**Latest Version** (as of 2026-02-17): `dict_concised_2014_20251229`
- Updated: 2025/12/29
- File URL: `https://language.moe.gov.tw/001/Upload/Files/site_content/M0001/respub/download/dict_concised_2014_20251229.zip`

**Data Availability**:
- 📄 Text database (文字資料庫) — `.xlsx` format
- 🖼️ Image files (圖片檔) — optional
- 🔊 Audio files (聲音檔) — optional, split across 5 zips

**For this skill**: We use only the `.xlsx` text database.

### Other MOE Dictionaries (Future Implementation)

**重編國語辭典修訂本** (Revised Comprehensive Mandarin Dictionary)
- URL: https://language.moe.gov.tw/001/Upload/Files/site_content/M0001/respub/dict_revised_download.html
- More comprehensive, includes historical usage
- Use case: Academic/research lookups

**成語典** (Idiom Dictionary)
- URL: https://language.moe.gov.tw/001/Upload/Files/site_content/M0001/respub/dict_idiom_download.html
- Specialized for Chinese idioms/set phrases
- Use case: Idiom definitions and usage

**國語小字典** (Elementary Dictionary)
- URL: https://language.moe.gov.tw/001/Upload/Files/site_content/M0001/respub/dict_mini_download.html
- Simplified, for young learners
- Use case: Basic definitions, simple language

## Version Tracking

Each dictionary file encodes its update date in the filename:

Format: `dict_[name]_2014_YYYYMMDD`

Examples:
- `dict_concised_2014_20251229` → Updated 2025-12-29
- `dict_revised_2014_20240315` → Updated 2024-03-15

**Metadata Storage**:

Local version info is stored in `~/.openclaw/dictionaries/metadata.json`:

```json
{
  "concised": {
    "version": "20251229",
    "downloaded_at": "2026-02-17T12:34:56Z",
    "path": "~/.openclaw/dictionaries/dict_concised_2014/",
    "filename": "dict_concised_2014.xlsx"
  }
}
```

This allows scripts to:
1. Compare local version with MOE's latest
2. Determine if an update is needed
3. Track update history

## Update Schedule

**Recommended Cron**: Monthly (~ every 30 days)

MOE typically updates dictionaries quarterly, but checking monthly provides a good balance between freshness and API efficiency.

**Manual Override**: Users can trigger `update_dictionary --force` to download immediately, regardless of version.

## Implementation Notes

- **Download URL Pattern**: Replace version number in filename to get latest
  - Old: `dict_concised_2014_20200929.zip`
  - New: `dict_concised_2014_20251229.zip`
  - Pattern: `https://language.moe.gov.tw/001/Upload/Files/site_content/M0001/respub/download/dict_concised_2014_YYYYMMDD.zip`

- **Extraction**: Zip contains folder with same name as zip file (minus .zip)
  - `dict_concised_2014_20251229.zip` → `dict_concised_2014_20251229/`

- **Data File Location**: After extraction, xlsx is in the extracted folder
  - Path: `dict_concised_2014_20251229/dict_concised_2014.xlsx`

- **Storage**: Keep extracted xlsx in versioned folder structure for easy rollback/comparison
  ```
  ~/.openclaw/dictionaries/
  ├── metadata.json
  ├── dict_concised_2014_20251229/
  │   └── dict_concised_2014.xlsx
  └── dict_concised_2014_20200929/
      └── dict_concised_2014.xlsx (old version)
  ```
