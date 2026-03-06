# you2idea Pipeline Details

## Data Flow

```
solograph-cli index-youtube              [Index videos → FalkorDB]
  ↓ (export-data.py)
make export                             [FalkorDB → all-videos.json + videos.json]
  ↓ (export-vectors.py)
make export-vectors                     [FalkorDB → vectors.bin + chunks-meta.json + graph.json]
  ↓ (fetch-transcripts.py)
make fetch-transcripts                  [Download VTT via yt-dlp → public/data/vtt/]
  ↓ (upload-r2.sh)
make upload                             [Upload to R2 CDN (incremental)]
  ↓
make build                              [Astro SSG/SSR build]
  ↓
make deploy                             [Cloudflare Pages deploy]
```

## FalkorDB Graph Schema (YouTube source)

**Nodes:**
- `Channel` — YouTube channel (handle, name, subscriber count)
- `Video` — indexed video (title, videoId, created, duration, view_count)
- `VideoChunk` — timestamped text segment (text, chapter, start_time, start_seconds, embedding)
- `Tag` — auto-detected topic (name, confidence score)

**Edges:**
- `Channel → HAS_VIDEO → Video`
- `Video → HAS_CHUNK → VideoChunk`
- `Video → HAS_TAG → Tag` (weighted by confidence)

## Useful Cypher Queries

```cypher
-- Video count per channel
MATCH (c:Channel)-[:HAS_VIDEO]->(v:Video)
RETURN c.name, COUNT(v) ORDER BY COUNT(v) DESC

-- Recent videos (last 30 days)
MATCH (v:Video) WHERE v.created > '2026-01-14'
RETURN v.title, v.created ORDER BY v.created DESC LIMIT 20

-- Videos about specific topic
MATCH (v:Video)-[:HAS_TAG]->(t:Tag)
WHERE t.name CONTAINS 'startup'
RETURN v.title, t.name, t.confidence ORDER BY t.confidence DESC

-- Chunk search by chapter name
MATCH (v:Video)-[:HAS_CHUNK]->(c:VideoChunk)
WHERE c.chapter CONTAINS 'idea'
RETURN v.title, c.chapter, c.start_time, LEFT(c.text, 200)
```

## Export Output Files

| File | Size | Content |
|------|------|---------|
| `all-videos.json` | ~680KB | All videos with chapters (search index) |
| `videos.json` | ~33KB | Channels + recent + stats (UI data) |
| `vectors.bin` | ~16MB | Float32 embeddings (N × 384) |
| `chunks-meta.json` | ~5MB | Chunk text + video metadata |
| `graph.json` | ~200KB | Channels, tags, edges, related videos |
| `vtt/*.vtt` | ~150MB total | Raw VTT subtitles (727 files) |
