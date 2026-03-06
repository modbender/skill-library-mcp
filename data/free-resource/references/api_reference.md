# API Reference

---

## Pixabay API

### Endpoints

| Endpoint | URL | Description |
|----------|-----|-------------|
| Search Images | `GET https://pixabay.com/api/` | Search royalty-free images |
| Search Videos | `GET https://pixabay.com/api/videos/` | Search royalty-free videos |

### Common Parameters (Images & Videos)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `key` | string | **required** | API key |
| `q` | string | *(all)* | Search term, max 100 chars |
| `lang` | string | `en` | Language: `cs,da,de,en,es,fr,id,it,hu,nl,no,pl,pt,ro,sk,fi,sv,tr,vi,th,bg,ru,el,ja,ko,zh` |
| `id` | string | – | Retrieve single resource by ID |
| `category` | string | – | `backgrounds,fashion,nature,science,education,feelings,health,people,religion,places,animals,industry,computer,food,sports,transportation,travel,buildings,business,music` |
| `min_width` | int | `0` | Minimum width (px) |
| `min_height` | int | `0` | Minimum height (px) |
| `editors_choice` | bool | `false` | Editor's Choice only |
| `safesearch` | bool | `false` | Safe content only |
| `order` | string | `popular` | `popular` or `latest` |
| `page` | int | `1` | Page number |
| `per_page` | int | `20` | Results per page (5-200) |

### Image-Only Parameters

| Parameter | Type | Default | Values |
|-----------|------|---------|--------|
| `image_type` | string | `all` | `all,photo,illustration,vector` |
| `orientation` | string | `all` | `all,horizontal,vertical` |
| `colors` | string | – | Comma-separated: `grayscale,transparent,red,orange,yellow,green,turquoise,blue,lilac,pink,white,gray,black,brown` |

### Video-Only Parameters

| Parameter | Type | Default | Values |
|-----------|------|---------|--------|
| `video_type` | string | `all` | `all,film,animation` |

### Image Response Fields

| Field | Description |
|-------|-------------|
| `id` | Unique identifier |
| `pageURL` | Source page on Pixabay |
| `type` | `photo`, `illustration`, or `vector` |
| `tags` | Comma-separated tags |
| `previewURL` | Low-res preview (max 150px) |
| `webformatURL` | Medium size (max 640px, valid 24h). Replace `_640` with `_180`,`_340`,`_960` for other sizes |
| `largeImageURL` | Scaled image (max 1280px) |
| `views,downloads,likes,comments` | Engagement metrics |
| `user,user_id,userImageURL` | Contributor info |

### Video Response Fields

| Field | Description |
|-------|-------------|
| `id` | Unique identifier |
| `pageURL` | Source page |
| `type` | `film` or `animation` |
| `tags` | Comma-separated tags |
| `duration` | Duration in seconds |
| `videos` | Object with `large` (3840x2160), `medium` (1920x1080), `small` (1280x720), `tiny` (960x540) renditions. Each has `url,width,height,size,thumbnail` |
| `views,downloads,likes,comments` | Engagement metrics |
| `user,user_id,userImageURL` | Contributor info |

### Rate Limits

- 100 requests / 60 seconds per API key
- Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- Cache results for 24 hours
- HTTP 429 on rate limit exceeded

---

## Freesound API

### Endpoints

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/apiv2/search/` | GET | Search sounds | Token |
| `/apiv2/sounds/<id>/` | GET | Get sound details | Token |
| `/apiv2/sounds/<id>/similar/` | GET | Get similar sounds | Token |
| `/apiv2/sounds/<id>/comments/` | GET | Get sound comments | Token |
| `/apiv2/sounds/<id>/download/` | GET | Download original file | OAuth2 |

### Authentication

#### Token Authentication (Recommended for read-only)

1. Create a Freesound account at https://freesound.org
2. Apply for API credentials at https://freesound.org/apiv2/apply
3. Use the "Client secret/Api key" from your credentials

**Usage:**
```bash
# As GET parameter
curl "https://freesound.org/apiv2/search/?query=piano&token=YOUR_API_KEY"

