# Wikimedia Commons API Reference

Source: [Commons API](https://commons.wikimedia.org/w/api.php), [MediaWiki API](https://www.mediawiki.org/wiki/Special:MyLanguage/API:Main_page)

## Base URL

- **Commons API:** `https://commons.wikimedia.org/w/api.php`

## Common parameters

- `action=query` – Fetch data.
- `format=json` – Prefer JSON.
- `origin=*` – For CORS from browsers if needed.

## Search for images (files)

- **action=query**  
  **list=search**  
  **srsearch=**&lt;query&gt; e.g. "Paris Eiffel Tower"  
  **srnamespace=6** – File namespace (images on Commons).  
  **srlimit=**&lt;number&gt;  
  **srwhat=** (e.g. text, title, nearmatch)

Example:

```
GET https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch=Paris+landmarks&srnamespace=6&srlimit=20&format=json
```

Response: `query.search[]` with `title` (e.g. "File:Example.jpg"), `pageid`, etc.

## Get image URLs and metadata

- **action=query**  
  **titles=**File:Example.jpg (pipe-separated for multiple)  
  **prop=imageinfo**  
  **iiprop=url|extmetadata|size|mime**  
  **iiurlwidth=** (optional, for thumbnail width)

Example:

```
GET https://commons.wikimedia.org/w/api.php?action=query&titles=File:Example.jpg&prop=imageinfo&iiprop=url|extmetadata&format=json
```

Response: `query.pages[pageid].imageinfo[0].url` (direct image URL), `extmetadata` (ImageDescription, Artist, LicenseShortName, etc.).

## Continuation (many results)

- Use **list=search** with **sroffset** for pagination.
- Use **query-continue** in response (or **continue** in API) when returned to get next page.

## Usage in this skill

1. **list=search** with `srsearch=<city name> landmarks` (or "tourist", "sights") and `srnamespace=6` to get file titles.
2. **prop=imageinfo** with **iiprop=url|extmetadata** for those titles to get download URL and captions/descriptions.
3. Download images from `imageinfo[].url` and store captions from `extmetadata.ImageDescription.value` or `extmetadata.ObjectName.value` for the travel brochure/video.
