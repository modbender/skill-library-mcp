# Photos Operations - iCloud

Use iCloud Photos access with explicit scope and controlled downloads.

## Basic Access Pattern

```bash
python3 - <<'PY'
from pyicloud import PyiCloudService
api = PyiCloudService("user@icloud.com")
print(list(api.photos.albums.keys())[:10])
PY
```

## Download Safety Pattern

1. Select album and sample one asset first.
2. Download original or requested variant.
3. Verify file integrity before scaling up.

## Common Reliability Checks

| Check | Why it matters |
|-------|----------------|
| Album exists before iteration | Prevents null/empty loops |
| Asset count matches expectation | Avoids partial assumptions |
| Version choice explicit (`original`, `thumb`) | Prevents wrong quality output |

## Boundaries

- Do not bulk download without user-approved destination and quota awareness.
- Do not delete remote photos from this workflow.