# As Authorization header
curl -H "Authorization: Token YOUR_API_KEY" "https://freesound.org/apiv2/search/?query=piano"
```

#### OAuth2 Authentication (Required for downloads & write operations)

OAuth2 is required for downloading original files, uploading, rating, etc.

### Search Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | – | Search term (supports +/- modifiers, phrases in quotes) |
| `filter` | string | – | Filter results (see filter syntax below) |
| `sort` | string | `score` | Sort order (see sort options below) |
| `fields` | string | `id,name,tags,username,license` | Comma-separated fields to return |
| `page` | int | `1` | Page number |
| `page_size` | int | `15` | Results per page (max 150) |
| `group_by_pack` | bool | `0` | Group results by pack |
| `similar_to` | int/array | – | Find sounds similar to ID or vector |
| `similar_space` | string | – | Similarity space (laion_clap, freesound_classic) |

### Sort Options

| Option | Description |
|--------|-------------|
| `score` | Relevance (default) |
| `duration_desc` / `duration_asc` | By duration |
| `created_desc` / `created_asc` | By upload date |
| `downloads_desc` / `downloads_asc` | By download count |
| `rating_desc` / `rating_asc` | By rating |

### Filter Syntax

```
# Basic filter
filter=tag:piano

# Range filter (numeric)
filter=duration:[0.1 TO 1.0]
filter=avg_rating:[3 TO *]

# Logical operators
filter=type:(wav OR aiff)
filter=description:(piano AND note)

# Geographic filter (distance)
filter={!geofilt sfield=geotag pt=41.3833,2.1833 d=10}
```

### Available Filters

**Basic Metadata:**
- `id`, `name`, `tag`, `description`, `category`, `subcategory`
- `username`, `pack`, `license`, `type` (wav, aiff, ogg, mp3, m4a, flac)
- `channels`, `samplerate`, `bitrate`, `bitdepth`, `filesize`, `duration`
- `created`, `is_geotagged`, `is_remix`, `was_remixed`, `is_explicit`
- `num_downloads`, `avg_rating`, `num_ratings`, `num_comments`

**Audio Descriptors:**
- `bpm`, `bpm_confidence`
- `pitch`, `pitch_min`, `pitch_max`, `pitch_var`
- `note_name`, `note_midi`, `note_confidence`
- `tonality`, `tonality_confidence`
- `loudness`, `dynamic_range`
- `spectral_centroid`, `spectral_entropy`, `spectral_flatness`
- `temporal_centroid`, `log_attack_time`
- `loopable`, `single_event`, `reverbness`

### Sound Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Unique identifier |
| `url` | string | Freesound page URL |
| `name` | string | Sound name |
| `tags` | array | Tag array |
| `description` | string | Description text |
| `category` | string | Top-level category |
| `subcategory` | string | Sub-category |
| `geotag` | string | Latitude/longitude |
| `created` | string | Upload date |
| `license` | string | License type |
| `type` | string | File type (wav, mp3, etc.) |
| `channels` | int | Number of channels |
| `filesize` | int | File size in bytes |
| `bitrate` | int | Bitrate |
| `bitdepth` | int | Bit depth |
| `duration` | float | Duration in seconds |
| `samplerate` | int | Sample rate |
| `username` | string | Uploader username |
| `num_downloads` | int | Download count |
| `avg_rating` | float | Average rating (0-5) |
| `num_ratings` | int | Rating count |
| `num_comments` | int | Comment count |
| `previews` | object | Preview audio URLs |
| `images` | object | Waveform/spectrogram URLs |

### Preview URLs

```json
{
  "preview-hq-mp3": "https://... (~128kbps)",
  "preview-lq-mp3": "https://... (~64kbps)",
  "preview-hq-ogg": "https://... (~192kbps)",
  "preview-lq-ogg": "https://... (~80kbps)"
}
```

### Rate Limits & Usage

- API is rate-limited; check response headers for limits
- Cache results when possible
- Attribute Freesound and the sound creator when using sounds
- Respect the license terms of each sound

### License Types

Common licenses on Freesound:
- Creative Commons 0 (Public Domain)
- Creative Commons Attribution
- Creative Commons Attribution Noncommercial

---

## Jamendo API

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v3.0/tracks` | GET | Search/get tracks |
| `/v3.0/albums` | GET | Search/get albums |
| `/v3.0/artists` | GET | Search/get artists |
| `/v3.0/artists/tracks` | GET | Get artist's tracks |
| `/v3.0/artists/albums` | GET | Get artist's albums |

### Authentication

1. Create a Jamendo account at https://www.jamendo.com
2. Apply for API credentials at https://devportal.jamendo.com/
3. Use the Client ID in your requests

