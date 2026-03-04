# Serper.dev API Reference

Base: `https://google.serper.dev`
Auth: `X-API-KEY` header
All endpoints: POST with JSON body

## Endpoints (1 credit each, except shopping=2)

| Endpoint | Key Response Fields |
|---|---|
| `/search` | organic[], knowledgeGraph?, answerBox?, peopleAlsoAsk?, relatedSearches?, credits |
| `/news` | news[]{title, link, snippet, date, source, imageUrl} |
| `/images` | images[]{title, imageUrl, link, source, imageWidth, imageHeight} |
| `/videos` | videos[]{title, link, snippet, date, duration, channel} |
| `/places` | places[]{title, address, rating, ratingCount, category, phoneNumber, website} |
| `/shopping` | shopping[]{title, price, source, link, rating, ratingCount} ⚠️ 2 credits |
| `/scholar` | organic[]{title, link, publicationInfo, snippet, year, citedBy, pdfUrl?} |
| `/patents` | organic[]{title, snippet, priorityDate, filingDate, grantDate, publicationNumber, inventor, assignee} |
| `/autocomplete` | suggestions[]{value} |
| `/account` | {balance, rateLimit} |

## Common Params
- `q` (required) — query
- `num` (1-100) — results count
- `gl` — country code (us, it, de...)
- `hl` — language (en, it, de...)
- `tbs` — time filter (qdr:h, qdr:d, qdr:w, qdr:m, qdr:y)
- `page` — pagination
- `as_ylo` — scholar: from year