**Usage:**
```bash
curl "https://api.jamendo.com/v3.0/tracks/?client_id=YOUR_CLIENT_ID&search=rock"
```

### Track Search Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `client_id` | string | **required** | Client ID from devportal |
| `search` | string | – | Free text search |
| `namesearch` | string | – | Fuzzy name search |
| `tags` | string | – | Tag search (AND logic, `+` separated) |
| `fuzzytags` | string | – | Fuzzy tag search (OR logic) |
| `artist_id` | int | – | Filter by artist ID |
| `artist_name` | string | – | Filter by artist name |
| `album_id` | int | – | Filter by album ID |
| `limit` | int | 10 | Results per page (max 200) |
| `offset` | int | 0 | Pagination offset |
| `order` | string | `relevance` | Sort order |
| `include` | string | – | Extra info: `musicinfo`, `stats`, `licenses`, `lyrics` |

### Music Attribute Filters

| Parameter | Values | Description |
|-----------|--------|-------------|
| `vocalinstrumental` | `vocal`, `instrumental` | Vocal or instrumental |
| `acousticelectric` | `acoustic`, `electric` | Acoustic or electric |
| `speed` | `verylow`, `low`, `medium`, `high`, `veryhigh` | Music speed |
| `gender` | `male`, `female` | Vocalist gender |
| `lang` | 2-letter code | Lyrics language |
| `featured` | `true`, `1` | Featured tracks only |

### Date/Duration Filters

| Parameter | Format | Description |
|-----------|--------|-------------|
| `datebetween` | `yyyy-mm-dd_yyyy-mm-dd` | Release date range |
| `durationbetween` | `from_to` | Duration range in seconds |

### Audio Formats

| Format | Quality |
|--------|---------|
| `mp31` | 96kbps MP3 |
| `mp32` | 192kbps VBR MP3 (recommended) |
| `ogg` | OGG Vorbis |
| `flac` | Lossless FLAC |

### Sort Options

Add `_asc` or `_desc` suffix for direction:
- `relevance` (default)
- `popularity_week`, `popularity_month`, `popularity_total`
- `downloads_week`, `downloads_month`, `downloads_total`
- `listens_week`, `listens_month`, `listens_total`
- `name`, `releasedate`, `duration`

### Track Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Track ID |
| `name` | string | Track name |
| `duration` | int | Duration in seconds |
| `artist_id` | string | Artist ID |
| `artist_name` | string | Artist name |
| `album_id` | string | Album ID |
| `album_name` | string | Album name |
| `album_image` | string | Album cover URL |
| `audio` | string | Stream URL |
| `audiodownload` | string | Download URL |
| `audiodownload_allowed` | bool | Whether download is allowed |
| `license_ccurl` | string | Creative Commons license URL |
| `releasedate` | string | Release date (yyyy-mm-dd) |
| `image` | string | Track image URL |
| `shorturl` | string | Short link |
| `shareurl` | string | Share link |

### Music Info (via `include=musicinfo`)

```json
{
  "vocalinstrumental": "instrumental",
  "lang": "",
  "gender": "",
  "acousticelectric": "electric",
  "speed": "high",
  "tags": {
    "genres": ["rock", "electronic"],
    "instruments": ["guitar", "drums"],
    "vartags": ["energetic", "happy"]
  }
}
```

### Album Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Album ID |
| `name` | string | Album name |
| `releasedate` | string | Release date |
| `artist_id` | string | Artist ID |
| `artist_name` | string | Artist name |
| `image` | string | Album cover URL |
| `zip` | string | ZIP download URL |
| `zip_allowed` | bool | Whether download is allowed |

### Artist Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Artist ID |
| `name` | string | Artist name |
| `website` | string | Artist website |
| `joindate` | string | Join date |
| `image` | string | Artist image URL |
| `shorturl` | string | Short link |
| `shareurl` | string | Share link |

### Rate Limits

- 35,000 requests / month (non-commercial apps)
- Cache results when possible
- Attribution required for Creative Commons licensed content

### License Types

Jamendo tracks are published under Creative Commons licenses:
- CC BY (Attribution)
- CC BY-NC (Attribution-NonCommercial)
- CC BY-ND (Attribution-NoDerivs)
- CC BY-NC-ND (Attribution-NonCommercial-NoDerivs)
- CC BY-SA (Attribution-ShareAlike)
- CC BY-NC-SA (Attribution-NonCommercial-ShareAlike)
